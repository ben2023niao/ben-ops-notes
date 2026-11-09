---
id: "doc-b7e0becda5ac"
title: "【方案】前端代码迁移 AWS S3：桶与厂家目录对照"
date: "2026-09-11T00:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Docker", "Nginx", "CDN", "安全运维", "故障排查"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-11-0030-%E3%80%90%E6%96%B9%E6%A1%88%E3%80%91%E5%89%8D%E7%AB%AF%E4%BB%A3%E7%A0%81%E8%BF%81%E7%A7%BBAWS-S3-%E6%A1%B6%E4%B8%8E%E5%8E%82%E5%AE%B6%E7%9B%AE%E5%BD%95%E5%AF%B9%E7%85%A7.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-11-0030-【方案】前端代码迁移AWS-S3-桶与厂家目录对照.md"
sourceSha256: "19826eec742c2b77547843b489124095bfd3901096c1065d2d3c372991ffddb6"
sourceSystem: "project-doc"
---

# 【方案】前端代码迁移 AWS S3：桶与厂家目录对照

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609110030-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BLinux%2BShell-%E3%80%90%E6%96%B9%E6%A1%88%E3%80%91%E5%89%8D%E7%AB%AF%E4%BB%A3%E7%A0%81%E8%BF%81%E7%A7%BB%20AWS%20S3%EF%BC%9A%E6%A1%B6%E4%B8%8E%E5%8E%82%E5%AE%B6%E7%9B%AE%E5%BD%95%E5%AF%B9%E7%85%A7.md)

> 整理日期：2026-09-11 00:30｜日期依据：文件名日期

时间：2026-09-11 00:30（Asia/Manila）
项目：某业务公司 / PGServer master
状态：方案与工具就绪；等待 AWS 建桶授权

> ✅ 2026-09-12 落地补充：本方案已实现并跑通。落地的同步工具是
> `docker/scripts/s3_gcs_sdk_sync.py`（boto3 ↔ google-cloud-storage **SDK 直连**），
> 封装在容器 `bizops-resource-sync` 里、跑在**后端 03**（宝塔不承担同步压力）；
> 机器人主页有「静态资源同步S3到GCS」按钮（仅 @benb6879 / @Ben_Bird 可执行）。
> GCS 目标桶名是 **`newgg2-bizops-gcs-<prefix>-sa`（巴西）/ `newgg2-bizops-gcs-<prefix>`（香港）**。
> **动手前必读**：docker/doc/2026-09-12-1930-【架构+踩坑】客户端资源同步S3到GCS的SDK实现与全部坑记录.md
> （记录 11 个坑：SDK 上传 400、每对象 3 进程吃 CPU、VM scopes、gsutil token 缓存、
> CF token IP 白名单、cacheEverything 缓存 404/旧内容等）。

## 一、背景与目标

前端开发与运维确认：**后续前端代码不再放 git**。
新的流程：

```text
前端开发  --上传-->  AWS S3（大阪 ap-northeast-3）
                          |
                          |  谷歌侧按前缀从对应 S3 拉取（rsync）
                          v
                    GCS 巴西 -sa（Worker 实际回源）+ GCS 香港（镜像）
                          |
                          v
              Cloudflare Worker -> 静态域名（CDN）
```

S3 只做「前端代码源」，一份即可；GCS 仍负责对外分发（巴西/香港双桶）。

## 二、厂家 ↔ 桶 ↔ 域名 对照总表

| 厂家 | git 目录（旧，将废弃） | GCS 前缀 | GCS 巴西(live) | GCS 香港(镜像) | Worker 前缀 | 静态域名 | 拟建 S3 桶 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PG（当前） | pgnew | pg-static | bizops-gcs-pg-static-sa | bizops-gcs-pg-static | pg-static | pg-static.\* | bizops-s3-pg-static |
| PG3 | pg3static | pg3-static | bizops-gcs-pg3-static-sa | bizops-gcs-pg3-static | pg3-static | pg3-static.\* | bizops-s3-pg3-static |
| PG4 | pg4static | pg4-static | bizops-gcs-pg4-static-sa | bizops-gcs-pg4-static | pg4-static | pg4-static.\* | bizops-s3-pg4-static |
| PG5 | pg5static | pg5-static | bizops-gcs-pg5-static-sa | bizops-gcs-pg5-static | pg5-static | pg5-static.\* | bizops-s3-pg5-static |
| PG6 | pg6static | pg6-static | bizops-gcs-pg6-static-sa | bizops-gcs-pg6-static | pg6-static | pg6-static.\* | bizops-s3-pg6-static |
| PG7 | pg7static | pg7-static | bizops-gcs-pg7-static-sa | bizops-gcs-pg7-static | pg7-static | pg7-static.\* | bizops-s3-pg7-static |
| vendor_a（0） | vendor_astatic | vendor_a-statics | bizops-gcs-vendor_a-statics-sa | bizops-gcs-vendor_a-statics | vendor_a-statics | vendor_a-statics.\* | bizops-s3-vendor_a-statics |
| vendor_a1 | vendor_astatic1 | vendor_a-statics1 | bizops-gcs-vendor_a-statics1-sa | bizops-gcs-vendor_a-statics1 | vendor_a-statics1 | vendor_a-statics1.\* | bizops-s3-vendor_a-statics1 |
| vendor_a2 | vendor_astatic2 | vendor_a-statics2 | bizops-gcs-vendor_a-statics2-sa | bizops-gcs-vendor_a-statics2 | vendor_a-statics2 | vendor_a-statics2.\* | bizops-s3-vendor_a-statics2 |
| vendor_a3 | vendor_astatic3 | vendor_a-statics3 | bizops-gcs-vendor_a-statics3-sa | bizops-gcs-vendor_a-statics3 | vendor_a-statics3 | vendor_a-statics3.\* | bizops-s3-vendor_a-statics3 |
| vendor_a4 | vendor_astatic4 | vendor_a-statics4 | bizops-gcs-vendor_a-statics4-sa | bizops-gcs-vendor_a-statics4 | vendor_a-statics4 | vendor_a-statics4.\* | bizops-s3-vendor_a-statics4 |
| vendor_a5 | vendor_astatic5 | vendor_a-statics5 | bizops-gcs-vendor_a-statics5-sa | bizops-gcs-vendor_a-statics5 | vendor_a-statics5 | vendor_a-statics5.\* | bizops-s3-vendor_a-statics5 |
| PP | ppstatic | pp-static | bizops-gcs-pp-static-sa | bizops-gcs-pp-static | pp-static | pp-static.\* | bizops-s3-pp-static |
| PPK | popok | ppk-static | bizops-gcs-ppk-static-sa | bizops-gcs-ppk-static | ppk-static | ppk-static.\* | bizops-s3-ppk-static |
| vendor_c | vendor_cstatic | vendor_c-static | bizops-gcs-vendor_c-static-sa | bizops-gcs-vendor_c-static | vendor_c-static | vendor_c-static.\* | bizops-s3-vendor_c-static |
| PANDA | vendor_d | vendor_d-static | bizops-gcs-vendor_d-static-sa | bizops-gcs-vendor_d-static | vendor_d-static | vendor_d-static.\* | bizops-s3-vendor_d-static |
| G759 | G759static | g759-static | **bizops-gcs-g759-static**（注意：不是 -sa） | **bizops-gcs-g759-static-asia** | g759-static | g759-static.\* | bizops-s3-g759-static |

补充：

- 静态域名后缀共 20 个根域（`cdn-tokyo-bizops.icu`、`6xv8q.cyou` 等），
  Worker 前缀相同，只是 zone 不同。
- 备份桶 `gs://bizops-game-statics-gcs/<prefix>/` 保留每个前缀的一份历史镜像。
- **G759 是唯一命名例外**：没有 `-sa`，live 桶就叫 `bizops-gcs-g759-static`。

## 三、各桶顶层目录（= 前端代码该放哪）

> 表中「运维产物」指 health.json / _probe / pintest / `bizops-gcs-*-sa`（历史误建的嵌套副本）
> 等非前端资源，前端不需要关心。

| 前缀 | 体量(巴西) | 对象数 | 目录特征 | 顶层目录 |
| --- | --- | --- | --- | --- |
| pg-static | 3.09 GiB | 39325 | **游戏ID数字目录** | 100,101,102,…,1623475,1755623,1760238,1786529,1815268,1879752,1918451 … 共 130+ 个数字目录；另有 index.html、404.html、shared、126_back |
| pg3-static | 651 MiB | 8373 | 游戏ID | 1543462,1799745,1849515,1940257,1950910,1981965,1997301,2009635,2024510,2035783,2040102,2058347,2081892,2100928,67,71 + shared |
| pg4-static | 1.75 GiB | 22168 | 游戏ID | 1,100,101,105,…,2012025 + shared,shared13,shared14,shared15,shared18 |
| pg5-static | 513 MiB | 6462 | 游戏ID | 102,103,114,121,122,125,1432733,1529867,1601012,1666445,1799745,1850016,1879752,3,35,59,61,91,93,94,95,97 + shared |
| pg6-static | 43 MiB | 687 | 游戏ID | 1834850,1935269 + shared |
| pg7-static | 78 MiB | 1057 | 游戏ID | 1897678,1903012,1971587 + shared,shared13 |
| vendor_a-statics | 1.33 GiB | 22453 | **游戏短名目录** | aa,ali,bbc,bfs,bh,bk,bog,cbt,chilli,cny,coininfinity,csh,df,dotd,ed,fb,fd,fg,fg3,fg4,fgp,fivestar,fs,fullhouse,fullhouse3,ge,gem3,gj,gq,ifff,kk2,lbingo,ln,luckygoldbricks,luckytree,mc,mcp,me,ms,mw,mw2,mw3,mw4,nightclub,ols,ols2,ols3,petra,pirate,pp,rc,rs2,samba,sr,sss,starburst,sweetheart,sweetheart3,sweetheart4,taxi,thor,tks,tph,twinwins,utaxi,wa,wondershow,ww,xiyangyang（69 款）+ astarte,astarte2,src,cocos-js,images,language,static,smallicon,npm |
| vendor_a-statics1 | 321 MiB | 3945 | 游戏短名 | cnt,dft,fg4,fhb,lj,lj2,lt,mpt,mpt_ori,rc2,tcb,tcb_backup,tcgox + astarte,astarte2,static,smallicon |
| vendor_a-statics2 | 111 MiB | 1519 | 游戏短名 | lj,lj500,lm + astarte,astarte2,static,smallicon |
| vendor_a-statics3 | 3.15 GiB | 21065 | 游戏短名 | afr,ap,bc100,cai,cashcoin,cbs2,cc4x4,cj,ctk,eg,fdm,fg5,fha,fullhouse5,ge2,jcuf,jf,jf2,jpj,lch,lj,loe,lvlc,mcp2,mp2,pa,pirate2,qt,rx10000,sk,sos2,sweetheart5,tcgp,tll,tlp,tpt,tsq,uln,upirate,witch + astarte,astarte2,static,smallicon |
| vendor_a-statics4 | 2.03 GiB | 12456 | 游戏短名 | bboss,bite,cc3x3,cc4x4uf,clb,cof,crown40,cts,cz72,dad,fcuf,fha,gb,ge2,gme,jc,ka,lgs,mpt2,psd_ori,pw,roe,sc,smg,tct,tct2,tcwt,tlb,tltb,tptb,ubh,x7hot + astarte,astarte2,assets,data,JLTOLO,static,smallicon,_nuxt |
| vendor_a-statics5 | 1.97 GiB | 21584 | 游戏短名 | ar2fccc,bby,bc20,bfc,bikini,c7d,cbs,cbt2,cc,cc3x5,col,crown,dbg,dl,jce,lgs,ltn,lwc,phoenix,ps,rg7,rxmw,saj,samurai,tfp,ucny,wl,x15hot,yg500,zeus + astarte,astarte2,astarte2_b9e3f,static,smallicon,_nuxt |
| pp-static | 19.5 GiB | 28891 | **gs2c/** 为前端主目录 | gs2c（含 common/v5/games-html5/… 等） |
| ppk-static | 1.96 GiB | 8448 | popok/ 与 promotion/ | popok, promotion |
| vendor_c-static | 1.17 GiB | 25971 | **下划线游戏名目录** | 100_joker_staxx,3_luxor_pots,… ,power_crown,sunny_fruits,thunder_coins_xxl,wolf_power …（54 款）+ config |
| vendor_d-static | 1.33 GiB | 79933 | **连字符游戏名目录** | aquarius-fortune-wheel,aztecs-mystery,…,year-of-the-golden-horse（60+ 款）+ assets,history,share-ui-game-client,_next,sw.js |
| g759-static | 968.8 MiB | 13009 | games/ + reso 目录 | games, reso.slo888.com, cdn-cgi |

## 四、Cloudflare Worker 对应关系

Worker `summer-wave-c94f`（静态代理）逻辑：

```text
hostname 第一段 = 前缀
BUCKET_MAP[前缀] -> GCS 桶（**统一取巴西 live 桶**）
再按 https://<bucket>.storage.googleapis.com/<path> 回源，
CORS 放开、GET 200 缓存 7 天（缓存键带版本盐 CACHE_SALT）
```

```text
BUCKET_MAP:
  pg-static      -> bizops-gcs-pg-static-sa
  pg3-static     -> bizops-gcs-pg3-static-sa
  pg4-static     -> bizops-gcs-pg4-static-sa
  pg5-static     -> bizops-gcs-pg5-static-sa
  pg6-static     -> bizops-gcs-pg6-static-sa
  pg7-static     -> bizops-gcs-pg7-static-sa
  vendor_a-statics   -> bizops-gcs-vendor_a-statics-sa
  vendor_a-statics1  -> bizops-gcs-vendor_a-statics1-sa
  vendor_a-statics2  -> bizops-gcs-vendor_a-statics2-sa
  vendor_a-statics3  -> bizops-gcs-vendor_a-statics3-sa
  vendor_a-statics4  -> bizops-gcs-vendor_a-statics4-sa
  vendor_a-statics5  -> bizops-gcs-vendor_a-statics5-sa
  pp-static      -> bizops-gcs-pp-static-sa
  ppk-static     -> bizops-gcs-ppk-static-sa
  vendor_c-static -> bizops-gcs-vendor_c-static-sa
  vendor_d-static   -> bizops-gcs-vendor_d-static-sa
  g759-static    -> bizops-gcs-g759-static        <- 唯一不是 -sa 的
```

非静态前缀（api/games 等）Worker 直接放行，保持原 CF → nginx 链路。

## 五、要做的动作

```text
1) AWS 账户 517506432530，区域 ap-northeast-3（大阪）
   建 17 个桶：bizops-s3-<prefix>（私有 + 版本控制）
2) 从 GCS 巴西桶导入一次现有前端资源（合计 39.92 GiB）
3) 逐前缀核对对象数与大小
4) 之后前端更新流程：开发传 S3 -> 谷歌侧按前缀从 S3 拉到 GCS -sa 与 asia
```

### 需要的 IAM 权限

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow",
     "Action": ["s3:CreateBucket", "s3:ListBucket", "s3:GetBucketLocation",
                "s3:PutBucketPublicAccessBlock", "s3:PutBucketVersioning"],
     "Resource": ["arn:aws:s3:::bizops-s3-*"]},
    {"Effect": "Allow",
     "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject",
                "s3:AbortMultipartUpload", "s3:ListMultipartUploadParts"],
     "Resource": ["arn:aws:s3:::bizops-s3-*/*"]}
  ]
}
```

当前宝塔上 `/root/bizops-h5-download.env` 的身份
`arn:aws:iam::517506432530:user/linux-uploader` 缺少 `s3:CreateBucket`，
策略挂到这个用户后即可用（无需新建访问密钥）。

## 六、工具

```text
docker/scripts/gcs_static_inventory.sh        盘点各桶体量/对象数/顶层目录
docker/scripts/s3_static_buckets_create.py    建 17 个桶（--dry-run 可预演）
docker/scripts/gcs_to_s3_static_import.sh     逐前缀导入（gsutil 落盘 -> aws s3 sync）
```

## 七、执行结果（2026-09-11 00:40 起）

### 建桶

```text
2026-09-11 00:32（UTC 18:32Z）17/17 全部创建成功，区域 ap-northeast-3（大阪）
每个桶：BlockPublicAccess 全开（私有）+ 版本控制 Enabled
bizops-s3-pg-static / pg3 / pg4 / pg5 / pg6 / pg7
bizops-s3-vendor_a-statics / vendor_a-statics1..5
bizops-s3-pp-static / ppk-static / vendor_c-static / vendor_d-static / g759-static
```

### 中文备注

```text
S3 没有"描述"字段，改用两处：
1) 桶根对象 `_README_厂家说明.txt`（17/17 写入成功，控制台点进桶即可见）
   含：厂家 / 内容 / 顶层目录说明 / 对应 GCS 桶 / CDN 域名 / 更新方式
2) 桶标签（厂家、备注、顶层目录、GCS对应桶、CDN域名）
   —— 首次执行被拒：策略 bizops-s3-statics-rw 缺少 s3:PutBucketTagging
   如需标签需在策略第一条 Statement 补 "s3:PutBucketTagging","s3:GetBucketTagging"
```

### 导入（进行中）

```text
顺序按体量从小到大：pg6 → pg7 → vendor_a-statics2 → vendor_a-statics1 → pg5 → pg3 →
  g759 → vendor_c → vendor_a-statics → vendor_d → pg4 → ppk → vendor_a-statics5 →
  vendor_a-statics4 → pg-static → vendor_a-statics3 → pp-static(19.5G，最后)
后台日志：/root/vendor_a-zips/gcs2s3-import.log
进度播报：/opt/bizops-scripts/s3_import_poster.py（每 10 分钟发一次群）
每完成一个前缀输出 `PROGRESS n/17 pct% <prefix> local=<n> s3=<n>`
（s3 侧比本地多 1 个对象 = 中文说明文件）
```

### ⚠️ 踩坑：GCS 的「目录别名」对象让 gsutil 落盘失败

```text
现象：vendor_a-statics2 / vendor_a-statics1 / pg5 / pg3 / g759 / vendor_c 等前缀
      被脚本判为 rsync 失败而跳过，S3 里只有说明文件、没有业务资源。

根因：GCS 为了让 https://<域名>/<目录>/（带结尾斜杠）可访问，
      在每个目录下放了**名字以 "/" 结尾的对象**：
        gs://bizops-gcs-vendor_a-statics2-sa/lj/、/lj500/、/lm/
        gs://bizops-gcs-vendor_a-statics1-sa/cnt/、/dft/、/_probe/slash/
        gs://bizops-gcs-pg5-static-sa/1879752/  (pg5 21 个)
      gsutil 下载时会尝试写成"名字以斜杠结尾的本地文件"，报
        InvalidUrlError: Invalid destination path: …/lj/
      并让整次 gsutil rsync 返回非 0。试过 -x '/$' 过滤，无效。

修复（docker/scripts/gcs_to_s3_static_import.sh）：
  1) rsync 非 0 不再中断，只记录 note，其余文件照常落盘上传
  2) 先把别名对象列到 _markers/<prefix>.txt
  3) 上传后用 s3api put-object --key "<目录>/" 在 S3 原样补建
     （否则日后 S3→GCS 反向同步会丢别名，/cnt/ /lj/ 这类地址会重新 404）
  4) 兜底：某前缀一个文件都没落盘才算真失败，跳过并报错

验证（vendor_a-statics2）：落盘 1516 + 别名 3 + 说明 1 = S3 实测 1520 个对象，
s3 ls 可见 PRE lj/、PRE lj500/、PRE lm/
```

### 进度播报

`docker/scripts/s3_import_poster.py` 每分钟发一次：

```text
总体进度条 + 实时网速（↓下载 / ↑上传）
✅已完成 n/17 + ⏳进行中厂家
每个厂家各自的进度条：✅完成100% / ⏳当前(下载或上传 n/total) / ⌛未开始0%
```
