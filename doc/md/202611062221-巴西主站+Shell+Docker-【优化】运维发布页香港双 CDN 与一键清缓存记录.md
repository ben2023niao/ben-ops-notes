---
id: "doc-92dd7e120e64"
title: "【优化】运维发布页香港双 CDN 与一键清缓存记录"
date: "2026-11-06T22:21:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "Docker", "Nginx", "自动化", "CDN", "DNS", "安全运维"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-11-06-2221-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E8%BF%90%E7%BB%B4%E5%8F%91%E5%B8%83%E9%A1%B5%E9%A6%99%E6%B8%AF%E5%8F%8CCDN%E4%B8%8E%E4%B8%80%E9%94%AE%E6%B8%85%E7%BC%93%E5%AD%98%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-11-06-2221-【优化】运维发布页香港双CDN与一键清缓存记录.md"
sourceSha256: "a2a44bdd5dfcfb886de96965a1ed168e680623f760725b267d916df796b49dd6"
sourceSystem: "project-doc"
---

# 【优化】运维发布页香港双 CDN 与一键清缓存记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202611062221-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BShell%2BDocker-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E8%BF%90%E7%BB%B4%E5%8F%91%E5%B8%83%E9%A1%B5%E9%A6%99%E6%B8%AF%E5%8F%8C%20CDN%20%E4%B8%8E%E4%B8%80%E9%94%AE%E6%B8%85%E7%BC%93%E5%AD%98%E8%AE%B0%E5%BD%95.md)

> 整理日期：2026-11-06 22:21｜日期依据：文件名日期

更新时间：2026-11-06 22:21（Asia/Manila）

执行范围：`deliverables/bizops-ops-console`、巴西宝塔 `bizops-ops-console`、香港腾讯 EdgeOne、香港 Cloudflare。

## 一、请求

```text
1. 更新 bizops-ops-console 的“运维发布页.html”；
2. 详细补充香港同时使用 Cloudflare 与腾讯云 EdgeOne 的架构；
3. 研究并实现腾讯 CDN 的网页按钮清缓存；
4. 汇总文档发群；
5. 提交本地 Git，提交结果发群。
```

## 二、开始前 Git 基线

主仓库：

```text
目录：/Users/operator/Projects/ops/private-notes/master
本地 master：5a431790
origin/master：a72f41fb
origin/ben：9f59b4f3
工作区：干净
本地 master 领先 origin/master 19 个提交
```

独立香港仓库：

```text
目录：/Users/operator/Projects/ops/private-notes/cn
本地 cn：1fbe688f
origin/cn：5c3b3de6
工作区：干净
本地 cn 领先 origin/cn 142 个提交
```

## 三、香港 CDN 现状

此前页面把香港缓存清理主要描述成 Cloudflare，信息不完整。实际是两层：

### 3.1 腾讯 EdgeOne

```text
m4q7z1.shop  zone-3vm5evyb78ic  22 个加速域名
k8x2v9.shop  zone-3vm7ccg417yf  22 个加速域名
源站：192.0.2.37:80 HTTP
```

负责：

```text
动态 8 个：
pg-games / api / vendor_b-games / pp-games /
ppk-games / vendor_d-games / vendor_c-games / g759-games

静态 14 个：
pg-static / pg3-static / pg4-static / pg5-static / pg6-static / pg7-static /
pp-static / ppk-static / vendor_d-static / vendor_c-static / g759-static /
vendor_b-static / vendor_b-static1 / vendor_b-static2
```

### 3.2 Cloudflare

```text
hkcloudplay06.com  fd8476ddbd25b40f4c870d8066329aca
hkcloudplay07.com  ad235f3123a5c6259f5b2e699bdd7b93
```

06/07 继续由 Cloudflare Worker `bizops-hk-static-proxy` 提供静态资源。
Worker 自定义缓存键无法按单个 URL 或厂家精准失效，只能整 zone
`purge_everything`。

## 四、页面更新

文件：

```text
deliverables/bizops-ops-console/web/运维发布页.html
```

主要变化：

```text
1. 顶部增加“香港 EdgeOne + Cloudflare”状态标签；
2. 香港 CDN 卡片改为双 CDN 架构说明；
3. 分别展示 EdgeOne 与 Cloudflare 的域名、用途和控制台入口；
4. 增加“预检清理范围”和“一键清理香港 CDN”按钮；
5. 清理过程在当前卡片内实时输出；
6. 自动显示 EdgeOne JobId、Cloudflare zone ID、失败列表和退出码；
7. 清理成功后自动勾选“香港 CDN 静态资源缓存已清理”；
8. 保留 56 个主机名的手动兜底清单；
9. 明确 Cloudflare 整 zone 清理会影响 06/07 上全部静态资源；
10. 页面版本升级为 2026-11-06-r10。
```

## 五、服务端实现

新增：

```text
deliverables/bizops-ops-console/app/cdn.py
deliverables/bizops-ops-console/tests/test_cdn.py
```

接口：

```text
POST /api/cdn/purge
{
  "providers": ["edgeone", "cloudflare"],
  "vendors": ["pg", "vendor_a", "vendor_b", "pp"],
  "dry_run": false
}
```

安全边界：

```text
1. 浏览器不能提交 host、zone、URL 或 API endpoint；
2. provider 只允许 edgeone / cloudflare；
3. vendor 映射和静态前缀固定在服务端；
4. EdgeOne 站点 ID 固定在服务端；
5. Cloudflare 只允许 hkcloudplay06.com / hkcloudplay07.com；
6. API 凭据只从容器 /run/secrets 读取；
7. 任务复用 jobs / job_events 和 SSE 实时流；
8. 全过程写入审计，密钥不会进入日志；
9. dry-run 只调用 DescribeZones 和 Cloudflare Zone:Read，不清缓存。
```

EdgeOne 清理方法：

```text
Action：CreatePurgeTask
Type：purge_host
Method：invalidate
Targets：按所选厂家的静态主机名生成，最多 20 个一批
```

Cloudflare 清理方法：

```text
POST /zones/{zone_id}/purge_cache
{"purge_everything": true}
```

## 六、Secret 配置

线上 `bizops-ops-console` 新增三份只读 Secret：

```text
/run/secrets/tencentcloud_secret_id
/run/secrets/tencentcloud_secret_key
/run/secrets/cloudflare_api_token
```

权限：

```text
owner：10001:10001
mode：0400
```

腾讯云凭据来自本机 macOS Keychain；Cloudflare Token 从巴西宝塔原有
`/root/bizops-cf-workers.env` 读取。所有密钥值均未输出到终端、文档或 Git。

## 七、验证

### 7.1 单元测试

```text
Ran 7 tests
OK
```

覆盖：

```text
厂家到静态前缀映射；
vendor_a / vendor_b 共享前缀去重；
非法 provider / vendor 拒绝；
EdgeOne purge_host payload；
Cloudflare purge_everything payload；
腾讯云两站点只读预检；
Cloudflare 两 zone 只读预检。
```

### 7.2 本地登录态 API

```text
Job：e683f9d1fbc340fc
预检厂家：pp
EdgeOne 目标：2
EdgeOne 两站点 visible=true
退出码：0
未调用清缓存写接口
```

### 7.3 线上部署

备份：

```text
/opt/bizops-ops-console/backups/code-before-20261106-221854.tar.gz
```

镜像：

```text
bizops-ops-console:20261106-r10
image id：sha256:bbc190f41b8a3d6f74add1a4e8df08596afafa2a2f10c5b4e5f2211674601e98
```

容器：

```text
status：running
health：healthy
version：2026-11-06-r10
入口：http://192.0.2.8:8787
```

### 7.4 线上双 CDN 只读预检

```text
Job：fb5f580dfb5e4351
EdgeOne targets：28
Cloudflare zones：2
EdgeOne m4q7z1.shop：visible
EdgeOne k8x2v9.shop：visible
Cloudflare hkcloudplay06.com：visible
Cloudflare hkcloudplay07.com：visible
退出码：0
实际清缓存：未执行
```

说明：本轮只验证按钮后端链路和凭据权限，没有对线上 CDN 执行实际
purge，避免在没有发布变更时制造冷缓存。

## 八、影响范围

```text
1. 只更新 bizops-ops-console 运维控制台；
2. 未重启任何游戏业务容器；
3. 未修改香港 01/02；
4. 未修改 Nginx、DNS、Worker、EdgeOne 规则或缓存内容；
5. 未修改巴西与香港版本文件；
6. 控制台新增 Secret 只被 CDN 清理接口按需读取。
```

## 九、回滚

```bash
cd /opt/bizops-ops-console
tar -xzf backups/code-before-20261106-221854.tar.gz -C .
docker compose -f deploy/docker-compose.yml up -d --force-recreate
```

缓存清理本身不需要回滚；即使误清，只会让后续首次请求回源并重建缓存，
不会删除业务数据。

## 十、群通知

```text
开始：message_id 890
功能完成：message_id 891
汇总：message_id 892
文档：message_id 893
提交结果：发送后补录
```
