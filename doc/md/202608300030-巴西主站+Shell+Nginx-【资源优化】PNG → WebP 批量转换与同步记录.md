---
id: "doc-abc90fc9b8f4"
title: "【资源优化】PNG → WebP 批量转换与同步记录"
date: "2026-08-30T00:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Nginx", "CDN", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-08-30-0030-%E3%80%90%E8%B5%84%E6%BA%90%E4%BC%98%E5%8C%96%E3%80%91PNG%E8%BD%ACWebP%E6%89%B9%E9%87%8F%E8%BD%AC%E6%8D%A2%E4%B8%8E%E5%90%8C%E6%AD%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-08-30-0030-【资源优化】PNG转WebP批量转换与同步记录.md"
sourceSha256: "fa60564dd02dc1e1bf9f1d59ae3c591c23e7470956c31a183a2ad45d87f392ef"
sourceSystem: "project-doc"
---

# 【资源优化】PNG → WebP 批量转换与同步记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202608300030-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BNginx-%E3%80%90%E8%B5%84%E6%BA%90%E4%BC%98%E5%8C%96%E3%80%91PNG%20%E2%86%92%20WebP%20%E6%89%B9%E9%87%8F%E8%BD%AC%E6%8D%A2%E4%B8%8E%E5%90%8C%E6%AD%A5%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-08-30 00:30｜日期依据：文件名日期

时间：2026-08-30 00:30（Asia/Manila）
项目：某业务公司 / PGServer master
执行人：Codex（本地工作区 + 宝塔 + GCS）

## 一、背景

前端静态资源 PNG 为最大头（源目录 38400+ 张 / 7.6GB，12 个厂商目录）。
CF Polish 已先行自动转 WebP（省 43-45%），本次做**源站主动转换**：
PNG 字节直接替换为 WebP（保持 .png 文件名，URL 不变），桶对象 Content-Type 改 image/webp，
进一步减小源站体积、降低回源流量，且非 CF 路径同样受益。

## 二、备份（先行，可回滚）

```text
/www/backup/static-png-20260829.tar          6.0G（主 7 目录 38400 张 PNG + 清单）
/www/backup/static-png-special-20260829.tar  1.6G（pg3/4/5、vendor_a-statics1/2 特殊目录）
还原：解 tar 覆盖源目录 → 重新 gcs sync
```

## 三、转换

工具：cwebp 1.2.2（apt webp 包；Pillow method=6 对 5MB 大图过慢弃用）

```text
参数：-q 85 -m 4，4 进程并行（xargs -P 4）
规则：webp 比 png 小 ≥10% 才替换，否则保留原 PNG
结果（45227 张）：
  28188 张 → WebP 字节（RIFF..WEBP 校验通过）
  17039 张 → 保留 PNG（小图标类 webp 无收益）
体积：7.6GB → 3.9GB（省约 50% / 3.8GB）
```

## 四、同步与 Content-Type

```text
/opt/sync_webp.sh：
  逐厂商 rsync 源目录 → live(-sa 圣保罗) + asia(东京) 桶
  setmeta：仅对 WebP 字节的 .png 对象改 Content-Type:image/webp（PNG 字节不动）
日志：/www/wwwlogs/gcs_webp_sync.log；完成标记 /tmp/webp_sync.done
```

## 五、验证（同步完成后）

- 抽样对象 Content-Type: image/webp + 体积；
- CF URL 返回 image/webp；游戏页加载 smoke；
- 回滚：备份 tar 还原 + 重同步。

## 六、大 JS / 字体 / JSON（本轮结论）

```text
大 JS：pp game-history-client main.*.min.js 1.3MB/1.1MB 仅被
  lastGameHistory*.html 引用（非主游戏路径，script 无 defer）——建议 defer/分包，
  vendor 代码改动需灰度，本轮不盲改；
字体：1 个 ttf 237KB（Montserrat-Medium），CSS 未声明 woff2，转 woff2 需改
  vendor CSS，收益小，暂缓；
JSON：生产 90447 个 JSON，全量引用审计过慢，降级为专项审计待办（P3）。
```

## 七、待办

- 同步/验证完成后更新本记录 + 提交；
- 把 setmeta 步骤并入 gcs_static_sync cron（防后续同步回退 Content-Type）；
- 大 JS defer/分包灰度方案（前端/灰度）；
- JSON 专项审计。

## 八、执行结果（2026-08-30 凌晨）

### 转换

```text
工具：cwebp 1.2.2（apt webp），-q 85 -m 4，xargs -P 4
总数 45227；28188 转 WebP，17039 保留 PNG（webp 无 10% 收益跳过）
源目录 7.6GB → 3.9GB（省约 50%）
备份：/www/backup/static-png-20260829.tar(6.0G) + static-png-special-20260829.tar(1.6G)
```

### 同步踩坑与修复

```text
坑1：gsutil rsync 误加 -r 参数（rsync 不支持）→ 全部 CommandException，0 文件上传；
坑2：gsutil -h 必须放在子命令前（gsutil -h "..." cp），放 cp 后报 Incorrect option；
坑3：gsutil setmeta / 单文件 cp 并发低（~1.5 对象/s），56k 对象不可行。
解决：rsync（去 -r，12 厂商 ~3 分钟）+ GCS JSON API 并发 PATCH
      （64 线程，28188 对象 79 秒，354/s，0 失败）。
```

### 最终验证

```text
源站对象：字节=WebP（Content-Length 11130 等），Content-Type=image/webp
抽样：vendor_a-statics-sa / pp-static-sa / g759-static 全部通过
cron：/www/server/cron/gcs_static_sync 尾部追加 /opt/webp_setmeta_only.sh
      （近 1 天新增 webp 对象自动 PATCH 类型，备份 .bak-20260830）
```

### 脚本资产（生产宝塔 /opt/，文档化保留）

```text
/opt/webp_convert_c.sh      源目录 PNG→WebP（cwebp q85 m4）
/opt/rsync_live.sh          12 厂商 rsync 到 live(-sa) 桶 + PATCH
/opt/patch_webp_ct.py       GCS JSON API 并发 PATCH Content-Type:image/webp
/opt/cp_webp.sh             gsutil -h 正确姿势单文件上传
/opt/webp_setmeta_only.sh   cron 尾步（近 1 天新增）
```

### 待办（外部）

- CF 缓存清理（3 套 zone 面板 Purge Everything）后，浏览器拉到新 webp 字节；
- asia(东京) 桶未动（香港走 AWS CloudFront，不在当前服务路径），后续如需同步再跑同一套。

## 九、清缓存后复测（2026-08-30）

用户面板清理 3 套 zone CF 缓存；另发现宝塔 nginx 源站 static_cache 仍存旧 PNG
（1h TTL 未过期），已清空两机源站缓存目录（缓存可重建，安全）并 reload。

```text
3 套 zone（xqv9m8 / vendor_a-cdn-2026 / cdn-tokyo-bizops）：
  图片：content-type image/webp，11130B vs 原 20067B（省 45%）
  大图：43500B vs 原 82942B（省 48%）
  真实 URL 无参数同样出 webp；cf MISS→HIT 正常
游戏页/资源 smoke：pg4-static/126、g759 游戏页、vendor_d 游戏页 全 200
```

结论：源站主动转换（省 50%）+ CF Polish 边缘压缩（40-50%）双保险；
新文件 URL 不变、可回滚（备份 tar）。
