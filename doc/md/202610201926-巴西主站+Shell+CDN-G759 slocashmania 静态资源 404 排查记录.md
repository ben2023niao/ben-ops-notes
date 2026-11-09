---
id: "doc-11faf0119e98"
title: "G759 slocashmania 静态资源 404 排查记录"
date: "2026-10-20T19:26:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "CDN", "故障排查"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-10-20-1926-%E3%80%90%E8%BF%90%E7%BB%B4%E3%80%91G759-sloca%E8%B5%84%E6%BA%90404%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-10-20-1926-【运维】G759-sloca资源404排查记录.md"
sourceSha256: "2dfe38b0577c546052b81738c1a00c57fee8f215678121f42df77df47b4d20f4"
sourceSystem: "project-doc"
---

# G759 slocashmania 静态资源 404 排查记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610201926-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BCDN-G759%20slocashmania%20%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90%20404%20%E6%8E%92%E6%9F%A5%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-10-20 19:26｜日期依据：文件名日期

时间：2026-10-20 19:26（北京）｜2026-10-20 08:26（巴西圣保罗）
反馈：测试人员在 `g759-static.xqv9m8.icu` 打开 slocashmania 时，
      `slocashmania_lang/native` 下 4 个 png/jpg 返回 404；test/uat 正常。

## 一、结论

**资源没有丢，源站和 CDN 都是 200。** 4 个文件在 GCS 桶
`newgg2-bizops-gcs-g759-static` 里都存在，直连 GCS 与走
`g759-static.xqv9m8.icu` / `g759-static.vendor_a-cdn-2026.icu` 均返回 HTTP 200。

最可能的原因是测试人员浏览器/边缘还留着旧缓存里的 404：
2026-10-20 13:54 之前 Worker 会把 404 也缓存 7 天，
当天 13:54 已通过给 g759 加缓存版本键 `v1` 整体失效，但**用户本地浏览器**的 404
需要清缓存或无痕窗口才会消失。

## 二、逐文件实测

从宝塔（巴西出口）实测：

| 文件 | 大小 | GCS 直连 | CDN xqv9m8 | CDN vendor_a-cdn-2026 |
| --- | --- | --- | --- | --- |
| `14/147b324b0.3fcaf.png` | 81,912 | 200 | 200 | 200 |
| `1e/1ea965735.fb801.png` | 274,501 | 200 | 200 | 200 |
| `1f/1f0e7d470.bf949.png` | 78,075 | 200 | 200 | 200 |
| `b0/b0c25bfc-c8dc-4f96-b3a8-2eaf10786cc2.8c980.jpg` | 232,440 | 200 | 200 | 200 |

完整 URL（已发群，消息 329；可复制的 txt 见消息 330）：

```text
https://g759-static.xqv9m8.icu/games/slocashmania/assets/slocashmania_lang/native/14/147b324b0.3fcaf.png
https://g759-static.xqv9m8.icu/games/slocashmania/assets/slocashmania_lang/native/1e/1ea965735.fb801.png
https://g759-static.xqv9m8.icu/games/slocashmania/assets/slocashmania_lang/native/1f/1f0e7d470.bf949.png
https://g759-static.xqv9m8.icu/games/slocashmania/assets/slocashmania_lang/native/b0/b0c25bfc-c8dc-4f96-b3a8-2eaf10786cc2.8c980.jpg
```

## 三、建议测试方式

1. 先用无痕窗口打开上面 4 条 URL，确认返回图片；
2. 如果无痕可以、正常窗口不行 → 是本地缓存，清站点缓存即可；
3. 如果无痕仍然 404，请把**完整 URL + 请求时间 + 所在地区/VPN**发出来，
   再按具体节点查边缘缓存。

## 四、复核命令

```bash
# 直连 GCS
curl -sI "https://newgg2-bizops-gcs-g759-static.storage.googleapis.com/games/slocashmania/assets/slocashmania_lang/native/1e/1ea965735.fb801.png"

# 走 CDN
curl -sI "https://g759-static.xqv9m8.icu/games/slocashmania/assets/slocashmania_lang/native/1e/1ea965735.fb801.png"
```
