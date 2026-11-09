---
id: "doc-f46939f1c1fd"
title: "【发布收尾+静态同步】V20260909 vendor_a3-5 静态 GCS/Worker 与游戏抽检定时任务"
date: "2026-09-09T21:24:00+08:00"
dateSource: "正文日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "监控告警", "自动化", "CDN", "DNS", "安全运维"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-09-2124-%E3%80%90%E5%8F%91%E5%B8%83%E6%94%B6%E5%B0%BE%2B%E9%9D%99%E6%80%81%E5%90%8C%E6%AD%A5%E3%80%91V20260909%20vendor_a3-5%E9%9D%99%E6%80%81GCS/Worker%E4%B8%8E%E6%B8%B8%E6%88%8F%E6%8A%BD%E6%A3%80%E5%AE%9A%E6%97%B6%E4%BB%BB%E5%8A%A1%E4%B8%8A%E7%BA%BF%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-09-2124-【发布收尾+静态同步】V20260909 vendor_a3-5静态GCS/Worker与游戏抽检定时任务上线记录.md"
sourceSha256: "22e46f8be2166660c2ea29807b68871068f3d1039a83a07bde3612e58859c184"
sourceSystem: "project-doc"
---

# 【发布收尾+静态同步】V20260909 vendor_a3-5 静态 GCS/Worker 与游戏抽检定时任务

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609092124-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BDocker-%E3%80%90%E5%8F%91%E5%B8%83%E6%94%B6%E5%B0%BE%2B%E9%9D%99%E6%80%81%E5%90%8C%E6%AD%A5%E3%80%91V20260909%20vendor_a3-5%20%E9%9D%99%E6%80%81%20GCS-Worker%20%E4%B8%8E%E6%B8%B8%E6%88%8F%E6%8A%BD%E6%A3%80%E5%AE%9A%E6%97%B6%E4%BB%BB%E5%8A%A1.md)

> 整理日期：2026-09-09 21:24｜日期依据：正文日期

时间：2026-09-09 21:24（Asia/Manila）
项目：某业务公司 / PGServer master（巴西生产）
结果：✅ 静态 vendor_astatic3/4/5 全量同步 GCS；Worker/DNS/CDN 配置完成；
新游戏静态抽检 32/32 通过并接入每 10 分钟定时任务

## 一、背景

```text
V20260909：新增 25 款 vendor_a + 7 款 PP；需要
  - 静态 vendor_astatic3/4/5 从 client.git 同步 GCS；
  - 新增二级域名 vendor_a-statics3/4/5 cdn 配置；
  - vendor_a.json 增加 game_ids（v3/v4/v5）；
  - 游戏上线后可打开性抽检 + 定时任务。
```

## 二、静态同步

```text
源：client.git master=e8556a76
  vendor_astatic3=19112 / vendor_astatic4=9672 / vendor_astatic5=20374（共 49,158 文件）
目标（三路全部完成）：
  bizops-gcs-vendor_a-statics3/4/5-sa（巴西）
  bizops-gcs-vendor_a-statics3/4/5（香港/东京）
  bizops-game-statics-gcs/vendor_a-statics3/4/5（backup）
过程：分块 2500/批（下载→上传→清理），磁盘峰值受控；
期间清理宝塔旧备份/临时 pack/旧归档，磁盘 100%→40%。
```

## 三、CDN/Worker

```text
DNS：vendor_a-statics3/4/5.cdn-tokyo-bizops.icu → 对应 -sa 桶（proxied，与老域名一致）
Worker Routes：vendor_a-statics3/4/5.cdn-tokyo-bizops.icu/* → summer-wave-c94f
Worker BUCKET_MAP：新增 vendor_a-statics3/4/5
Worker 部署前备份：/root/bizops-cf-backups/20260909-before-vendor_a3-5/summer-wave-c94f.js
（群附件 5452/5453；cdn-tokyo 全量配置备份 5455）
```

## 四、游戏可打开性抽检

```text
抽检 32 款新游戏公开静态入口：
  vendor_a 25：vendor_a-statics3/4/5.cdn-tokyo-bizops.icu/<dir>/index.html
  PP 7：pp-static.../vs<symbol>/desktop/bootstrap.js
结果：32/32 HTTP 200。
定时任务：docker/scripts/new_game_static_check.py
  宝塔 crontab */10；失败才告警飞机群，正常静默写日志。
```

## 五、服务器清理

```text
宝塔：旧结果集备份、git 临时 pack、旧 PP/PNG 归档清理；
      磁盘使用从 100% 降至约 40-63%（随日志波动）。
后端02/03：docker build cache/悬空镜像/tmp/旧日志清理；
      02=53%、03=44%。
结果集权限：01/02/03 全厂家 chown uid1000 + 同步脚本自动修复（已提交）。
```

## 六、本地提交内容

```text
git_static_gcs_sync.py：STATIC_MAP 增加 vendor_astatic3/4/5
summer-wave-static-proxy.js：Worker BUCKET_MAP 增加 vendor_a-statics3/4/5
new_game_static_check.py：新游戏定时抽检
（vendor_a3_5 一次性同步/进度脚本仅部署在服务器，不纳入仓库）
```

## 七、群通知回执（节选）

```text
5437/5438/5449/5451-5455/5469/5471/5472/5478/5480/5541/5580-5581 等
（同步进度由后台按 1% 与每目录完成自动发送）
```

## 八、本地提交

```text
（提交结果见群消息）
```
