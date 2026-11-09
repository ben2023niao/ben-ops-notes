---
id: "doc-recovery-toolkit-20261110-02"
title: "某支付平台数据库恢复脚本与工具说明"
description: "某支付平台 数据库恢复工具链完整归档，覆盖主库日备、binlog PITR、57 张历史 _bak 表恢复、隔离只读实例、在线核验与安全门禁，包含全部 13 个脚本源码、中文备注和 SHA256 校验信息。"
date: "2026-11-10T04:45:00+08:00"
dateSource: "附件文件名"
author: "BEN"
difficulty: "高级"
categories: ["数据库与恢复", "MySQL"]
tags: ["某支付平台", "数据库恢复", "PITR", "binlog", "XtraBackup", "MySQL", "备份恢复", "支付数据", "Shell", "Python"]
sourcePath: "/Users/operator/Downloads/2026_11_10_0445_恢复工具_某支付平台数据库恢复脚本与工具说明.md"
sourceSha256: "c8b091077279a2c2ab8a18ac637d2b79a917a32d96e94f2a158912614b9d28ff"
archiveSha256: "94247f1432e7029ec76cb3a5a65bce50e1216a4b58f54c22722393b6f501f68e"
archiveBytes: 49896
---

# 某支付平台数据库恢复脚本与工具说明

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 平台：某支付平台  
> 归档时间：2026-11-10 04:45（Asia/Manila，UTC+8）  
> 范围：主库日备与 binlog PITR，以及 2026-07-15 XtraBackup 中 57 张历史 `_bak` 表恢复。

本文完整归档某支付平台 本次误删恢复所用的审计、导出、回放、历史表导入、在线核验和重建工具。正文先说明工具包边界、目录职责和交付物校验结果，再记录恢复结论、删除位置、恢复链、实际运行数据、安全门禁和每一个脚本的源码，供本次支付业务恢复审计、复盘和受控复现使用。

## 一、归档范围与数据边界

本工具包覆盖 某支付平台 主库日备导入、DROP 前 binlog PITR、57 张历史 `_bak` 表隔离导出与导入、数据库和恢复材料核验，以及文档与 ZIP 重建。ZIP 只含 README、校验清单和 13 个脚本，不含数据库密码、Token、私钥、云 API Key 或支付业务数据。

某海外中转站 上约 7.36 GiB 的 某支付平台 恢复材料属于支付业务数据，不放入工具 ZIP，也不发送到群。恢复群只传脚本、说明、文件大小和哈希。本文记录材料数量和校验结论，不嵌入数据包、业务记录或凭据。

## 二、工具包目录与中文备注

目录按恢复阶段拆分。恢复发现、主库 PITR、历史 `_bak` 表处理、核验和重建工具各自独立，便于审计每一步输入、停止条件和输出。

```text
paydb-recovery-toolkit-20261110/
├── README.md
│   └── 恢复链、目录说明、核验结果、全部源码
├── SHA256SUMS
│   └── 包内逐文件完整性校验
├── 01_discovery/
│   ├── emergency_bastion_exec.py
│   │   └── 经新堡垒机执行受限只读命令
│   ├── emergency_database_recovery_audit.py
│   │   └── 数据库、复制状态和 binlog 盘点
│   ├── emergency_web_db_discovery.py
│   │   └── 从 Web 配置定位目标库并自动脱敏
│   └── emergency_backup_discovery.py
│       └── 备份机 SQL / XtraBackup / tar 盘点
├── 02_main_pitr/
│   ├── paydb_binlog_export.sh
│   │   └── DROP 前停止位导出与 DROP 门禁
│   └── paydb_main_restore.sh
│       └── 日备导入、GTID 清理、binlog 回放、计数核验
├── 03_bak_tables/
│   ├── paydb_backup_reader.service
│   │   └── 本地 socket、禁止网络的临时只读 MySQL
│   ├── paydb_bak_export_all.sh
│   │   └── 57 张 _bak 表 4 路并行协调导出
│   ├── paydb_bak_export_one.sh
│   │   └── 单表导出、压缩、SHA256、上传
│   └── paydb_bak_import_on_db1.sh
│       └── 下载、校验、事件保护、逐表导入、表名核对
├── 04_verify/
│   ├── paydb_verify.sql
│   │   └── 表数、核心行数、事件、CHECK TABLE
│   └── paydb_artifact_verify.sh
│       └── 某海外中转站 材料、gzip、61 项 SHA256 核验
└── 05_rebuild_docs/
    └── build_paydb_recovery_toolkit.py
        └── 一键重建文档与 ZIP
```

## 三、工具包与恢复材料核验

本次导入时实际检查了 Markdown 和 ZIP。原始 Markdown 的 SHA256 与归档记录一致；ZIP 的 SHA256 和字节数一致，压缩包 CRC 测试无错误。ZIP 内共 15 个文件，由 `SHA256SUMS`、README 和 13 个脚本组成；校验清单列出 14 个文件，全部通过，校验文件本身按惯例不计入自身清单。

| 核验项 | 实际结果 |
|---|---|
| ZIP 压缩完整性 | 通过，无 CRC 错误 |
| ZIP 内文件 | 15 个 |
| 脚本文件 | 13 个 |
| `SHA256SUMS` 条目 | 14 项 |
| 包内 SHA256 | 14/14 通过 |
| 明文凭据扫描 | 密码、Token、私钥、Access Key 均为 0 命中 |
| 支付业务数据 | 工具 ZIP 内为 0 |

| 附件 | SHA256 | 大小 |
|---|---|---:|
| Markdown 说明文档 | `c8b091077279a2c2ab8a18ac637d2b79a917a32d96e94f2a158912614b9d28ff` | 68,261 bytes |
| 完整工具包 ZIP | `94247f1432e7029ec76cb3a5a65bce50e1216a4b58f54c22722393b6f501f68e` | 49,896 bytes |

某海外中转站 恢复材料另行使用 `paydb_artifact_verify.sh` 核验。当前记录为 57 个 `_bak` 表 SQL 包、3 个 binlog 导出 SQL、1 个日备 tar 包，gzip 坏包 0，61 项 SHA256 全部通过，`.sql.gz` 合计 约 7.36 GiB。

## 四、恢复结论与完成状态

- 某支付平台 主库已通过 **备份节点 日备 + binlog PITR** 恢复到 DROP 前位置。
- 主恢复里程碑：2026-11-07 13:50:15 CST 完成；当时 `paydb` 152 张表，`user_account=约 55 万`、`user_profile=约 55 万`、`transaction_detail=约 118 万`。
- 57 张历史 `_bak` 表已从 2026-07-15 XtraBackup 快照导出并全部导入；2026-11-07 17:26:23 CST 完成，失败 0。
- `_bak` 导入后里程碑：`paydb` 187 张表，其中含 `_bak` 的基表 69 张；`transaction_detail=约 118 万`。
- 2026-11-10 04:33:45 CST 在线复核：187 张表、69 张 `_bak` 表、约 78,050.14 MB；`user_account=约 55 万`、`user_profile=约 55 万`、`transaction_detail=约 116 万`。这些是恢复后继续运行中的实时值，不是 11 月 7 日恢复快照值。
- 事件计划当前 8 个：7 个启用、1 个停用；`e_migrate_data` 原状态为停用，未擅自启用。
- `paydb2`、`paydb_20220101` 未纳入本次数据恢复，保持排期状态。

## 五、删除点与安全停止位置

```text
数据库：paydb
删除时间：2026-11-07 00:08:40 CST
binlog：/data/mysql/log/mysql-bin.000091
删除位置：693350583 / 693350648
导出停止位：693350648
DROP 检查：0
```

导出的恢复包使用 `mysqlbinlog --skip-gtids --database=paydb --stop-position=693350648`。
脚本在发布前还会再次扫描 `DROP DATABASE paydb`，命中即拒绝继续。

## 六、实际恢复链

### 1. 日备恢复

备份节点 上的日备为：

```text
/data/backup/paydb_backup_20261107_000001.tar.gz
大小：1,003,596,503 bytes
SHA256：d6135cd3b9014e14c2142d5c7f7342bde9116e94e06879fe44b692557cbe6bae
```

解包到 `/data/paydb-recovery-20261107/temp_20261107_000001/`，共 114 个表 SQL。
导入时清除源库 `SET @@GLOBAL.GTID_PURGED=...`，避免污染目标实例 GTID 状态。

### 2. binlog PITR

只提取 `paydb` 库在 `2026-11-07 00:00:00` 之后、DROP 完成位置之前的事件：

```text
paydb-binlog-before-drop-20261107.sql.gz
大小：3,250,451 bytes
SHA256：6600694357d161b298782de3ad4fbef36ef71a1527750e543f90b880036fe8ea
```

实际回放使用 `mysql --force`。日志中有 15 条 `ERROR 1062`（重复主键）
和 2 条 `ERROR 1032`（目标记录不存在），没有其他 SQL 错误；回放结束后
通过核心计数、对象数量和后续在线业务变化核验。`--force` 是本次实际口径，
重新演练时必须在隔离库先验证，不能直接覆盖在线 主节点。

### 3. 57 张 `_bak` 表

来源为 备份节点：

```text
/data/backup/2026-07-15_20-22-51
类型：XtraBackup 历史物理快照
```

使用 `innobackupex --apply-log --export` 后，以本地 socket、
`--skip-networking --skip-grant-tables` 启动临时 MySQL，避免任何网络访问。

备份中目标范围共 57 张表名含 `_bak` 的表：

```text
导出：2026-11-07 14:29:45 → 14:42:28 CST
并发：4 个 worker
导出：57/57，失败 0
上传：57/57，失败 0
导入：57/57，失败 0
目标表名缺失：0
```

导入脚本先暂停原有启用事件，逐表导入，再恢复事件状态。本次旧脚本曾因恢复 SQL
缺少 `USE paydb` 报 `ERROR 1046`；本工具包已修复该缺陷。

## 七、某海外中转站 恢复材料

目录：

```text
/data/recovery-staging
```

截至 2026-11-10 只读核验：

```text
57 个 paydb-bak-*.sql.gz
3 个 binlog 导出 SQL
1 个 paydb_backup_20261107_000001.tar.gz
gzip 坏包：0
SHA256 清单：61 项，全部通过
.sql.gz 合计：约 7.36 GiB（7.36 GiB）
```

恢复材料属于支付业务数据，**不放入本工具 ZIP，不发送到群**。群内只发送脚本、
说明、大小和哈希，不发送数据包本身。

## 八、安全边界

- 工具包不包含数据库密码、SSH 私钥、Telegram Token、云 API Key 或业务数据。
- 密码只从 root-only helper、受限环境文件或进程环境读取。
- 临时历史库必须使用 `--skip-networking`，只通过本地 socket 访问。
- 回放目标已有数据时，`paydb_main_restore.sh` 默认拒绝继续。
- 主库恢复脚本必须显式设置 `PAY_PLATFORM_CONFIRM_RESTORE=I_UNDERSTAND_PAY_PLATFORM_RESTORE`。
- 任何导出包发现 `DROP DATABASE paydb` 都必须停止，不得发布或回放。
- 回放完成不等于支付链路验收完成；仍需 DBA、开发和业务共同核验。

## 九、复现顺序

1. 用 `01_discovery` 工具确认源、目标、Web 配置、删除位和备份材料。
2. 用 `paydb_binlog_export.sh` 生成安全 binlog SQL。
3. 用 `paydb_main_restore.sh` 在隔离库或已批准目标库导入日备并回放。
4. 用 `paydb_verify.sql` 核对表数、核心行数、事件和 `CHECK TABLE`。
5. 用 `paydb_backup_reader.service` 启动本地只读历史实例。
6. 用 3 个 `_bak` 脚本完成导出、中转和导入。
7. 用 `paydb_artifact_verify.sh` 核验某海外中转站 恢复材料。
8. 将结果提交 DBA、开发和支付业务验收。

## 十、脚本与完整源码

以下内容为本次实际使用脚本，以及根据实际审计命令固化的可复现版本。
实际恢复时主链曾分步通过堡垒机执行；`paydb_main_restore.sh` 是这些步骤的
受控封装，增加确认门禁、GTID 清理、事件保护和非空库拒绝。


### 10.1 01_discovery 恢复发现与只读盘点

通过新堡垒机和 Web 配置定位 主节点、备份节点、备份、binlog 与恢复源；输出自动脱敏。

#### `01_discovery/emergency_bastion_exec.py`

**中文备注：** 通过新堡垒机在指定资产执行受限只读命令。

````python
#!/usr/bin/env python3
# ============================================================================
# 平台：某支付平台
# 恢复阶段：01_discovery
# 中文备注：通过新堡垒机在指定资产执行受限只读命令。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
"""Run a named read-only audit script through the replacement JumpServer."""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import os
import time
from pathlib import Path

import pexpect

from emergency_bastion_deep_audit import clean, parse_assets
from emergency_bastion_ioc_scan import spawn_jumpserver
from emergency_web_db_discovery import DISCOVERY_SCRIPT


PRESETS = {
    "web-db": (DISCOVERY_SCRIPT, "__WEB_DB_BEGIN__", "__WEB_DB_END__"),
}


def run_asset(name: str, script: str, start: str, end: str) -> dict[str, object]:
    result: dict[str, object] = {"asset": name, "status": "unknown"}
    child = spawn_jumpserver()
    try:
        child.send("/")
        child.expect("搜索:", timeout=10)
        child.send(name)
        child.send("\r")
        child.expect(name, timeout=15)
        time.sleep(0.8)
        child.send("\r")
        login = child.expect(
            [
                r"\[[^\]]+@[^\]]+\]\s*[#$] ",
                r"(?:Permission denied|Authentication failed|Connection refused|"
                r"没有可用的授权账号或终端协议|无法获取连接选项)",
                pexpect.TIMEOUT,
            ],
            timeout=35,
        )
        if login != 0:
            result["status"] = "login_failed" if login == 1 else "login_timeout"
            result["transcript"] = clean(child.before or "", name)
            return result
        payload = base64.b64encode(
            gzip.compress(script.encode("utf-8"), compresslevel=9)
        ).decode("ascii")
        child.sendline(f"echo {payload} | base64 -d | gzip -d | bash")
        state = child.expect(
            [end, pexpect.TIMEOUT],
            timeout=int(os.environ.get("某业务公司_BASTION_EXEC_TIMEOUT", "240")),
        )
        block = clean(child.before or "", name)
        if start in block:
            block = block.rsplit(start, 1)[-1]
        result["status"] = "scanned" if state == 0 else "scan_timeout"
        result["transcript"] = block.replace(end, "")
        return result
    finally:
        child.close(force=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", required=True)
    preset_or_command = parser.add_mutually_exclusive_group(required=True)
    preset_or_command.add_argument("--preset", choices=sorted(PRESETS))
    preset_or_command.add_argument(
        "--command-b64", help="base64-encoded read-only shell command"
    )
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset", action="append", default=[])
    args = parser.parse_args()
    if args.command_b64:
        script = base64.b64decode(args.command_b64).decode("utf-8")
        start, end = "__COMMAND_BEGIN__", "__COMMAND_END__"
        script = f"printf '{start}\\n'\n{script}\nprintf '{end}\\n'\n"
    else:
        script, start, end = PRESETS[args.preset]
    assets = parse_assets(Path(args.assets))
    if args.asset:
        selected = set(args.asset)
        assets = [item for item in assets if item[0] in selected]
    results: list[dict[str, object]] = []
    for name, ip in assets:
        print(name, flush=True)
        try:
            result = run_asset(name, script, start, end)
            result["ip"] = ip
        except Exception as exc:
            result = {
                "asset": name,
                "ip": ip,
                "status": "exception",
                "error": f"{type(exc).__name__}: {exc}",
            }
        results.append(result)
        Path(args.output).write_text(
            json.dumps({"assets": results}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(result["status"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
````

#### `01_discovery/emergency_database_recovery_audit.py`

**中文备注：** 批量盘点数据库目录、复制状态、binlog 和业务库时间。

````python
#!/usr/bin/env python3
# ============================================================================
# 平台：某支付平台
# 恢复阶段：01_discovery
# 中文备注：批量盘点数据库目录、复制状态、binlog 和业务库时间。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
"""Read-only MySQL recovery-point audit through the authorized JumpServer."""

from __future__ import annotations

import base64
import argparse
import json
import os
import time
from pathlib import Path

import pexpect

from emergency_bastion_ioc_scan import clean, spawn_jumpserver


TARGETS = [
    ("sample-node-01", "192.0.2.10"),
    ("sample-node-02", "192.0.2.11"),
    ("sample-node-03", "192.0.2.12"),
    ("sample-node-04", "192.0.2.13"),
    ("sample-node-05", "192.0.2.14"),
    ("sample-node-06", "192.0.2.15"),
    ("sample-node-07", "192.0.2.16"),
    ("sample-node-08", "192.0.2.17"),
    ("sample-node-09", "192.0.2.18"),
    ("sample-node-10", "192.0.2.19"),
    ("sample-node-11", "192.0.2.20"),
    ("sample-node-12", "192.0.2.21"),
    ("sample-node-13", "192.0.2.22"),
    ("sample-node-14", "192.0.2.23"),
    ("sample-node-15", "192.0.2.24"),
    ("sample-node-16", "192.0.2.25"),
    ("sample-node-17", "192.0.2.26"),
    ("sample-node-18", "192.0.2.27"),
    ("aws-us-newgpay-online-db", "192.0.2.28"),
    ("sample-node-19", "192.0.2.29"),
    ("sample-node-20", "192.0.2.30"),
    ("sample-node-21", "192.0.2.31"),
    ("sample-node-22", "192.0.2.32"),
    ("sample-node-23", "192.0.2.33"),
    ("sample-node-24", "192.0.2.34"),
    ("sample-node-25", "192.0.2.35"),
]

MYSQL_AUDIT_SCRIPT = r"""
set +e
printf '__DB_BEGIN__\n'
printf 'HOST='; hostname
printf 'IP='; hostname -I
printf 'MYSQL_DATA='; sudo -n ls /data/mysql/data 2>/dev/null | paste -sd, -
echo
printf 'MYSQL_SCRIPT='
for f in /root/mysql.sh /home/centos/mysql.sh; do sudo -n test -f "$f" && printf '%s,' "$f"; done
echo
if sudo -n test -f /root/mysql.sh; then
  printf '%s\n' \
    'SELECT @@server_id AS server_id, @@hostname AS hostname, @@read_only AS read_only, @@super_read_only AS super_read_only;' \
    'SHOW DATABASES;' \
    'SHOW MASTER STATUS;' \
    'SHOW SLAVE STATUS\G' \
    'SELECT table_schema, COUNT(*) AS tables_count FROM information_schema.tables WHERE table_schema NOT IN ("mysql","performance_schema","information_schema","sys") GROUP BY table_schema ORDER BY table_schema;' \
    'SELECT table_schema, MAX(update_time) AS latest_update_time FROM information_schema.tables WHERE table_schema NOT IN ("mysql","performance_schema","information_schema","sys") GROUP BY table_schema ORDER BY table_schema;' \
  | sudo -n env PATH=/data/mysql/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin bash /root/mysql.sh 2>&1
elif sudo -n test -f /home/centos/mysql.sh; then
  printf '%s\n' \
    'SELECT @@server_id AS server_id, @@hostname AS hostname, @@read_only AS read_only, @@super_read_only AS super_read_only;' \
    'SHOW DATABASES;' \
    'SHOW MASTER STATUS;' \
    'SHOW SLAVE STATUS\G' \
    'SELECT table_schema, COUNT(*) AS tables_count FROM information_schema.tables WHERE table_schema NOT IN ("mysql","performance_schema","information_schema","sys") GROUP BY table_schema ORDER BY table_schema;' \
    'SELECT table_schema, MAX(update_time) AS latest_update_time FROM information_schema.tables WHERE table_schema NOT IN ("mysql","performance_schema","information_schema","sys") GROUP BY table_schema ORDER BY table_schema;' \
  | sudo -n env PATH=/data/mysql/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin bash /home/centos/mysql.sh 2>&1
else
  echo MYSQL_HELPER_NOT_FOUND
fi
printf '__DB_END__\n'
"""


def scan(name: str, ip: str) -> dict[str, object]:
    result: dict[str, object] = {"asset": name, "ip": ip, "status": "unknown"}
    child = spawn_jumpserver()
    try:
        child.send("/")
        child.expect("搜索:", timeout=10)
        child.send(name)
        child.send("\r")
        child.expect(name, timeout=15)
        time.sleep(0.8)
        child.send("\r")
        index = child.expect(
            [
                r"\[[^\]]+@[^\]]+\]\s*[#$] ",
                r"(?:Permission denied|Authentication failed|Connection refused|"
                r"没有可用的授权账号或终端协议|无法获取连接选项)",
                pexpect.TIMEOUT,
            ],
            timeout=25,
        )
        if index != 0:
            result["status"] = "login_failed" if index == 1 else "login_timeout"
            result["transcript"] = clean(child.before or "", name)
            return result
        encoded = base64.b64encode(MYSQL_AUDIT_SCRIPT.encode()).decode("ascii")
        child.sendline(f"echo {encoded} | base64 -d | bash")
        index = child.expect(
            [r"__DB_END__", pexpect.TIMEOUT],
            timeout=45,
        )
        block = clean(child.before or "", name)
        if "__DB_BEGIN__" in block:
            block = block.rsplit("__DB_BEGIN__", 1)[-1]
        result["status"] = "scanned" if index == 0 else "scan_timeout"
        result["transcript"] = block
        return result
    finally:
        child.close(force=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument(
        "--output", default="/tmp/emergency-database-recovery-audit.json"
    )
    args = parser.parse_args()
    targets = TARGETS
    if args.only:
        selected = set(args.only)
        targets = [item for item in targets if item[0] in selected]
    output = Path(args.output)
    results = []
    for name, ip in targets:
        print(name, flush=True)
        try:
            result = scan(name, ip)
        except Exception as exc:
            result = {
                "asset": name,
                "ip": ip,
                "status": "exception",
                "error": f"{type(exc).__name__}: {exc}",
            }
        results.append(result)
        output.write_text(
            json.dumps({"assets": results}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(result["status"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
````

#### `01_discovery/emergency_web_db_discovery.py`

**中文备注：** 从 Web 发布目录定位 database.php，自动隐藏密码后再输出。

````python
#!/usr/bin/env python3
# ============================================================================
# 平台：某支付平台
# 恢复阶段：01_discovery
# 中文备注：从 Web 发布目录定位 database.php，自动隐藏密码后再输出。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
"""Discover database endpoints from web application configs.

Credentials are redacted in output. The legacy JumpServer credential remains
inside the legacy host process and is used only for the requested read.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from emergency_bastion_deep_audit import parse_assets


OLD_HOST = "192.0.2.36"
BUILD_HOST = "root@192.0.2.37"

DISCOVERY_SCRIPT = r"""
set +e
printf '__WEB_DB_BEGIN__\n'
printf 'HOST='; hostname
printf 'IP='; hostname -I
printf 'DATE='; date '+%F %T %Z'
printf 'NGINX_ROOTS='
sudo -n grep -RhE '^[[:space:]]*root[[:space:]]+[^;]+;' \
  /etc/nginx /www/server/panel/vhost /www/server/nginx/conf 2>/dev/null |
  sed -E 's#^[[:space:]]*root[[:space:]]+##; s#;[[:space:]]*$##' |
  sort -u | head -60 | paste -sd, -
echo
files=$(sudo -n timeout 20s find /www/wwwroot /data/wwwroot /data/release /home -maxdepth 6 \
  -type f -size -2M -newermt '2026-01-01' \
  \( -name '.env' -o -name '*.env' -o -name 'database.php' \
     -o -name 'database_release.php' -o -name 'settings.php' \) \
  ! -path '*/vendor/*' ! -path '*/vendor_pwa/*' ! -path '*/node_modules/*' \
  ! -path '*/.git/*' ! -path '*/.github/*' ! -path '*/.travis.yml' \
  -printf '%T@|%p\n' 2>/dev/null | sort -nr | cut -d'|' -f2- | head -25)
files=$(printf '%s\n' $files | grep -E '/(config|application|conf|settings)/|/\.env$|database' | head -25)
printf 'CONFIG_FILES=%s\n' "$files" | head -c 8000
echo
idx=0
for f in $files; do
  idx=$((idx+1))
  [ "$idx" -gt 25 ] && break
  printf 'FILE_%s=%s\n' "$idx" "$f"
  printf 'SHA_%s=' "$idx"; sudo -n sha256sum "$f" 2>/dev/null | awk '{print $1}'
  printf 'LINES_%s=' "$idx"
  sudo -n grep -aEin \
    'DB_HOST|DB_PORT|DB_NAME|DB_USER|DB_PASS|MYSQL_HOST|MYSQL_PORT|MYSQL_USER|MYSQL_PASS|database|hostname|username|password|redis_host|redis_port|redis_password|spring.datasource' \
    "$f" 2>/dev/null | head -40 |
    sed -E 's/(password|passwd|pass|pwd|secret|token|key)[^,;]*/\1=<REDACTED>/Ig' |
    paste -sd '|' -
  echo
done
printf '__WEB_DB_END__\n'
"""

REMOTE_RUNNER = r"""
import base64
import io
import sys
import django

django.setup()

import paramiko
from assets.models import SystemUser

target = "__IR_TARGET_IP__"
payload = base64.b64decode("__IR_SCRIPT_B64__")
last_error = ""

for name in ("centos-basic", "centos-yfb", "centos-DBA", "centos"):
    try:
        user = SystemUser.objects.get(name=name)
        kwargs = {
            "hostname": target,
            "port": 22,
            "username": user.username,
            "timeout": 15,
            "banner_timeout": 15,
            "auth_timeout": 15,
            "allow_agent": False,
            "look_for_keys": False,
        }
        if user.private_key:
            kwargs["pkey"] = paramiko.RSAKey.from_private_key(
                io.StringIO(user.private_key), password=user.password or None
            )
        elif user.password:
            kwargs["password"] = user.password
        else:
            continue
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(**kwargs)
        stdin, stdout, stderr = client.exec_command("bash -s", timeout=120)
        stdin.write(payload)
        stdin.channel.shutdown_write()
        sys.stdout.write(stdout.read().decode("utf-8", "replace"))
        sys.stdout.flush()
        sys.stderr.write(stderr.read().decode("utf-8", "replace"))
        client.close()
        raise SystemExit(0)
    except SystemExit:
        raise
    except Exception as exc:
        last_error = f"{name}:{type(exc).__name__}"

print("__CONNECT_FAILED__=" + last_error)
"""


def run_remote(name: str, ip: str, key: Path, timeout: int) -> tuple[int, str, str]:
    password = os.environ.get("BASTION_BOOTSTRAP_PASSWORD", "")
    if not password:
        raise RuntimeError("BASTION_BOOTSTRAP_PASSWORD is required")
    import base64
    encoded = base64.b64encode(DISCOVERY_SCRIPT.encode("utf-8")).decode("ascii")
    runner = REMOTE_RUNNER.replace("__IR_TARGET_IP__", ip).replace(
        "__IR_SCRIPT_B64__", encoded
    )
    proxy = (
        "sshpass -e ssh -o StrictHostKeyChecking=accept-new "
        f"-o ConnectTimeout=15 -W %h:%p {BUILD_HOST}"
    )
    env = os.environ.copy()
    env["SSHPASS"] = password
    proc = subprocess.run(
        [
            "ssh",
            "-i",
            str(key),
            "-o",
            "IdentitiesOnly=yes",
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=accept-new",
            "-o",
            "ConnectTimeout=15",
            "-o",
            f"ProxyCommand={proxy}",
            f"root@{OLD_HOST}",
            (
                "cd /opt/jumpserver/apps && "
                "LANG=en_US.utf8 LC_ALL=en_US.utf8 "
                "DJANGO_SETTINGS_MODULE=jumpserver.settings "
                "/opt/py3/bin/python -"
            ),
        ],
        input=runner,
        text=True,
        capture_output=True,
        env=env,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--key", default="/Users/operator/Downloads/jumpser-old.crash"
    )
    parser.add_argument("--web", action="append", default=[])
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    assets = parse_assets(Path(args.assets))
    if args.web:
        wanted = set(args.web)
        assets = [item for item in assets if item[0] in wanted]
    results: list[dict[str, object]] = []
    for name, ip in assets:
        print(name, flush=True)
        result: dict[str, object] = {"asset": name, "ip": ip, "status": "unknown"}
        try:
            rc, stdout, stderr = run_remote(name, ip, Path(args.key), args.timeout)
            if "__WEB_DB_END__" in stdout:
                result["status"] = "scanned"
                result["transcript"] = stdout.split("__WEB_DB_BEGIN__", 1)[-1].replace(
                    "__WEB_DB_END__", ""
                )
            else:
                result["status"] = "scan_failed" if rc else "scan_timeout"
                result["transcript"] = stdout[-5000:]
                result["error"] = stderr[-2000:]
        except Exception as exc:
            result["status"] = "exception"
            result["error"] = f"{type(exc).__name__}: {exc}"
        results.append(result)
        Path(args.output).write_text(
            json.dumps({"assets": results}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(result["status"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
````

#### `01_discovery/emergency_backup_discovery.py`

**中文备注：** 盘点备份机上的 SQL、xbstream、tar 包和备份脚本。

````python
#!/usr/bin/env python3
# ============================================================================
# 平台：某支付平台
# 恢复阶段：01_discovery
# 中文备注：盘点备份机上的 SQL、xbstream、tar 包和备份脚本。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
"""Discover recent database backup artifacts on authorized backup servers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from emergency_bastion_deep_audit import parse_assets
from emergency_bastion_exec import run_asset


BACKUP_SCRIPT = r"""
set +e
printf '__BACKUP_BEGIN__\n'
printf 'HOST='; hostname
printf 'DATE='; date '+%F %T %Z'
printf 'MOUNTS='; df -hT /data /backup /opt 2>/dev/null | tail -n +2 | paste -sd, -
echo
printf 'RECENT_FILES='
sudo -n timeout 35s find /data /backup /backups /opt -maxdepth 7 -type f \
  \( -iname '*.sql' -o -iname '*.sql.gz' -o -iname '*.sql.xz' -o -iname '*.sql.zst' \
     -o -iname '*.xb' -o -iname '*.xbstream' -o -iname '*.tar.gz' \
     -o -iname 'xtrabackup_checkpoints' -o -iname '*dump*' \) \
  -newermt '2026-01-01' -printf '%TY-%Tm-%Td|%TH:%TM|%u|%m|%s|%p;' 2>/dev/null |
  sort | tail -200 | paste -sd, -
echo
printf 'RECENT_DIRS='
sudo -n timeout 35s find /data /backup /backups /opt -maxdepth 5 -type d \
  \( -iname '*backup*' -o -iname '*dump*' -o -iname '*xtrabackup*' \) \
  -newermt '2026-01-01' -printf '%TY-%Tm-%Td|%TH:%TM|%u|%m|%p;' 2>/dev/null |
  sort | tail -100 | paste -sd, -
echo
printf 'LARGE_FILES='
sudo -n timeout 25s find /data /backup /backups -maxdepth 6 -type f -size +100M \
  -printf '%TY-%Tm-%Td|%TH:%TM|%u|%m|%s|%p;' 2>/dev/null |
  sort | tail -100 | paste -sd, -
echo
printf 'BACKUP_SCRIPTS='
sudo -n timeout 20s grep -RIlE 'mysqldump|xtrabackup|mariabackup|innobackupex|sql.gz' \
  /root /home /usr/local/bin /opt /data 2>/dev/null | head -100 | paste -sd, -
echo
printf '__BACKUP_END__\n'
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset", action="append", default=[])
    args = parser.parse_args()
    assets = parse_assets(Path(args.assets))
    if args.asset:
        selected = set(args.asset)
        assets = [item for item in assets if item[0] in selected]
    results: list[dict[str, object]] = []
    for name, ip in assets:
        print(name, flush=True)
        try:
            result = run_asset(
                name, BACKUP_SCRIPT, "__BACKUP_BEGIN__", "__BACKUP_END__"
            )
            result["ip"] = ip
        except Exception as exc:
            result = {
                "asset": name,
                "ip": ip,
                "status": "exception",
                "error": f"{type(exc).__name__}: {exc}",
            }
        results.append(result)
        Path(args.output).write_text(
            json.dumps({"assets": results}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(result["status"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
````

### 10.2 02_main_pitr 主库日备与 binlog PITR

恢复 某支付平台 主库：备份节点 日备 114 个表文件导入，再回放到 DROP 前位置。

#### `02_main_pitr/paydb_binlog_export.sh`

**中文备注：** 从 mysql-bin.000091 导出 paydb SQL，固定 DROP 前停止位并做 DROP 门禁。

````bash
#!/bin/bash
# ============================================================================
# 平台：某支付平台
# 恢复阶段：02_main_pitr
# 中文备注：从 mysql-bin.000091 导出 paydb SQL，固定 DROP 前停止位并做 DROP 门禁。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# ============================================================================
# 平台：某支付平台
# 恢复阶段：主库 PITR binlog 导出
# 中文备注：从 备份节点 的 mysql-bin.000091 导出 DROP 之前、仅属于 paydb 的 SQL。
# 安全说明：本文件不包含密码、Token 或私钥；输出包会先检查不得包含 DROP。
# ============================================================================
set -euo pipefail

mysqlbinlog_bin="${PAY_PLATFORM_MYSQLBINLOG_BIN:-/data/mysql/bin/mysqlbinlog}"
source_binlog="${PAY_PLATFORM_SOURCE_BINLOG:?PAY_PLATFORM_SOURCE_BINLOG is required}"
database="${PAY_PLATFORM_DATABASE:-paydb}"
start_datetime="${PAY_PLATFORM_START_DATETIME:?PAY_PLATFORM_START_DATETIME is required}"
stop_position="${PAY_PLATFORM_STOP_POSITION:?PAY_PLATFORM_STOP_POSITION is required}"
output="${PAY_PLATFORM_BINLOG_OUTPUT:?PAY_PLATFORM_BINLOG_OUTPUT is required}"

[[ -x "$mysqlbinlog_bin" ]] || {
  echo "MYSQLBINLOG_NOT_EXECUTABLE=$mysqlbinlog_bin" >&2
  exit 2
}
[[ -r "$source_binlog" ]] || {
  echo "SOURCE_BINLOG_NOT_READABLE=$source_binlog" >&2
  exit 3
}
[[ "$stop_position" =~ ^[0-9]+$ ]] || {
  echo "INVALID_STOP_POSITION=$stop_position" >&2
  exit 4
}

output_dir="$(dirname "$output")"
mkdir -p "$output_dir"
partial="${output}.part"
error_log="${output}.mysqlbinlog.err"
manifest="${output}.sha256"
rm -f "$partial"
trap 'rm -f "$partial"' EXIT

# --skip-gtids 避免在恢复目标上重新注入源库 GTID。
# --database 只保留 paydb；--stop-position 固定在 DROP 完成位置之前。
sudo -n "$mysqlbinlog_bin" \
  --skip-gtids \
  --database="$database" \
  --start-datetime="$start_datetime" \
  --stop-position="$stop_position" \
  "$source_binlog" 2>"$error_log" | gzip -9 >"$partial"

gzip -t "$partial"

# 安全门禁：即使停止位置写错，也拒绝发布包含 DROP DATABASE 的恢复包。
if gzip -dc "$partial" | grep -aEiq \
    "DROP[[:space:]]+DATABASE([[:space:]]|.*\`)$database"; then
  echo "DROP_EVENT_DETECTED=1 OUTPUT=$partial" >&2
  exit 25
fi

mv -f "$partial" "$output"
sha256="$(sha256sum "$output" | awk '{print $1}')"
size="$(stat -c %s "$output")"
printf '%s  %s\n' "$sha256" "$(basename "$output")" >"$manifest"

printf 'BINLOG_EXPORT=%s\n' "$output"
printf 'BINLOG_BYTES=%s\n' "$size"
printf 'BINLOG_SHA256=%s\n' "$sha256"
printf 'DROP_EVENT_DETECTED=0\n'
````

#### `02_main_pitr/paydb_main_restore.sh`

**中文备注：** 导入日备表 SQL、清理 GTID_PURGED、回放安全 binlog 并输出核心计数。

````bash
#!/bin/bash
# ============================================================================
# 平台：某支付平台
# 恢复阶段：02_main_pitr
# 中文备注：导入日备表 SQL、清理 GTID_PURGED、回放安全 binlog 并输出核心计数。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# ============================================================================
# 平台：某支付平台
# 恢复阶段：主库日备 + binlog PITR
# 中文备注：导入 备份节点 日备的 114 个表 SQL，再回放到 DROP 前位置。
# 安全说明：本文件不包含密码；必须显式确认，已有数据默认拒绝覆盖。
# ============================================================================
set -euo pipefail

database="${PAY_PLATFORM_RESTORE_DATABASE:-paydb}"
backup_tar="${PAY_PLATFORM_BACKUP_TAR:-/data/backup/paydb_backup_20261107_000001.tar.gz}"
restore_root="${PAY_PLATFORM_RESTORE_ROOT:-/data/paydb-recovery-20261107}"
table_dir="${PAY_PLATFORM_TABLE_SQL_DIR:-$restore_root/temp_20261107_000001}"
binlog_sql="${PAY_PLATFORM_BINLOG_SQL:?PAY_PLATFORM_BINLOG_SQL is required}"
mysql_helper="${PAY_PLATFORM_MYSQL_HELPER:-/root/mysql.sh}"
mysql_bin="${PAY_PLATFORM_MYSQL_BIN:-/data/mysql/bin/mysql}"
confirm="${PAY_PLATFORM_CONFIRM_RESTORE:-}"
allow_nonempty="${PAY_PLATFORM_ALLOW_NONEMPTY:-0}"
binlog_force="${PAY_PLATFORM_BINLOG_FORCE:-1}"

[[ "$confirm" == "I_UNDERSTAND_PAY_PLATFORM_RESTORE" ]] || {
  echo "Set PAY_PLATFORM_CONFIRM_RESTORE=I_UNDERSTAND_PAY_PLATFORM_RESTORE" >&2
  exit 2
}
[[ -x "$mysql_bin" ]] || {
  echo "MYSQL_NOT_EXECUTABLE=$mysql_bin" >&2
  exit 3
}
[[ -r "$binlog_sql" ]] || {
  echo "BINLOG_SQL_NOT_READABLE=$binlog_sql" >&2
  exit 4
}

# 密码只从 root-only mysql.sh 读取，不输出到终端或日志。
mysql_password="$(
  awk '{
    for (i = 1; i <= NF; i++) {
      if ($i ~ /^-p/) {
        value = substr($i, 3)
        if (value != "") {
          print value
          exit
        }
      }
    }
  }' "$mysql_helper"
)"
case "$mysql_password" in
  \'*\'|\"*\")
    mysql_password="${mysql_password:1:${#mysql_password}-2}"
    ;;
esac
[[ -n "$mysql_password" ]] || {
  echo "MYSQL_PASSWORD_PARSE_FAILED" >&2
  exit 5
}

mysql_run() {
  MYSQL_PWD="$mysql_password" "$mysql_bin" \
    --socket=/tmp/mysql.sock -uroot --connect-timeout=8 "$@"
}

# 若日备尚未解包，则先解到独立恢复目录。
if [[ ! -d "$table_dir" || -z "$(find "$table_dir" -maxdepth 1 -type f -name '*.sql' -print -quit)" ]]; then
  [[ -r "$backup_tar" ]] || {
    echo "BACKUP_TAR_NOT_READABLE=$backup_tar" >&2
    exit 6
  }
  mkdir -p "$restore_root"
  tar -xzf "$backup_tar" -C "$restore_root"
fi

mapfile -t table_files < <(find "$table_dir" -maxdepth 1 -type f -name '*.sql' | sort)
[[ "${#table_files[@]}" -gt 0 ]] || {
  echo "NO_TABLE_SQL=$table_dir" >&2
  exit 7
}

mysql_run <<SQL
CREATE DATABASE IF NOT EXISTS \`$database\` DEFAULT CHARACTER SET latin1;
SQL

existing_tables="$(mysql_run --batch --skip-column-names -e \
  "SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA='$database'")"
if [[ "$existing_tables" -gt 0 && "$allow_nonempty" != "1" ]]; then
  echo "REFUSE_NONEMPTY_DATABASE=$database TABLES=$existing_tables" >&2
  echo "Set PAY_PLATFORM_ALLOW_NONEMPTY=1 only after a verified backup." >&2
  exit 8
fi

log_dir="${PAY_PLATFORM_RESTORE_LOG_DIR:-/tmp}"
log="$log_dir/paydb-main-restore-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "$log_dir"
exec > >(tee -a "$log") 2>&1

# 全局事件调度器在导入期间关闭，避免日备中的事件在数据未完整时触发。
event_scheduler_original="$(mysql_run --batch --skip-column-names -e \
  'SELECT @@GLOBAL.event_scheduler')"
restore_event_scheduler() {
  mysql_run -e \
    "SET GLOBAL event_scheduler=$event_scheduler_original" >/dev/null 2>&1 || true
}
trap restore_event_scheduler EXIT
mysql_run -e 'SET GLOBAL event_scheduler=OFF'

echo "RESTORE_START=$(date '+%F %T %Z')"
echo "DATABASE=$database"
echo "TABLE_DIR=$table_dir TABLE_FILES=${#table_files[@]}"

index=0
for file in "${table_files[@]}"; do
  index=$((index + 1))
  echo "TABLE_IMPORT_START=$index/$(
    echo "${#table_files[@]}"
  ) $(basename "$file")"

  # 日备 SQL 带源库 GTID_PURGED；清掉该语句，避免污染恢复实例的 GTID 状态。
  {
    printf 'SET SESSION sql_log_bin=0;\nSET SESSION foreign_key_checks=0;\n'
    awk '
      BEGIN { skip = 0 }
      /^SET @@GLOBAL\.GTID_PURGED=/ { skip = 1 }
      skip == 0 { print }
      skip == 1 && /;$/ { skip = 0 }
    ' "$file"
  } | mysql_run "$database"
  echo "TABLE_IMPORT_RC=0 TABLE=$(basename "$file")"
done

echo "TABLE_IMPORT_FINISH=$index $(date '+%F %T %Z')"

# 发布前再次检查 SQL 包里没有 DROP DATABASE。
gzip -t "$binlog_sql"
if gzip -dc "$binlog_sql" 2>/dev/null | grep -aEiq \
    "DROP[[:space:]]+DATABASE([[:space:]]|.*\`)$database"; then
  echo "DROP_EVENT_DETECTED=1" >&2
  exit 25
fi

mysql_args=(--force)
if [[ "$binlog_force" != "1" ]]; then
  mysql_args=()
fi

echo "BINLOG_REPLAY_START=$(date '+%F %T %Z')"
gzip -dc "$binlog_sql" | mysql_run "${mysql_args[@]}" "$database"
echo "BINLOG_REPLAY_RC=0 FINISH=$(date '+%F %T %Z')"

# 输出核心计数供恢复人员立即比对；完整核验继续执行 paydb_verify.sql。
mysql_run --table "$database" -e "
SELECT NOW() AS checked_at, @@hostname AS mysql_host;
SELECT COUNT(*) AS total_tables FROM information_schema.TABLES
 WHERE TABLE_SCHEMA=DATABASE();
SELECT COUNT(*) AS bak_tables FROM information_schema.TABLES
 WHERE TABLE_SCHEMA=DATABASE() AND LOWER(TABLE_NAME) LIKE '%\\_bak%';
SELECT
 (SELECT COUNT(*) FROM user_account) AS user_account_rows,
 (SELECT COUNT(*) FROM user_profile) AS user_profile_rows,
 (SELECT COUNT(*) FROM transaction_detail) AS transaction_detail_rows;
SELECT COUNT(*) AS events_total,
       SUM(STATUS='ENABLED') AS events_enabled,
       SUM(STATUS='DISABLED') AS events_disabled
  FROM information_schema.EVENTS WHERE EVENT_SCHEMA=DATABASE();
"

restore_event_scheduler
trap - EXIT
echo "RESTORE_FINISH=$(date '+%F %T %Z')"
````

### 10.3 03_bak_tables 历史 _bak 表隔离导出与导入

从 2026-07-15 XtraBackup 隔离快照导出 57 张历史 _bak 表，再导入 主节点。

#### `03_bak_tables/paydb_backup_reader.service`

**中文备注：** 仅本地 socket、skip-networking 的临时只读 MySQL 实例定义。

````ini
# ============================================================================
# 平台：某支付平台
# 恢复阶段：03_bak_tables
# 中文备注：仅本地 socket、skip-networking 的临时只读 MySQL 实例定义。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# ============================================================================
# 平台：某支付平台
# 恢复阶段：2026-07-15 XtraBackup 隔离只读实例
# 中文备注：仅通过本地 socket 启动 skip-grant 临时 MySQL，供导出 57 张 _bak 表。
# 安全说明：--skip-networking 禁止网络访问；不修改主业务 MySQL。
# ============================================================================
[Unit]
Description=某支付平台 recovery-only MySQL reader for July XtraBackup
After=network.target
ConditionPathIsDirectory=/data/backup/2026-07-15_20-22-51

[Service]
Type=simple
User=mysql
Group=mysql
ExecStart=/data/mysql/bin/mysqld --no-defaults --basedir=/data/mysql --datadir=/data/backup/2026-07-15_20-22-51 --plugin-dir=/data/mysql/lib/plugin --user=mysql --socket=/tmp/mysql3307.sock --pid-file=/tmp/mysql3307.pid --skip-networking --skip-grant-tables --skip-log-bin --innodb-buffer-pool-size=2G --log-error=/tmp/mysql3307.err
Restart=no

[Install]
WantedBy=multi-user.target
````

#### `03_bak_tables/paydb_bak_export_all.sh`

**中文备注：** 4 路并发协调 57 张 _bak 表导出。

````bash
#!/bin/bash
# ============================================================================
# 平台：某支付平台
# 恢复阶段：03_bak_tables
# 中文备注：4 路并发协调 57 张 _bak 表导出。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# ============================================================================
# 平台：某支付平台
# 恢复阶段：57 张历史 _bak 表导出
# 中文备注：按表清单启动 4 路并发导出，每张表交给一个独立 worker。
# 安全说明：本文件不包含密码、Token 或私钥；MySQL 只在目标机本地受限环境读取。
# ============================================================================
set -uo pipefail

# 所有路径都允许通过环境变量覆盖，便于在故障机上复现而不修改脚本。
root="${PAY_PLATFORM_BAK_ROOT:-/data/paydb-bak-work}"
tables_file="${1:-${root}/paydb-bak-tables.txt}"
export_dir="${EXPORT_DIR:-${root}/exports-20261107-v2}"
log_dir="${LOG_DIR:-${root}/logs-20261107-v2}"
worker="${WORKER_SCRIPT:-/usr/local/sbin/paydb_bak_export_one.sh}"
parallel="${PARALLEL:-4}"

# 先验证输入，避免 xargs 在无表清单时静默成功。
[[ -s "$tables_file" ]] || {
  echo "TABLE_LIST_MISSING=$tables_file" >&2
  exit 2
}
[[ -x "$worker" ]] || {
  echo "WORKER_NOT_EXECUTABLE=$worker" >&2
  exit 3
}

mkdir -p "$export_dir" "$log_dir"
printf 'COORDINATOR_START=%s\n' "$(date '+%F %T %Z')" \
  | tee "${log_dir}/coordinator.log"
printf 'TABLES=%s PARALLEL=%s\n' "$(wc -l < "$tables_file")" "$parallel" \
  | tee -a "${log_dir}/coordinator.log"

# 每行是一张表；-P 控制并发，-n 1 保证 worker 一次只处理一张表。
xargs -r -P "$parallel" -n 1 "$worker" <"$tables_file"
rc=$?
printf 'COORDINATOR_RC=%s\n' "$rc" | tee -a "${log_dir}/coordinator.log"
printf 'COORDINATOR_FINISH=%s\n' "$(date '+%F %T %Z')" \
  | tee -a "${log_dir}/coordinator.log"
exit "$rc"
````

#### `03_bak_tables/paydb_bak_export_one.sh`

**中文备注：** 单表导出、压缩、SHA256 记录和上传中转机。

````bash
#!/bin/bash
# ============================================================================
# 平台：某支付平台
# 恢复阶段：03_bak_tables
# 中文备注：单表导出、压缩、SHA256 记录和上传中转机。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# ============================================================================
# 平台：某支付平台
# 恢复阶段：57 张历史 _bak 表单表导出
# 中文备注：从隔离只读 MySQL 导出单表，压缩、校验后传到宝塔中转目录。
# 安全说明：本文件不包含密码、Token 或私钥；只使用本地 socket 和受限传输密钥。
# ============================================================================
set -uo pipefail

table="${1:?usage: paydb_bak_export_one.sh TABLE}"
export_dir="${EXPORT_DIR:-/data/paydb-bak-work/exports-20261107-v2}"
log_dir="${LOG_DIR:-/data/paydb-bak-work/logs-20261107-v2}"
mysql_bin="${MYSQL_BIN:-/data/mysql/bin/mysqldump}"
socket="${MYSQL_SOCKET:-/tmp/mysql3307.sock}"
transfer_key="${TRANSFER_KEY:-/tmp/.bizops-transfer-key}"
transfer_target="${TRANSFER_TARGET:-root@192.0.2.38:/root/vendor_a-zips/}"

# 只保留安全文件名，避免表名中的特殊字符影响本地路径。
safe="$(printf '%s' "$table" | tr -c 'A-Za-z0-9_.-' '_')"
final="${export_dir}/paydb-bak-${safe}.sql.gz"
partial="${final}.part"
failed="${export_dir}/paydb-bak-${safe}.sql.gz.failed"
log="${log_dir}/paydb-bak-${safe}.log"

mkdir -p "$export_dir" "$log_dir"
# 中断或失败时不留下可被误认为完整包的 .part 文件。
rm -f "$partial"
trap 'rm -f "$partial"' EXIT

{
  printf 'TABLE_START=%s %s\n' "$table" "$(date '+%F %T %Z')"
  printf 'EXPORT_TARGET=%s\n' "$final"
} | tee "$log"

set -o pipefail
# 隔离实例使用 skip-grant-tables 并以本地 socket 只读运行；
# --single-transaction 与 --quick 避免长时间锁表和大内存占用。
sudo -n "$mysql_bin" \
  --socket="$socket" \
  -uroot \
  --single-transaction \
  --quick \
  --skip-lock-tables \
  --hex-blob \
  --set-gtid-purged=OFF \
  --no-create-db \
  paydb "$table" | gzip -1 >"$partial"
rc=$?
printf 'DUMP_RC=%s\n' "$rc" >>"$log"

if [[ "$rc" -ne 0 || ! -s "$partial" ]]; then
  mv -f "$partial" "$failed" 2>/dev/null || true
  printf 'TABLE_FAIL=%s %s\n' "$table" "$(date '+%F %T %Z')" >>"$log"
  exit "$rc"
fi

mv -f "$partial" "$final"
# 大小和 SHA256 同时落日志，供中转机、目标机逐项比对。
size="$(stat -c %s "$final")"
sha="$(sha256sum "$final" | awk '{print $1}')"
printf 'EXPORT_BYTES=%s\nEXPORT_SHA256=%s\n' "$size" "$sha" >>"$log"

# 传输密钥权限由 root/受控账号维护，脚本只检查文件非空。
if [[ -s "$transfer_key" ]]; then
  timeout 1800 scp -q \
    -i "$transfer_key" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$final" "$transfer_target"
  scp_rc=$?
else
  scp_rc=127
fi
printf 'SCP_RC=%s\n' "$scp_rc" >>"$log"
printf 'TABLE_FINISH=%s %s\n' "$table" "$(date '+%F %T %Z')" >>"$log"

# SCP 失败时向协调器返回非零，整批任务会标记失败。
[[ "$scp_rc" -eq 0 ]]
````

#### `03_bak_tables/paydb_bak_import_on_db1.sh`

**中文备注：** 下载、gzip 校验、暂停事件、逐表导入并核对 57 个表名。

````bash
#!/bin/bash
# ============================================================================
# 平台：某支付平台
# 恢复阶段：03_bak_tables
# 中文备注：下载、gzip 校验、暂停事件、逐表导入并核对 57 个表名。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# ============================================================================
# 平台：某支付平台
# 恢复阶段：57 张历史 _bak 表导入 主节点
# 中文备注：下载、解压前校验、临时关闭事件和约束、逐表导入并核对目标表名。
# 安全说明：本文件不包含密码、Token 或私钥；MySQL 密码只从 root-only helper 读取。
# ============================================================================
set -uo pipefail

source_host="${PAY_PLATFORM_BAK_SOURCE_HOST:-root@192.0.2.38}"
source_dir="${PAY_PLATFORM_BAK_SOURCE_DIR:-/root/vendor_a-zips}"
work_dir="${PAY_PLATFORM_BAK_WORK_DIR:-/data/paydb-bak-restore}"
key="${PAY_PLATFORM_BAK_TRANSFER_KEY:-/tmp/.bizops-transfer-key}"
mysql_helper="${PAY_PLATFORM_MYSQL_HELPER:-/root/mysql.sh}"
database="${PAY_PLATFORM_DATABASE:-paydb}"
expected="${PAY_PLATFORM_BAK_EXPECTED:-57}"
mysql_bin="${PAY_PLATFORM_MYSQL_BIN:-/data/mysql/bin/mysql}"

# 兼容历史 mysql.sh 中 -pPASSWORD、-p 'PASSWORD' 和 -p "PASSWORD" 三种写法。
# 密码只保存在当前进程变量中，不写入日志。
mysql_password="$(
  awk '{
    for (i = 1; i <= NF; i++) {
      if ($i ~ /^-p/) {
        value = substr($i, 3)
        if (value != "") {
          print value
          exit
        }
      }
    }
  }' "$mysql_helper"
)"
case "$mysql_password" in
  \'*\'|\"*\")
    mysql_password="${mysql_password:1:${#mysql_password}-2}"
    ;;
esac
[[ -n "$mysql_password" ]] || {
  echo "MYSQL_PASSWORD_PARSE_FAILED"
  exit 23
}

mysql_run() {
  MYSQL_PWD="$mysql_password" "$mysql_bin" -uroot --connect-timeout=8 \
    --batch --skip-column-names "$@"
}

# 下载目录可复用；日志保留完整执行轨迹。
mkdir -p "$work_dir/download" "$work_dir/logs"
log="$work_dir/logs/import-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$log") 2>&1

events_enable="$work_dir/events-enable.sql"
events_disable="$work_dir/events-disable.sql"
events_restore_done=0
restore_events() {
  [[ "$events_restore_done" -eq 0 ]] || return 0
  events_restore_done=1
  if [[ -s "$events_enable" ]]; then
    echo "RESTORE_EVENTS_BEGIN $(date '+%F %T %Z')"
    if mysql_run <"$events_enable"; then
      echo "RESTORE_EVENTS_RC=0"
      return 0
    fi
    rc=$?
    echo "RESTORE_EVENTS_RC=$rc"
    return "$rc"
  fi
  return 0
}
# 任何中途失败都尝试恢复导入前已启用的事件。
trap 'restore_events || true' EXIT

echo "SYNC_START=$(date '+%F %T %Z')"
existing="$(find "$work_dir/download" -maxdepth 1 -type f -name 'paydb-bak-*.sql.gz' | wc -l)"
if [[ "$existing" -eq "$expected" ]]; then
  sync_rc=0
  echo "SYNC_SKIPPED_EXISTING=$existing"
else
  scp -q -i "$key" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$source_host:$source_dir/paydb-bak-*.sql.gz" \
    "$work_dir/download/"
  sync_rc=$?
fi
echo "SYNC_RC=$sync_rc"
[[ "$sync_rc" -eq 0 ]] || exit "$sync_rc"

mapfile -t files < <(find "$work_dir/download" -maxdepth 1 -type f -name 'paydb-bak-*.sql.gz' | sort)
echo "SYNC_FILES=${#files[@]}"
[[ "${#files[@]}" -eq "$expected" ]] || exit 20

# 先全量做 gzip 完整性检查，任何坏包都不得进入写库阶段。
for file in "${files[@]}"; do
  if ! gzip -t "$file"; then
    echo "GZIP_INVALID=$file"
    exit 21
  fi
done
echo "GZIP_VERIFY=ok"

# 记录导入前处于 ENABLED 的事件；导入期间逐条 DISABLE。
# 生成的文件必须自带 USE，否则退出时恢复会在“No database selected”处失败。
printf "%s\n" "
USE \`$database\`;
SELECT CONCAT('USE \`$database\`; ALTER EVENT \`', EVENT_NAME, '\` ENABLE;')
FROM information_schema.EVENTS
WHERE EVENT_SCHEMA='$database' AND STATUS='ENABLED';
" | mysql_run >"$events_enable"
printf "%s\n" "
USE \`$database\`;
SELECT CONCAT('USE \`$database\`; ALTER EVENT \`', EVENT_NAME, '\` DISABLE;')
FROM information_schema.EVENTS
WHERE EVENT_SCHEMA='$database' AND STATUS='ENABLED';
" | mysql_run >"$events_disable"
echo "EVENTS_TO_RESTORE=$(wc -l < "$events_enable")"
if mysql_run <"$events_disable"; then
  echo "EVENTS_DISABLED_RC=0"
else
  echo "EVENTS_DISABLED_RC=$?"
  exit 24
fi

# 每张表都在独立事务上下文中执行，并临时关闭外键检查。
# 单表失败立即停止，不把后续表继续写入造成难以判断的半完成状态。
for file in "${files[@]}"; do
  base="$(basename "$file" .sql.gz)"
  echo "TABLE_IMPORT_START=$base $(date '+%F %T %Z')"
  {
    printf 'USE `%s`;\nSET FOREIGN_KEY_CHECKS=0;\n' "$database"
    gzip -dc "$file"
    printf '\nSET FOREIGN_KEY_CHECKS=1;\n'
  } | mysql_run
  rc=$?
  echo "TABLE_IMPORT_RC=$rc TABLE=$base"
  [[ "$rc" -eq 0 ]] || exit "$rc"
done

echo "TABLE_DATA_IMPORT_DONE=$(date '+%F %T %Z')"
# 不依赖导入日志，直接到 information_schema 验证 57 个目标表名都存在。
verified=0
missing=0
for file in "${files[@]}"; do
  base="$(basename "$file" .sql.gz)"
  table="${base#paydb-bak-}"
  exists="$(printf "%s\n" "
SELECT COUNT(*)
FROM information_schema.TABLES
WHERE TABLE_SCHEMA='$database' AND TABLE_NAME='$table';
" | mysql_run)"
  if [[ "$exists" == "1" ]]; then
    verified=$((verified + 1))
  else
    echo "TABLE_MISSING=$table"
    missing=$((missing + 1))
  fi
done
echo "EXPECTED_TABLES_PRESENT=$verified/$expected"
[[ "$missing" -eq 0 ]] || exit 22

restore_events
restore_rc=$?
trap - EXIT
[[ "$restore_rc" -eq 0 ]] || exit "$restore_rc"

echo "IMPORT_FINISH=$(date '+%F %T %Z')"
exit 0
````

### 10.4 04_verify 在线核验与恢复材料校验

恢复后只读核验表数、历史表数、核心行数、事件状态和所有恢复材料。

#### `04_verify/paydb_verify.sql`

**中文备注：** 在线数据库核验 SQL；只执行 SELECT 和 CHECK TABLE。

````sql
-- 平台：某支付平台
-- 恢复阶段：04_verify
-- 中文备注：在线数据库核验 SQL；只执行 SELECT 和 CHECK TABLE。
-- 安全说明：本文件不包含密码、Token 或私钥。
-- ============================================================================
-- 平台：某支付平台
-- 恢复阶段：主库与 57 张 _bak 表恢复后核验
-- 中文备注：核对表数、历史表数、核心行数、事件状态和数据时间。
-- 安全说明：本文件只执行 SELECT 与 CHECK TABLE，不修改业务数据。
-- ============================================================================

SELECT
  NOW() AS checked_at,
  @@hostname AS mysql_host,
  @@version AS mysql_version,
  CURRENT_USER() AS mysql_user;

SELECT
  COUNT(*) AS total_tables,
  SUM(TABLE_TYPE = 'BASE TABLE') AS base_tables,
  SUM(TABLE_TYPE = 'VIEW') AS views,
  ROUND(COALESCE(SUM(DATA_LENGTH + INDEX_LENGTH), 0) / 1024 / 1024, 2)
    AS size_mb,
  COALESCE(SUM(TABLE_ROWS), 0) AS innodb_estimated_rows
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'paydb';

SELECT
  COUNT(*) AS bak_tables
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'paydb'
  AND TABLE_TYPE = 'BASE TABLE'
  AND LOWER(TABLE_NAME) LIKE '%\_bak%';

SELECT
  (SELECT COUNT(*) FROM user_account) AS user_account_rows,
  (SELECT COUNT(*) FROM user_profile) AS user_profile_rows,
  (SELECT COUNT(*) FROM transaction_detail) AS transaction_detail_rows;

SELECT
  EVENT_NAME,
  STATUS,
  INTERVAL_VALUE,
  INTERVAL_FIELD
FROM information_schema.EVENTS
WHERE EVENT_SCHEMA = 'paydb'
ORDER BY EVENT_NAME;

SELECT
  TABLE_NAME,
  COALESCE(DATE_FORMAT(UPDATE_TIME, '%Y-%m-%d %H:%i:%s'), 'NULL')
    AS latest_update_time
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'paydb'
  AND TABLE_TYPE = 'BASE TABLE'
ORDER BY UPDATE_TIME DESC, TABLE_NAME
LIMIT 20;

CHECK TABLE paydb.user_account, paydb.user_profile, paydb.transaction_detail;
````

#### `04_verify/paydb_artifact_verify.sh`

**中文备注：** 核验某海外中转站 上 57 个 _bak 包、gzip 完整性和 61 项 SHA256 清单。

````bash
#!/bin/bash
# ============================================================================
# 平台：某支付平台
# 恢复阶段：04_verify
# 中文备注：核验某海外中转站 上 57 个 _bak 包、gzip 完整性和 61 项 SHA256 清单。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# ============================================================================
# 平台：某支付平台
# 恢复阶段：某海外中转站 恢复材料完整性核验
# 中文备注：核对 57 个 _bak 包、压缩完整性、SHA256 清单和证据包数量。
# 安全说明：本文件只读校验，不删除、不移动、不导入任何业务数据。
# ============================================================================
set -euo pipefail

artifact_dir="${PAY_PLATFORM_ARTIFACT_DIR:-/data/recovery-staging}"
manifest="${PAY_PLATFORM_ARTIFACT_MANIFEST:-$artifact_dir/paydb-target.sha256}"
expected_bak="${PAY_PLATFORM_EXPECTED_BAK:-57}"

cd "$artifact_dir"

bak_files="$(find . -maxdepth 1 -type f -name 'paydb-bak-*.sql.gz' | wc -l)"
partial_files="$(find . -maxdepth 1 -type f -name '*.part' | wc -l)"
failed_files="$(find . -maxdepth 1 -type f -name '*.failed' | wc -l)"

echo "ARTIFACT_DIR=$artifact_dir"
echo "BAK_FILES=$bak_files EXPECTED=$expected_bak"
echo "PARTIAL_FILES=$partial_files"
echo "FAILED_FILES=$failed_files"

[[ "$bak_files" -eq "$expected_bak" ]]
[[ "$partial_files" -eq 0 ]]
[[ "$failed_files" -eq 0 ]]

bad_gzip=0
for file in paydb-bak-*.sql.gz; do
  if ! gzip -t "$file"; then
    echo "GZIP_INVALID=$file"
    bad_gzip=$((bad_gzip + 1))
  fi
done
echo "GZIP_BAD=$bad_gzip"
[[ "$bad_gzip" -eq 0 ]]

[[ -s "$manifest" ]]
sha256sum -c "$manifest"

echo "MANIFEST_ENTRIES=$(wc -l < "$manifest")"
echo "ARTIFACT_VERIFY=OK"
````

### 10.5 05_rebuild_docs 工具包重建

一键重建本说明、分类目录、SHA256 清单和可发群 ZIP。

#### `05_rebuild_docs/build_paydb_recovery_toolkit.py`

**中文备注：** 某支付平台 恢复工具包构建器。

````python
#!/usr/bin/env python3
# ============================================================================
# 平台：某支付平台
# 恢复阶段：05_rebuild_docs
# 中文备注：某支付平台 恢复工具包构建器。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
"""生成 某支付平台 数据库恢复脚本与工具包。

输出：
1. 中文 Markdown 总说明，含目录树、恢复链、核验结果和全部脚本源码；
2. 按阶段分类的脚本副本；
3. SHA256SUMS；
4. 可发群的 zip 压缩包。

实际业务数据库导出包、binlog SQL 和 57 张 _bak 表压缩包不放入本工具包，
避免把支付业务数据发到群聊。
"""

from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261110"
OUT_DIR = ROOT / "deliverables" / f"paydb-recovery-toolkit-{STAMP}"
DOC_NAME = "某支付平台数据库恢复脚本与工具说明.md"
DOC_PATH = (
    ROOT
    / "docs"
    / "history"
    / f"2026-11-10-0445-【恢复工具】{DOC_NAME}"
)


GROUPS = [
    (
        "01_discovery",
        "通过新堡垒机和 Web 配置定位 主节点、备份节点、备份、binlog 与恢复源；输出自动脱敏。",
        [
            (
                "emergency_bastion_exec.py",
                "通过新堡垒机在指定资产执行受限只读命令。",
            ),
            (
                "emergency_database_recovery_audit.py",
                "批量盘点数据库目录、复制状态、binlog 和业务库时间。",
            ),
            (
                "emergency_web_db_discovery.py",
                "从 Web 发布目录定位 database.php，自动隐藏密码后再输出。",
            ),
            (
                "emergency_backup_discovery.py",
                "盘点备份机上的 SQL、xbstream、tar 包和备份脚本。",
            ),
        ],
    ),
    (
        "02_main_pitr",
        "恢复 某支付平台 主库：备份节点 日备 114 个表文件导入，再回放到 DROP 前位置。",
        [
            (
                "paydb_binlog_export.sh",
                "从 mysql-bin.000091 导出 paydb SQL，固定 DROP 前停止位并做 DROP 门禁。",
            ),
            (
                "paydb_main_restore.sh",
                "导入日备表 SQL、清理 GTID_PURGED、回放安全 binlog 并输出核心计数。",
            ),
        ],
    ),
    (
        "03_bak_tables",
        "从 2026-07-15 XtraBackup 隔离快照导出 57 张历史 _bak 表，再导入 主节点。",
        [
            (
                "paydb_backup_reader.service",
                "仅本地 socket、skip-networking 的临时只读 MySQL 实例定义。",
            ),
            (
                "paydb_bak_export_all.sh",
                "4 路并发协调 57 张 _bak 表导出。",
            ),
            (
                "paydb_bak_export_one.sh",
                "单表导出、压缩、SHA256 记录和上传中转机。",
            ),
            (
                "paydb_bak_import_on_db1.sh",
                "下载、gzip 校验、暂停事件、逐表导入并核对 57 个表名。",
            ),
        ],
    ),
    (
        "04_verify",
        "恢复后只读核验表数、历史表数、核心行数、事件状态和所有恢复材料。",
        [
            (
                "paydb_verify.sql",
                "在线数据库核验 SQL；只执行 SELECT 和 CHECK TABLE。",
            ),
            (
                "paydb_artifact_verify.sh",
                "核验某海外中转站 上 57 个 _bak 包、gzip 完整性和 61 项 SHA256 清单。",
            ),
        ],
    ),
    (
        "05_rebuild_docs",
        "一键重建本说明、分类目录、SHA256 清单和可发群 ZIP。",
        [
            (
                "build_paydb_recovery_toolkit.py",
                "某支付平台 恢复工具包构建器。",
            ),
        ],
    ),
]


def read_source(name: str) -> str:
    path = ROOT / "scripts" / name
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def add_chinese_header(name: str, stage: str, note: str, source: str) -> str:
    if name.endswith(".sql"):
        header = [
            "-- 平台：某支付平台",
            f"-- 恢复阶段：{stage}",
            f"-- 中文备注：{note}",
            "-- 安全说明：本文件不包含密码、Token 或私钥。",
            "",
        ]
        return "\n".join(header) + source

    header = [
        "# ============================================================================",
        "# 平台：某支付平台",
        f"# 恢复阶段：{stage}",
        f"# 中文备注：{note}",
        "# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。",
        "# ============================================================================",
        "",
    ]
    shebang, separator, body = source.partition("\n")
    if separator and shebang.startswith("#!"):
        return shebang + "\n" + "\n".join(header) + body.lstrip("\n")
    return "\n".join(header) + source


def tree_lines() -> list[str]:
    lines = [
        f"paydb-recovery-toolkit-{STAMP}/",
        "├── README.md",
        "├── SHA256SUMS",
    ]
    for group, _, files in GROUPS:
        lines.append(f"├── {group}/")
        for index, (name, _) in enumerate(files):
            branch = "└──" if index == len(files) - 1 else "├──"
            lines.append(f"│   {branch} {name}")
    return lines


def build() -> Path:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    sections: list[str] = []
    for group, group_note, files in GROUPS:
        target_dir = OUT_DIR / group
        target_dir.mkdir()
        sections.append(f"## {group}\n\n{group_note}\n")
        for name, note in files:
            source = read_source(name)
            bundled = add_chinese_header(name, group, note, source)
            (target_dir / name).write_text(bundled, encoding="utf-8")
            language = (
                "python"
                if name.endswith(".py")
                else "sql"
                if name.endswith(".sql")
                else "ini"
                if name.endswith(".service")
                else "bash"
            )
            sections.extend(
                [
                    f"### `{group}/{name}`",
                    "",
                    f"**中文备注：** {note}",
                    "",
                    f"````{language}",
                    bundled.rstrip(),
                    "````",
                    "",
                ]
            )

    tree = "\n".join(tree_lines())
    document = f"""# 某支付平台数据库恢复脚本与工具说明

> **平台标识：某支付平台**  
> 文档时间：2026-11-10（Asia/Manila；数据库时间为 UTC+8）  
> 适用场景：数据库被删除后，使用日备、binlog 和 XtraBackup 历史快照恢复 某支付平台 主库及 57 张 `_bak` 表。

## 一、结论与完成状态

- 某支付平台 主库已通过 **备份节点 日备 + binlog PITR** 恢复到 DROP 前位置。
- 主恢复里程碑：2026-11-07 13:50:15 CST 完成；当时 `paydb` 152 张表，`user_account=约 55 万`、`user_profile=约 55 万`、`transaction_detail=约 118 万`。
- 57 张历史 `_bak` 表已从 2026-07-15 XtraBackup 快照导出并全部导入；2026-11-07 17:26:23 CST 完成，失败 0。
- `_bak` 导入后里程碑：`paydb` 187 张表，其中含 `_bak` 的基表 69 张；`transaction_detail=约 118 万`。
- 2026-11-10 04:33:45 CST 在线复核：187 张表、69 张 `_bak` 表、约 78,050.14 MB；`user_account=约 55 万`、`user_profile=约 55 万`、`transaction_detail=约 116 万`。这些是恢复后继续运行中的实时值，不是 11 月 7 日恢复快照值。
- 事件计划当前 8 个：7 个启用、1 个停用；`e_migrate_data` 原状态为停用，未擅自启用。
- `paydb2`、`paydb_20220101` 未纳入本次数据恢复，保持排期状态。

## 二、删除点与安全停止位置

```text
数据库：paydb
删除时间：2026-11-07 00:08:40 CST
binlog：/data/mysql/log/mysql-bin.000091
删除位置：693350583 / 693350648
导出停止位：693350648
DROP 检查：0
```

导出的恢复包使用 `mysqlbinlog --skip-gtids --database=paydb --stop-position=693350648`。
脚本在发布前还会再次扫描 `DROP DATABASE paydb`，命中即拒绝继续。

## 三、目录树

```text
{tree}
```

## 四、实际恢复链

### 1. 日备恢复

备份节点 上的日备为：

```text
/data/backup/paydb_backup_20261107_000001.tar.gz
大小：1,003,596,503 bytes
SHA256：d6135cd3b9014e14c2142d5c7f7342bde9116e94e06879fe44b692557cbe6bae
```

解包到 `/data/paydb-recovery-20261107/temp_20261107_000001/`，共 114 个表 SQL。
导入时清除源库 `SET @@GLOBAL.GTID_PURGED=...`，避免污染目标实例 GTID 状态。

### 2. binlog PITR

只提取 `paydb` 库在 `2026-11-07 00:00:00` 之后、DROP 完成位置之前的事件：

```text
paydb-binlog-before-drop-20261107.sql.gz
大小：3,250,451 bytes
SHA256：6600694357d161b298782de3ad4fbef36ef71a1527750e543f90b880036fe8ea
```

实际回放使用 `mysql --force`。日志中有 15 条 `ERROR 1062`（重复主键）
和 2 条 `ERROR 1032`（目标记录不存在），没有其他 SQL 错误；回放结束后
通过核心计数、对象数量和后续在线业务变化核验。`--force` 是本次实际口径，
重新演练时必须在隔离库先验证，不能直接覆盖在线 主节点。

### 3. 57 张 `_bak` 表

来源为 备份节点：

```text
/data/backup/2026-07-15_20-22-51
类型：XtraBackup 历史物理快照
```

使用 `innobackupex --apply-log --export` 后，以本地 socket、
`--skip-networking --skip-grant-tables` 启动临时 MySQL，避免任何网络访问。

备份中目标范围共 57 张表名含 `_bak` 的表：

```text
导出：2026-11-07 14:29:45 → 14:42:28 CST
并发：4 个 worker
导出：57/57，失败 0
上传：57/57，失败 0
导入：57/57，失败 0
目标表名缺失：0
```

导入脚本先暂停原有启用事件，逐表导入，再恢复事件状态。本次旧脚本曾因恢复 SQL
缺少 `USE paydb` 报 `ERROR 1046`；本工具包已修复该缺陷。

## 五、某海外中转站 恢复材料

目录：

```text
/data/recovery-staging
```

截至 2026-11-10 只读核验：

```text
57 个 paydb-bak-*.sql.gz
3 个 binlog 导出 SQL
1 个 paydb_backup_20261107_000001.tar.gz
gzip 坏包：0
SHA256 清单：61 项，全部通过
.sql.gz 合计：约 7.36 GiB（7.36 GiB）
```

恢复材料属于支付业务数据，**不放入本工具 ZIP，不发送到群**。群内只发送脚本、
说明、大小和哈希，不发送数据包本身。

## 六、安全边界

- 工具包不包含数据库密码、SSH 私钥、Telegram Token、云 API Key 或业务数据。
- 密码只从 root-only helper、受限环境文件或进程环境读取。
- 临时历史库必须使用 `--skip-networking`，只通过本地 socket 访问。
- 回放目标已有数据时，`paydb_main_restore.sh` 默认拒绝继续。
- 主库恢复脚本必须显式设置 `PAY_PLATFORM_CONFIRM_RESTORE=I_UNDERSTAND_PAY_PLATFORM_RESTORE`。
- 任何导出包发现 `DROP DATABASE paydb` 都必须停止，不得发布或回放。
- 回放完成不等于支付链路验收完成；仍需 DBA、开发和业务共同核验。

## 七、复现顺序

1. 用 `01_discovery` 工具确认源、目标、Web 配置、删除位和备份材料。
2. 用 `paydb_binlog_export.sh` 生成安全 binlog SQL。
3. 用 `paydb_main_restore.sh` 在隔离库或已批准目标库导入日备并回放。
4. 用 `paydb_verify.sql` 核对表数、核心行数、事件和 `CHECK TABLE`。
5. 用 `paydb_backup_reader.service` 启动本地只读历史实例。
6. 用 3 个 `_bak` 脚本完成导出、中转和导入。
7. 用 `paydb_artifact_verify.sh` 核验某海外中转站 恢复材料。
8. 将结果提交 DBA、开发和支付业务验收。

## 八、脚本与完整源码

以下内容为本次实际使用脚本，以及根据实际审计命令固化的可复现版本。
实际恢复时主链曾分步通过堡垒机执行；`paydb_main_restore.sh` 是这些步骤的
受控封装，增加确认门禁、GTID 清理、事件保护和非空库拒绝。

{chr(10).join(sections)}
"""

    (OUT_DIR / "README.md").write_text(document, encoding="utf-8")
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(document, encoding="utf-8")

    checksum_lines = []
    for path in sorted(OUT_DIR.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            checksum_lines.append(
                f"{digest}  {path.relative_to(OUT_DIR).as_posix()}"
            )
    (OUT_DIR / "SHA256SUMS").write_text(
        "\n".join(checksum_lines) + "\n", encoding="utf-8"
    )

    archive = ROOT / "deliverables" / f"paydb-recovery-toolkit-{STAMP}.zip"
    with zipfile.ZipFile(
        archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as bundle:
        for path in sorted(OUT_DIR.rglob("*")):
            if path.is_file():
                bundle.write(path, path.relative_to(OUT_DIR.parent))
    return archive


if __name__ == "__main__":
    print(build())
````

## 十一、归档复核结论

某支付平台 主库已通过 备份节点 日备和 binlog PITR 恢复到 DROP 前位置，DROP 检查为 0；主恢复于 2026-11-07 13:50:15 CST 完成，失败 0。57 张历史 `_bak` 表完成导出、上传、导入各 57/57，目标表名缺失 0，并于 2026-11-07 17:26:23 CST 完成。

2026-11-10 04:33:45 CST 的在线复核结果为 187 张表、69 张 `_bak` 表，`user_account=约 55 万`、`user_profile=约 55 万`、`transaction_detail=约 116 万`。这些是恢复后继续运行中的实时值，不代表 11 月 7 日恢复快照。`paydb2` 和 `paydb_20220101` 未纳入本次数据恢复。

工具包已通过 ZIP、包内 SHA256、脚本源码和凭据扫描复核。主库恢复必须显式确认，非空目标库默认拒绝执行，临时历史实例只使用本地 socket 和 `--skip-networking`，任何恢复 SQL 出现 `DROP DATABASE paydb` 都必须停止。所有脚本仅用于 某支付平台 本次恢复审计和受控复盘。
