---
id: "doc-90a0816b32f6"
title: "【优化】发布页镜像拉取与 Image ID 校验改为循环记录"
date: "2026-10-28T16:46:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "自动化"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-10-28-1646-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E5%8F%91%E5%B8%83%E9%A1%B5%E9%95%9C%E5%83%8F%E6%8B%89%E5%8F%96%E4%B8%8EImageID%E6%A0%A1%E9%AA%8C%E6%94%B9%E4%B8%BA%E5%BE%AA%E7%8E%AF%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-10-28-1646-【优化】发布页镜像拉取与ImageID校验改为循环记录.md"
sourceSha256: "034da7db093a8ea4d80c3f4f0f2220937492a3f463a795ccf84a50f6655e5444"
sourceSystem: "project-doc"
---

# 【优化】发布页镜像拉取与 Image ID 校验改为循环记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-10-28-1646-【优化】发布页镜像拉取与ImageID校验改为循环记录.md`

> 整理日期：2026-10-28 16:46｜日期依据：文件名日期

更新时间：2026-10-28 16:46（Asia/Manila）

状态：发布页循环改造完成，巴西/香港实机校验通过。

## 一、开始前基线

```text
本地 ops master：ed1b1206
本地工作区：干净
远端 ops master：8fcefd60
远端业务 ben：a145929c
```

## 二、需求

原发布页对每个厂家重复输出：

```text
docker pull ...
expected=...
actual=...
if ...
```

9 个厂家会产生大量重复行。需求是改成循环，减少页面命令长度，同时保留：

- 启动前拉取目标镜像；
- 启动后逐个容器比较实际 Image ID；
- 旧镜像直接失败；
- 巴西/香港 registry 正确；
- tada_ws / jili 正确映射 tada 镜像。

## 三、实现

### 3.1 拉取循环

```bash
images='api pg tada ppk pp playson panda g759'
for image in $images; do
  docker pull <registry>/game-service-$image:<tag>
done
```

- 只生成当前勾选厂家的唯一镜像清单。
- 巴西和香港同时勾选 tada_ws 时不重复拉 tada。

### 3.2 Image ID 校验循环

```bash
items='api:api pg:pg tada:tada tada_ws:tada ...'
for item in $items; do
  vendor=${item%%:*}
  image=${item#*:}
  expected=$(docker image inspect <registry>/game-service-${image}:<tag> --format '{{.Id}}')
  actual=$(docker inspect game-service-${vendor}-prod --format '{{.Image}}')
  if [ "$actual" != "$expected" ]; then
    echo "仍在运行旧镜像"
    exit 1
  fi
done
```

- 厂家名和镜像名分开映射，TADA WS2、香港 JILI 不会漏检。
- 容器实际 Image ID 与目标 tag ID 不一致立即终止。

## 四、验证

```text
HTML 解析：通过
Chrome 实际渲染：通过
巴西 registry：203.0.113.1:5000
香港 registry：34.39.180.82:5000
巴西 01 循环校验：9/9 通过
香港 01 循环校验：9/9 通过
```

循环校验覆盖：

```text
api / pg / tada / tada_ws / ppk / pp / playson / panda / g759
香港额外验证 jili，tada_ws 与 jili 均映射 tada 镜像
```

本轮只修改发布页和文档，未重启生产容器，未改镜像、业务数据或域名。

## 五、修改文件

```text
运维发布页.html
workbench/CURRENT_TASK.md
workbench/CURRENT_STATE.md
workbench/ACTIVE_TASKS.md
docs/history/2026-10-28-1646-【优化】发布页镜像拉取与ImageID校验改为循环记录.md
```
