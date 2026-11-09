#!/usr/bin/env python3
"""Build the BSQP recovery-toolkit note from the supplied archive Markdown."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SOURCE_SHA256 = "8f43f44e562579dbcb96e7390e8d050da2599503c3e05972708c2f0d3065ff0b"
ARCHIVE_SHA256 = "6acd8487205190ea5a2cb6be8730e76036eb490a302bad904f9670124947d0f0"
ARCHIVE_BYTES = 128138

ANNOTATED_TREE = """bsqp-recovery-toolkit-20261110/
├── README.md
│   └── 完整说明、目录备注、全部脚本源码
├── SHA256SUMS
│   └── 包内逐文件完整性校验
├── 01_source_export/
│   ├── bsqp_source_export_full.sh
│   │   └── 导出 17 个业务库全量 SQL 基线
│   ├── bsqp_source_binlog_export.sh
│   │   └── 从 relay/binlog 导出增量 SQL
│   ├── bsqp_source_binlog_parallel.sh
│   │   └── relay/binlog 分片并行导出
│   └── bsqp_accounts_my2sql_export.sh
│       └── 用户核心表 my2sql 抽取
├── 02_baseline_pitr/
│   ├── bsqp_target_download_parallel.sh
│   │   └── 目标机并行下载与校验恢复包
│   ├── bsqp_target_import_baseline.sh
│   │   └── 全量基线导入
│   ├── bsqp_target_import_named.sh
│   │   └── 指定数据库基线导入
│   ├── bsqp_target_import_remaining.sh
│   │   └── 剩余数据库补导
│   ├── bsqp_finalize_log_baselines.sh
│   │   └── 日志库基线完成标记与切换
│   ├── bsqp_target_finish_log_baselines.sh
│   │   └── 大日志库收尾与增量启动
│   ├── bsqp_target_apply_incremental.sh
│   │   └── 单路增量 SQL 回放
│   ├── bsqp_target_apply_incremental_parallel.sh
│   │   └── 表级并行增量回放
│   ├── bsqp_filtered_pitr.sh
│   │   └── 带库表过滤的安全 PITR
│   ├── bsqp_accounts_my2sql_apply.sh
│   │   └── 用户核心表回放入口
│   └── bsqp_my2sql_apply_parallel.py
│       └── 按 UID 分片的并行回放器
├── 03_table_parallel/
│   ├── bsqp_small_table_backup.sh
│   │   └── 回放前逐表备份
│   ├── bsqp_wait_and_apply_small.sh
│   │   └── 等待解包后自动回放小表
│   ├── bsqp_apply_small_table_sql.sh
│   │   └── 小表优先、同表保序回放
│   ├── bsqp_import_closed_chunks.sh
│   │   └── 已完成 SQL 分片导入
│   └── bsqp_replay_uid_sharded.sh
│       └── 按 UID 稳定分片回放大表
├── 04_large_log_tables/
│   ├── bsqp_apply_append_only_desc.sh
│   │   └── 大日志表仅 INSERT 的倒序补写
│   └── bsqp_resume_key_sharded.py
│       └── 按主键稳定分片并支持断点续跑
├── 05_monitoring_verify/
│   ├── bsqp_restore_monitor.py
│   │   └── 恢复状态采集与群播报
│   ├── run_bsqp_restore_monitor.sh
│   │   └── 常驻监控启动器
│   ├── emergency_bastion_exec.py
│   │   └── 经堡垒机执行只读检查
│   ├── bsqp_online_verify.sql
│   │   └── 行数、主键、时间边界核验 SQL
│   └── bsqp_restore_flush_guard.sh
│       └── 临时参数自动恢复保护
└── 06_rebuild_docs/
    └── build_bsqp_recovery_toolkit.py
        └── 一键重建文档、目录树和工具包"""

GROUP_LABELS = [
    ("01_source_export", "源端导出"),
    ("02_baseline_pitr", "全量基线与 PITR"),
    ("03_table_parallel", "小表与表级并行"),
    ("04_large_log_tables", "超大日志表专项"),
    ("05_monitoring_verify", "监控、核验与参数保护"),
    ("06_rebuild_docs", "工具包重建"),
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

        group_match = re.match(r"^## (0[1-6]_[a-z_]+)\s*$", line)
        if group_match:
            group_number += 1
            group = group_match.group(1)
            label = dict(GROUP_LABELS)[group]
            output.append(f"### 8.{group_number} {group} {label}")
            continue
        file_match = re.match(r"^### (`[^`]+`)\s*$", line)
        if file_match:
            output.append(f"#### {file_match.group(1)}")
            continue
        output.append(line)
    return "\n".join(output) + "\n"


def build(source_path: Path) -> str:
    source = source_path.read_text(encoding="utf-8")
    first_section = source.index("## 一、本次恢复结果")
    scripts_section = source.index("## 01_source_export")
    source_sections = source[first_section:scripts_section]
    scripts = rewrite_script_headings(source[scripts_section:])

    source_sections = source_sections.replace("## 一、本次恢复结果", "## 四、本次恢复结果")
    source_sections = source_sections.replace("## 二、目录树", "## 已合并目录树")
    source_sections = source_sections.replace("## 三、恢复流程", "## 五、恢复流程")
    source_sections = source_sections.replace("## 四、安全边界", "## 六、安全边界")
    source_sections = source_sections.replace(
        "## 五、关键环境变量", "## 七、关键环境变量"
    )
    source_sections = source_sections.replace(
        "## 六、脚本与完整源码", "## 八、脚本与完整源码"
    )
    source_sections = re.sub(
        r"## 已合并目录树.*?(?=## 五、恢复流程)",
        "",
        source_sections,
        flags=re.S,
    )

    header = f"""---
id: "doc-bsqp-recovery-toolkit-20261110"
title: "BSQP 百盛数据库恢复脚本与工具说明"
description: "BSQP 百盛数据库恢复工具链的完整归档说明，覆盖 29 个归档内容文件、17 个业务库基线、relay/binlog PITR、并行增量回放、回放前备份、在线核验与群播报，并保留 5,287 行文档、全部脚本源码及 SHA256 校验信息。"
date: "2026-11-10T04:20:00+08:00"
dateSource: "附件文件名"
author: "BEN"
difficulty: "高级"
categories: ["数据库与恢复", "MySQL"]
tags: ["BSQP 百盛", "数据库恢复", "PITR", "binlog", "my2sql", "MySQL", "Shell", "Python", "备份恢复", "监控告警"]
sourcePath: "/Users/ben/Downloads/2026_11_10_0420_恢复工具_BSQP百盛数据库恢复脚本与工具说明.md"
sourceSha256: "{SOURCE_SHA256}"
archiveSha256: "{ARCHIVE_SHA256}"
archiveBytes: {ARCHIVE_BYTES}
---

# BSQP 百盛数据库恢复脚本与工具说明

> 平台：BSQP 百盛  
> 归档时间：2026-11-10 04:20（Asia/Manila，UTC+8）  
> 用途：全量基线导入、relay/binlog PITR、增量回放、超大表并发、回放前备份、在线核验与恢复播报。

本文保留 BSQP 百盛本次误删恢复所用的整套工具说明和脚本源码。正文先说明项目边界、目录职责和归档校验结果，再记录恢复结果、执行流程、安全约束及每一件工具的源码，供本次恢复审计、故障复盘和后续同类任务复核使用。

## 一、归档范围与项目边界

本工具包只覆盖本次 BSQP 百盛全量基线恢复、增量 PITR、表级并发回放、大日志表专项处理、恢复前备份、在线核验和机器人播报。29 个归档内容文件由 README 和 28 个脚本组成，脚本均标注平台、恢复阶段、中文备注和安全说明；`SHA256SUMS` 是单独的校验元数据文件。归档内容包括 5,287 行 Markdown 文档、工具包目录树、全部脚本源码、运行参数、核验口径和通知规则。

巴西 03 上的恢复工具链属于另一个项目 GDpay，与本次 BSQP 百盛恢复无关，没有混入本工具包。本文中的结论也只适用于 BSQP 百盛本次恢复审计与复盘。

归档记录显示，ZIP 完整性检查通过，包内逐文件 SHA256 全部通过；没有发现明文密码、Telegram Token、SSH 私钥、云 API 密钥或会话凭据。运行凭据只从受限配置或进程环境读取。本次站点导入保留了原始 Markdown 和脚本正文，没有把 ZIP、数据库凭据或运行资源写入公开仓库。

## 二、工具包目录与中文备注

目录按恢复阶段拆分，源端导出、目标机基线导入与 PITR、表级并行、超大日志表、监控核验和文档重建相互独立。执行时可以按阶段定位入口，也便于在失败后只重跑对应环节。

```text
{ANNOTATED_TREE}
```

## 三、归档核验结果

| 核验项 | 归档结果 | 复核口径 |
|---|---|---|
| 归档内容文件 | 29 个 | README 与 28 个脚本 |
| 校验元数据 | `SHA256SUMS` | 逐文件 SHA256 |
| Markdown 正文 | 5,287 行 | 原始说明文档 |
| 脚本标注 | 全部具备 | 平台、恢复阶段、中文备注、安全说明 |
| ZIP 完整性 | 检查通过 | 归档操作记录 |
| 包内文件校验 | 全部通过 | `SHA256SUMS` |
| 凭据扫描 | 未发现明文凭据 | 密码、Token、私钥和会话凭据 |
| 项目隔离 | 仅 BSQP 百盛 | 巴西 03 的 GDpay 工具链未混入 |

原始 Markdown 文件在本次站点导入时再次执行 SHA256，结果与归档记录一致，说明进入知识库的正文来源没有被替换。ZIP 未随站点文件一起提交，保留以下指纹用于后续交付物追溯。

| 附件 | SHA256 | 大小 |
|---|---|---:|
| Markdown 说明文档 | `{SOURCE_SHA256}` | 198,816 bytes |
| 完整工具包 ZIP | `{ARCHIVE_SHA256}` | 128,138 bytes |

归档交付顺序为先发送 Markdown 说明文档，再发送完整 ZIP。两者对应同一套 `bsqp-recovery-toolkit-20261110` 文件清单，验收时应同时核对 Markdown 哈希、ZIP 哈希和 `SHA256SUMS`。

"""
    footer = """

## 九、归档复核结论

本次 BSQP 百盛恢复工具链已完成文档化归档。29 个归档内容文件、17 个业务库基线导出、relay/binlog PITR、表级并发、超大日志表专项回放、回放前备份、在线核验和通知脚本均有对应说明；脚本源码在本文中完整保留。

P5 的 27/27 张表和 P6 的 96/96 个 SQL 文件均完成回放且失败数为 0。`versus_list`、`balance_versus_relation`、`versus`、`sx_record_log` 的最后数据时间均为 `2026-11-07 00:04:59`；相关表主键数量等于行数，`CHECK TABLE` 全部返回 `OK`。回放结束后 `innodb_flush_log_at_trx_commit=1`、`event_scheduler=ON`。历史断层 `2025-06～2026-04` 已由业务确认不处理，不阻塞本次开服。

后续复用本工具包时，应先确认恢复对象、截止时间、业务库范围和备份可用性，再按目录顺序执行。回放完成只代表数据任务结束，主从切换、业务验收和网站开放仍需人工确认。所有脚本仅用于本次 BSQP 百盛恢复审计与复盘。
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
