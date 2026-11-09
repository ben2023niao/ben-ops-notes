---
id: "doc-753ba28d2c2b"
title: "机器人功能对接线上 nginx 检查与备份时间戳冲突修复"
date: "2026-08-15T00:05:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Nginx", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-15_0005-%E3%80%90%E6%A3%80%E6%9F%A5%2B%E4%BF%AE%E5%A4%8D%E8%AE%B0%E5%BD%95%E3%80%91%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%8A%9F%E8%83%BD%E5%AF%B9%E6%8E%A5nginx%E4%B8%8E%E5%A4%87%E4%BB%BD%E6%97%B6%E9%97%B4%E6%88%B3%E5%86%B2%E7%AA%81%E4%BF%AE%E5%A4%8D.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-15_0005-【检查+修复记录】机器人功能对接nginx与备份时间戳冲突修复.md"
sourceSha256: "437ab9f2b856fc266ea3a42ad1e491150fcc85747afc813b93f7d730f5b06201"
sourceSystem: "project-doc"
---

# 机器人功能对接线上 nginx 检查与备份时间戳冲突修复

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608150005-18Game%20%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83%2BShell%2BPython-%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%8A%9F%E8%83%BD%E5%AF%B9%E6%8E%A5%E7%BA%BF%E4%B8%8A%20nginx%20%E6%A3%80%E6%9F%A5%E4%B8%8E%E5%A4%87%E4%BB%BD%E6%97%B6%E9%97%B4%E6%88%B3%E5%86%B2%E7%AA%81%E4%BF%AE%E5%A4%8D.md)

> 整理日期：2026-08-15 00:05｜日期依据：文件名日期

环境标签：通用 / ben-bot / 前端域名维护 / nginx / 16.208.38.88

时间：2026-08-15 00:05（Asia/Manila）

## 背景

用户要求检查线上 nginx 修改后，机器人 加域名 / 删除域名 / SSL续签 / 搜索域名 是否仍能对接。

## 检查结论

- 线上 conf.d 仅 `10-youdianse-prod-maps.conf` + `20-youdianse-prod-unified.conf`，与仓库模板一致（此前改动均已入库）。
- 服务器脚本 md5 与仓库一致（7337c773…）。
- 逐项验证：
  - 快速检查：93 主机，模式/证书状态正确（redirect/ua 等）。
  - 加域名 dry-run：ua/h5/pc/redirect 四类主机与模式计算正确。
  - 删除域名 dry-run：不存在域名正确报错。
  - SSL 续签：`cert -d h5.youdianse.com` → “已有有效证书，跳过签发” ✅
  - 搜索：`youdianse` 匹配 9 个，渲染正常（含 🗑 删除按钮）。
  - 真实 add→del 往返：写入 server_name/maps + reload 正常。

## 发现并修复的 Bug

- 现象：真实 add 成功后立即 del 崩溃 `shutil.Error: [Errno 17] File exists`，删除未执行。
- 根因：`backup_all()` 备份目录名用秒级时间戳（`%Y-%m-%d_%H-%M-%S`），同秒内连续操作（add 后 del）会复用同一目录，`shutil.copytree(..., dirs_exist_ok=True, symlinks=True)` 遇到已存在的符号链接时抛 FileExistsError。
- 修复：
  1. 备份时间戳改为微秒精度（`%Y-%m-%d_%H-%M-%S-%f`），同秒操作不再冲突。
  2. `main()` 里 `backup_all()` 加 try/except：备份失败只警告，不阻断删除/续签等主操作。
- 验证：连续 add→del 两次均成功（同秒生成两个独立备份目录 16-03-19-928904 / 16-03-19-729232），残留测试域名已清理，nginx -t 通过。

## 结论

- 机器人加/删/续签/搜索与当前 nginx 配置完全对接。
- 备份时间戳冲突已修复，删除/续签不再被备份问题卡死。
