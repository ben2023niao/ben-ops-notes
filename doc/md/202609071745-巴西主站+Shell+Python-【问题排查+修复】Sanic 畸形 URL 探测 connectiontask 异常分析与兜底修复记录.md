---
id: "doc-397fa77a9901"
title: "【问题排查+修复】Sanic 畸形 URL 探测 connectiontask 异常分析与兜底修复记录"
date: "2026-09-07T17:45:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Nginx", "自动化", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-07-1745-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%2B%E4%BF%AE%E5%A4%8D%E3%80%91Sanic%E7%95%B8%E5%BD%A2URL%E6%8E%A2%E6%B5%8Bconnection_task%E5%BC%82%E5%B8%B8%E5%88%86%E6%9E%90%E4%B8%8E%E5%85%9C%E5%BA%95%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-07-1745-【问题排查+修复】Sanic畸形URL探测connection_task异常分析与兜底修复记录.md"
sourceSha256: "dc0d444120c1177688ef5e7690625b2a4f1dc35aa950e05b29e8c997d726d848"
sourceSystem: "project-doc"
---

# 【问题排查+修复】Sanic 畸形 URL 探测 connectiontask 异常分析与兜底修复记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-09-07-1745-【问题排查+修复】Sanic畸形URL探测connection_task异常分析与兜底修复记录.md`

> 整理日期：2026-09-07 17:45｜日期依据：文件名日期

时间：2026-09-07 17:45（Asia/Manila）
项目：某业务公司 / PGServer master
范围：巴西后端 01 vendor_d（bizops-vendor_d-release-01）→ 全部 Sanic 厂家服务（代码层兜底）
结果：✅ 根因定位 + 仓库代码修复 + 隔离验证 PASS + 本地提交

## 一、问题

群内贴出的线上报错：

```text
Srv 0 2026-09-06 23:29:16 +0000 ERROR: protocol.connection_task uncaught
httptools.parser.errors.HttpParserInvalidURLError: invalid url b'icanhazip.com:443'
...
sanic.exceptions.BadRequest: Bad Request / Bad URL: icanhazip.com:443
```

疑问：icanhazip.com:443 这个 URL 从哪来？Nginx 转发是否漏配
`proxy_set_header X-Real-IP $remote_addr`？

## 二、定位证据

```text
来源文件：后端 01 /opt/pgserver/logs/bizops-vendor_d-release-01/vendor_d.log-20260907-000241.gz
行号：7928（Srv 0 2026-09-06 23:29:16 +0000）
Traceback 与群内截图逐行一致：Request.__init__ parse_url 失败 → BadRequest
→ error_response → create_empty_request 再次用同一畸形 URL 构造请求 → 二次异常
→ connection_task uncaught。
```

该异常没有出现在宝塔/备用机 Nginx access log，因为：

```text
后端 01 公网 IP 192.0.2.10 的 9090（platform-api）与 9102（vendor_d 容器
9018 映射）可被公网直接访问（GCP 防火墙 game9000-10000 192.0.2.3/0 全开）。
探测请求绕过 Nginx 直达 Sanic，因此 Nginx 无日志、X-Real-IP 无从参与。
```

## 三、根因

```text
1. 外部扫描器把游戏/API 端口当开放 HTTP 代理探测，发送：
   CONNECT icanhazip.com:443 HTTP/1.1
   （同源还有 google.com / proxiesfood.com / ipify 等，仓库与线上历史日志均有）。
2. Sanic 的 httptools 只能解析 origin-form / absolute-form URL，解析不了
   authority-form 的 icanhazip.com:443，抛 BadRequest。
3. Sanic 25.3.0 error_response 内 create_empty_request 会用同一原始 URL 再建
   一次 Request，解析再次失败 → 二次异常未捕获 → 连接任务 uncaught、无响应。
   这是 Sanic 上游长期已知问题（sanic-org/sanic #2528 / #2735），25.3.0 与
   后续版本该路径仍相同，单靠升级 Sanic 不能消除。
4. 不影响其他 worker/服务；只有被探测的那条连接异常结束，服务未中断、非被攻破。
```

回答群内两个问题：

```text
Q1 icanhazip.com:443 怎么来的？
A1 公网扫描器探测“服务器能否当开放代理”的标准请求。仓库内 icanhazip 只用于
   巡检脚本查询公网出口 IP，不在任何业务/反代请求路径上。

Q2 nginx 有没有配 X-Real-IP？
A2 已配置。socket/api/pg/all-games/vendor_a 等公共反代 location 均有
   proxy_set_header X-Real-IP $remote_addr。X-Real-IP 只影响后端取真实客户端
   IP，与 URL 解析异常无关；本次请求根本没有经过 nginx。
```

## 四、代码修复

新增仓库根 `sitecustomize.py`：

```text
容器 PYTHONPATH=/app 且所有服务从 /app 启动，Python 解释器会自动加载该文件。
它把 sanic.http.http1.Http.create_empty_request 替换为安全版本：原始 URL 解析
失败时回退为 / 构造空请求，使 Sanic 正常返回 400 Bad Request，不再产生
connection_task uncaught。对全部 Sanic 厂家服务统一生效，幂等，无 Sanic
依赖版本变更、无需修改 share.so 或业务代码。
```

## 五、验证

```text
1. 语法检查：python3 -m py_compile sitecustomize.py PASS。
2. 运行中 vendor_d 容器内单元验证：原 create_empty_request 对畸形 URL 抛
   BadRequest；补丁回退后成功构造 Request（raw_url=/）。
3. 隔离测试容器（pgserver:master-035305f3，--network none）：
   - /app/sitecustomize.py 自动导入 PASS，Http.create_empty_request
     已被替换为 _safe_create_empty_request；
   - CONNECT icanhazip.com:443 实测返回 HTTP/1.1 400 Bad Request，
     无 uncaught 异常。
4. 全程未触碰运行中的生产进程，测试容器与临时文件已清理。
```

## 六、安全建议（待执行）

```text
1. 后端 01 公网 9090/9102 直开，是这类探测能直达 Sanic 的根因；建议收敛 GCP
   防火墙规则（game9000-10000 从 192.0.2.3/0 收窄为 VPC 内网 + 需要的厂家/运维
   源 IP），需先确认厂家回调等公网访问依赖。
2. 线上容器生效方式：把 sitecustomize.py 同步进各容器 /app 后重启对应服务
   （或随下次镜像发布自动带入）；建议按发布窗口执行并逐容器验证。
```

## 七、群通知回执

```text
5237 连通性测试
5238 任务开始 + 本地/远端提交确认（补发）
5239 日志定位（补发）
5240 来源分析 / X-Real-IP 回答（补发）
5241 根因判定（补发）
5242 代码修复与隔离验证
5243 doc 完成
5244 本地提交结果
```

## 八、结论

```text
非授权安全测试成功、非业务故障、与 X-Real-IP 无关；是公网扫描器对直连端口的开放
代理探测触发了 Sanic 错误响应路径的二次异常。代码层兜底修复已完成并本地提交，
生产容器同步与防火墙收敛作为待执行项跟进。
```
