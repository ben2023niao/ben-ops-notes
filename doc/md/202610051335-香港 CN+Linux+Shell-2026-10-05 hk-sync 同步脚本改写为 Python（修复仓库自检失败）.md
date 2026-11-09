---
id: "doc-ba639c93f80b"
title: "2026-10-05 hk-sync 同步脚本改写为 Python（修复仓库自检失败）"
date: "2026-10-05T13:35:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Linux", "Shell", "Python", "Docker", "监控告警", "故障排查", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/cn/docker/doc/2026-10-05-1335-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91hk-sync%E8%84%9A%E6%9C%AC%E6%94%B9%E5%86%99%E4%B8%BAPython%E5%B9%B6%E4%BF%AE%E5%A4%8DCI%E8%87%AA%E6%A3%80.md"
sourcePath: "~/Projects/ops/private-notes/cn/docker/doc/2026-10-05-1335-【运维】hk-sync脚本改写为Python并修复CI自检.md"
sourceSha256: "8b4d72ae031693b4a811f4f948bc40701fd2044fb05cbc5a043851a060bc22e7"
sourceSystem: "project-doc"
---

# 2026-10-05 hk-sync 同步脚本改写为 Python（修复仓库自检失败）

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610051335-%E9%A6%99%E6%B8%AF%20CN%2BLinux%2BShell-2026-10-05%20hk-sync%20%E5%90%8C%E6%AD%A5%E8%84%9A%E6%9C%AC%E6%94%B9%E5%86%99%E4%B8%BA%20Python%EF%BC%88%E4%BF%AE%E5%A4%8D%E4%BB%93%E5%BA%93%E8%87%AA%E6%A3%80%E5%A4%B1%E8%B4%A5%EF%BC%89.md)

> 整理日期：2026-10-05 13:35｜日期依据：文件名日期

## 一、起因

```text
跑 docker/ci/check.py 时自检失败：
  Shell scripts are not allowed; implement these tools in Python:
  - docker/deploy/hongkong/hk-sync.sh
规则来源：docker/ci/check.py 的 reject_shell_scripts()，
         —— docker/ 下不得新增 Shell 脚本，运维工具统一用 Python。
该 .sh 是 12:10 那轮随「同步脚本优化复核」入仓的，之后自检就一直没过。
按用户「验证失败先修复，必须提交代码」的要求，本轮补齐。
```

## 二、改法

```text
1) 新增 docker/deploy/hongkong/hk_sync.py —— 行为、参数、输出与旧 sh 完全一致：
     python3 hk_sync.py runtime|results|all [--dry-run -i 等 rsync 额外参数]
   · rsync 参数保持：runtime 与旧版同（-avP --delete --delete-delay --partial
     --partial-dir=.rsync-partial --timeout=180 --stats --exclude logs/ game_result_datas/ conf/
     *.db-shm *.db-wal）；results 同（-rtvP --delete --delete-delay --partial --timeout=300
     --chown=1000:1000）。
   · 免交互：sshpass -f /root/.rsync-pass + SSH keepalive（密码不入仓）。
   · 实时输出同时追加日志 /var/log/hk-runtime-sync.log（不可写时只告警、不中断）。
   · 同步后自动校验 /data/server-runtime/conf/configs-*.py（是否仍含 is_top_new_configs）。
   · 支持环境变量覆盖：HK_SYNC_SRC / HK_SYNC_RUNTIME_SRC / HK_SYNC_RESULTS_SRC / HK_SYNC_DST /
     RSYNC_PASSFILE / RSYNC_LOG。
2) 删除 docker/deploy/hongkong/hk-sync.sh（旧 sh 留档在 12:10 那次提交里，可随时回看）。
3) 香港 prod-01 / prod-02 同步更新：/opt/bizops-hk-ops/hk_sync.py 已就位（旧 hk-sync.sh 保留，
   不改动用户手感；新脚本是替代品）。
```

## 三、验证

```text
· 本地：python3 docker/ci/check.py -> exit 0，最后一行 “docker ops checks passed”
        （包含 shell script check passed: 0 files）。
· 本地功能：用 stub rsync/sshpass 跑 `hk_sync.py all --dry-run -i`，
        两条 rsync 命令行与旧 sh 逐字一致，日志正常落盘，退出码 0。
· 两台服务器：py_compile 通过、--help 正常；md5 = 569299ff85c3306777106341b6f446fb（本地/01/02 三处一致）。
· prod-01 实跑 `runtime --dry-run -i`：rc=0，DRY RUN 正常（total size 71,512,862），
  结尾 conf 自检：configs-vendor_b.py is_top_new_configs=1、configs-vendor_d.py is_top_new_configs=1（未被同步源覆盖）。
· prod-02 直接调 check_conf()：同上，vendor_b 102 行 / vendor_d 47 行、均为 1。
· /root/.rsync-pass 两台都在（600，root:root）。
```

## 四、关联

```text
docker/deploy/hongkong/hk_sync.py（新脚本）
docker/doc/2026-10-05-1210-【优化+故障处理】香港同步脚本优化复核与vendor_b崩溃修复.md（原始优化与 vendor_b 崩溃根因）
docker/ci/check.py（reject_shell_scripts 规则）
```
