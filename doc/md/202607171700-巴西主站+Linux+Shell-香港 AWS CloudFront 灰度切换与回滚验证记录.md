---
id: "doc-bf2ee9bd80e2"
title: "香港 AWS CloudFront 灰度切换与回滚验证记录"
date: "2026-07-17T17:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Docker", "Nginx", "CDN", "DNS", "安全运维"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/hongkong/cn/2026-07-17-1700-%E3%80%90%E7%BD%91%E7%BB%9C%E8%B0%83%E6%95%B4%E3%80%91%E9%A6%99%E6%B8%AFAWS-CloudFront%E7%81%B0%E5%BA%A6%E5%88%87%E6%8D%A2%E4%B8%8E%E5%9B%9E%E6%BB%9A%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/hongkong/cn/2026-07-17-1700-【网络调整】香港AWS-CloudFront灰度切换与回滚验证记录.md"
sourceSha256: "87878aa7b9f189f007960fc850343e01545af205e28d84df0712d7fa8178ef71"
sourceSystem: "project-doc"
---

# 香港 AWS CloudFront 灰度切换与回滚验证记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202607171700-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BLinux%2BShell-%E9%A6%99%E6%B8%AF%20AWS%20CloudFront%20%E7%81%B0%E5%BA%A6%E5%88%87%E6%8D%A2%E4%B8%8E%E5%9B%9E%E6%BB%9A%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-07-17 17:00｜日期依据：文件名日期

> 后续范围更新：同日稍后 `cn` 收口为 PG、PP、PPK、PANDA、vendor_b + platform-api。当前状态为静态 50、动态游戏 25、核心/API 8；vendor_a、vendor_c、Socket 已下线。完整变更见 `2026-07-17-1900-【架构改造+网络调整】香港CN五厂商收口与vendor_b-AWS接入完整记录.md`。下文保留首次灰度过程，供审计和回滚参考。

## 执行结果

2026-07-17 已按厂商和域名前缀完成 Cloudflare DNS 灰度切换：

| 类型 | 已切换 | 验收结果 |
| --- | ---: | --- |
| 静态资源 | 55 | 55/55 为 DNS-only CNAME、TTL 60，HTTP 200、CORS 正常并由 CloudFront 响应 |
| 动态游戏 | 20 | PG、PP、PPK、PANDA 各 5 个域名，20/20 配置正确 |
| 核心/API | 8 | 8/8 配置正确；Verify 200，WebSocket `/ws2` 返回 101 |
| **合计** | **83** | **83/83 DNS 配置复核通过** |

当前链路：

```text
静态域名 -> Cloudflare DNS-only CNAME -> CloudFront OAC -> 香港私有 S3
动态域名 -> Cloudflare DNS-only CNAME -> CloudFront -> 香港 Nginx -> 外部双后端
```

Cloudflare 只负责权威 DNS，不再代理这些精确域名的业务流量。原有通配 A 记录仍保留，回滚时删除精确 CNAME 即可恢复通配记录接管。

## 已切换域名

以下静态前缀均已覆盖 `hkcloudplay01.com` 至 `hkcloudplay05.com`：

```text
pg-static
pg3-static
pg4-static
pg5-static
vendor_a-statics
vendor_a-statics1
vendor_a-statics2
pp-static
ppk-static
vendor_c-static
vendor_d-static
```

以下动态游戏前缀均已覆盖 `hkcloudplay01.com` 至 `hkcloudplay05.com`：

```text
pg-games
pp-games
ppk-games
vendor_d-games
```

已切换的核心/API 域名：

```text
api.hkplaycore.com
games.hkplaycore.com
verify.hkplaycore.com
pg-api.hkplaycore.com
pp-api.hkplaycore.com
ppk-api.hkplaycore.com
vendor_d-api.hkplaycore.com
socket.hkplaycore.com
```

## 暂不切换

下列 12 个动态域名没有创建精确 CloudFront CNAME，仍由原通配记录处理：

```text
vendor_a-api.hkplaycore.com
vendor_a-games.hkcloudplay01.com ～ vendor_a-games.hkcloudplay05.com

vendor_c-api.hkplaycore.com
vendor_c-games.hkcloudplay01.com ～ vendor_c-games.hkcloudplay05.com
```

原因：vendor_a 当前源站链路返回 `502`，vendor_c 当前源站链路返回 `503`。强制走 CloudFront 时结果一致，因此没有把源站故障扩大到新 DNS。待后端恢复后，必须先强制解析验证，再单独灰度切换。

## 灰度批次与备份

每次写 DNS 前，脚本都会把原记录保存到香港 Nginx 服务器的 root-only 目录：

```text
/root/bizops-cloudflare-dns-backups/<UTC时间戳>/
```

本次批次：

| UTC 时间戳 | 内容 |
| --- | --- |
| `20260717T085230Z` | 首个 `pg-static.hkcloudplay01.com` 灰度记录 |
| `20260717T085517Z` | 回滚演练后重新应用首个 PG 静态记录 |
| `20260717T085909Z` | PG 静态域名扩至 5 个 Zone |
| `20260717T090018Z` | PG3、PG4、PG5 静态域名 |
| `20260717T090211Z` | vendor_a 三组静态域名 |
| `20260717T090330Z` | PP、PPK 静态域名 |
| `20260717T090501Z` | vendor_c、PANDA 静态域名 |
| `20260717T090842Z` | PG 游戏域名 |
| `20260717T090849Z` | PG API 域名 |
| `20260717T090954Z` | PP、PPK、PANDA 游戏域名 |
| `20260717T091020Z` | PP、PPK、PANDA API 域名 |
| `20260717T091203Z` | API、Games、Verify、Socket 核心域名 |

## 回滚验证

已对首个 PG 静态域名实际执行回滚，不是只检查脚本：

1. 删除新建的精确 CloudFront CNAME。
2. Cloudflare 通配 A 记录恢复接管。
3. 确认旧链路可访问。
4. 再次应用精确 CNAME，并重新验证 CloudFront。

按批回滚命令：

```bash
ssh root@192.0.2.14
/usr/local/bin/cloudflare-aws-cutover rollback \
  /root/bizops-cloudflare-dns-backups/<UTC时间戳>
```

回滚后应检查 DNS、HTTP 和业务页面，不要删除原通配记录或备份目录。

## 速度对比

使用同一个约 5.07 MB 的 PG 静态文件进行三次下载测试：

| 测试链路 | 平均首字节 | 平均总耗时 | 说明 |
| --- | ---: | ---: | --- |
| 切换前 Cloudflare 旧链路 | 约 1.06 秒 | 约 6.13 秒 | 本地节点 |
| 切换后 AWS CloudFront | 约 0.45 秒 | 约 5.52 秒 | 同一本地节点 |
| 香港服务器访问已预热 CloudFront | - | 约 0.13～0.23 秒 | 约 22～38 MB/s |

本地 Cloudflare trace 显示测试出口位于日本东京，不是中国大陆节点，因此以上数据只能证明当前出口及香港节点有改善，不能冒充国内实测。中国大陆验收仍需使用关闭代理的国内网络或提供国内服务器，从相同文件进行首包、总耗时和完整进游戏对比。

## 运维脚本

仓库文件：

```text
docker/deploy/hongkong/cloudflare_aws_cutover.py
```

香港服务器：

```text
/usr/local/bin/cloudflare-aws-cutover
```

常用命令：

```bash
# 查看静态或动态游戏域名的精确记录
/usr/local/bin/cloudflare-aws-cutover status pg-static pg-games

# 查看核心/API 精确记录
/usr/local/bin/cloudflare-aws-cutover status-core api verify vendor_b-api

# 按前缀切换 5 个 Zone
/usr/local/bin/cloudflare-aws-cutover apply pg-static

# 只切一个 Zone 做灰度
ONLY_ZONE=hkcloudplay01.com \
  /usr/local/bin/cloudflare-aws-cutover apply pg-static

# 核心/API 域名切换
/usr/local/bin/cloudflare-aws-cutover apply-core api verify vendor_b-api

# 安全下线精确记录，操作前自动备份，可用 rollback 恢复
/usr/local/bin/cloudflare-aws-cutover remove vendor_a-statics vendor_c-static
/usr/local/bin/cloudflare-aws-cutover remove-core socket
```

脚本不包含 Cloudflare Token，令牌仅保存在香港服务器 `/root/.config/cloudflare/api-token`，不得提交 Git 或发送到群里。

## 飞机群进度

| 消息 ID | 内容 |
| ---: | --- |
| `2704` | 首个 PG 静态域名灰度、实际回滚演练及速度对比 |
| `2705` | PG Static 5/5 |
| `2706` | PG3、PG4、PG5 Static 15/15 |
| `2707` | vendor_a Static 15/15 |
| `2708` | PP/PPK Static 与 PP 特殊规则 |
| `2709` | 55 个静态域名全部完成 |
| `2710` | PG 动态域名 6/6 |
| `2711` | PP、PPK、PANDA 动态域名 18/18 |
| `2712` | 核心域名与动态灰度最终汇总 |

## 后续事项

- 从真实中国大陆网络测试首包、完整加载、进入游戏和 WebSocket 稳定性。
- 观察 CloudFront 4xx/5xx、流量和费用，再决定是否长期保留全部分配。
- vendor_a/vendor_c 后端恢复后先验证源站，再单独灰度，不与其他厂商一起切。
- 静态资源更新后继续从 GCS 增量同步到香港 S3；确认迁移稳定前不删除 GCS 源数据。
