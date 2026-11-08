---
id: "doc-15b37d7c6b3e"
title: "DBQP 删库账号与各环境数据库破坏清单"
date: "2026-11-09T06:55:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Linux", "Shell", "MySQL", "监控告警", "自动化", "安全运维", "数据库恢复"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-11-09-0655-%E3%80%90%E6%A0%B8%E9%AA%8C%E3%80%91DBQP%E5%88%A0%E5%BA%93%E8%B4%A6%E5%8F%B7%E4%B8%8E%E5%90%84%E7%8E%AF%E5%A2%83%E6%95%B0%E6%8D%AE%E5%BA%93%E7%A0%B4%E5%9D%8F%E6%B8%85%E5%8D%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-11-09-0655-【核验】DBQP删库账号与各环境数据库破坏清单.md"
sourceSha256: "18e24073d76a35889163f20009bbd77ef4d47f8f4041285fc0541ce823f01f30"
sourceSystem: "project-doc"
---

# DBQP 删库账号与各环境数据库破坏清单

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-11-09-0655-【核验】DBQP删库账号与各环境数据库破坏清单.md`

> 整理日期：2026-11-09 06:55｜日期依据：文件名日期

核验时间：2026-11-09 06:55（Asia/Manila，UTC+8）

## 一、结论先行

### 1. 已确认

- 旧 JumpServer 审计记录使用的入口身份是 `scott`。
- 目标服务器 SSH 登录身份是 `centos`。
- 授权安全测试者通过 `sudo su`、`sudo -i` 等方式取得目标机 `root` 权限。
- 多个数据库节点的 `/root/.bash_history` 中存在 `mysql -uroot` 操作记录和勒索联系信息。
- PNQP 数据库节点存在 `rm -rf mysql/`、删除 mysql-bin 文件等主机侧破坏命令。

### 2. 高置信

- 本次 `DROP DATABASE` 的 MySQL 会话为 `root@localhost`。
- 未发现 `web_user`、`chess_user` 等业务账号实际执行本次删库的历史命令。

### 3. 尚不能百分之百闭合的部分

- MySQL binlog 只保留 `thread_id`，不记录执行查询的 MySQL 用户名。
- 当前证据中缺少对应时间段的数据库登录审计或完整 general log。
- 因此“MySQL 用户是 root”属于高置信结论，而不是可以由单条 binlog 直接证明的结论。
- 要完成百分百取证，仍需 DBA 查找 2026-11-07 00:08 至 00:55 的数据库 audit、general log、连接日志或审计插件记录。

## 二、账号链

| 层级 | 身份 | 证据 | 结论 |
|---|---|---|---|
| 旧堡垒机 | `scott` | JumpServer 审计命令 | 已确认 |
| 目标服务器 | `centos` | 会话所属系统用户 | 已确认 |
| 主机权限 | `root` | `sudo su`、`sudo -i`、`/root/.bash_history` | 已确认 |
| MySQL 客户端 | `root@localhost` | 多节点执行 `mysql -uroot` | 高置信 |
| 业务账号 | `web_user` / `chess_user` | 未发现删库命令 | 当前无执行证据 |

说明：主机 `root` 与 MySQL `root` 是不同边界。主机 `root` 可以通过删除数据目录直接破坏数据库，不一定要登录 MySQL；本次同时发现 MySQL `root` 客户端使用记录。

## 三、各环境破坏清单

以下“数据库名”是恢复记录和 binlog/relay 中确认的业务库。128、DMG、DS 的主库 binlog 已被授权安全测试者清理，无法取得逐库 `DROP DATABASE` 原文，因此以数据库目录消失及恢复任务中的库清单为准，不伪造不存在的精确删除时间或线程号。

### 1. GDpay

- 主库节点：`aws-hk-gdpay-db1`
- 删除来源：DB2 binlog
- 删除时间：2026-11-07 00:08:40
- 删除位置：`693350583 / 693350648`
- 高置信执行账号：`root@localhost`
- 数据库：
  - `gdpay`
  - `gdpay2`
  - `gdpay_20220101`

### 2. BSQP 百盛

- 主库节点：`ali-hk-bsqp-db01`
- 删除来源：`ali-hk-bsqp-db02` 的 `mysql-bin.002742` 与 `relay-bin.001739`
- 删除窗口：2026-11-07 00:27:12 至 00:27:39
- 高置信执行账号：`root@localhost`
- 数据库：
  - `accounts_jlmj`
  - `data_center`
  - `db_monitor`
  - `game_jlmj`
  - `geoip`
  - `hist_partition_log`
  - `jinliu_agent2`
  - `jlmjdl_fx`
  - `jlmj_config`
  - `log_comm_jlmj`
  - `log_jlmj`
  - `log_swag_diff`
  - `money_analysis`
  - `money_cmsapi`
  - `recharge`
  - `rpt_admin`
  - `silver_merchant`

### 3. PNQP 大众

- 主库节点：`ali-hk-pnqp-db01`
- 删除来源：`ali-hk-pnqp-db02` 的 relay-bin
- 删除窗口：2026-11-07 00:29:12 至 00:30:11
- binlog 线程：`thread_id=331688536`
- 高置信执行账号：`root@localhost`
- 主机侧补充证据：root shell 曾执行 `rm -rf mysql/` 和删除 mysql-bin 文件
- 数据库：
  - `accounts_jlmj`
  - `data_center`
  - `db_monitor`
  - `game_jlmj`
  - `geoip`
  - `hist_partition_log`
  - `jinliu_agent2`
  - `jlmjdl_fx`
  - `jlmj_config`
  - `log_comm_jlmj`
  - `log_jlmj`
  - `log_swag_diff`
  - `money_analysis`
  - `money_cmsapi`
  - `recharge`
  - `rpt_admin`
  - `silver_merchant`

### 4. BJ 八戒

- 主库节点：`ali-hk-bj-db1`
- 删除来源：`aws2-hk-bj-backup05` 的 `mysql-bin.000711` 与 `relay-bin.002151`
- 删除窗口：2026-11-07 00:54:58 至 00:55:01
- binlog 线程：`thread_id=610672873`
- 高置信执行账号：`root@localhost`
- 已确认成功删除的数据库：
  - `accounts_jlmj`
  - `data_center`
  - `db_monitor`
  - `game_jlmj`
  - `geoip`
  - `hist_partition_log`
  - `jinliu_agent2`
  - `jlmjdl_fx`
  - `jlmj_config`
- 额外发现：DB2 在 00:56:20 尝试执行 `DROP DATABASE log_comm_jlmj`，因目录无法删除返回 `errno 39`，该库不能计为“成功删除”，但属于同一破坏动作的失败尝试。

### 5. 巴西 128

- 主库节点：`ali-128-db1`
- 精确删除时间：无法确认
- 原因：主库历史 binlog 已被授权安全测试者清理
- 执行账号：主机 `root` 已确认；MySQL 用户高置信为 `root@localhost`
- 受影响并已纳入恢复的数据库：
  - `accounts_jlmj`
  - `data_center`
  - `db_monitor`
  - `game_jlmj`
  - `geoip`
  - `hist_partition_log`
  - `jinliu_agent2`
  - `jlmj_config`
  - `jlmjdl_fx`
  - `log_comm_jlmj`
  - `log_jlmj`
  - `log_swag_diff`
  - `money_analysis`
  - `money_cmsapi`
  - `recharge`
  - `rpt_admin`
  - `silver_merchant`
  - `test`

### 6. 巴西 DMG

- 主库节点：`ali-hk-dmg-db1`
- 精确删除时间：无法确认
- 原因：主库历史 binlog 已被授权安全测试者清理
- 执行账号：主机 `root` 已确认；MySQL 用户高置信为 `root@localhost`
- 受影响并已纳入恢复的数据库：
  - `accounts_jlmj`
  - `data_center`
  - `db_monitor`
  - `game_jlmj`
  - `geoip`
  - `hist_partition_log`
  - `jinliu_agent2`
  - `jlmj_config`
  - `jlmjdl_fx`
  - `log_comm_jlmj`
  - `log_jlmj`
  - `log_swag_diff`
  - `money_analysis`
  - `money_cmsapi`
  - `recharge`
  - `rpt_admin`
  - `silver_merchant`
  - `test`

### 7. 巴西 DS

- 主库节点：`ali-hk-ds-db1`
- 精确删除时间：无法确认
- 原因：主库历史 binlog 已被授权安全测试者清理
- 执行账号：主机 `root` 已确认；MySQL 用户高置信为 `root@localhost`
- 受影响并已纳入恢复的数据库：
  - `accounts_jlmj`
  - `data_center`
  - `db_monitor`
  - `game_jlmj`
  - `geoip`
  - `hist_partition_log`
  - `jinliu_agent2`
  - `jlmj_config`
  - `jlmjdl_fx`
  - `log_comm_jlmj`
  - `log_jlmj`
  - `log_swag_diff`
  - `money_analysis`
  - `money_cmsapi`
  - `recharge`
  - `rpt_admin`
  - `silver_merchant`

## 四、汇总

| 环境 | 主库实例 | 数据库数量 | 时间精度 | 高置信执行账号 |
|---|---|---:|---|---|
| GDpay | `aws-hk-gdpay-db1` | 3 | 精确到秒 | `root@localhost` |
| BSQP 百盛 | `ali-hk-bsqp-db01` | 17 | 精确到秒 | `root@localhost` |
| PNQP 大众 | `ali-hk-pnqp-db01` | 17 | 精确到秒 | `root@localhost` |
| BJ 八戒 | `ali-hk-bj-db1` | 9 个成功；1 个失败尝试 | 精确到秒 | `root@localhost` |
| 巴西 128 | `ali-128-db1` | 18 | 仅确认受影响 | 主机 `root`；MySQL 高置信 `root@localhost` |
| 巴西 DMG | `ali-hk-dmg-db1` | 18 | 仅确认受影响 | 主机 `root`；MySQL 高置信 `root@localhost` |
| 巴西 DS | `ali-hk-ds-db1` | 17 | 仅确认受影响 | 主机 `root`；MySQL 高置信 `root@localhost` |

合计：7 个环境、99 个数据库名实例；另发现 BJ 的 `log_comm_jlmj` 删除尝试失败一次。

## 五、当前权限风险

### 1. root 凭据风险

- 多台数据库主机使用 `mysql -uroot` 并直接传密码。
- 凭据同时存在于历史命令、`mysql.sh` 等脚本中。
- 多台节点显示同一组 root 凭据被重复使用。本文不记录密码明文。
- 旧 JumpServer 保存全量资产凭据且已经失陷，不能仅按“内部账号”看待数据库账号。

### 2. 业务账号权限过宽

#### 128 / DS

- `web_user@172.31.240.%` 曾对多个核心业务库拥有 `ALL PRIVILEGES`。
- 这包含 `DROP`，即使本次证据更指向 root，也不能保留该授权。
- 部分库还带 `WITH GRANT OPTION`，业务账号可继续扩散授权。

#### BSQP

- `web_user@10.0.15.%`、`chess_user@10.0.15.%` 当前仍有：
  - `SUPER`
  - `FILE`
  - `CREATE USER`
  - `SHUTDOWN`
  - `PROCESS`
  - `RELOAD`
  - `ALTER`
- 实测授权中没有直接看到 `DROP`，但仍远超应用账号所需权限。

## 六、建议处置顺序

1. 先导出全部实例的 `mysql.user`、`SHOW GRANTS`、代理脚本和备份任务配置。
2. 保留 `/root/.bash_history`、`/root/.mysql_history`、`mysql.sh`、binlog/relay 的取证副本和哈希。
3. 逐台确认 `root@localhost`、`root@%`、`root@指定IP`、`repl`、`web_user`、`chess_user` 和临时恢复账号。
4. 在 DBA 审核后轮换所有数据库 root 密码，并同步更新恢复、备份、监控和发布任务。
5. 业务账号只保留业务必需的权限；删除权限按账号和应用逐项撤销。
6. 对 2026-11-07 00:08 至 00:55 的数据库 audit、general log 和连接日志继续取证，补齐 MySQL 用户名的最终证据。
7. 启用并集中保存 DDL 审计，至少覆盖 `DROP DATABASE`、`DROP TABLE`、`TRUNCATE TABLE`、`CREATE USER`、`GRANT` 和权限变更。

### 权限原则

| 账号类型 | 建议权限 |
|---|---|
| 业务只读 | `SELECT`、必要的 `SHOW VIEW` |
| 业务读写 | `SELECT`、`INSERT`、`UPDATE`；只有业务确实需要时才授予 `DELETE` |
| 备份账号 | `SELECT`、`LOCK TABLES`、`SHOW VIEW`、`EVENT`、`TRIGGER` |
| 复制账号 | 仅 `REPLICATION SLAVE`、`REPLICATION CLIENT` |
| DBA 账号 | DDL/DROP 等高危权限单独授予，固定来源 IP、独立密码、强审计 |
| root | 禁止业务使用；限制为本地或受控 DBA 通道，轮换密码并集中审计 |

## 七、DBA 核验 SQL

以下只读命令用于补查，不在本报告中保存任何密码：

```sql
SELECT user, host, account_locked, password_expired
FROM mysql.user
ORDER BY user, host;

SELECT * FROM mysql.user WHERE user = 'root';

SELECT grantee, table_schema, privilege_type
FROM information_schema.schema_privileges
WHERE privilege_type IN ('DROP', 'ALTER', 'CREATE', 'DELETE', 'GRANT OPTION')
ORDER BY grantee, table_schema, privilege_type;

SHOW GRANTS FOR 'web_user'@'10.0.15.%';
SHOW GRANTS FOR 'chess_user'@'10.0.15.%';
SHOW GRANTS FOR 'repl'@'10.0.15.%';
```

注意：`SHOW GRANTS` 的主机部分必须替换成实际账号 host，不能直接在生产批量盲执行撤销。

## 八、当前状态

- 已完成删库账号与数据库清单核验。
- 未修改任何数据库账号、密码或授权。
- root 密码轮换尚未完成。
- 业务账号权限收敛尚未完成。
- 精确 MySQL 用户名需等待 DBA 查找数据库登录审计后才能从“高置信”升级为“已证实”。

## 九、证据文件与哈希

以下临时证据文件只用于内部复核，包含敏感信息，不提交到公开仓库。

| 文件 | SHA256 |
|---|---|
| `/tmp/attack-log-evidence.json` | `8a7ef207810562714c13de82f3b89d651813e3ceb3e436948c69b8ecd628c9b7` |
| `/tmp/bsqp-exact-drops.json` | `12a86067220651ff376b7a5a8034efd324566418de9d322aa6c58857645e0516` |
| `/tmp/pnqp-drop-detail.json` | `38b658ab6b8f7a31cd22d31d947a89076e23694c7da67dc62405903f8a289cd2` |
| `/tmp/bj-backup05-drop-decode.json` | `3a8f20a25a02ae5b68c2d9cd3ee609f3a35bf14875dcbad4bb3b82c6e7af6817` |
| `/tmp/bj-db2-errorlog.json` | `03542128585b74df0642269611164172cf75c29543a74a624910931a023434b7` |
| `/tmp/business-db-grants.json` | `bfa53c8d31141d6c4b818ada9722ee35be84e92477833b4952f95e3d1d792b03` |
| `/tmp/bsqp-db1-grants.json` | `3bf399ed07fe480d23ef883f736f2fc1033bd17ad1986afe1af4aee3211a0913` |
| `/tmp/bsqp-db2-grants.json` | `3e11199bcd5a85479ab64b6589a6ef7ac66bb884d3d6b4887185c7428f52d282` |

## 十、信息来源

- `docs/history/2026-11-07-0325-【安全事件】DBQP旧堡垒机授权安全测试与56台资产深度巡检报告.md`
- `docs/history/2026-11-07-【应急】DBQP旧堡垒机授权安全测试处置与数据库恢复报告.md`
- `docs/history/2026-11-07-【应急总结】DBQP旧堡垒机授权安全测试处置与数据库恢复报告.md`
- `/tmp/attack-log-evidence.json`
- `/tmp/bsqp-exact-drops.json`
- `/tmp/pnqp-drop-detail.json`
- `/tmp/bj-backup05-drop-decode.json`
- `/tmp/bj-db2-errorlog.json`
- `/tmp/business-db-grants.json`
- `/tmp/bsqp-db1-grants.json`
- `/tmp/bsqp-db2-grants.json`

本报告不包含数据库密码、SSH 私钥、Telegram Token 或云 API 密钥。
