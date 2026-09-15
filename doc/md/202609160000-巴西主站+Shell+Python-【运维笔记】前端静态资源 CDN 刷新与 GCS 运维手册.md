---
id: "doc-1c6fe55d5d96"
title: "【运维笔记】前端静态资源 CDN 刷新与 GCS 运维手册"
date: "2026-09-16T00:00:00+08:00"
dateSource: "正文日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Python", "Docker", "CDN", "安全运维", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/%E3%80%90%E8%BF%90%E7%BB%B4%E7%AC%94%E8%AE%B0%E3%80%91%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90CDN%E5%88%B7%E6%96%B0%E4%B8%8EGCS%E8%BF%90%E7%BB%B4%E6%89%8B%E5%86%8C.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/【运维笔记】静态资源CDN刷新与GCS运维手册.md"
sourceSha256: "180ad882b166f0cf3d6d50dad80a39936a0cd010d753fff4a2ed29bb8284d574"
sourceSystem: "project-doc"
---

# 【运维笔记】前端静态资源 CDN 刷新与 GCS 运维手册

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/【运维笔记】静态资源CDN刷新与GCS运维手册.md`

> 整理日期：2026-09-16 00:00｜日期依据：正文日期

适用：`newgg2-0520` 项目的厂家前端/客户端静态资源（Panda / TADA / PG / PP / PPK / PlaySon / G759）。
链路：`AWS S3（大阪，开发上传）→ 巴西 GCS 桶（newgg2-dbqp-gcs-<前缀>）→ Cloudflare Worker → 静态域名`。
本手册只讲"人工就能照着做"的操作，命令可以直接复制。

---

## 一、刷新某个厂家的 CDN 缓存（最常用）

### 1. 先记住两条硬事实（2026-09-16 实测）

```
1) 按 URL 刷新（purge files）对静态链路【无效】。
   实测：purge 之后请求仍返回 cf-cache=HIT，缓存条目没被清掉。
   原因：Worker 用 fetch(cf.cacheKey + cacheEverything) 缓存，缓存键是
        https://<前缀>.internal-static-pool/<路径>，不是真实 URL。
2) 唯一有效的方式：整 zone 刷新（purge_everything），
   或者改 Worker 里的缓存盐后重新部署（影响全部厂家）。
```

所以"只刷新某一个厂家"做不到。我们的做法是：**只对服务该厂家静态域名的那些 zone** 做
`purge_everything`，把影响面压到最小（这些 zone 是共享的，其它厂家缓存也会被清，但只是回源一次，
会自动重新缓存，风险很低）。

### 2. 操作（在宝塔上执行，CF token 有 IP 白名单，必须在宝塔跑）

**最省事、最可靠：全部刷新（开发只改了一个图标也建议直接全刷）**

```bash
bash /opt/dbqp-scripts/cf_purge_zones.sh --all
# 期望输出：每个 zone 一行 OK，最后 PURGE_DONE ok=23 fail=0（2026-09-16 实测 23/23 OK）
```

全刷的影响：所有静态域名的边缘缓存被清一次，用户下次访问会回源 GCS 重新缓存；
只是短暂回源流量，不会影响业务（我们已多次执行，无异常）。

**想尽量只刷一个厂家（做不到"只刷单个文件"，见下面 1. 的两条硬事实）**

```bash
# 只刷 panda（自动挑出服务 panda-static.* 的 zone，实测 22 个 zone）
bash /opt/dbqp-scripts/cf_purge_zones.sh --vendor panda

# 指定 zone
bash /opt/dbqp-scripts/cf_purge_zones.sh --zones xqv9m8.icu,q7m9v8.icu
```

看到 `PURGE_DONE ok=22 fail=0` 即成功（单个 zone 失败会打印 FAIL 原因）。

### 2.1 静态域名分布（复验时别用错 zone，否则会看到 520）

```text
所有厂家的静态域名都分布在下面这些 zone（共 23 个，每个厂家都有 <前缀>-static.<zone>）：
  xqv9m8.icu              tada-cdn-2026.icu       tada-cdn-game.icu
  tada-host-2026.icu      tada-host-game.icu      tada-cf-2026.cyou
  tada-cf-game.cyou       cdn-tokyo-dbqp.icu      cdn-tokyo-dbqp.cyou
  cdn-manila-dbqp.icu     cdn-manila-dbqp.cyou    q7m9v8.icu
  qv9m8.icu               7m9v8.icu               6qv8m.icu
  6xv8q.cyou              7v8k3.cyou              8m7xv.cyou
  m6xv8q.cyou             m7v8k3.cyou             p8m7xv.cyou
  t6qv8m.icu              d1b2q3p.cfd

已知例外（不是故障，别误判）：
  · q7m9v8.icu 只服务 pg/pp/ppk/panda 等，不服务 tada-*；
    访问 https://tada-statics4.q7m9v8.icu/... 会返回 520 —— 这是既有的域名配置差异。
  · d1b2q3p.cfd 的静态子域未生效（也返回 520）。
复验时请用「厂家自己的域名」，例如：
  panda-static.* / tada-statics4.xqv9m8.icu / pg-static.q7m9v8.icu / pp-static.q7m9v8.icu
```

### 3. 立刻验证（应看到 `cf-cache=MISS` 且 `200`）

```bash
UA='Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X)'
curl -s -o /dev/null -D - -A "$UA" https://panda-static.xqv9m8.icu/health.json \
  | grep -iE 'HTTP/|cf-cache-status'
# 期望：HTTP/2 200  +  cf-cache-status: MISS（MISS = 已经回源，缓存已生效）
```

再抽几个真实资源（把 `<游戏目录>` 换成实际目录，例如 `aquarius-fortune-wheel`）：

```bash
for p in <游戏目录>/index.html <游戏目录>/health.json; do
  printf "%-50s " "$p"
  curl -s -o /dev/null -D - -A "$UA" "https://panda-static.xqv9m8.icu/$p" \
    | awk 'BEGIN{IGNORECASE=1}/^HTTP/{s=$2}/^cf-cache-status/{c=$2}END{gsub(/\r/,"",c);print s, c}'
done
```

---

## 二、怀疑"开发更新了资源但线上还是旧的/404"时怎么查

### 1. 先比对 GCS 与 AWS S3，看差异（零数据搬运）

```bash
# 在 03 上（容器里有 GCS/S3 SDK 与凭据）
docker run --rm --network host \
  -v /opt/dbqp-scripts:/opt/dbqp-scripts:ro \
  -v /root/dbqp-h5-download.env:/creds/aws.env:ro \
  --entrypoint python3 dbqp-resource-sync:latest \
  /opt/dbqp-scripts/gcs_s3_diff.py --prefix panda-static --out /tmp/panda_diff.txt
```

输出四类：GCS 缺失 / 大小不符 / 内容不符 / GCS 独有，并把需要处理的 key 写到 `/tmp/panda_diff.txt`。

> ⚠️ 不要用 GCS 对象的 `updated` 时间判断谁新谁旧：做过桶迁移（服务端 rewrite）后，
> 全量对象的时间都会被刷成迁移当天，看不出真实改动（2026-09-16 实测 panda 全部 91092 个对象
> 时间都是迁移那天）。

### 2. 需要把 S3 的缺失文件补到 GCS

```bash
# 只补"GCS 完全没有"的文件（安全，不覆盖内容不一致的）
docker run --rm --network host \
  -v /opt/dbqp-scripts/gcs-br:/opt/dbqp-scripts:ro \
  -v /root/dbqp-h5-download.env:/creds/aws.env:ro \
  --entrypoint python3 dbqp-resource-sync:latest \
  /opt/dbqp-scripts/s3_gcs_sdk_sync.py --prefix panda-static --apply --only-missing --skip-cdn

# 全量同步（会把 S3 版本覆盖到 GCS，慎用：可能回退开发直传 GCS 的新版本）
... --prefix panda-static --apply
```

补完/同步完，**必须再刷一次 CDN**（见第一节），否则线上还是旧内容。

---

## 三、每次动完桶之后的固定自检（防止 2026-09-14 那种事故）

事故回顾：迁移时新建的 GCS 桶默认私有，缺 `allUsers:objectViewer`，
Worker 匿名回源拿到 403，又被 `cacheEverything` 缓存 7 天 → 玩家"进不去游戏"。

```bash
# 1) 桶必须公开读
for p in panda-static tada-statics4; do
  gcloud storage buckets add-iam-policy-binding gs://newgg2-dbqp-gcs-$p \
    --member=allUsers --role=roles/storage.objectViewer >/dev/null 2>&1
  code=$(curl -s -o /dev/null -w '%{http_code}' "https://newgg2-dbqp-gcs-$p.storage.googleapis.com/health.json")
  printf "%-34s 匿名直读 health=%s\n" "$p" "$code"   # 期望 200
done

# 2) 走 CDN 再验一次（期望 200；cf-cache 是 MISS 还是 HIT 都无所谓）
curl -s -o /dev/null -w '%{http_code}\n' https://panda-static.xqv9m8.icu/health.json
```

---

## 四、人工验收：点开就能进游戏的链接怎么来

平台签发的是带 `ssoKey` 的启动 URL（约 10 分钟有效）。三种拿法：

1. **面板直接点**（最简单）：`https://ff789p3.com/#/dashboard/game` 登录后点卡片。
2. **深链签发**（可以指定任意 gameID，绕过面板列表限制）：
   `https://ff789p3.com/#/game/play?id=1&gameId=1&gameVenueId=90&thirdId=<gameID>&categoryId=-1&status=Enable&name=TADA+Slot`
   （TADA 用 `gameVenueId=90`；PG 用 `85`）
3. **批量签发脚本**：`docker/scripts/mint_game_urls.py`（跑在 03 的浏览器容器里），
   把要测的 gameID 写进脚本里的 `GAMES` 即可，输出每条 URL。

拿到 URL 后用手机打开即可；要做自动抽测用 `docker/scripts/game_probe.py`
（支持 `--ua-preset ios|android|desktop`、`--direct-url`，会输出 4xx/JS 报错/截图）。

---

## 五、常用地址与脚本索引

| 用途 | 位置 |
| --- | --- |
| 刷新 CDN（本手册一） | `docker/scripts/cf_purge_zones.sh`（宝塔上跑） |
| GCS 与 S3 差异比对 | `docker/scripts/gcs_s3_diff.py` |
| S3→GCS 同步（含 only-missing） | `docker/scripts/s3_gcs_sdk_sync.py` |
| 单游戏抓包探针 | `docker/scripts/game_probe.py` |
| 批量签发游戏启动 URL | `docker/scripts/mint_game_urls.py` |
| 桶迁移工具（含建桶即公开） | `docker/scripts/gcs-br-migrate/` |
| 03 上的运行副本 | `/opt/dbqp-scripts/`、`/opt/dbqp-scripts/gcs-br/` |
| 日志 | `/var/log/dbqp-br/`（每厂家一个日志 + state/*.json） |
| 浏览器测试镜像 | 03 上 `dbqp-browser-test:latest`（不在时用 `/opt/dbqp-browser-test/Dockerfile` 重建） |

静态域名池（platform 侧配置）：`/app/platform-api/conf/domains/<厂家>.json`，
每个厂家配两个域名，**启动时随机二选一**，所以"同一台手机换一次进入"可能落到不同域名。

---

## 六、常见坑（都踩过）

1. **URL 级 purge 对 Worker 缓存无效** → 只能 zone 级 purge（或改 Worker 缓存盐）。
2. **新建/重建的 GCS 桶默认私有** → 必须补 `allUsers:objectViewer`，否则 403 被缓存。
3. **缓存会把 404/403 也缓存住**（`cacheEverything`），所以"文件其实已经有了"也可能一直 404，
   补完文件一定要刷缓存。
4. **浏览器侧也有 7 天缓存**（Worker 给 200 打了 `Cache-Control: public, max-age=604800`），
   用户报"还是旧的"时，让他清缓存或用隐私窗口。
5. **国家白名单**：Worker 与后端都限制 `BR/SG/HK/AE`。
   用户报打不开时先让他打开 `https://<静态域名>/cdn-cgi/trace` 看 `loc=`。
6. **CF token 有 IP 白名单**：只能在宝塔上刷缓存，从 03 直接调会 403。

---

## 七、最短处置流程（照着做）

```text
【开发改了某个图标/某个文件】
1. 在宝塔刷缓存：      bash /opt/dbqp-scripts/cf_purge_zones.sh --all
                       期望 PURGE_DONE ok=23 fail=0
2. 复验（用厂家自己的域名，不要用不服务它的 zone）：
   curl -s -o /dev/null -D - -A 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X)' \
     https://panda-static.xqv9m8.icu/<改动的文件路径> | grep -iE 'HTTP/|cf-cache-status'
   期望 200 + cf-cache-status: MISS
3. 让报问题的用户清一下浏览器缓存（Worker 给 200 打了 7 天浏览器缓存），或换隐私窗口再试。
4. 若怀疑"文件根本没传上来"：在 03 跑 gcs_s3_diff.py 比对，再决定是否补文件（补完要再刷一次）。
```

记录：2026-09-16 开发更新 panda 的一个图标后，按上面第 1、2 步执行，
23/23 zone 刷新成功；全厂家 × 4 个 zone 共 32 条抽检里 30 条 200/MISS，
另外 2 条是 q7m9v8.icu 不服务 tada-*（既有配置差异，与本次刷新无关）。

---

## 八、为什么 `gcloud storage rsync` 在 panda 这种桶上非常慢（2026-09-16 实测）

开发常跑的命令：

```bash
gcloud storage rsync -r panda gs://newgg2-dbqp-gcs-panda-static/ \
  --delete-unmatched-destination-objects --exclude=".*health\.json$" --dry-run
```

它慢的原因（按影响从大到小）：

```text
1) rsync 必须把【源和目标全量枚举后逐个比较】。
   panda 桶有 91092 个对象，本地 panda 目录约 3 万个文件。
   实测：只列举目标桶带元数据(name+size+md5) = 5.9 秒（巴西本机）；
        用 `gcloud storage ls` 列举同样数量 = 17 秒。
2) --delete-unmatched-destination-objects 是最大的放大器：
   本地只有约 3 万个文件，桶里有 91092 个对象 → 约 6.1 万个对象属于
   "目标独有"，每一个都要作为"待删除候选"参与判定。
   实测：把 --dry-run 的源目录设为【空目录】，光是"列举 + 删除判定"就要 54 秒（巴西本机）。
3) --dry-run 不会省掉上面任何一步，它只是不执行写入/删除，比较阶段完全一样。
4) 逐个文件的比较本身有成本：实测 100 个本地文件对 586 个目标对象 = 5 秒
   （约 25~50ms/文件）。按 3 万个本地文件 + 9.1 万个目标对象估算，
   巴西本机也要几十分钟；开发从本地电脑跑（到 GCS 的往返延迟高得多）就会到小时级。
5) 判"是否需要同步"要看修改时间；GCS 对象没有本地意义的 mtime
   （panda 全量对象的 updated 都是迁移那天 2026-09-14 11:48），
   于是退化成"逐个算哈希比较"，等于把本地每个文件都完整读一遍。
6) --exclude 只在枚举之后生效，不会减少枚举/判定的开销。
```

⚠️ 顺带提醒：`--delete-unmatched-destination-objects` 对 panda 是**危险参数**——
本地目录是"部分镜像"（约 3 万），桶里有 9.1 万，真跑（去掉 --dry-run）会删掉约 6 万个对象。

**更快、更安全的做法（推荐给开发）**

```text
a) 先做"元数据比对"找出差异，不要用 rsync 全量比较：
   docker/scripts/gcs_s3_diff.py（panda 全量比对约 40 秒，零数据搬运）
   → 得到"需要上传/需要删除"的 key 清单
b) 只传清单里的文件：
   gcloud storage cp -I <changed_keys.txt> gs://newgg2-dbqp-gcs-panda-static/
   （用 -n/--no-clobber 或先 --dry-run 确认）
c) 要"镜像"就放到离桶近的机器上跑（例如 03，圣保罗同区），
   不要在本地电脑对 9 万对象的桶做全量 rsync；
d) 源其实是 AWS S3 时，直接跑 SDK 同步（不落本地磁盘）：
   docker/scripts/s3_gcs_sdk_sync.py --prefix panda-static --apply --only-missing
e) 更新完记得刷 CDN：bash /opt/dbqp-scripts/cf_purge_zones.sh --all
```
