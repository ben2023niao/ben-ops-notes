#!/usr/bin/env python3
"""Build the GDpay recovery-toolkit note from the supplied archive Markdown."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SOURCE_SHA256 = "c8b091077279a2c2ab8a18ac637d2b79a917a32d96e94f2a158912614b9d28ff"
ARCHIVE_SHA256 = "94247f1432e7029ec76cb3a5a65bce50e1216a4b58f54c22722393b6f501f68e"
ARCHIVE_BYTES = 49896

ANNOTATED_TREE = """gdpay-recovery-toolkit-20261110/
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
│   ├── gdpay_binlog_export.sh
│   │   └── DROP 前停止位导出与 DROP 门禁
│   └── gdpay_main_restore.sh
│       └── 日备导入、GTID 清理、binlog 回放、计数核验
├── 03_bak_tables/
│   ├── gdpay_backup_reader.service
│   │   └── 本地 socket、禁止网络的临时只读 MySQL
│   ├── gdpay_bak_export_all.sh
│   │   └── 57 张 _bak 表 4 路并行协调导出
│   ├── gdpay_bak_export_one.sh
│   │   └── 单表导出、压缩、SHA256、上传
│   └── gdpay_bak_import_on_db1.sh
│       └── 下载、校验、事件保护、逐表导入、表名核对
├── 04_verify/
│   ├── gdpay_verify.sql
│   │   └── 表数、核心行数、事件、CHECK TABLE
│   └── gdpay_artifact_verify.sh
│       └── 巴西 03 材料、gzip、61 项 SHA256 核验
└── 05_rebuild_docs/
    └── build_gdpay_recovery_toolkit.py
        └── 一键重建文档与 ZIP"""

GROUP_LABELS = [
    ("01_discovery", "恢复发现与只读盘点"),
    ("02_main_pitr", "主库日备与 binlog PITR"),
    ("03_bak_tables", "历史 _bak 表隔离导出与导入"),
    ("04_verify", "在线核验与恢复材料校验"),
    ("05_rebuild_docs", "工具包重建"),
]


def rewrite_script_headings(text: str) -> str:
    output: list[str] = []
    fence_char = ""
    fence_len = 0
    group_number = 0
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            value = marker.group(1)
            if not fence_char:
                fence_char = value[0]
                fence_len = len(value)
            elif value[0] == fence_char and len(value) >= fence_len:
                fence_char = ""
                fence_len = 0
            output.append(line)
            continue
        if fence_char:
            output.append(line)
            continue

        group_match = re.match(r"^## (0[1-5]_[a-z_]+)\s*$", line)
        if group_match:
            group_number += 1
            group = group_match.group(1)
            label = dict(GROUP_LABELS)[group]
            output.append(f"### 10.{group_number} {group} {label}")
            continue
        file_match = re.match(r"^### (`[^`]+`)\s*$", line)
        if file_match:
            output.append(f"#### {file_match.group(1)}")
            continue
        output.append(line)
    return "\n".join(output) + "\n"


def build(source_path: Path) -> str:
    source = source_path.read_text(encoding="utf-8")
    first_section = source.index("## 一、结论与完成状态")
    scripts_section = source.index("## 01_discovery")
    source_sections = source[first_section:scripts_section]
    scripts = rewrite_script_headings(source[scripts_section:])

    replacements = [
        ("## 一、结论与完成状态", "## 四、恢复结论与完成状态"),
        ("## 二、删除点与安全停止位置", "## 五、删除点与安全停止位置"),
        ("## 四、实际恢复链", "## 六、实际恢复链"),
        ("## 五、巴西 03 恢复材料", "## 七、巴西 03 恢复材料"),
        ("## 六、安全边界", "## 八、安全边界"),
        ("## 七、复现顺序", "## 九、复现顺序"),
        ("## 八、脚本与完整源码", "## 十、脚本与完整源码"),
    ]
    for old, new in replacements:
        source_sections = source_sections.replace(old, new)
    source_sections = re.sub(
        r"## 三、目录树.*?(?=## 六、实际恢复链)",
        "",
        source_sections,
        flags=re.S,
    )

    header = f"""---
id: "doc-gdpay-recovery-toolkit-20261110"
title: "GDpay 数据库恢复脚本与工具说明"
description: "GDpay 数据库恢复工具链完整归档，覆盖主库日备、binlog PITR、57 张历史 _bak 表恢复、隔离只读实例、在线核验与安全门禁，包含全部 13 个脚本源码、中文备注和 SHA256 校验信息。"
date: "2026-11-10T04:45:00+08:00"
dateSource: "附件文件名"
author: "BEN"
difficulty: "高级"
categories: ["数据库与恢复", "MySQL"]
tags: ["GDpay", "数据库恢复", "PITR", "binlog", "XtraBackup", "MySQL", "备份恢复", "支付数据", "Shell", "Python"]
sourcePath: "/Users/ben/Downloads/2026_11_10_0445_恢复工具_GDpay数据库恢复脚本与工具说明.md"
sourceSha256: "{SOURCE_SHA256}"
archiveSha256: "{ARCHIVE_SHA256}"
archiveBytes: {ARCHIVE_BYTES}
---

# GDpay 数据库恢复脚本与工具说明

> 平台：GDpay  
> 归档时间：2026-11-10 04:45（Asia/Manila，UTC+8）  
> 范围：主库日备与 binlog PITR，以及 2026-07-15 XtraBackup 中 57 张历史 `_bak` 表恢复。

本文完整归档 GDpay 本次误删恢复所用的审计、导出、回放、历史表导入、在线核验和重建工具。正文先说明工具包边界、目录职责和交付物校验结果，再记录恢复结论、删除位置、恢复链、实际运行数据、安全门禁和每一个脚本的源码，供本次支付业务恢复审计、复盘和受控复现使用。

## 一、归档范围与数据边界

本工具包覆盖 GDpay 主库日备导入、DROP 前 binlog PITR、57 张历史 `_bak` 表隔离导出与导入、数据库和恢复材料核验，以及文档与 ZIP 重建。ZIP 只含 README、校验清单和 13 个脚本，不含数据库密码、Token、私钥、云 API Key 或支付业务数据。

巴西 03 上约 7.36 GiB 的 GDpay 恢复材料属于支付业务数据，不放入工具 ZIP，也不发送到群。恢复群只传脚本、说明、文件大小和哈希。本文记录材料数量和校验结论，不嵌入数据包、业务记录或凭据。

## 二、工具包目录与中文备注

目录按恢复阶段拆分。恢复发现、主库 PITR、历史 `_bak` 表处理、核验和重建工具各自独立，便于审计每一步输入、停止条件和输出。

```text
{ANNOTATED_TREE}
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
| Markdown 说明文档 | `{SOURCE_SHA256}` | 68,261 bytes |
| 完整工具包 ZIP | `{ARCHIVE_SHA256}` | 49,896 bytes |

巴西 03 恢复材料另行使用 `gdpay_artifact_verify.sh` 核验。当前记录为 57 个 `_bak` 表 SQL 包、3 个 binlog 导出 SQL、1 个日备 tar 包，gzip 坏包 0，61 项 SHA256 全部通过，`.sql.gz` 合计 7,902,704,918 bytes。

"""
    footer = """

## 十一、归档复核结论

GDpay 主库已通过 DB2 日备和 binlog PITR 恢复到 DROP 前位置，DROP 检查为 0；主恢复于 2026-11-07 13:50:15 CST 完成，失败 0。57 张历史 `_bak` 表完成导出、上传、导入各 57/57，目标表名缺失 0，并于 2026-11-07 17:26:23 CST 完成。

2026-11-10 04:33:45 CST 的在线复核结果为 187 张表、69 张 `_bak` 表，`account=549,556`、`account_detailed=549,556`、`money_details=1,160,007`。这些是恢复后继续运行中的实时值，不代表 11 月 7 日恢复快照。`gdpay2` 和 `gdpay_20220101` 未纳入本次数据恢复。

工具包已通过 ZIP、包内 SHA256、脚本源码和凭据扫描复核。主库恢复必须显式确认，非空目标库默认拒绝执行，临时历史实例只使用本地 socket 和 `--skip-networking`，任何恢复 SQL 出现 `DROP DATABASE gdpay` 都必须停止。所有脚本仅用于 GDpay 本次恢复审计和受控复盘。
"""
    return header + source_sections.lstrip() + "\n" + scripts.rstrip() + footer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(args.source), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
