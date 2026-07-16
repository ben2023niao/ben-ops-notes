---
id: "doc-ea7757ce22b7"
title: "cn 分支精简与香港工具 Python 化记录"
date: "2026-07-17T11:09:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "Nginx", "自动化", "CDN", "DNS"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/hongkong/cn/2026-07-17-1109-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91cn%E5%88%86%E6%94%AF%E7%B2%BE%E7%AE%80%E4%B8%8E%E9%A6%99%E6%B8%AF%E5%B7%A5%E5%85%B7Python%E5%8C%96%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/hongkong/cn/2026-07-17-1109-【架构改造】cn分支精简与香港工具Python化记录.md"
sourceSha256: "a467691e1fe96d63b5659d81ec8eec5ba0d95263c0b00de6cef6484420f8b6c2"
sourceSystem: "project-doc"
---

# cn 分支精简与香港工具 Python 化记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/hongkong/cn/2026-07-17-1109-【架构改造】cn分支精简与香港工具Python化记录.md`

> 整理日期：2026-07-17 11:09｜日期依据：文件名日期

## 目标

2026-07-17 明确 `cn` 不再发布后端，只负责香港 Nginx、AWS S3/CloudFront/ACM 和 Cloudflare DNS。仓库按此边界精简，并把香港入口实际使用的 Shell 工具全部改为 Python。

## Shell 盘点与处理

改造前 `docker/` 下有 20 个 Shell 文件，共 2,384 行：

- 香港 AWS/Cloudflare 工具 9 个。
- ben-bot 构建和容器入口 4 个。
- 巴西宝塔定时任务脱敏快照 7 个。

先完成了等价 Python 转换和编译验证。随后根据最终职责边界，删除不属于香港入口的 ben-bot、后端发布和巴西快照，只保留香港 9 个工具及 1 个共享模块。最终 `docker/` 下 `.sh`/`.bash` 文件为 0。

CI 已增加硬性检查，后续重新加入 Shell 文件会直接失败。

## 香港工具替换

保留的 Python 文件：

```text
cf_api.py
cloudflare_aws_cutover.py
configure_cloudfront_pg_static.py
configure_cloudfront_pp_customizations.py
create_cloudfront_dynamic.py
create_cloudfront_static_distributions.py
hk_ops_common.py
sync_acm_cloudflare.py
sync_gcs_to_s3.py
validate_cloudfront_static.py
```

香港服务器继续保留原无扩展名命令，调用方不用改变。2026-07-17 已将 `/usr/local/bin` 对应 9 个命令替换为 Python，替换前备份：

```text
/root/dbqp-python-migration-backups/20260717T110904Z
```

备份目录包含原文件和 `SHA256SUMS`。如需回滚，可从该目录把对应命令复制回 `/usr/local/bin`，恢复权限后重新执行只读验证。

## 回归结果

| 检查 | 结果 |
| --- | ---: |
| 仓库 Shell 文件 | 0 |
| Python 全量编译 | 通过 |
| Cloudflare Token 验证 | `success=true` |
| 新旧 Cloudflare status 输出 | 一致 |
| 静态域名 | 50/50 HTTP 200 |
| Google/AWS 样本哈希 | 10/10 一致 |
| CORS 与 CloudFront Cache | 50/50 正常 |
| 私有 S3 公网直连 | 403 |
| 动态 CloudFront 别名定义 | 33 |
| 静态同步映射 | 10 |

验证期间没有执行 DNS 写入、CloudFront 更新或 S3 删除。

## 删除范围

- `docker/ben-bot/`
- 后端业务 `docker/Dockerfile`
- `docker/services/`
- 后端发布 `docker/deploy/*.py`，仅保留 `deploy/hongkong/`
- 后端和浏览器发布辅助 `docker/scripts/`
- 巴西宝塔与服务器快照 `docker/线上服务器信息/`
- 与香港当前入口无关的历史文档

## 最终目录

精简后只保留 `ci`、`conf`、`deploy/hongkong` 和香港文档。该边界用于防止后续 AI 或运维误把 `cn` 当成后端发布分支。

## 安全说明

- 未把 AWS、Cloudflare 或 Telegram 凭证提交到 Git。
- `docker/cf.api` 继续由 `.gitignore` 排除。
- 线上替换前有 root-only 备份。
- Google 源数据和旧 CloudFront/S3 回滚资源未删除。
