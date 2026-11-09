---
id: "doc-2b7c7f293284"
title: "2026-10-05 香港 nginx 的 vendor_b 静态改为走 vendor_b 自己的大阪桶（对齐香港 Worker）"
date: "2026-10-05T12:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Docker", "Nginx", "CDN", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/cn/docker/doc/2026-10-05-1230-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E9%A6%99%E6%B8%AFnginx%E7%9A%84vendor_b%E9%9D%99%E6%80%81%E6%94%B9%E4%B8%BA%E8%B5%B0%E8%87%AA%E5%B7%B1%E7%9A%84%E5%A4%A7%E9%98%AA%E6%A1%B6%EF%BC%88%E5%AF%B9%E9%BD%90%E9%A6%99%E6%B8%AFWorker%EF%BC%89.md"
sourcePath: "~/Projects/ops/private-notes/cn/docker/doc/2026-10-05-1230-【架构改造】香港nginx的vendor_b静态改为走自己的大阪桶（对齐香港Worker）.md"
sourceSha256: "2d434d1429085d7bcb8693567f84f293e225f8ca7c96e07ea0d777dcff622db7"
sourceSystem: "project-doc"
---

# 2026-10-05 香港 nginx 的 vendor_b 静态改为走 vendor_b 自己的大阪桶（对齐香港 Worker）

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610051230-%E9%A6%99%E6%B8%AF%20CN%2BDocker%2BNginx-2026-10-05%20%E9%A6%99%E6%B8%AF%20nginx%20%E7%9A%84%20vendor_b%20%E9%9D%99%E6%80%81%E6%94%B9%E4%B8%BA%E8%B5%B0%20vendor_b%20%E8%87%AA%E5%B7%B1%E7%9A%84%E5%A4%A7%E9%98%AA%E6%A1%B6%EF%BC%88%E5%AF%B9%E9%BD%90%E9%A6%99%E6%B8%AF%20Worker%EF%BC%89.md)

> 整理日期：2026-10-05 12:30｜日期依据：文件名日期

## 一、需求

```text
用户：vendor_b 需要映射到 vendor_b 自己的静态资源；参考香港 Worker 里 vendor_b 的关系。
（此前我们的 nginx 把 vendor_b-static* 映射到 /data/static/vendor_astatic*（vendor_a 的静态目录），是复用巴西的旧口径。）
本轮按流程发群通知。
```

## 二、依据：香港 Worker 里的 vendor_b 关系

```js
// docker/deploy/hongkong/cdn-backup/worker/bizops-hk-static-proxy.js（开发替换后的线上版）
const BUCKET_MAP = new Map([
    ["pg-static","bizops-s3-pg-static"], … ,
    ["vendor_b-static",  "bizops-s3-vendor_b-static"],    // vendor_b 自己的桶
    ["vendor_b-static1", "bizops-s3-vendor_b-static1"],   // vendor_b 自己的桶
    // vendor_b-static2 不在映射里（未命中 -> Worker 直接放行给源站）
]);
→ 回源地址：https://<bucket>.s3.ap-northeast-3.amazonaws.com<path>
补充：巴西没有 vendor_b（巴西 Worker 只有 vendor_a-statics1~5），所以 vendor_b 只能对它自己的桶。
```

结论：香港这边应该 `vendor_b-static → bizops-s3-vendor_b-static`、`vendor_b-static1 → bizops-s3-vendor_b-static1`，
这正是我们通用静态块的写法（`bizops-s3-<前缀>`），因此**不需要再给 vendor_b 单独开本地目录映射**。

## 三、改动（standby nginx）

```text
删除之前那一段「vendor_b/vendor_a 静态资源：本地目录优先」的 map + server 块
  （原来把 vendor_b-static/1/2 映射到 /data/static/vendor_astatic{,1,2}，再回源兜底到 vendor_b 桶）
改为：vendor_b-static* 落到通用静态块（server_name ~^[a-z0-9]+-static[0-9]?\.<域>$）
  -> 回源 bizops-s3-<前缀>，也就是 **vendor_b 自己的大阪桶**
  同时自动获得通用块里的规则（见 snippets/bizops-hk-standby-static-extra.conf）：
    目录请求 302 -> index.html ｜ customizations.info 返回空 200 ｜ .js 强制 charset=utf-8 ｜ OPTIONS 204 + CORS
备份：/etc/nginx/sites-available/bizops-hk-standby.conf.bak-20261005-vendor_bown
校验：nginx -t 通过 -> systemctl reload nginx
```

## 四、验证（源站 + 经 EdgeOne + CF 对照）

| 请求 | 改动前（vendor_a 本地目录） | 改动后（vendor_b 自己的桶） | CF 链路（06/07 Worker） |
| --- | --- | --- | --- |
| `/ifff/index.html` | 200，34,745B（vendor_a 的内容） | **200，34,238B** | 200，34,238B |
| `/favicon.ico` | 200，555B | 200，555B | 200，555B |
| `/ifff/`（目录） | 302 | 302 -> index.html | 302 |
| `…/customizations.info` | 403（vendor_b 块没有该规则） | **200，0B，application/octet-stream** | 200，0B |

```text
经 EdgeOne 复核（两站点 m4q7z1 / k8x2v9）：
  https://vendor_b-static.<域>/ifff/index.html -> 200  34238B  text/html
  https://vendor_b-static.<域>/favicon.ico     -> 200   555B
  https://vendor_b-static.<域>/ifff/           -> 302
  …/vs20starprss/desktop/customizations.info -> 200  0B  application/octet-stream
与 vendor_b 桶直连对比：bizops-s3-vendor_b-static/ifff/index.html = 200 / 34238B（一致）
EdgeOne 缓存刷新：两站点 purge_host vendor_b-static / vendor_b-static1 / vendor_b-static2
  JobId 3vtchhuq66a3（m4q7z1）｜ 3vtchi31tzrf（k8x2v9），FailedList 均为空
```

## 五、说明与遗留

```text
1. vendor_b-static1 的桶（bizops-s3-vendor_b-static1）当前是空的 -> 该域名下资源 403，与 CF 链路表现一致
   （等开发上传后自动可用，nginx 不需要再改）。
2. vendor_b-static2：Worker 里没有这个映射、vendor_b 也没有对应桶（bizops-s3-vendor_b-static2 不存在）→ 现在 404；
   历史上它也基本没被访问（日志里累计 1 次请求），保持与 Worker 一致即可。
3. /data/static/vendor_astatic{,1,2}（约 3GB）现在没有被任何配置引用，先留在磁盘上，需要时可回收。
4. vendor_b 游戏页此前报的 `/ifff/htt/…` 403 与本次改动无关（该资源在 vendor_b 桶里也不存在），
   开发侧已确认由他们改代码兼容。
```

## 六、关联

```text
docker/deploy/hongkong/nginx-standby.conf（本轮的改动）
docker/deploy/hongkong/nginx-standby-static-extra.conf（通用规则：customizations.info / .js）
docker/deploy/hongkong/cdn-backup/worker/bizops-hk-static-proxy.js（香港 Worker，vendor_b 映射依据）
docker/doc/2026-10-02-1630-【架构改造】香港nginx的vendor_b-vendor_a静态本地化与index-js修复.md（上一版：本地目录方案，本轮已废弃）
```
