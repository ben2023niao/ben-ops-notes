---
id: "doc-47d98e7d5980"
title: "【优化+修复】发布台历史镜像选择、逐节点状态与香港 vendor_b 502 修复记录"
date: "2026-11-05T17:44:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "监控告警", "自动化", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-11-05-1744-%E3%80%90%E4%BC%98%E5%8C%96%2B%E4%BF%AE%E5%A4%8D%E3%80%91%E5%8F%91%E5%B8%83%E5%8F%B0%E5%8E%86%E5%8F%B2%E9%95%9C%E5%83%8F%E9%80%89%E6%8B%A9%E9%80%90%E8%8A%82%E7%82%B9%E7%8A%B6%E6%80%81%E4%B8%8E%E9%A6%99%E6%B8%AFvendor_b502%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-11-05-1744-【优化+修复】发布台历史镜像选择逐节点状态与香港vendor_b502修复记录.md"
sourceSha256: "4be51d64b4ac3999064dce60ced97f5c22ff158c2990fe068328085e2090ddac"
sourceSystem: "project-doc"
---

# 【优化+修复】发布台历史镜像选择、逐节点状态与香港 vendor_b 502 修复记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202611051744-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BDocker-%E3%80%90%E4%BC%98%E5%8C%96%2B%E4%BF%AE%E5%A4%8D%E3%80%91%E5%8F%91%E5%B8%83%E5%8F%B0%E5%8E%86%E5%8F%B2%E9%95%9C%E5%83%8F%E9%80%89%E6%8B%A9%E3%80%81%E9%80%90%E8%8A%82%E7%82%B9%E7%8A%B6%E6%80%81%E4%B8%8E%E9%A6%99%E6%B8%AF%20vendor_b%20502%20%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-11-05 17:44｜日期依据：文件名日期

更新时间：2026-11-05 17:44（Asia/Manila）

执行范围：`bizops-ops-console`、香港 01/02、03 香港运行模板、vendor_b 公网链路。

## 一、结论

本轮需求已完成并验证：

- 版本号旁新增“历史版本”，读取 03 私有镜像仓库中八个厂家共同存在的正式标签；
- 历史标签可直接回填版本号，用于重发或回滚；
- 一键发布输出逐行标记实际节点名称与 IP；
- 服务器状态改为读取六台节点的实时容器，不再沿用历史任务结果；
- 状态校验核对具体厂家容器名、运行状态、镜像版本、重启和 OOM；
- 香港全量重发成功，01/02 各 10 个容器统一为 `2026110516-ben`；
- 香港节点 `configs-api.py` 在发布前后 SHA256 不变；
- 香港 vendor_b 502 已恢复，公网连续 12 次请求全部 HTTP 200。

## 二、开始前基线

```text
本地 master：7efba04f
本地工作区：3 个与本任务相关的未提交修改
origin/master：a72f41fb
origin/ben：9748ad32
03 HEAD：9f59b4f3
03 工作区：干净
控制台：bizops-ops-console:20261105-r6
控制台运行中任务：0
```

## 三、香港 vendor_b 502 根因

旧香港发布任务在停止 HK01 后中止：

```text
stopped game-service-api-prod
stopped game-service-pg-prod
stopped game-service-vendor_b-prod
failed on game-service-vendor_a_ws-prod: unknown vendor
```

该时段 HK01 缺失 `api/pg/vendor_b` 三个容器，上游轮询命中 HK01 时返回 502。
HK02 当时正常。应用日志没有 `MSG199`，因此前端看到的 502 来自上游节点缺失，
不是 vendor_b 应用抛出业务异常。

修复：

- 香港 `stop.sh` 增加 `vendor_a_ws` 白名单；
- 页面持久化的旧九厂家香港选择自动迁移为当前十厂家；
- HK01 缺失的三个容器先恢复；
- 随后通过发布页全量重发香港 01/02，消除混合版本。

## 四、发布台改造

### 4.1 历史版本选择

新增受鉴权接口：

```text
GET /api/image-tags
```

接口在 03 查询以下八个仓库并只返回全部仓库共有的正式版本标签：

```text
api pg vendor_a ppk pp vendor_c vendor_d g759
```

标签过滤规则：

```text
YYYYMMDD-ben
YYYYMMDDHH-ben
```

页面点击“历史版本”后展示公共标签；“使用此版本”会立即回填版本号并写入审计。
实测可用标签包含：

```text
2026110516-ben
20261105-ben
20261102-ben
20261028-ben
```

### 4.2 逐节点实时输出

每个后端节点输出不再混在一起，示例：

```text
[香港 01 192.0.2.16] ========== 拉取目标镜像 ==========
[02 192.0.2.17] ========== 停止容器 ==========
[香港 02 192.0.2.17] ========== 校验启动镜像 ID ==========
```

同时输出机器可解析的事件：

```text
NODE_EVENT|start|hk|香港 01|192.0.2.16
NODE_EVENT|done|hk|香港 01|192.0.2.16|0
```

### 4.3 实时服务器状态

新增受鉴权接口：

```text
GET /api/server-status
```

服务端并行探测：

```text
巴西 01/02/04/05：各 9 个指定业务容器
香港 01/02：各 10 个指定业务容器
```

状态卡显示当前节点实际进度，例如“拉取目标镜像”“停止容器”“同步文件”；
发布结束后刷新为实际运行数，并识别缺少容器、版本混杂、重启中、OOM 和历史重启。
历史任务失败不会再污染当前节点状态。

### 4.4 香港配置保护

香港发布同步明确排除：

```text
conf/configs-api.py
```

执行门禁：

```text
发布前备份节点本地 configs-api.py
rsync 排除 conf/configs-api.py
校验同步前后目标 SHA256 完全一致
```

本次香港 01/02 发布后 SHA256 均为：

```text
e80f6cb4b21c7f9a3694f689cd1a058da68794a7dc4f68cadce0ef80a8e82938
```

## 五、香港全量发布结果

```text
Job：ee10134bc262493b
版本：2026110516-ben
状态：passed
退出码：0
页面：无 JS 异常
```

两台节点最终均为：

```text
game-service-api-prod
game-service-pg-prod
game-service-vendor_b-prod
game-service-vendor_a-prod
game-service-vendor_a_ws-prod
game-service-ppk-prod
game-service-pp-prod
game-service-vendor_c-prod
game-service-vendor_d-prod
game-service-g759-prod
```

发布后实时状态：

```text
br01  ok  9/9
br02  ok  9/9
br04  ok  9/9
br05  ok  9/9
hk01  ok  10/10
hk02  ok  10/10
```

## 六、vendor_b 验证

节点：

```text
HK01 game-service-vendor_b-prod：running，RestartCount=0，OOMKilled=false
HK02 game-service-vendor_b-prod：running，RestartCount=0，OOMKilled=false
```

最近 10 分钟容器日志：

```text
MSG199 命中：0
ERROR / CRITICAL / Traceback / Exception：0
```

接口：

```text
https://vendor_b-api.hkplaycore.com/game-setting/game-info-list
https://vendor_b-games.m4q7z1.shop/game-setting/game-info-list
https://vendor_b-games.k8x2v9.shop/game-setting/game-info-list
```

三项均返回 HTTP 200，响应 `Code=0`、`Message=成功`；公网接口连续 12 次请求
全部 HTTP 200。

## 七、控制台部署

代码备份：

```text
/opt/bizops-ops-console/backups/code-before-20261105-172830.tar.gz
SHA256：1188a2c9e4192ebcaac3a967a36e3ffd2a9b2f6701536907e24d17e4578df9d4
```

最终容器：

```text
image：bizops-ops-console:20261105-r7
image ID：sha256:4b48df3c5d2d82db19a468168f4e506e125afaafe1008d93d1e9ebc7c6e16322
status：running / healthy
entry：http://192.0.2.8:8787
```

生产验证：

```text
/api/health：200，version=2026-11-05-r7
/api/image-tags：200，只返回正式版本标签
/api/server-status：200，六台节点全部 ok
手机视口 Chromium 390×844：JS 错误 0
生成香港单节点/批量/一键发布命令：bash -n 全部通过
```

## 八、回滚

控制台代码回滚：

```bash
cd /opt/bizops-ops-console
tar -xzf backups/code-before-20261105-172830.tar.gz -C .
docker compose -f deploy/docker-compose.yml up -d --force-recreate
```

香港业务回滚可直接在页面“历史版本”选择上一正式标签后重发。节点
`configs-api.py` 由节点本地独立保留，回滚发布也不会覆盖。

## 九、群通知与 Git

汇总消息：854

完整文档消息：855

Git 提交：已提交本地 `master`；最终提交 SHA 与结果见监控群。
