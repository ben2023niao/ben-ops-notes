---
id: "doc-0beae11b7a39"
title: "【核对】香港腾讯云 EdgeOne 历史接入与本机凭据归档记录"
date: "2026-11-06T22:11:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Nginx", "CDN", "DNS", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-11-06-2211-%E3%80%90%E6%A0%B8%E5%AF%B9%E3%80%91%E9%A6%99%E6%B8%AF%E8%85%BE%E8%AE%AF%E4%BA%91EdgeOne%E5%8E%86%E5%8F%B2%E6%8E%A5%E5%85%A5%E4%B8%8E%E6%9C%AC%E6%9C%BA%E5%87%AD%E6%8D%AE%E5%BD%92%E6%A1%A3%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-11-06-2211-【核对】香港腾讯云EdgeOne历史接入与本机凭据归档记录.md"
sourceSha256: "cbc545fafefcb718e3f4f255e205bd5c7bcc65595238afd9838bafb26a10f4b3"
sourceSystem: "project-doc"
---

# 【核对】香港腾讯云 EdgeOne 历史接入与本机凭据归档记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202611062211-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BLinux%2BNginx-%E3%80%90%E6%A0%B8%E5%AF%B9%E3%80%91%E9%A6%99%E6%B8%AF%E8%85%BE%E8%AE%AF%E4%BA%91%20EdgeOne%20%E5%8E%86%E5%8F%B2%E6%8E%A5%E5%85%A5%E4%B8%8E%E6%9C%AC%E6%9C%BA%E5%87%AD%E6%8D%AE%E5%BD%92%E6%A1%A3%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-11-06 22:11｜日期依据：文件名日期

更新时间：2026-11-06 22:11（Asia/Manila）

执行范围：某业务公司 主仓库、独立 `cn` 工作区、香港线上域名快照、EdgeOne 只读 API、DNS 与 HTTP 健康检查。

## 一、请求

```text
1. 检查香港域名历史配置变化；
2. 确认香港是否已经使用腾讯云 CDN / EdgeOne；
3. 若未使用则接入，若已使用则核对运行状态；
4. 将腾讯云账号及 API 凭据安全保存在本机，供后续 AI 操作；
5. 汇总文档发群；
6. 提交本地 Git，并发送提交结果。
```

## 二、开始前基线

主仓库：

```text
路径：/Users/operator/Projects/ops/private-notes/master
本地 master：0b5af47f
origin/master：a72f41fb
origin/ben：9f59b4f3
工作区：干净
本地 master 领先 origin/master 18 个提交
```

独立香港仓库：

```text
路径：/Users/operator/Projects/ops/private-notes/cn
本地 cn：1fbe688f
origin/cn：5c3b3de6
工作区：干净
本地 cn 领先 origin/cn 142 个提交
```

说明：`origin/cn` 最新提交时间为 2026-08-12，当前腾讯 EdgeOne 历史只存在于本机
未推送的 `cn` 提交中，不能只看远程分支。

## 三、历史配置变化

已确认的关键提交：

```text
2026-09-30 12:24  371f660d  m4q7z1.shop 接入 EdgeOne，动态+静态走香港 standby Nginx
2026-09-30 16:50  cdac4bdc  香港后端域名配置切换到 m4q7z1.shop
2026-10-02 14:47  e241b85c  新增 k8x2v9.shop 并切换香港后端
2026-10-02 14:50  74d125a3  新增 p3w9n5.shop 商户入口，三域名写入香港 01/02
2026-10-02 15:01  69da705a  EdgeOne 三站点规则中文标注
2026-10-08 14:21  ce069e9b  修复 EdgeOne HTTP 回源导致 X-Forwarded-Proto=http
2026-10-08 14:43  ffa52a77  修复 EdgeOne 链路目录跳转变 HTTP
2026-10-14 10:54  1fbe688f  清理香港 PP 静态资源 EdgeOne 缓存
```

本地 `cn` 工作树共 99 份 Markdown/TXT，其中 35 份明确涉及：

```text
腾讯云 / 腾讯 CDN / Tencent Cloud / EdgeOne
m4q7z1.shop / k8x2v9.shop / p3w9n5.shop
```

主仓库香港线上域名快照 `infrastructure/hongkong/domains/live-20261024/`
也显示：

```text
7 个厂商文件同时包含 m4q7z1.shop 与 k8x2v9.shop；
pg.json 另外包含 p3w9n5.shop；
r2v8k4.shop 未进入线上域名配置。
```

## 四、腾讯云当前状态

通过本机 Keychain 中的 API 凭据调用腾讯云官方只读接口：

```text
CDN DescribeDomains：0 个域名
EdgeOne DescribeZones：4 个站点
```

| 站点 | Zone ID | 站点状态 | 加速域名 | 域名状态 | 当前用途 |
| --- | --- | --- | ---: | --- | --- |
| `m4q7z1.shop` | `zone-3vm5evyb78ic` | active | 22 | 22 online | 香港游戏主入口 |
| `k8x2v9.shop` | `zone-3vm7ccg417yf` | active | 22 | 22 online | 香港游戏备用入口 |
| `p3w9n5.shop` | `zone-3vm7chzbxkcb` | active | 2 | 2 online | 香港商户 / socket |
| `r2v8k4.shop` | `zone-3vm7cf444lhw` | initializing | 0 | 无 | 空站点，无业务 |

三个正式站点共 46 个加速域名，全部回源：

```text
192.0.2.37:80 HTTP
```

对应机器：

```text
bizops-hongkong-nginx-standby-01
公网：192.0.2.37
内网：192.0.2.1
```

游戏站点结构：

```text
动态 8 个：
pg-games / api / vendor_b-games / pp-games /
ppk-games / vendor_d-games / vendor_c-games / g759-games

静态 14 个：
pg-static / pg3-static / pg4-static / pg5-static / pg6-static / pg7-static /
pp-static / ppk-static / vendor_d-static / vendor_c-static / g759-static /
vendor_b-static / vendor_b-static1 / vendor_b-static2
```

商户站点结构：

```text
p3w9n5.shop
socket.p3w9n5.shop
```

## 五、公网验证

DNS 已解析到 EdgeOne 节点，抽样 8 个端点全部 HTTP 200：

```text
https://p3w9n5.shop/healthz                 200
https://socket.p3w9n5.shop/healthz          200
https://pg-games.m4q7z1.shop/health         200
https://pg-static.m4q7z1.shop/health.json   200
https://vendor_b-games.m4q7z1.shop/health       200
https://pg-games.k8x2v9.shop/health         200
https://pg-static.k8x2v9.shop/health.json   200
https://vendor_b-games.k8x2v9.shop/health       200
```

静态资源抽样返回：

```text
HTTP/2 200
server: nginx/1.18.0 (Ubuntu)
eo-cache-status: HIT
```

## 六、结论

```text
香港已经使用腾讯云 EdgeOne，不需要再次接入。

当前状态：
1. m4q7z1.shop、k8x2v9.shop、p3w9n5.shop 三个站点全部 active；
2. 46 个正式加速域名全部 online；
3. 三站统一回源香港 standby Nginx 192.0.2.37:80；
4. 动态、静态、商户抽样均正常，静态命中 EdgeOne 缓存；
5. r2v8k4.shop 仅为空站点，不建议贸然投入使用。

本轮未修改腾讯云、DNS、Nginx、服务器、容器或业务数据。
```

## 七、本机凭据保存

按用户要求，腾讯云凭据已保存到 macOS Keychain，未写入 Git 或本文档。

API 凭据：

```text
Keychain service：bizops-tencent-edgeone-api
Keychain account：[邮箱已脱敏]
内容：account_id、username、secret_id、secret_key、region 的 JSON
region：ap-singapore
```

控制台登录密码：

```text
Keychain service：bizops-tencent-edgeone-console
Keychain account：[邮箱已脱敏]
```

本机索引：

```text
/Users/operator/.config/tencentcloud/bizops-edgeone.md
权限：600
```

索引文件只包含账号 ID、用户名、Keychain service 名称和读取方式，不含密码或 SecretKey。

## 八、安全事项

```text
1. 当前使用的是腾讯云主账号 API 密钥；
2. 长期操作应改为仅授予 QcloudTEOFullAccess 的子用户密钥；
3. 主账号 SecretKey 已在聊天中出现，应尽快轮换；
4. 本机 cn 仓库的 old-gitlab remote 内嵌旧凭据，应轮换后改用 SSH key 或 credential helper；
5. AI 使用时只在进程内从 Keychain 读取，禁止输出密钥、写入命令行参数或提交仓库。
```

## 九、群通知

```text
开始核对：message_id 886
汇总：message_id 887
文档：message_id 888
提交结果：发送后补录
```
