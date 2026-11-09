---
id: "doc-7bbb0c7a4d7c"
title: "【运维】vendor_a 623 静态资源覆盖 + PG 日志窗口取回记录"
date: "2026-09-10T22:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Python", "CDN", "安全运维", "故障排查"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-10-2230-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91vendor_a623%E9%9D%99%E6%80%81%E8%A6%86%E7%9B%96%2BPG%E6%97%A5%E5%BF%97%E7%AA%97%E5%8F%A3%E5%8F%96%E5%9B%9E%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-10-2230-【运维】vendor_a623静态覆盖+PG日志窗口取回记录.md"
sourceSha256: "50f4b77b8e6dff794547a88264d74641bbada08716ef811692eba3bb85cbfa8a"
sourceSystem: "project-doc"
---

# 【运维】vendor_a 623 静态资源覆盖 + PG 日志窗口取回记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609102230-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BLinux%2BShell-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91vendor_a%20623%20%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%E8%A6%86%E7%9B%96%20%2B%20PG%20%E6%97%A5%E5%BF%97%E7%AA%97%E5%8F%A3%E5%8F%96%E5%9B%9E%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-09-10 22:30｜日期依据：文件名日期

时间：2026-09-10 22:30（Asia/Manila）
项目：某业务公司 / PGServer master
结果：✅ 623(col) 三路桶强制覆盖并逐文件 checksum 校验一致；
✅ PG 2026-09-09 17:06:29.618 前后各 100 行日志取回并发群

## 一、vendor_a 623 静态资源覆盖

### 定位

```text
游戏：623 闪电币 Coin of Lightning
目录：vendor_astatic5/col        （623 在 vendor_a.json 的 SPECIAL_GAMES_v5）
源  ：client.git origin/master = e93428a04a（无新提交）
```

### 覆盖范围

```text
gs://bizops-gcs-vendor_a-statics5-sa       （巴西，Worker 实际回源）
gs://bizops-gcs-vendor_a-statics5          （香港）
gs://bizops-game-statics-gcs/vendor_a-statics5（backup）
每桶 561 个对象，强制覆盖（gsutil cp -r，不带 -n）
```

### 校验

```text
gsutil rsync -r -n -c <本地树> gs://<bucket>/col/
  巴西 : content-diff=0
  香港 : content-diff=0
  backup: content-diff=0
抽样 md5：git blob md5 与 GCS md5Hash 逐一吻合
CDN 200：col/index.html、col/application.2f276.js、
         col/assets/game/config.d02cb.json、col/assets/game/game.d02cb.zip、
         col/src/import-map.e7209.json、col/src/system.bundle.692e9.js
```

### 发现（反馈 C++）

`col/index.html` 引用了 5 个 git 里不存在的文件，CDN 全为 404：

```text
favicon0.ico / favicon1.ico        rel=icon，浏览器必请求，不影响游戏加载
vendor_b_powered_by_TaDa.png           api/skin 分支用（api=3）
TaDa_APP_apng.png                  api=301 / vendor_a_CASINO
VegasEmpire.png                    api=20110（SSS）
```

后 3 个在**全部 vendor_a 游戏**的 git 仓库里都不存在，属长期缺失；favicon 在其它
游戏（favicon0 17 个、favicon1 99 个）有，说明 col 这版漏传了。

### 结论

覆盖前 GCS 内容与 git 已经一致（缺失 0、大小全等、md5 全等），本次属于“重新落一遍”，
没有产生内容变更。若 623 仍打不开，需要带 ssoKey 的真实浏览器复现来区分
“静态 404”还是“接口返回异常”。

## 二、PG 日志窗口取回

### 需求

Ben(C++) 要 2026-09-09 17:06:29.618 前后 100 行 PG 日志。

### 日志位置与命名

```text
后端 prod-01/02/03：/opt/pgserver/logs/<release-dir>/pg.log
轮转文件按“轮转时刻”命名：pg.log-YYYYMMDD-HHMMSS.gz
  -> 17:06 的行在 17:0x / 17:1x 的轮转文件里
访问方式：prod 是密码登录，口令在 bot 容器环境变量 PGSERVER_DEPLOY_PASS，
          宝塔上用 sshpass 连接（宝塔与容器内都有 /usr/bin/sshpass）
```

### 工具

```bash
python3 /opt/bizops-scripts/pg_log_window.py "2026-09-09 17:06:29.618" \
        --context 100 --hosts 192.0.2.1,192.0.2.1 --out /root/vendor_a-zips/xxx.txt
```

### 取回结果

```text
prod-01 bizops-pg-release-01/pg.log-20260909-170941.gz 第 1168 行命中
窗口 1068-1268（200 行）
prod-02 该时间点无对应日志

17:06:29.617 WARNING do_game_spin_v4:2031 - ext_type=new_user key:
             pg_1492288_control_2_0 not found. use normal.
17:06:29.618 ERROR   do_game_spin_v4:2031 - error no candidates for level: 16
17:06:29.618 ERROR   do_game_spin_v4:2031 - error select_multiple_by_level returned None for 16
请求：gameid=1492288 player=MyGame-679967810913 BRL bet=6000 win=0 tx_status=0
```

初步判断：先提示控制档位 key 不存在（回落 normal），紧接着按 level 16 取候选返回
None，两条 ERROR 属同一次 spin 的连锁报错，指向“level 16 档位无候选/控制档位未命中”。

安全提示：窗口内含该局玩家会话 JWT（URL 参数 `p=`），仅限内部群排查。

## 三、脚本清单（本次新增/改动）

```text
vendor_a_game_static_overwrite.py  单个游戏从 git 强制覆盖到三路桶 + checksum 校验
pg_log_window.py               后端 PG 日志按时间戳取 ±N 行（支持多后端）
git_gcs_gap_check.py           增加 --strip-prefix / --check-size / 子目录支持
```
