---
id: "doc-61a864fc113c"
title: "某业务公司 全服务器 CVE 与安全基线巡检记录"
date: "2026-11-08T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "Python", "Go", "安全运维", "故障排查", "CVE-2018-1111"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-11-08-%E5%AE%89%E5%85%A8%E5%B7%A1%E6%A3%80_某业务公司%E5%85%A8%E6%9C%8D%E5%8A%A1%E5%99%A8CVE%E4%B8%8E%E4%BF%AE%E5%A4%8D%E6%AD%A5%E9%AA%A4.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-11-08-安全巡检_某业务公司全服务器CVE与修复步骤.md"
sourceSha256: "e0dc1406bfd48f3ef2aeefb40695f25bf9a869144223ed51f2baee6a7e4d5028"
sourceSystem: "project-doc"
---

# 某业务公司 全服务器 CVE 与安全基线巡检记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/master/docs/history/2026-11-08-安全巡检_某业务公司全服务器CVE与修复步骤.md`

> 整理日期：2026-11-08 00:00｜日期依据：文件名日期

巡检时间：2026-11-08 23:36（Asia/Manila）

## 一、结论

本次合并新、旧 JumpServer 资产表后共识别 175 台主机，其中 131 台完成只读采集，44 台因账号、网络、旧堡垒机凭据不可用或终端输出异常未完成。未完成主机不能判定为安全，完整名单和原因已写入 HTML 报告。

系统软件包通过实际安装版本与 OSV Red Hat/Ubuntu 数据匹配，共命中 1,197 个唯一 CVE：

| 等级 | 数量 |
|---|---:|
| Critical | 3 |
| Important / High | 573 |
| Moderate / Medium | 561 |
| Low | 50 |
| Unknown | 10 |

项目依赖从 44 个去重后的 Composer、npm、PyPI、Go 清单中解析 3,499 个依赖版本，共命中 686 个唯一 CVE：

| 等级 | 数量 |
|---|---:|
| Critical | 75 |
| High | 304 |
| Moderate | 224 |
| Medium | 2 |
| Low | 47 |
| Unknown | 34 |

## 二、最高优先级 CVE

### 系统软件包

- `CVE-2018-1111`：DHCP client 命令注入，命中 98 台；修复包版本至少 `12:4.2.5-68.el7_5.1`。
- `CVE-2021-43527`：NSS 堆溢出，命中 111 台；修复包版本至少 `0:3.67.0-4.el7_9`。
- `CVE-2021-44142`：Samba 越界访问，命中 1 台；修复包版本至少 `0:4.10.16-18.el7_9`。

### 项目依赖

- `CVE-2019-18889`：Symfony Cache 不安全反序列化，命中 16 台。
- `CVE-2019-9081`：Laravel Framework 反序列化，命中 12 台。
- `CVE-2020-13909`、`CVE-2021-3129`：Laravel Ignition 未授权 RCE，各命中 12 台。
- `CVE-2018-16385`、`CVE-2018-18530`：ThinkPHP SQL 注入，各命中 2 台。
- `CVE-2020-28502`、`CVE-2021-31597`：xmlhttprequest-ssl 任意代码执行/证书校验问题，分别命中 8 台。

完整 CVE、受影响主机、修复版本、手工修复命令和复核命令见 HTML 报告。

## 三、手工修复顺序

1. 先隔离公网 SSH、管理端口和数据库端口，只保留确认过的源 IP。
2. 升级 Critical 系统和依赖 CVE；内核、glibc、OpenSSL、systemd、OpenSSH 更新后重启主机。
3. CentOS 7 已停止常规安全维护，不能仅靠补丁长期维持；列入受支持系统迁移计划。
4. Composer、npm、PyPI、Go 依赖按报告指定修复版本升级，并重新生成 lockfile。
5. 升级后执行包版本核对、安全更新检查、服务健康检查、端口连通性和业务回归。

## 四、未完成项

- 44 台主机本次不能完成采集，报告中已列出资产名、IP、失败状态和原因。
- 项目依赖扫描覆盖可直接解析的锁文件和固定版本；私有包、Maven/Gradle 复杂工程和容器内代码仍需补扫。
- OSV 命中包含仍在受影响版本的历史 CVE；是否被厂商回补仍需结合对应系统安全公告和实际包版本确认。

## 五、验证命令

```bash
# CentOS / RHEL
rpm -q <package>
yum updateinfo list security installed
systemctl --failed
needs-restarting -r

# Ubuntu / Debian
dpkg-query -W <package>
apt list --upgradable 2>/dev/null | grep security || true
systemctl --failed
needrestart -r l

# Composer
composer audit --locked
composer check-platform-reqs

# npm
npm audit --omit=dev

# Python
pip-audit

# Go
govulncheck ./...
```

本记录和 HTML 不包含服务器密码、SSH 私钥、Telegram Token 或云 API 密钥。
