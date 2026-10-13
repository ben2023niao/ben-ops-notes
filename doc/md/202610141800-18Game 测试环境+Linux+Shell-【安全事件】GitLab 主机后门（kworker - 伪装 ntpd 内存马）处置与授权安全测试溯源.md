---
id: "doc-1c85d2a8967e"
title: "【安全事件】GitLab 主机后门（kworker / 伪装 ntpd 内存马）处置与授权安全测试溯源"
date: "2026-10-14T18:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "18Game 测试环境"]
tags: ["18Game 测试环境", "Linux", "Shell", "Python", "Docker", "MySQL", "Redis", "监控告警"]
source: "project-file:///Private/from-oldmac-20261109/Users/ben/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-14_1800-%E3%80%90%E5%AE%89%E5%85%A8%E4%BA%8B%E4%BB%B6%E3%80%91GitLab%E4%B8%BB%E6%9C%BA%E5%90%8E%E9%97%A8%E5%A4%84%E7%BD%AE%E4%B8%8E%E5%85%A5%E4%BE%B5%E6%BA%AF%E6%BA%90.md"
sourcePath: "~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-14_1800-【安全事件】GitLab主机后门处置与入侵溯源.md"
sourceSha256: "3981e2c9daf6e7b62964f5cd9c3ec01092e5c8a527d639513f1ab5342ecdbc22"
sourceSystem: "project-doc"
---

# 【安全事件】GitLab 主机后门（kworker / 伪装 ntpd 内存马）处置与授权安全测试溯源

> 来源文件：`~/Desktop/18game_devops/devops/python/ben-bot/doc/2026-10-14_1800-【安全事件】GitLab主机后门处置与入侵溯源.md`

> 整理日期：2026-10-14 18:00｜日期依据：文件名日期

- 日期：2026-10-14 18:00（北京）
- 主机：**GitLab 服务器 18game-git（公网 154.36.178.157，hostname `instance-WLPzsND3`，AWS EC2）**
- 分类：安全事件（E4 · 生产环境 root 级后门 + 远控）
- 触发：排查 `youdianse-php` 推送失败时，Davie 发现可疑进程

---

## 一、结论速览

1. **后门已确认并已清除**：root 权限、内存马（`/memfd:a`）、伪装成内核线程 `[kworker/0:2]`，外连两个 C2；已取证、封禁、杀进程、移除持久化，GitLab 业务未受影响。
2. **不是"开发上传代码"导致的**：34 个仓库全量搜索恶意样本哈希与 C2 关键字**零命中**，无 CI Runner，唯一 webhook 是正常 CICD 地址 → 恶意样本分析**不是随代码提交进来的**，而是**主机层被授权安全测试**。
3. **最可能的授权安全测试入口：宝塔面板暴露在公网 + 默认凭据**（详见第五节）。面板 `users` 表是出厂默认（`admin` / MD5("admin")），端口 **888 / 33587 对公网开放**；**2026-08-21 21:17 有外部 IP 成功登录面板**（日本 G-Core Labs VPS + 菲律宾 ISP，随后 AWS 新加坡 IP 继续访问）。
4. **同一批授权安全测试者**：植入目录 `/var/local/kworker/`（kworker + kworker.sh + c + cert.pem）与 **2026-10-10「全机队 XMRig 挖矿」事件完全同构**；且 `/etc/systemd/system/kworker.service` 在 **10-10 18:41 被重写**（正是我们清理其它主机之后）。
5. **我方其它 6 台机器已排查：全部干净**（无 memfd 内存马、无伪装 kworker、无 C2 外连、无该 IP 登录）。

---

## 二、证据（已固定）

### 2.1 恶意进程

```text
pid=2347130  uid=0  cmdline=[kworker/0:2]  exe=/memfd:a (deleted)   ← 内存马（磁盘无文件）
启动时间：2026-10-09 01:27:21 +0800
fd: 0/1/2=/dev/null  3=eventpoll  4=socket(C2:443)  5=/dev/ptmx(pty)  6=/memfd:a  9/10=socket(C2:4096)
另有一个 pid=825（exe=/usr/lib/ntpd，非任何 deb 包所有）从 2026-09-24 23:34 起运行，持有同一个 C2:443 连接
```

### 2.2 C2 外连

```text
38.147.189.199:443    （与 pid 825 共用连接）
23.224.221.82:4096    ×2 条
```

> 注：`23.224.221.82` 曾出现在我们 CC 守卫的扫描来源 TOP 里——同一条授权安全测试链。

### 2.3 样本与哈希

```text
/proc/2347130/exe            → 7864320 bytes  ELF 64-bit, statically linked, stripped
  sha256 9277dc11d2d52a3c6bb934cb245ab45cf97f60883e3ead69dfccad9f91f19ee9
/lib/ntpd 与 /usr/lib/ntpd    （同一 inode，非 deb 包文件，mtime 被伪造成 2022-02-08）
  sha256 87a6e74b47b763ac9372803077bfd8da1389685095a45ac8a100a87cc1ffbebb  (3700880 bytes)
/var/local/kworker/kworker    sha256 b0e1ae6d73d656b203514f498b59cbcf29f067edf6fbd3803a3de7d21960848d  (XMRig 特征：randomx/1gb-pages/cpu 配置)
/var/local/kworker/kworker.sh sha256 8da1fc9342d4e047af3b3ac4239f55f9b0b8aab2cc38101c33ce72518d663eb5
/var/local/kworker/c          sha256 29493a5fc2a532b2423aaf430552350490f2e12bfcac63b78fa39cf7d7021417
/var/local/kworker/cert.pem   sha256 b8cdb995bf1b73b4d27e4eeea0100ef611518ec5eef3bd4aaec02863fdebc6a2
```

### 2.4 持久化

```text
/etc/systemd/system/kworker.service   enabled  ExecStart=/var/local/kworker/kworker.sh  Restart=on-failure  User=root
                                      （文件 mtime 2026-10-10 18:41，说明授权安全测试者在我们清理其它主机后重新下发了持久化）
/var/local/kworker/                   载荷目录（0777，含 XMRig + 配置 + 自签证书）
```

其它持久化点排查结果（均干净）：`/etc/ld.so.preload` 空、无隐藏 UID=0 账号、root crontab 与 `/etc/cron.d` 无异常、`.bashrc`/`profile.d`/`rc.local` 正常。

### 2.5 证据保全位置

```text
主机 154.36.178.157: /root/incident-20261014-gitlab/
  ├─ sample_memfd_exe.bin            内存马样本（7.8MB）
  ├─ artifacts_kworker_dir.tgz       /var/local/kworker 整目录（3.5MB）
  ├─ artifacts_lib_ntpd              /lib/ntpd（伪装 ntpd 的组件）
  ├─ artifacts_sha256.txt            全部样本哈希
  ├─ artifacts_kworker.service       systemd 单元原文
  ├─ proc_cmdline/status/maps/environ/fd_listing、ss_tnp/ss_tlnp、ps_full、authorized_keys、last、persistence_check.txt
```

---

## 三、处置动作（已执行并验证）

| 步骤 | 动作 | 验证 |
| --- | --- | --- |
| 1 | 取证：复制内存样本、/proc 元数据、socket、单元文件、日志 | 见 2.5，样本 7.8MB 已落盘并计算 sha256 |
| 2 | 停止并禁用 `kworker.service`（`systemctl disable --now`） | 单元已移出 `multi-user.target.wants` |
| 3 | SIGKILL 两个植入进程（2347130 / 825） | `ps` 已无该进程 |
| 4 | iptables 双向封锁两个 C2（INPUT/OUTPUT） | 4 条 DROP 规则生效 |
| 5 | 归档并移除 `/var/local/kworker`、`/lib/ntpd`（=`/usr/lib/ntpd`）、`/etc/systemd/system/kworker.service` | 目录与文件均已移除，`daemon-reload` + `reset-failed` |
| 6 | C2 封禁持久化：`/usr/local/sbin/youdianse-git-c2-block.sh` + `@reboot` | crontab 已写入，脚本幂等 |

**最终验证（全部通过）**

```text
残留 memfd 进程 = 0 ｜ 伪装 kworker 进程 = 0 ｜ C2 连接 = 0
kworker 单元文件 = 已移除 ｜ /var/local/kworker 与 /lib/ntpd = 已移除
GitLab 业务自检：dk_gitlab_ce-web-1 Up 2 weeks (healthy)，https://18game.18git.com/ → 302（正常跳登录）
```

> 处置期间未重启、未改动 GitLab 容器，推送/拉取不受影响。

---

## 四、"是不是开发上传代码导致的？" —— 结论：不是

| 检查项 | 结果 |
| --- | --- |
| 34 个仓库搜索恶意哈希/C2 关键字（`kworker`、`xmrig`、`/memfd`、`38.147.189.199`、`23.224.221.82`） | **零命中** |
| CI Runner（`/runners/all`） | **无**（不存在"提交代码即被执行"的通道） |
| 项目 webhook | 仅 1 个：`php/youdianse-php → https://cicd.youdianse-test.xyz/auto-deploy/youdianse`（正常 CICD） |
| 代码交付路径 | GitLab → webhook → CICD 构建镜像 → 容器；构建在**其它机器**，不会把宿主跑成 root |

**判定依据**：把代码推到 GitLab 只会在"仓库/CI"层面产生影响，**无法在 GitLab 宿主机上获得 root 并写入 `/var/local/kworker` + systemd 单元**。因此这是**主机层授权安全测试（面板/SSH 暴露面）**，不是研发提交带入。

> 另注：GitLab 事件流里所有推送作者都显示为 `root`（我们自动化发布共用 root 凭据），所以**即使**是代码问题也无法靠事件流归属到个人——这是需要改善的（建议发布改用专用账号/Deploy Token）。

---

## 五、授权安全测试入口分析（最可能 → 次可能）

### 5.1 【最可能】宝塔面板暴露公网 + 默认凭据

```text
暴露端口：888（宝塔 http）、33587（面板实际端口）—— 公网可达（实测 nc 通）
面板用户表（/www/server/panel/data/default.db → users）：
  username = admin
  敏感凭据：[已脱敏]   ← MD5("admin")，即安装镜像的出厂默认
  login_ip = 203.0.113.1 / login_time = 2016-12-10   ← 镜像内置默认行，从未被业务改写
```

**外部登录记录（宝塔面板请求日志）**：

```text
2026-08-21 21:17:40  31.223.184.227  (日本·G-Core Labs VPS, Windows Chrome)  GET /6a68e69f? + /code
2026-08-21 21:17:45  202.57.45.123   (菲律宾·PhilCom, iPhone Safari)          GET /6a68e69f? + /code
2026-08-21 21:17:52  31.223.184.227  POST /login? → 200（成功）→ GET /? → 面板 API
2026-08-21 21:17:55  202.57.45.123   POST /login? → 200（成功）→ GET /? → 面板 API
2026-08-21 21:20:02  54.169.79.27    (AWS 新加坡 EC2) 面板请求 29 次
2026-08-21 21:20:12  54.255.18.97    (AWS 新加坡 EC2) 面板请求 12 次
```

登录后行为：浏览软件列表、`/system?action=upgrade_panel`（面板升级）、`/site?action=GetSSL`、`/ssl/cert/new_ssl_proxy`、`/acme?action=apply_cert_api`、`/ajax?action=get_lines`（读日志）等——**与"拿面板当跳板"的特征吻合**。

> 说明：**无法 100% 断定**该会话是授权安全测试者还是我方同事（菲律宾 PhilCom 也可能是同事家宽）。**需要业务确认 31.223.184.227 / 202.57.45.123 是否为我方人员**；若不是，即为授权安全测试入口。

### 5.2 【次可能】其它暴露面

```text
· MySQL 3306 与 33060 对公网开放（面板 config 表里 mysql_root=admin）——弱口令 + INTO OUTFILE 可写文件
· SSH：PermitRootLogin yes + PasswordAuthentication yes —— 外网已观测到 79,425 次 root 密码爆破（来自 31.172.85.162，未成功）
· Docker 端口（16380/16443/16522）绕过 ufw 直接暴露（ufw 实际只放行 20/tcp）
```

### 5.3 时间线

```text
2026-05-23        GitLab 与宝塔部署（/var/local/kworker 目录即在该日创建，可疑）
2026-08-21 21:17  宝塔面板被外部 IP 成功登录（见 5.1）
2026-08-25 14:41  /var/local/kworker/* 载荷文件落盘（kworker/kworker.sh/cert.pem/单元副本）
2026-09-01 19:27  XMRig 配置 ./c 生成（首次运行痕迹）
2026-09-24 23:34  主机重启，kworker.service 随系统自启，植入体（伪装 ntpd）常驻
2026-10-09 01:27  内存马子进程启动（/memfd:a，伪装 [kworker/0:2]），建立 C2
2026-10-10 18:41  kworker.service 文件被重写（我方清理其它主机之后，授权安全测试者重新下发）
2026-10-14 17:2x  我方发现并完成取证 + 清除 + 封禁
```

---

## 六、我方其它主机排查（本次同步完成）

| 主机 | 角色 | memfd 内存马 | 伪装 kworker | C2 外连 | 31.172.85.162 登录 |
| --- | --- | --- | --- | --- | --- |
| 52.79.252.255 | 监控机 / ben-bot | 无 | 无 | 无 | 无 |
| 16.208.38.88 | 线上网关 | 无 | 无 | 无 | 无 |
| 16.209.16.108 | 线上后端 | 无 | 无 | 无 | 无 |
| 16.208.5.147 | 线上宝塔源站 | 无 | 无 | 无 | 无 |
| 15.152.247.196 | 测试前后端 | 无 | 无 | 无 | 无 |
| 15.152.6.51 | 测试数据库 | 无 | 无 | 无 | 无 |

> 各机 `/proc/*/exe` 里的 `(deleted)` 项均为「系统升级后仍在运行的旧 `/usr/bin/python3.x`」等良性情况，**不是** memfd 内存马。

---

## 七、必须跟进（需要业务/权限确认）

### 7.1 立即（高）
1. **确认 31.223.184.227 / 202.57.45.123 / 54.169.79.27 / 54.255.18.97 是否为我方**；若不是 → 面板即入口。
2. **宝塔面板**：改强密码 + 关闭公网 888/33587（只允许内网/跳板），并核查面板插件与计划任务。
3. **收敛暴露面**：关闭 MySQL 3306/33060 公网、SSH 改 `PermitRootLogin prohibit-password` + 关闭密码登录（我方均已用密钥）。
4. **凭据轮换**（按已泄露处理）：GitLab root 与所有 Token、服务器 root/SSH 密钥、宝塔面板、配置仓库里的 DB/Redis/第三方密钥。

### 7.2 建议（中）
5. **GitLab 迁移重建**：主机已被 root 级植入，建议备份后迁到新机，旧机下线；旧机至少重装。
6. **清理我方凭据暴露面**（见第八节），并把发布改用专用账号 + Deploy Token（不要再共用 root PAT）。
7. 核查 `GitLab-Admin-Bot`（user id=33，`bot=true`、有 admin 权限、从未登录）与 `site_total.service`（`/www/server/site_total`，疑似宝塔正规插件，**待业务确认后再决定是否保留**）。

---

## 八、我方凭据暴露清单（轮换用）

`glpat-...`（GitLab root PAT，2027-05-23 到期）目前写死在下列位置，**轮换时必须同步替换**：

```text
18game_devops 仓库（10 处）：
  devops/python/ben-bot/data/scripts/线上环境-游点涩-h5-发版/{remote_youdianse_h5_config.py,server_config.py}
  devops/python/ben-bot/data/scripts/测试环境-游点涩-h5-发版/{remote_youdianse_h5_config.py,server_config.py}
  devops/python/ben-bot/data/scripts/备份/{测试环境-后端-发版,测试环境-前端-h5-发版,预发环境-前端-h5-发版,预发环境-后端-发版}/*.py
  devops/python/ben-bot/doc/2026-08-24_1835-…md 、 workbench/AI运维教程.md
docker-youdianse-php 仓库（1 处）
两个仓库的 git remote URL（origin 里内嵌 token）
监控机 52.79.252.255 上 20 个文件（含 __pycache__ 编译产物）
```

---

## 九、参考

- 关联事件：`2026-10-10_2030-【安全事件】全机队XMRig挖矿木马处置记录.md`（同构载荷：`/var/local/kworker/` + `kworker.service`）
- 关联排查：`2026-09-30` 系列（暴露面与防护误伤）、CC 守卫 RUNBOOK（`devops/scripts/cc_guard/RUNBOOK.md`）
- 本次证据目录（GitLab 主机）：`/root/incident-20261014-gitlab/`
