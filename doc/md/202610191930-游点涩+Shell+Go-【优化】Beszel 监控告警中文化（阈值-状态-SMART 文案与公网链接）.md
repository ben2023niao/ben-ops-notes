---
id: "doc-62a9900e13f3"
title: "【优化】Beszel 监控告警中文化（阈值/状态/SMART 文案与公网链接）"
date: "2026-10-19T19:30:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Go", "Docker", "监控告警", "自动化", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-19-1930-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91Beszel%E7%9B%91%E6%8E%A7%E5%91%8A%E8%AD%A6%E4%B8%AD%E6%96%87%E5%8C%96%EF%BC%88%E9%98%88%E5%80%BC-%E7%8A%B6%E6%80%81-SMART-%E5%85%AC%E7%BD%91%E9%93%BE%E6%8E%A5%EF%BC%89.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-19-1930-【优化】Beszel监控告警中文化（阈值-状态-SMART-公网链接）.md"
sourceSha256: "106360f6bf93b4872c4105cf87ed3088a3844b1b1f7d8e5549f4f155d953e9d1"
sourceSystem: "project-doc"
---

# 【优化】Beszel 监控告警中文化（阈值/状态/SMART 文案与公网链接）

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-19-1930-【优化】Beszel监控告警中文化（阈值-状态-SMART-公网链接）.md`

> 整理日期：2026-10-19 19:30｜日期依据：文件名日期

- 时间：2026-10-19 19:20 ~ 19:50（北京时间）
- 环境：监控机 52.79.252.255（Beszel Hub，端口 8090）
- 目标：把推到群里的英文告警（`bandwidth below threshold` / `Bandwidth averaged 19.75 MB/s for the previous 3 minutes`）改成中文，并把告警里的链接从 `localhost` 换成公网地址

## 一、改前状态

```
镜像：henrygd/beszel     版本：0.18.7
环境：APP_URL=http://localhost:8090   ← 告警链接点不开
告警示例：
  游点涩-后端 bandwidth below threshold
  Bandwidth averaged 34.93 MB/s for the previous 3 minutes.
  http://localhost:8090/system/yt4ds9f5otowhgu

通知链路：Beszel → Telegram（shoutrrr webhook telegram://***@telegram/?channels=-5039045344）
```

Beszel 的告警文案**写死在 Go 代码里**，没有多语言开关，只能改源码重建镜像。

## 二、做法

1. 拉取 **官方 v0.18.7 源码**，打中文文案补丁（只改文案，逻辑不动）
2. 用 `Dockerfile.zh`（前端 vite 构建 + Go 交叉编译）构建 `beszel-zh:v0.18.7`
3. 停旧容器（改名保留，便于回滚）→ 用新镜像重建容器，**沿用原数据卷 `beszel_data`**
4. `APP_URL` 改为 `http://52.79.252.255:8090`（实测公网可访问，HTTP 200）

补丁与构建文件已入库：

```
ops/production/beszel/beszel-zh-alerts.py   # 中文文案补丁
ops/production/beszel/Dockerfile.zh         # 构建用 Dockerfile
```

## 三、翻译范围

| 类型 | 改前 | 改后 |
| --- | --- | --- |
| 阈值告警标题 | `%s %s below threshold` / `above threshold` | `%s %s 低于阈值` / `高于阈值` |
| 阈值告警正文 | `%s averaged %.2f%s for the previous %v %s.` | `%s 最近 %v 分钟平均 %.2f%s` |
| 告警名（展示） | `bandwidth` / `memory` / `disk` / `temperature` / `cpu` | `带宽` / `内存` / `磁盘` / `温度` / `CPU 使用率` |
| 负载名 | `1m Load` / `5m Load` / `15m Load` | `1 分钟负载` / `5 分钟负载` / `15 分钟负载` |
| 在线状态 | `Connection to X is down 🔴` / `is up ✅` | `X：已断开 🔴` / `X：运行正常 ✅` |
| 磁盘使用率描述 | `Usage of /` | `/ 使用率` |
| 温度描述 | `Highest sensor X` | `最高传感器 X` |
| SMART | `Disk X SMART status changed to Y` | `磁盘 X SMART 状态变为 Y` |
| 链接文字 | `View X` | `查看 X` |

> 关键点：告警名在 `alerts_system.go` 里是**按英文名 switch 取值**的（`case "CPU"` / `"Memory"` / `"Bandwidth"` …），
> 所以**数据库里的告警名必须保持英文**，否则取值会落空、告警不再触发。本次只在“展示时”映射成中文。

## 四、验证

1. 二进制文案：`低于阈值` ✓、`高于阈值` ✓、`分钟` ✓、`带宽` ✓、`内存` ✓、`已断开` ✓、`运行正常` ✓、`查看` ✓（旧镜像对应项均为 0）
2. 服务健康：`http://203.0.113.1:8090` → 200；容器 `beszel-zh:v0.18.7` Up
3. **受控触发**：临时把「游点涩-后端 带宽」阈值 20 → 5，容器评估后于 `11:47:22 UTC` 产生告警记录并推送（走的是新二进制），随后已恢复阈值 20
4. 链接：`APP_URL=http://52.79.252.255:8090`，告警里不再出现 localhost

## 五、回滚

```bash
# 旧容器已保留为 beszel-old-1019（stopped）
docker rm -f beszel
docker rename beszel-old-1019 beszel
docker start beszel
```

## 六、后续维护

- 升级 Beszel 时：拉新版源码 → 执行 `beszel-zh-alerts.py` → `docker build -f Dockerfile.zh -t beszel-zh:<新版本>` → 改容器镜像
- 若官方调整了告警模板，补丁里的原文可能匹配不上（脚本会打印「未找到」），按新源码调整即可
- 新增告警类型（如 GPU/电池）时，在 `localizeAlertName` 里补一条映射
