---
id: "doc-59839aaa334b"
title: "2026-10-02 EdgeOne 三个站点规则中文标注 + 站点标签方案"
date: "2026-10-02T16:10:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Python", "Docker", "Nginx", "CDN", "DNS", "安全运维", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/cn/docker/doc/2026-10-02-1610-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91EdgeOne%E4%B8%89%E7%AB%99%E7%82%B9%E8%A7%84%E5%88%99%E4%B8%AD%E6%96%87%E6%A0%87%E6%B3%A8%E4%B8%8E%E7%AB%99%E7%82%B9%E6%A0%87%E7%AD%BE%E6%96%B9%E6%A1%88.md"
sourcePath: "~/Projects/ops/private-notes/cn/docker/doc/2026-10-02-1610-【运维记录】EdgeOne三站点规则中文标注与站点标签方案.md"
sourceSha256: "302e8cc4ac584740dee2d0c9cfa50fa420c0228400ea788595f846871597f5c0"
sourceSystem: "project-doc"
---

# 2026-10-02 EdgeOne 三个站点规则中文标注 + 站点标签方案

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/cn/docker/doc/2026-10-02-1610-【运维记录】EdgeOne三站点规则中文标注与站点标签方案.md`

> 整理日期：2026-10-02 16:10｜日期依据：文件名日期

## 一、需求

```text
用户：在腾讯云上给香港项目这几个域名写详细中文注释，例如「游戏 XX 厂家静态域名」「游戏动态接口域名」
      「商户域名」等，方便控制台里一眼看清用途。
涉及站点：m4q7z1.shop、k8x2v9.shop（游戏域名）、p3w9n5.shop（商户域名，含 socket.p3w9n5.shop）
本轮按要求不发送飞机群通知。
```

## 二、EdgeOne 的注释能力边界（实测）

```text
· 加速域名（AccelerationDomain）：Create/ModifyAccelerationDomain 都没有备注/描述字段
  -> 控制台的加速域名列表里无法通过 API 写自定义备注（只能在控制台看域名本身）
· DNS 记录（DnsRecord）：Create/ModifyDnsRecords 也没有备注字段 -> 同样写不了注释
· 规则引擎（RuleEngineItem）：支持 RuleName（≤255 字）+ Description（多行注释）✅ → 中文标注落在规则上
· 站点标签（Tags）：站点对象带 Tags 字段，走腾讯云全局标签服务（tag:TagResources）；
  但当前子用户 ai-edgeone-operator 只有 QcloudTEOFullAccess，调 tag 接口返回
  AuthFailure.UnauthorizedOperation（tag:DescribeResourceTagsByResourceIds 无权限）
· 站点同名标识 AliasZoneName：只允许数字 / 英文字母 / . - _，不能写中文
```

## 三、已实施：三个站点共 53 条规则改成中文名称 + 备注

```text
工具：docker/deploy/hongkong/edgeone_label.py（可 --dry-run 预演，幂等）
  python3 edgeone_label.py --domain m4q7z1.shop --zone zone-3vm5evyb78ic
  python3 edgeone_label.py --domain k8x2v9.shop --zone zone-3vm7ccg417yf
  python3 edgeone_label.py --domain p3w9n5.shop --zone zone-3vm7chzbxkcb --profile merchant

改后控制台里看到的规则名（每个游戏站点 25 条）：
  游戏静态域名·节点缓存7天（14个静态前缀）      备注写明 14 个前缀、缓存 7 天、回源香港 nginx → 大阪桶
  游戏动态接口·不缓存（8个动态子域）            备注写明 8 个动态域名、回源香港后端容器
  vendor_b游戏WebSocket·长连接（vendor_b-games）       备注写明 /lifeservice/ws2 与 /ws2、超时 120 秒
  回源Host·PG主站静态资源（pg-static）          备注写明「pg-static.<域>：静态资源域名，回源 Host 固定为该域名」
  回源Host·PG游戏接口（pg-games）              同上，动态接口
  …（PG3~PG7 / PP / PPK / vendor_d / Playson / G759 / vendor_b 静态与动态共 22 条，命名规律一致）

商户站点 p3w9n5.shop（3 条）：
  商户域名·不缓存（根域 + socket）              备注写明 p3w9n5.shop 与 socket.p3w9n5.shop、回源 platform-api 9090、
                                             口径与 CF 渠道 hk-socket.com 一致
  回源Host·商户根域（p3w9n5.shop）
  回源Host·商户socket域名（socket.p3w9n5.shop）

回归验证（改中文标注后链路无变化）：
  http://pg-games.m4q7z1.shop/health         -> 200
  http://pg-static.m4q7z1.shop/health.json   -> 200
  http://vendor_b-games.m4q7z1.shop/health       -> 200
  http://pg-games.k8x2v9.shop/health         -> 200（--resolve 到 EdgeOne 节点）
  http://socket.p3w9n5.shop/healthz          -> 200（--resolve 到 EdgeOne 节点）
```

## 四、待实施：站点级中文标签（需要授权或人工点一次）

```text
方案 A（推荐，给我权限我立刻做）：在 CAM 给子用户 ai-edgeone-operator 加一条 QcloudTagFullAccess
  （标签服务全读写），我就能用 tag:TagResources 把下面这些标签写上去。
方案 B：你在腾讯云控制台 -> 标签 控制台 / 站点列表里手动加同样的标签。

建议标签（键 -> 值）：
  m4q7z1.shop / k8x2v9.shop
    项目      -> 香港项目
    环境      -> 生产
    用途      -> 游戏域名（腾讯云 EdgeOne CDN）
    说明      -> 游戏静态资源 + 动态接口二级域名（14 静态 + 8 动态，与 hkcloudplay06/07 同名）
    渠道      -> 腾讯云 EdgeOne（备用渠道 Cloudflare / CloudFront）
  p3w9n5.shop
    项目      -> 香港项目
    环境      -> 生产
    用途      -> 商户域名（登录 / socket）
    说明      -> 根域 p3w9n5.shop + socket.p3w9n5.shop，回源香港 nginx -> platform-api 9090，
                 口径与 CF 渠道 hk-socket.com 一致
    渠道      -> 腾讯云 EdgeOne
```

## 五、关联

```text
docker/deploy/hongkong/edgeone_label.py（本轮新增：规则中文名称/备注）
docker/deploy/hongkong/edgeone_apply.py（站点加速域名与规则创建，含 merchant 模式）
docker/deploy/hongkong/cdn-backup/edgeone/（三站点配置快照）
docker/doc/2026-10-02-1500-【架构改造】p3w9n5商户域名接入与香港0102三域名生效.md
```
