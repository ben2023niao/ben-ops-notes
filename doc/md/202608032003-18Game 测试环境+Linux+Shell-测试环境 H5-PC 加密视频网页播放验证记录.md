---
id: "doc-865501fd6537"
title: "测试环境 H5/PC 加密视频网页播放验证记录"
date: "2026-08-03T20:03:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Nginx", "自动化", "CDN", "安全运维"]
source: "project-file:///Private/from-oldmac-20261109/Users/operator/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-03_2003-%E3%80%90%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95%2B%E5%AE%89%E5%85%A8%E4%BC%98%E5%8C%96%E3%80%91%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83H5-PC%E5%8A%A0%E5%AF%86%E8%A7%86%E9%A2%91%E7%BD%91%E9%A1%B5%E6%92%AD%E6%94%BE%E9%AA%8C%E8%AF%81.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-03_2003-【验证记录+安全优化】测试环境H5-PC加密视频网页播放验证.md"
sourceSha256: "6e760681ad85433540356214de622676fd5023296f3dc6fdcb6317bc72c0b490"
sourceSystem: "project-doc"
---

# 测试环境 H5/PC 加密视频网页播放验证记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-08-03_2003-【验证记录+安全优化】测试环境H5-PC加密视频网页播放验证.md`

> 整理日期：2026-08-03 20:03｜日期依据：文件名日期

时间：2026-08-03 20:03
分类：验证记录、安全优化、测试环境、后端 uploads、视频播放
范围：测试环境 H5/PC、`test-img.hbabaxb.cn`、后台 AWS S3 uploads、测试服务器 Nginx
风险等级：C1，测试环境小范围配置变更

## 1. 背景

本轮先在测试环境 H5/PC 页面检查视频资源。最初浏览器 Network 首页和典型页面没有捕获到视频请求，随后从后台 AWS S3 源桶 `18game-storage-dev-176528004422` 的 `uploads/` 中只读扫描对象，确认源桶内存在真实视频资源。

源桶扫描结果：

- 扫描对象：`uploads/`
- 分页：45 页
- 对象数量：44426
- 总大小：约 10323.2 MB
- 视频对象：87 个
- 视频类型：`mp4=86`、`avi=1`

后续在测试网页路由中发现真实视频引用：

- `https://test-h5.hbabaxb.cn/game/detail/285`
- `https://h5.youdianse-test.xyz/game/detail/285`

页面 HTML/SSR 数据中可找到 `test-img.hbabaxb.cn/uploads/...MP4`，且后端返回时已带 `token/t` 参数。

## 2. 原问题

抽查真实业务视频时发现：

- `test-img.hbabaxb.cn` 裸链访问视频会返回默认占位图，不能拿到原视频。
- `test-img.hbabaxb.cn` 带 `token/t` 访问真实业务视频返回 `502`。
- 同一个视频在旧 CloudFront `d391me9s8n5j5s.cloudfront.net` 可正常 `206 Range` 读取。
- 同一个视频在当前 `test-img` 回源的 `d1rct3ku9n07y3.cloudfront.net` 返回 `404`。

判断：

- 裸链防直开有效。
- 带 `token/t` 后不能播放，原因是当前 `test-img` 通用回源 `d1rct3ku9n07y3.cloudfront.net` 找不到这些视频。
- 当前 Nginx 规则只是检查 `token` 和 `t` 非空，以及 Referer 白名单；不是 md5 强验签。

## 3. 本次验证目标

用户要求：

> 抽几个视频上传，然后在现在测试环境 H5/PC 网页里面看看能不能正常加载渲染播放加密视频。

本轮目标：

1. 抽几个真实视频样本。
2. 上传或复制到独立测试路径。
3. 通过 `test-img.hbabaxb.cn` 形成带 `token/t` 的加密视频 URL。
4. 在当前测试 H5/PC 网页中实际渲染 `<video>`。
5. 验证浏览器 Network、mevendor_ata、播放状态。

## 4. 测试对象

从后台 AWS S3 源桶内选择 3 个已存在真实 mp4 视频，复制到独立 audit 路径：

```text
uploads/audit/video-playback/20260803/sample-01.mp4
uploads/audit/video-playback/20260803/sample-02.mp4
uploads/audit/video-playback/20260803/sample-03.mp4
```

S3 复制结果：

| 对象 | Content-Type | 大小 | 服务端加密 |
| --- | --- | ---: | --- |
| `sample-01.mp4` | `video/mp4` | 2786351 | AES256 |
| `sample-02.mp4` | `video/mp4` | 4625829 | AES256 |
| `sample-03.mp4` | `video/mp4` | 4844272 | AES256 |

说明：

- 这 3 个对象位于独立 `audit/video-playback` 前缀。
- 没有覆盖业务文件。
- 没有删除源文件。
- 没有上传外部不明素材。

## 5. S3 ACL 情况

新复制的 audit 对象通过源 CloudFront 读取时返回 `403`。

尝试仅对这 3 个 audit 对象补 `public-read` ACL：

- `PutObjectAcl` 返回 `AccessDenied`，当前 AWS 用户没有 `s3:PutObjectAcl` 权限。
- `CopyObject` 携带 `x-amz-acl: public-read` 返回 `AccessControlListNotSupported`，桶禁用 ACL。

处理原则：

- 没有扩大 AWS 权限。
- 没有修改桶策略。
- 没有改业务对象权限。

## 6. Nginx 精确测试回源

为了只验证网页播放链路，不影响业务通用 `/uploads/` 规则，本次只在测试服务器 `test-img` Nginx 中新增 3 个精确 location。

配置文件：

```text
/www/server/panel/vhost/nginx/test-img.hbabaxb.cn.conf
```

备份文件：

```text
/www/server/panel/vhost/nginx/test-img.hbabaxb.cn.conf.bak.audit_video_20260803_195039
```

新增精确路径：

```text
/uploads/audit/video-playback/20260803/sample-01.mp4
/uploads/audit/video-playback/20260803/sample-02.mp4
/uploads/audit/video-playback/20260803/sample-03.mp4
```

规则特点：

- 只命中上述 3 个精确路径。
- 不修改通用 `location ^~ /uploads/`。
- 不切换现有图片回源。
- 仍要求 `token` 非空。
- 仍要求 `t` 非空。
- 仍保留 Referer 白名单逻辑。
- 回源到已有可读源视频所在的 `d391me9s8n5j5s.cloudfront.net`。
- 对响应补 `Content-Type: video/mp4`。

执行结果：

```text
nginx -t 通过
nginx reload 成功
```

## 7. HTTP 验证结果

使用 `Range: bytes=0-1023` 验证，避免下载完整视频。

### 7.1 裸链验证

| 对象 | 状态 | Content-Type | Content-Range |
| --- | --- | --- | --- |
| `sample-01.mp4` | `206` | `image/webp` | `bytes 0-1023/13716` |
| `sample-02.mp4` | `206` | `image/webp` | `bytes 0-1023/13716` |
| `sample-03.mp4` | `206` | `image/webp` | `bytes 0-1023/13716` |

结论：

- 裸链不会返回原视频。
- 裸链返回默认占位图。
- 防直开有效。

### 7.2 带 token/t 验证

| 对象 | 状态 | Content-Type | Content-Range |
| --- | --- | --- | --- |
| `sample-01.mp4` | `206` | `video/mp4` | `bytes 0-1023/2786351` |
| `sample-02.mp4` | `206` | `video/mp4` | `bytes 0-1023/4625829` |
| `sample-03.mp4` | `206` | `video/mp4` | `bytes 0-1023/4844272` |

结论：

- 带 `token/t` 后 3 个样本都能通过 `test-img.hbabaxb.cn` 返回视频内容。
- Range 播放所需的 `206 Partial Content` 正常。
- Content-Type 为 `video/mp4`。

## 8. H5 网页播放验证

测试页面：

```text
https://test-h5.hbabaxb.cn/
```

验证方式：

- 打开当前 H5 测试页面。
- 临时在 DOM 中插入 3 个 `<video>` 元素。
- `src` 使用 `test-img.hbabaxb.cn/uploads/audit/video-playback/...mp4` 带 `token/t` 的地址。
- 设置 `muted`、`playsInline`、`controls`。
- 等待 mevendor_ata。
- 调用 `play()`。
- 观察 Network。

结果：

| 对象 | mevendor_ata | play() | error | readyState | 尺寸 |
| --- | --- | --- | --- | ---: | --- |
| `sample-01.mp4` | 成功 | 成功 | 0 | 3 | 854x481 |
| `sample-02.mp4` | 成功 | 成功 | 0 | 4 | 750x422 |
| `sample-03.mp4` | 成功 | 成功 | 0 | 3 | 640x480 |

Network：

```text
Media 206 video/mp4
```

H5 结论：

- 当前 H5 页面内可渲染加密视频。
- mevendor_ata 可加载。
- 浏览器可发起 Media Range 请求。
- muted play() 成功。

## 9. PC 网页播放验证

测试页面：

```text
https://pc.youdianse-test.xyz/
```

补充说明：

- `https://test-pc.hbabaxb.cn/` 在临时自动化会话中 Runtime 回包不稳定。
- 改用当前 PC 主测试入口 `https://pc.youdianse-test.xyz/` 做同等网页验证。

验证方式：

- 打开当前 PC 测试页面。
- 临时在 DOM 中插入 3 个 `<video>` 元素。
- 使用相同 3 个带 `token/t` 的 `test-img` audit 视频地址。
- 观察 video 状态和 Network。

结果：

| 对象 | readyState | paused | error | currentTime | 尺寸 |
| --- | ---: | --- | ---: | ---: | --- |
| `sample-01.mp4` | 4 | false | 0 | 18.096519 | 854x481 |
| `sample-02.mp4` | 4 | false | 0 | 13.631952 | 750x422 |
| `sample-03.mp4` | 4 | false | 0 | 19.316558 | 640x480 |

Network：

```text
Media 206 video/mp4
```

PC 结论：

- 当前 PC 页面内可渲染加密视频。
- 视频已进入播放状态。
- `paused=false`。
- `error=0`。
- 有播放进度。
- Network 为 `Media 206 video/mp4`。

## 10. 本轮结论

本轮验证通过：

1. `test-img.hbabaxb.cn` 加密视频裸链会被挡住，返回占位图。
2. 带 `token/t` 后可返回 `206 video/mp4`。
3. H5 当前网页中可加载、渲染、播放加密视频。
4. PC 当前网页中可加载、渲染、播放加密视频。
5. 本次变更只作用于 3 个 audit 精确路径，不影响业务图片和通用 uploads 规则。

需要注意：

- 本轮是 audit 精确路径验证，不代表所有业务视频通用链路已修复。
- 当前通用 `test-img` 回源仍是 `d1rct3ku9n07y3.cloudfront.net`，历史业务视频在该源上存在 `404` 的情况。
- 当前 token 规则仍是非空门槛，不是 md5 强验签。

## 11. 后续建议

### 11.1 修通业务视频通用链路

如果要让所有后台 uploads 视频都通过 `test-img` 播放，需要处理 `d1` 与 `d391` 的源差异：

1. 确认业务图片和视频的真实源分布。
2. 决定 `test-img` 通用回源是否继续使用 `d1`。
3. 如果视频仍在 `d391`，需要：
   - 同步视频到 `d1` 对应源；或
   - 为视频路径设计单独回源；或
   - 将 `test-img` 回源策略拆分为图片/视频不同源。

### 11.2 前端正式接入

当前网页验证是临时 DOM 注入。业务页面正式播放需要前端组件实际渲染：

```html
<video controls playsinline src="test-img 带 token/t 的视频地址"></video>
```

前端验收标准：

- DOM 中有 `video/source`。
- Network 中视频请求为 `206` 或 `200`。
- Content-Type 为 `video/mp4`。
- `loadedmevendor_ata` 成功。
- `videoWidth/videoHeight` 正常。
- 播放不报错。

### 11.3 强验签

当前规则不是强验签。若安全目标是“乱填 token 也不能播放”，需要新增：

- Nginx Lua/md5 校验；或
- EdgeOne Token 强校验；或
- 后端签名和 CDN 鉴权统一方案。

强验签上线前必须先确认：

- 后端生成 token 的算法和 Nginx/CDN 校验算法一致。
- token 有效期符合业务使用。
- H5/PC、图片、视频、缓存、Range 请求都能通过。

## 12. 回滚方式

如果需要撤销本次 audit 视频测试 Nginx 规则：

```bash
cp /www/server/panel/vhost/nginx/test-img.hbabaxb.cn.conf.bak.audit_video_20260803_195039 \
   /www/server/panel/vhost/nginx/test-img.hbabaxb.cn.conf
nginx -t
nginx -s reload
```

如果需要清理 S3 audit 对象，删除以下 3 个测试对象：

```text
uploads/audit/video-playback/20260803/sample-01.mp4
uploads/audit/video-playback/20260803/sample-02.mp4
uploads/audit/video-playback/20260803/sample-03.mp4
```

删除 S3 对象前需单独确认，因为删除属于破坏性操作，本轮未执行删除。

## 13. 飞机群通知

本轮已按用户要求，每个关键步骤同步到 3 个飞机群：

- `稳定备案域名+腾讯云原厂`
- `18game运维`
- `18GAME_ 上线群（正式環境）`

通知内容覆盖：

- 开始整理和验证。
- 源桶视频扫描。
- audit 视频复制。
- Nginx 精确回源变更。
- HTTP 验证结果。
- H5/PC 网页播放验证结果。
- 最终结论和影响范围。

## 14. 安全说明

本文不记录：

- AWS Access Key / Secret Key
- Telegram token
- SSH 私钥正文
- 完整带 token 的视频 URL
- `.env` 原文
- 数据库连接串
- Cookie / Session

本文记录的路径、域名、状态码和对象大小用于运维复盘和后续回滚。
