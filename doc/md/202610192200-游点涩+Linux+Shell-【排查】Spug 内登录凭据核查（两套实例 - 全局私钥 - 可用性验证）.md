---
id: "doc-0a99b5882613"
title: "【排查】Spug 内登录凭据核查（两套实例 / 全局私钥 / 可用性验证）"
date: "2026-10-19T22:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Linux", "Shell", "Python", "Docker", "MySQL", "监控告警", "CDN"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-19-2200-%E3%80%90%E6%8E%92%E6%9F%A5%E3%80%91Spug%20%E5%86%85%E5%87%AD%E6%8D%AE%E6%A0%B8%E6%9F%A5%EF%BC%88%E4%B8%A4%E5%A5%97%E5%AE%9E%E4%BE%8B%E3%80%81%E5%85%A8%E5%B1%80%E7%A7%81%E9%92%A5%E3%80%81%E5%8F%AF%E7%94%A8%E6%80%A7%E9%AA%8C%E8%AF%81%EF%BC%89.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-19-2200-【排查】Spug 内凭据核查（两套实例、全局私钥、可用性验证）.md"
sourceSha256: "501fbb6c423b239dce0f70c9c112b6914112890997db349b2a28ea4282a63e47"
sourceSystem: "project-doc"
---

# 【排查】Spug 内登录凭据核查（两套实例 / 全局私钥 / 可用性验证）

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-19-2200-【排查】Spug 内凭据核查（两套实例、全局私钥、可用性验证）.md`

> 整理日期：2026-10-19 22:00｜日期依据：文件名日期

- 时间：2026-10-19 21:40 ~ 22:00（北京时间）
- 目的：从 Spug 中找登录凭据，尝试把此前进不去的服务器接入监控/清理
- 结论：**找到两套 Spug、主机清单齐全，但其中保存的全局私钥已被目标机拒绝（凭据失效），无法借此获得新访问权限**

## 一、两套 Spug 实例

| 实例 | 主机 | 容器 | 主机记录数 |
| --- | --- | --- | ---: |
| 新 Spug | 16.208.32.40 | `spug`（openspug/spug-service）+ `spug-db`（mariadb:10.8.2） | 17 |
| 旧 Spug | 103.207.68.124 | 同上 | 6 |

数据库均为 `spug`，主机表为 `hosts`（字段：`name/hostname/port/username/pkey/desc`）。

### 主机清单（去掉名称中因字符集显示为 ? 的部分）

新 Spug（17 条）：

```
16.209.16.108 ubuntu | 13.208.101.121 ubuntu | 56.155.42.18 ec2-user | 15.168.164.29 ec2-user
13.208.245.64 ec2-user | 16.208.5.147 ubuntu | 16.208.32.40 ubuntu | 103.207.68.124 root
38.92.8.151 root | 38.92.8.34 root | 13.208.245.64 ec2-user | 138.252.248.139:38927 root
16.208.38.88 ubuntu | 15.152.247.196 ec2-user | 15.152.6.51 ec2-user | 191.40.41.155 root
45.135.237.47:13575 root | 173.231.49.86 root
```

旧 Spug（6 条）：

```
38.92.8.151 root | 38.92.8.34 root | 103.207.68.124 root
162.211.181.13 root | 15.152.247.196 ec2-user | 15.152.6.51 ec2-user
```

## 二、凭据存放方式（重要发现）

Spug 的主机密码/私钥机制：

```python
# apps/host/models.py
pkey = models.TextField(null=True)
def private_key(self):
    return self.pkey or AppSetting.get('private_key')
```

- 单机 `pkey` 为空时，回落到 **全局 `private_key`**（`settings` 表，长度 1675 字符）
- 该私钥在数据库里是**明文存储**（未加密），且**所有主机共用同一把**

本次已把它导出到旧 Spug 机的 `/root/spug_private_key`（600 权限），仅用于验证，**未写入文档、未发群、未外传**。

## 三、可用性验证：私钥已失效

```
ssh-keygen -y -f /root/spug_private_key   → 私钥格式有效（ssh-rsa AAAAB3Nza…）
ssh -i /root/spug_private_key root@38.92.8.34        → Permission denied (publickey,password)
ssh -i /root/spug_private_key root@38.92.8.151       → Permission denied
ssh -i /root/spug_private_key root@173.231.49.86     → Permission denied
ssh -i /root/spug_private_key root@45.135.237.47:13575 → Permission denied
ssh -i /root/spug_private_key root@138.252.248.139:38927 → Permission denied
ssh -i /root/spug_private_key root@191.40.41.155     → Permission denied
```

结论：Spug 保存的全局私钥**已被各主机移除/轮换**，与 Davie 反馈的「Spug 里的凭据已失效」一致。

## 四、此前缺失的主机是否在 Spug 里

在两套 Spug 的整库导出中检索：

```
38.54.17.130  → 未收录
103.107.199.30 → 未收录
43.241.16.84  → 未收录
43.160.201.59 → 未收录
101.47.158.5  → 未收录
3.35.9.127    → 未收录
162.211.181.13 → 旧 Spug 有记录（root / 22）
cdn-hk-01     → 未收录
```

对 162.211.181.13 的验证：**即使在旧 Spug 主机内部发起 SSH，也是连接超时**（`connect to host 162.211.181.13 port 22: Connection timed out`），说明该机当前网络不可达，与凭据无关。

## 五、结论与建议

1. Spug 的凭据**无法**用于接入缺失主机：要么未收录，要么私钥已失效，要么机器网络不可达
2. 这几台仍需运维通过**云控制台**确认状态并重新提供登录方式
3. 安全建议（重要）：
   - Spug 的全局私钥**明文存库且多机共用**，一旦 Spug 数据库泄露即等于拿到全部主机权限；建议改为**每机独立密钥**，并对 `settings.private_key` 做加密存储或改用 Vault/KMS
   - 建议轮换该共用私钥，并在各主机 `authorized_keys` 中清理不再使用的旧公钥
   - 限制 Spug 数据库的访问来源（当前仅容器网内访问，但宿主机 root 可直接读）
4. 新 Spug 中部分主机名在数据库里显示为 `???`（字符集写入问题），建议在 Spug 界面重新保存一次名称，便于审计

---

## 六、全机队扫描：确认只有两套 Spug（2026-10-19 22:10）

为排除「还有其它 Spug / 定时任务实例藏着凭据」，对**全部可 SSH 的 12 台服务器**逐一扫描：

扫描项：

```
docker ps -a | grep -i spug            # 容器
[ -d /data/spug ]                      # 数据目录
systemctl list-units --all | grep -i spug
ls /opt | grep -i spug                 # 安装目录
```

结果：

| 主机 | 是否存在 Spug |
| --- | --- |
| 52.79.252.255（监控机） | 否 |
| 154.36.178.157（GitLab） | 否 |
| 13.208.245.64（从库02） | 否 |
| 15.168.164.29（从库01） | 否 |
| 16.209.16.108（后端） | 否 |
| 16.208.38.88（网关） | 否 |
| **16.208.32.40（定时任务机）** | **是**（spug + spug-db，/data/spug，/opt/spug） |
| 15.152.247.196（测试后端） | 否 |
| **103.207.68.124（旧 Spug/任务机）** | **是**（spug + spug-db，/data/spug，/opt/spug） |
| 13.208.101.121（前端） | 否 |
| 56.155.42.18（主库） | 否 |
| 16.208.5.147（宝塔） | 否 |

**结论：全机队只有这两套 Spug，没有第三套。** 两套的 `hosts` 表 + 全库导出里都不包含 38.54.17.130、103.107.199.30、43.241.16.84、43.160.201.59、101.47.158.5、3.35.9.127、cdn-hk-01。

> 无法扫描的主机（无 SSH 或 sudo 受限）：msb 三台、打包机 154.95.24.45、测试 H5 38.92.8.34、SPJ 三台、短剧两台、宝塔（sudo 需密码）。如果本地/其它渠道确认这些机器上也跑过 Spug，需要提供入口后再扫。
