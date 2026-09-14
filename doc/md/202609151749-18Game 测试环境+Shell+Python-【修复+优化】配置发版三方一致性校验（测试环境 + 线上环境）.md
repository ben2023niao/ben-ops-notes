---
id: "doc-e2f0cec28824"
title: "【修复+优化】配置发版三方一致性校验（测试环境 + 线上环境）"
date: "2026-09-15T17:49:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Shell", "Python", "Docker", "Nginx", "监控告警", "自动化", "故障排查"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-15_1749-%E3%80%90%E4%BF%AE%E5%A4%8D%2B%E4%BC%98%E5%8C%96%E3%80%91%E9%85%8D%E7%BD%AE%E5%8F%91%E7%89%88%E4%B8%89%E6%96%B9%E4%B8%80%E8%87%B4%E6%80%A7%E6%A0%A1%E9%AA%8C%EF%BC%88%E6%B5%8B%E8%AF%95%2B%E7%BA%BF%E4%B8%8A%EF%BC%89.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-15_1749-【修复+优化】配置发版三方一致性校验（测试+线上）.md"
sourceSha256: "3fb1bf3a66c7cefe4c699aec61988f400e60ca76524534e265bce8c26a9b93be"
sourceSystem: "project-doc"
---

# 【修复+优化】配置发版三方一致性校验（测试环境 + 线上环境）

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-09-15_1749-【修复+优化】配置发版三方一致性校验（测试+线上）.md`

> 整理日期：2026-09-15 17:49｜日期依据：文件名日期

时间：2026-09-15 17:49（Asia/Manila）
环境标签：测试环境 / 线上环境 / CICD / ben-bot
通知群：`18game运维`（-4929911895） + `18GAME_ 上线群（正式環境）`（-1003762262155）

## 一、背景与问题

用户反馈：**测试环境发布新配置后，宿主机配置已更新，容器内仍是老配置**。

复核证据：

```text
测试环境 15.152.247.196（/opt/docker-youdianse-php，分支 dev）
  alb_white.txt：宿主机 md5=7c83cfed…（新） vs web/cron 容器 md5=2f12c2e4…（旧，08-27 15:57）
  alb_white_secret.txt：宿主机 c77ac424… vs 容器 68c67118…
  env/.env.dev：宿主机与容器一致 → env 正常，问题只在白名单类文件
```

用户追加要求：

1. 其它 txt 配置也要按同样机制同步（不能只写死 `alb_white*.txt`）；
2. 发布成功必须满足三方 md5 完全一致：**配置仓库文件 = 宿主机 = 各容器**；
3. `线上环境-游点涩-配置-发版` 参考 `测试环境-游点涩-配置-发版` 同步优化；
4. 全部操作留详细文档，每步通知两个群。

## 二、根因（CICD 侧）

```text
1. app-local-files（白名单等）不是 bind mount，而是发布时用 docker cp 写进容器；
2. 配置发版/自动同步走 sync_runtime_config_no_build()（只 up -d --force-recreate --no-build
   web nginx cron），未调用 sync_protected_app_local_files_to_containers()；
   只有完整发布 deploy() 才会 docker cp → 所以“配置发版”后宿主机生效、容器内不生效；
3. collect_runtime_config_sync_status() 只比对 env/nginx/php/fpm 挂载文件，
   不比对白名单 → 报告“复查已一致”，形成假阴性；
4. 同步目标写死 PROTECTED_APP_LOCAL_FILES，新增 txt 配置不会自动同步。
```

## 三、代码修复（docker-youdianse-php）

测试环境（dev，已推送 origin/dev）：

```text
e374b3c 修复：no-build 配置同步补齐 docker cp 本地配置文件进容器；
        同步目标改为 app_local_file_sync_targets()（受保护清单 + 源目录内全部文件）
5f47e81 升级：三方一致性校验 build_runtime_config_check()；
        collect_runtime_config_sync_status() 增加配置仓库比对源与 app_local_file_runtime_checks()
1abc4b8 修复：core.py 补充 CONFIG_REPO_DIR 导入（首次执行即暴露）
```

线上环境（main，本地提交 7e57614 + 现场部署）：

```text
7e57614 与 dev 同构：通用同步目标 + 三方校验 + 本地配置文件校验（web/cron）
部署：备份 /root/cicd-core-backup-20260915-174627.py → 替换 core.py →
     venv py_compile 通过 → systemctl restart cicd-web（active，18090 = 200）
```

## 四、ben-bot 发版脚本升级（本仓库）

```text
devops/python/ben-bot/data/scripts/测试环境-游点涩-配置-发版/youdianse_test_config_release.py
devops/python/ben-bot/data/scripts/线上环境-游点涩-配置-发版/youdianse_prod_config_release.py

改动：
  · 新增 VERIFY_TEMPLATE + build_verify_cmd()：发布后对 env 与 app-local-files 下全部文件
    执行 check3：配置仓库 = 宿主机 = web 容器 = cron 容器（sha256 前 12 位展示）
  · 成功判定：commit 命中 + 全部 file_match=true + admin/cicd 200；
    任一 file_match=false → “需人工复核”，不再只看 env 三方
  · 通知正文逐文件列出 ✅/❌ 与四方 sha 前 12 位
  · 修复枚举缺陷：app-local-files 目录 0700，普通用户 glob 展开失败 → 改为 sudo ls -1 枚举

部署：ben-bot 运行机 52.79.252.255
  /opt/telegram/18game_devops/devops/python/ben-bot/data/scripts/…
  备份 /root/bot-script-backup-20260915-174300/；两端 py_compile 通过
```

## 五、执行与验证结果

```text
测试环境：
  sync-config --force → needs_sync=false
  env 99cbb83a8846 ×3；alb_white.txt 1b0b87735bbc ×3；alb_white_secret.txt e9d6835716c0 ×3
  新增 ntrapi.1uhg.com（星姬调教工坊，测试环境）已落容器
  ben-bot 校验命令实测：全部 file_match=true，admin_login=200、cicd=200

线上环境：
  配置仓库 e93d818 新增“星姬调教工坊 线上生产服”alb_white_secret 行（值不在群/文档展开）
  sync-config --force → no-build 重建；needs_sync=false
  env 19fb51b824f0 ×3；alb_white.txt 684ff4d80eca ×4；alb_white_secret.txt ca03838617aa ×4
  容器 Up；admin=200、cicd=200、公网 https://www.youdianse.com/ 200；
  容器内 grep xjgf = 1（新行已生效）
  ben-bot 校验命令实测：三个文件 file_match=true
```

## 六、回滚与遗留

```text
回滚：
  · ben-bot 脚本：/root/bot-script-backup-20260915-174300/ 覆盖回去
  · 线上 CICD：/root/cicd-core-backup-20260915-174627.py 覆盖 + restart cicd-web
  · 配置仓库：按钮选上一版 git id d875175 回滚

遗留：
  1) 线上运维仓库落后 origin/main 61 个提交且工作区有本地改动，本次为精确替换上线，
     建议安排一次现场仓库整理；
  2) 新增 txt 配置已自动同步进容器，但如需进入“备份/恢复/Git 保护”清单，
    仍需加入 settings.json defaults.protected_app_local_files；
  3) 建议把三方一致性结果纳入 CICD 页面展示与失败告警。
```

## 七、线上新增配置回退（用户 2026-09-15 追加要求）

```text
要求：新加配置只发布测试环境，线上还原（线上数值待开发侧提供后再发布）。
执行：
  · 配置仓库 config-main：revert e93d818 → 7836b0f（已推送 origin/main，xjgf 行数 0）
  · 线上发版：sync-config --force → alb_white_secret.txt 1246 → 1150 字节；
    needs_sync=false；三方 sha 3688d137ddac（配置仓库/宿主机/web/cron 一致）
  · 验证：web/cron 容器内 xjgf 行数 0；容器 Up；admin=200、cicd=200、公网 www 200
当前状态：测试环境保留新行；线上已还原，等开发侧给出线上数值后再发布。
本次保留：三方一致性校验（CICD dev/main + ben-bot 两脚本）与通用同步机制。
```
