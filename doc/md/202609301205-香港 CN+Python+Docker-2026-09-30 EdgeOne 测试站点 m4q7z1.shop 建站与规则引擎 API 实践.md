---
id: "doc-faa00f87ff8c"
title: "2026-09-30 EdgeOne 测试站点 m4q7z1.shop 建站与规则引擎 API 实践"
date: "2026-09-30T12:05:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Python", "Docker", "CDN", "DNS", "安全运维", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/cn/docker/doc/2026-09-30-1205-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91EdgeOne%E6%B5%8B%E8%AF%95%E7%AB%99%E7%82%B9m4q7z1shop%E5%BB%BA%E7%AB%99%E4%B8%8E%E8%A7%84%E5%88%99%E5%BC%95%E6%93%8EAPI%E5%AE%9E%E8%B7%B5.md"
sourcePath: "~/Projects/work/game/pgserver/cn/docker/doc/2026-09-30-1205-【架构改造】EdgeOne测试站点m4q7z1shop建站与规则引擎API实践.md"
sourceSha256: "38bb46a952b2bad65ec4aa4edeccc94f365a10efc346a3e04d809827a38fbe0e"
sourceSystem: "project-doc"
---

# 2026-09-30 EdgeOne 测试站点 m4q7z1.shop 建站与规则引擎 API 实践

> 来源文件：`~/Projects/work/game/pgserver/cn/docker/doc/2026-09-30-1205-【架构改造】EdgeOne测试站点m4q7z1shop建站与规则引擎API实践.md`

> 整理日期：2026-09-30 12:05｜日期依据：文件名日期

## 一、本轮做了什么

```text
目标：用腾讯云 EdgeOne（国际版）建一个测试站点，验证「动态回源香港 standby + 静态回源 AWS S3 大阪」
      两条链路，作为多 CDN 渠道 A 的 Phase 0。

已完成（全部通过 API 执行，操作机器 = 香港 standby 34.150.1.185）：
  1. 只读确认凭据可用：DescribeZones -> 1 个站点
  2. 新建 2 个加速域名：dyn.m4q7z1.shop（动态）、static.m4q7z1.shop（静态）
  3. 新建 2 条规则引擎规则：动态改回源 Host + 不缓存；静态 7 天边缘缓存
  4. 启用 EdgeOne 自动创建的两条 CNAME 记录（默认是禁用状态）
  5. CheckCnameStatus 复核：两条加速域名 CNAME 状态 = active

未完成/进行中：站点本身仍处于 provisioning（Status=pending、ActiveStatus=inactive），
  调用其他接口会返回 OperationDenied.ZoneIsChanging「站点正在变更中」——
  需要等 EdgeOne 侧完成接入（NS 已经是 ns1/ns2.teodns.com）。
```

## 二、凭据与工具

```text
凭据：/root/.config/tencentcloud/edgeone.credentials（600，root）
      子用户 ai-edgeone-operator ｜ 策略 QcloudTEOFullAccess ｜ 站点 m4q7z1.shop
工具：docker/deploy/hongkong/tencent_teo_api.py（新，只依赖标准库）
      自实现 TC3-HMAC-SHA256 签名，无需 pip/SDK；凭据文件权限非 600 直接拒绝运行；
      接口名 --action，参数 --payload，默认端点 teo.intl.tencentcloudapi.com（国际站，可用 --endpoint 换国内站）。

⚠️ 安全事件：本轮首次读取凭据文件时脱敏正则写漏（文件是控制台下载的 CSV 格式，
     形如 `#SecretId IKID...`，没有等号），导致 SecretId/SecretKey 被打印到对话记录里。
     处置：**本周内到控制台把这把密钥删除后重建**（控制台 -> 访问管理 -> 用户 ->
     ai-edgeone-operator -> API 密钥），密钥只该在机器上存在。
```

## 三、站点与配置

```text
站点：m4q7z1.shop     ZoneId = zone-3vm5evyb78ic
  接入模式 Type=full（NS 接入）｜ Area=overseas（全球不含中国大陆）｜ PlanType=plan-basic
  NS = ns1.teodns.com / ns2.teodns.com（registrar 侧已切换）

加速域名：
  dyn.m4q7z1.shop     CNAME dyn.m4q7z1.shop.eo.dnse3.com
      源站 34.150.1.185（IP_DOMAIN）｜ OriginProtocol=HTTP ｜ HttpOriginPort=80
  static.m4q7z1.shop  CNAME static.m4q7z1.shop.eo.dnse3.com
      源站 dbqp-s3-pg-static.s3.ap-northeast-3.amazonaws.com（IP_DOMAIN，先用域名型）｜ HTTPS 443

规则引擎（CreateL7AccRules，RuleIds rule-3vm6y99k8liv / rule-3vm6y99ka03b）：
  dyn-hostheader-nocache：
      Condition = ${http.request.host} in ['dyn.m4q7z1.shop']
      Actions   = HostHeader{custom, ServerName=pg-games.hkcloudplay06.com} + Cache{NoCache on}
  static-cache-7d：
      Condition = ${http.request.host} in ['static.m4q7z1.shop']
      Actions   = Cache{CustomTime on, CacheTime=604800, IgnoreCacheControl=on}

DNS（站点内记录）：
  *.m4q7z1.shop   A      34.150.1.185                          enable   ← 手动加的直连测试记录
  dyn.m4q7z1.shop CNAME  dyn.m4q7z1.shop.eo.dnse3.com          enable   ← 原为 disable，本轮启用
  static.m4q7z1.shop CNAME static.m4q7z1.shop.eo.dnse3.com     enable   ← 原为 disable，本轮启用
```

## 四、API 踩坑（都是实测结论，下次直接抄）

```text
1. Condition 是**表达式字符串**，不是 JSON：
     对：${http.request.host} in ['dyn.m4q7z1.shop']
     错：{"Conditions":[{"Target":"host",...}]}  -> ConfigConditionSyntaxError
     错：host == "x"                            -> ConfigConditionUnknownTarget
     错：$host == "x"                           -> ConfigConditionSyntaxError
   来源：Terraform provider 示例（tencentcloud_teo_l7_acc_rule，
   condition = "$${http.request.host} in ['aaa.makn.cn']"，Terraform 里 $${} 转义成 ${}）。
   其它可用占位符：${http.request.file_extension}、${http.request.url_path} 等，支持 lower() 与 in []。
2. HostHeader 动作的 Action 枚举要**小写** `custom` / `followOrigin`
   （文档写 Custom，API 校验只认小写）。
3. 加速域名创建后，EdgeOne 会在站点 DNS 里**自动建一条同名 CNAME，但状态是 disable**，
   必须显式启用（ModifyDnsRecordsStatus），否则 DNS 一直返回手动加的 A 记录（绕过 CDN）。
4. 站点接入期间（Status=pending）调用其它接口会报
   OperationDenied.ZoneIsChanging「站点正在变更中，禁止该操作」——不是权限问题，等它跑完。
5. 站点 Area=overseas 就是「全球（不含中国大陆）」；AccelerateMainland 默认 off（未备案不能用）。
6. 测速/排障用 CheckCnameStatus 复核 CNAME 是否被 EdgeOne 认可（返回 active 才算配好）。
```

## 五、验证与现状

```text
密钥可用性：DescribeZones 返回 200（TotalCount=1）
CNAME 校验：CheckCnameStatus -> dyn / static 均 Status=active
DNS 现状（权威 NS ns1.teodns.com 直查）：dyn/static 仍返回 34.150.1.185
  —— 因为站点仍在 provisioning，CNAME 尚未生效；等站点 Status 变为 active 后再复核。
待生效后要做的验证：
  · dig dyn.m4q7z1.shop 应返回 EdgeOne 节点 IP（不再是 34.150.1.185）
  · curl https://dyn.m4q7z1.shop/health 期望 200（回源 Host 已改写为 pg-games.hkcloudplay06.com）
  · curl https://static.m4q7z1.shop/<真实对象> 期望 200，二次请求命中边缘缓存
```

## 六、待办

```text
[ ] 等站点 active，复核两条链路（命令见第五节）
[ ] 控制台删除并重建 ai-edgeone-operator 的 API 密钥（本轮密钥曾暴露在对话记录）
[ ] 测通后再决定：06 的 13 个静态前缀 + 9 个动态子域是否按 *-eo 方案灰度
[ ] 若要静态直连 S3 桶而非域名型源站，可评估 OriginType=AWS_S3
```

## 七、关联

```text
docker/deploy/hongkong/tencent_teo_api.py（本轮新增的调用工具）
docker/doc/2026-09-30-1145-【架构改造】香港项目接入腾讯云EdgeOne架构方案（动态+S3静态）.md
docker/doc/2026-09-30-1129-【架构改造】EdgeOne接入香港standby入口回源填写指南.md
docker/doc/2026-09-30-1147-【运维记录】腾讯云API密钥（子用户）创建与AI调用规范.md
```
