---
id: "doc-de60ba87d7c1"
title: "2026-09-30 EdgeOne 全托管给 AI 的能力边界与落地方案"
date: "2026-09-30T12:25:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Shell", "Docker", "自动化", "CDN", "DNS", "安全运维", "数据库恢复"]
source: "project-file:///Projects/work/game/pgserver/cn/docker/doc/2026-09-30-1225-%E3%80%90%E8%BF%90%E7%BB%B4%E8%AE%B0%E5%BD%95%E3%80%91EdgeOne%E5%85%A8%E6%89%98%E7%AE%A1%E7%BB%99AI%E7%9A%84%E8%83%BD%E5%8A%9B%E8%BE%B9%E7%95%8C%E4%B8%8E%E8%90%BD%E5%9C%B0%E6%96%B9%E6%A1%88.md"
sourcePath: "~/Projects/work/game/pgserver/cn/docker/doc/2026-09-30-1225-【运维记录】EdgeOne全托管给AI的能力边界与落地方案.md"
sourceSha256: "868cf06b3f1c4faadd068bcf20049ab059288b94a309cfb7214abbb503dfe8b5"
sourceSystem: "project-doc"
---

# 2026-09-30 EdgeOne 全托管给 AI 的能力边界与落地方案

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609301225-%E9%A6%99%E6%B8%AF%20CN%2BShell%2BDocker-2026-09-30%20EdgeOne%20%E5%85%A8%E6%89%98%E7%AE%A1%E7%BB%99%20AI%20%E7%9A%84%E8%83%BD%E5%8A%9B%E8%BE%B9%E7%95%8C%E4%B8%8E%E8%90%BD%E5%9C%B0%E6%96%B9%E6%A1%88.md)

> 整理日期：2026-09-30 12:25｜日期依据：文件名日期

## 一、结论

```text
EdgeOne（TEO）的配置项基本 100% 有 API，可以全托管给 AI 执行。
本轮已经用 API 完成的事情（除建密钥/改 NS 外全是 API）：建加速域名、配源站、
建规则引擎规则、**启用 EdgeOne 自动创建但默认禁用的 CNAME**（ModifyDnsRecordsStatus）、
复核 CNAME 状态。所以「CNAME 默认禁用」不是要人工点，而是要在配置里声明「必须启用」。
```

## 二、能力边界

````text
AI 用 API 全权负责（已实测可行）              需要人工/外部的一次性动作
├ 建站点         CreateZone                 ├ 域名 NS 指向 EdgeOne
├ 加速域名       Create/Modify/DeleteAccel  │   （注册商处改；注册商有 API 才能自动化）
├ 源站+回源协议  OriginInfo / 规则引擎        ├ 首次充值、开通套餐（钱的事）
├ 规则引擎       CreateL7AccRules            └ 创建第一把 API 密钥（鸡生蛋）
│   （缓存 / Host 头 / WebSocket / CORS / 302 / 重定向）
├ DNS 记录       Create/Modify/Enable/Delete
│   （含「启用自动建的 CNAME」）
├ 证书           免费证书申请 + 绑定
├ 缓存           PurgeCaches / PreloadCaches
├ 站点设置       ModifyZoneSetting（IPv6 / 压缩 / 默认缓存策略）
├ 站点开关       ModifyZoneStatus
└ 套餐           DescribePlans / BindZoneToPlan / RenewPlan

AI 侧管不到的两件事（明确记录，避免误解）：
  1. 域名 NS 切换：必须在注册商侧完成。若域名在腾讯云注册可用其 API；在 Cloudflare/
     GoDaddy 等则要人工或用那家的 API。
  2. 第一把密钥：必须人工在 CAM 创建（之后轮换也可以由 AI 走 CAM API，但需要 cam 权限，
     当前子用户只有 TEO 权限，所以轮换动作由人工做最省事）。
````

## 三、要真正全托管，需要补的三件工程活

```text
a) 幂等配置脚本 edgeone_apply.py（建议下一步就做）
   - 输入：一个 JSON（站点、加速域名、源站、规则、DNS 记录与启用状态）
   - 行为：先 Describe 现状，再按需 Create/Modify/ModifyDnsRecordsStatus，重复执行不产生
     重复资源（幂等），支持 --dry-run 只打印差异
   - 效果：改配置 = 改文件 + 跑脚本，控制台不再需要人工点
b) 配置备份 edgeone_backup.py
   - 导出到 docker/deploy/hongkong/cdn-backup/edgeone/<zone>.json
     （站点属性、加速域名、规则、DNS 记录、设置），纳入 git，与 CF 的 cdn-backup 对齐
c) 权限与安全收口
   - 子用户策略 QcloudTEOFullAccess（或自定义 teo:*），来源 IP 限制 34.150.1.185
   - 开云审计 CloudAudit：每次 AI 改动可追溯
   - 密钥 90 天轮换；凭据文件固定 /root/.config/tencentcloud/edgeone.credentials（600）
```

## 四、另一条路：Terraform

```text
provider tencentcloud，EdgeOne 资源前缀 tencentcloud_teo_*（zone / zone_setting /
l7_acc_rule / acceleration_domain / dns_record …）。
优点：配置即代码、plan 能预览 diff、状态文件可回溯。
代价：现有配置要先 import，CI 里要管 state，上手成本高于 a)+b)。
建议：先用 a)+b) 快速全托管，等 06 的 *-eo 方案定型后再评估迁移 Terraform。
```

## 五、与本项目现状的衔接

```text
· 工具已就位：docker/deploy/hongkong/tencent_teo_api.py（纯标准库 TC3 签名，任意 TEO 接口）
· 测试站点：m4q7z1.shop（zone-3vm5evyb78ic）仍在 provisioning（Status=pending），
  等 active 后才能端到端验证；验证通过再决定 06 的 13 静态 + 9 动态子域灰度。
· 安全待办：本轮密钥曾进入对话记录，需在 CAM 删除后重建并写回同一路径。
```

## 六、关联

```text
docker/deploy/hongkong/tencent_teo_api.py
docker/doc/2026-09-30-1205-【架构改造】EdgeOne测试站点m4q7z1shop建站与规则引擎API实践.md
docker/doc/2026-09-30-1147-【运维记录】腾讯云API密钥（子用户）创建与AI调用规范.md
docker/doc/2026-09-30-1145-【架构改造】香港项目接入腾讯云EdgeOne架构方案（动态+S3静态）.md
```
