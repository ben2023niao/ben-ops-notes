---
id: "doc-recovery-toolkit-20261110-01"
title: "某业务平台数据库恢复脚本与工具说明"
description: "某业务平台数据库恢复工具链的完整归档说明，覆盖 29 个归档内容文件、17 个业务库基线、relay/binlog PITR、并行增量回放、回放前备份、在线核验与群播报，并保留 5,287 行文档、全部脚本源码及 SHA256 校验信息。"
date: "2026-11-10T04:20:00+08:00"
dateSource: "附件文件名"
author: "BEN"
difficulty: "高级"
categories: ["数据库与恢复", "MySQL"]
tags: ["某业务平台", "数据库恢复", "PITR", "binlog", "my2sql", "MySQL", "Shell", "Python", "备份恢复", "监控告警"]
sourcePath: "/Users/operator/Downloads/2026_11_10_0420_恢复工具_某业务平台数据库恢复脚本与工具说明.md"
sourceSha256: "8f43f44e562579dbcb96e7390e8d050da2599503c3e05972708c2f0d3065ff0b"
archiveSha256: "6acd8487205190ea5a2cb6be8730e76036eb490a302bad904f9670124947d0f0"
archiveBytes: 128138
---

# 某业务平台数据库恢复脚本与工具说明

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 平台：某业务平台  
> 归档时间：2026-11-10 04:20（Asia/Manila，UTC+8）  
> 用途：全量基线导入、relay/binlog PITR、增量回放、超大表并发、回放前备份、在线核验与恢复播报。

本文保留某业务平台本次误删恢复所用的整套工具说明和脚本源码。正文先说明项目边界、目录职责和归档校验结果，再记录恢复结果、执行流程、安全约束及每一件工具的源码，供本次恢复审计、故障复盘和后续同类任务复核使用。

## 一、归档范围与项目边界

本工具包只覆盖本次某业务平台全量基线恢复、增量 PITR、表级并发回放、大日志表专项处理、恢复前备份、在线核验和机器人播报。29 个归档内容文件由 README 和 28 个脚本组成，脚本均标注平台、恢复阶段、中文备注和安全说明；`SHA256SUMS` 是单独的校验元数据文件。归档内容包括 5,287 行 Markdown 文档、工具包目录树、全部脚本源码、运行参数、核验口径和通知规则。

某海外中转站 上的恢复工具链属于另一个项目某支付平台，与本次某业务平台恢复无关，没有混入本工具包。本文中的结论也只适用于某业务平台本次恢复审计与复盘。

归档记录显示，ZIP 完整性检查通过，包内逐文件 SHA256 全部通过；没有发现明文密码、Telegram Token、SSH 私钥、云 API 密钥或会话凭据。运行凭据只从受限配置或进程环境读取。本次站点导入保留了原始 Markdown 和脚本正文，没有把 ZIP、数据库凭据或运行资源写入公开仓库。

## 二、工具包目录与中文备注

目录按恢复阶段拆分，源端导出、目标机基线导入与 PITR、表级并行、超大日志表、监控核验和文档重建相互独立。执行时可以按阶段定位入口，也便于在失败后只重跑对应环节。

```text
bizdb-recovery-toolkit-20261110/
├── README.md
│   └── 完整说明、目录备注、全部脚本源码
├── SHA256SUMS
│   └── 包内逐文件完整性校验
├── 01_source_export/
│   ├── bizdb_source_export_full.sh
│   │   └── 导出 17 个业务库全量 SQL 基线
│   ├── bizdb_source_binlog_export.sh
│   │   └── 从 relay/binlog 导出增量 SQL
│   ├── bizdb_source_binlog_parallel.sh
│   │   └── relay/binlog 分片并行导出
│   └── bizdb_user_accounts_my2sql_export.sh
│       └── 用户核心表 my2sql 抽取
├── 02_baseline_pitr/
│   ├── bizdb_target_download_parallel.sh
│   │   └── 目标机并行下载与校验恢复包
│   ├── bizdb_target_import_baseline.sh
│   │   └── 全量基线导入
│   ├── bizdb_target_import_named.sh
│   │   └── 指定数据库基线导入
│   ├── bizdb_target_import_remaining.sh
│   │   └── 剩余数据库补导
│   ├── bizdb_finalize_log_baselines.sh
│   │   └── 日志库基线完成标记与切换
│   ├── bizdb_target_finish_log_baselines.sh
│   │   └── 大日志库收尾与增量启动
│   ├── bizdb_target_apply_incremental.sh
│   │   └── 单路增量 SQL 回放
│   ├── bizdb_target_apply_incremental_parallel.sh
│   │   └── 表级并行增量回放
│   ├── bizdb_filtered_pitr.sh
│   │   └── 带库表过滤的安全 PITR
│   ├── bizdb_user_accounts_my2sql_apply.sh
│   │   └── 用户核心表回放入口
│   └── bizdb_my2sql_apply_parallel.py
│       └── 按 UID 分片的并行回放器
├── 03_table_parallel/
│   ├── bizdb_small_table_backup.sh
│   │   └── 回放前逐表备份
│   ├── bizdb_wait_and_apply_small.sh
│   │   └── 等待解包后自动回放小表
│   ├── bizdb_apply_small_table_sql.sh
│   │   └── 小表优先、同表保序回放
│   ├── bizdb_import_closed_chunks.sh
│   │   └── 已完成 SQL 分片导入
│   └── bizdb_replay_uid_sharded.sh
│       └── 按 UID 稳定分片回放大表
├── 04_large_log_tables/
│   ├── bizdb_apply_append_only_desc.sh
│   │   └── 大日志表仅 INSERT 的倒序补写
│   └── bizdb_resume_key_sharded.py
│       └── 按主键稳定分片并支持断点续跑
├── 05_monitoring_verify/
│   ├── bizdb_restore_monitor.py
│   │   └── 恢复状态采集与群播报
│   ├── run_bizdb_restore_monitor.sh
│   │   └── 常驻监控启动器
│   ├── emergency_bastion_exec.py
│   │   └── 经堡垒机执行只读检查
│   ├── bizdb_online_verify.sql
│   │   └── 行数、主键、时间边界核验 SQL
│   └── bizdb_restore_flush_guard.sh
│       └── 临时参数自动恢复保护
└── 06_rebuild_docs/
    └── build_bizdb_recovery_toolkit.py
        └── 一键重建文档、目录树和工具包
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
| 项目隔离 | 仅 某业务平台 | 某海外中转站 的 某支付平台 工具链未混入 |

原始 Markdown 文件在本次站点导入时再次执行 SHA256，结果与归档记录一致，说明进入知识库的正文来源没有被替换。ZIP 未随站点文件一起提交，保留以下指纹用于后续交付物追溯。

| 附件 | SHA256 | 大小 |
|---|---|---:|
| Markdown 说明文档 | `8f43f44e562579dbcb96e7390e8d050da2599503c3e05972708c2f0d3065ff0b` | 198,816 bytes |
| 完整工具包 ZIP | `6acd8487205190ea5a2cb6be8730e76036eb490a302bad904f9670124947d0f0` | 128,138 bytes |

归档交付顺序为先发送 Markdown 说明文档，再发送完整 ZIP。两者对应同一套 `bizdb-recovery-toolkit-20261110` 文件清单，验收时应同时核对 Markdown 哈希、ZIP 哈希和 `SHA256SUMS`。

## 四、本次恢复结果

- P5：27/27 张表回放完成，失败 0。
- P6：96/96 个 SQL 文件完成，失败 0。
- `contest_list`、`balance_relation`、`contest`、`record_log` 最后数据时间为 `2026-11-07 00:04:59`。
- 相关表主键数量均等于行数，`CHECK TABLE` 全部为 `OK`。
- 回放结束后 `innodb_flush_log_at_trx_commit=1`，`event_scheduler=ON`。
- 历史断层 `2025-06～2026-04` 已由业务确认不处理，不阻塞本次开服。

## 五、恢复流程

1. **源端全量导出**：从源库或备份机导出各业务库基线。
2. **源端 binlog 导出**：按 relay 文件区间和恢复截止时间生成表级 DML。
3. **目标机基线导入**：逐库导入全量 SQL，并写完成标记。
4. **早期 PITR**：按 UID 或表进行增量回放，恢复用户和日志主链路。
5. **小表优先回放**：按表并发；同一张表保持 binlog 顺序。
6. **超大表专项**：
   - `contest`、`record_log`：按最新 binlog 优先、仅回放 INSERT。
   - 剩余大表：按主键稳定分片，同一主键只进入一个 shard。
7. **持续核验**：检查行数、主键、最大时间、SQL 错误和 `CHECK TABLE`。
8. **自动化通知**：每 5 分钟播报进行中任务；全部回放完成后只发一次完成通知。

## 六、安全边界

- 脚本不包含数据库密码、Telegram Token、SSH 私钥或云 API 密钥。
- 凭据只从 root-only 配置文件或进程环境读取。
- 写库前必须完成备份；备份失败时脚本拒绝继续。
- 默认拒绝 DDL、DROP、TRUNCATE 和 YYYYMMDD 日期分区表。
- 同一张表只能由一个 worker 顺序处理；不同表或不同主键 shard 才允许并发。
- 临时性能参数在脚本退出时恢复。
- 回放完成不等于业务验收完成；主从切换和开放网站必须由人工确认。

## 七、关键环境变量

| 变量 | 用途 |
|---|---|
| `PGS_DATABASE` / `PGS_TABLES` | 源端导出的数据库与表 |
| `PGS_START_FILE` / `PGS_STOP_FILE` | relay/binlog 文件范围 |
| `PGS_STOP_DATETIME` | 安全恢复截止时间 |
| `PGS_DESTINATION` | SQL 包上传目标 |
| `某业务平台_SMALL_APPLY_WORKERS` | 表级回放并发数 |
| `某业务平台_SMALL_REUSE_COMBINED` | 复用已组装 SQL，断点续跑 |
| `某业务平台_APPEND_ONLY_START_FILE` | 超大日志表起始 relay 文件号 |
| `某业务平台_APPEND_ONLY_WORKERS` | 文件级并发数 |
| `某业务公司_BASTION_EXEC_TIMEOUT` | 堡垒机只读采集超时 |

## 八、脚本与完整源码

以下源码是本次在 某业务平台恢复中使用的工具副本。压缩包中的副本额外加入了
“平台、恢复阶段、中文备注、安全说明”头注释。


### 8.1 01_source_export 源端导出

从源端 relay/binlog 生成带表名和主键条件的可执行 SQL。

#### `01_source_export/bizdb_source_export_full.sh`

**中文备注：** 导出整库全量 SQL 基线，供目标机恢复 2026-05-10 基线。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：01_source_export
# 中文备注：导出整库全量 SQL 基线，供目标机恢复 2026-05-10 基线。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
set -uo pipefail

mysql_helper="${PGS_MYSQL_HELPER:-/root/mysql.sh}"
mysql_bin="${PGS_MYSQL_BIN:-/data/mysql/bin/mysqldump}"
transfer_key="${PGS_TRANSFER_KEY:-/tmp/.bizops-transfer-key}"
destination="${PGS_DESTINATION:-root@192.0.2.38:/root/vendor_a-zips}"
work_dir="${PGS_EXPORT_WORK_DIR:-/data/bizops-bizdb-export}"
workers="${PGS_EXPORT_WORKERS:-4}"
stamp="${PGS_EXPORT_STAMP:-20261107}"

databases=(
  users_db
  data_db
  monitor_db
  game_db
  history_partition_db
  agent_db
  config_db
  market_db
  common_log_db
  main_log_db
  diff_log_db
  finance_db
  cms_api_db
  recharge_db
  report_db
  merchant_db
)

password="$(
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
case "$password" in
  \'*\'|\"*\")
    password="${password:1:${#password}-2}"
    ;;
esac
[[ -n "$password" ]] || exit 2

install -d -m 750 "$work_dir" "$work_dir/logs"
printf '%s\n' "${databases[@]}" >"$work_dir/databases.txt"

export_one() {
  local database="$1"
  local safe="${database//[^A-Za-z0-9_.-]/_}"
  local filename="bizdb-full-${safe}-${stamp}.sql.gz"
  local remote="${destination}/${filename}"
  local log="$work_dir/logs/${safe}.log"
  {
    printf 'START=%s DATABASE=%s\n' "$(date '+%F %T %Z')" "$database"
    set -o pipefail
    MYSQL_PWD="$password" "$mysql_bin" \
      --socket=/tmp/mysql.sock \
      -uroot \
      --single-transaction \
      --quick \
      --skip-lock-tables \
      --routines \
      --triggers \
      --events \
      --hex-blob \
      --set-gtid-purged=OFF \
      --databases "$database" \
      | gzip -1 \
      | ssh -i "$transfer_key" \
          -o StrictHostKeyChecking=no \
          -o UserKnownHostsFile=/dev/null \
          -o ConnectTimeout=15 \
          "$destination_host" "cat > ${remote#*:}"
    local rc=$?
    printf 'EXPORT_RC=%s\n' "$rc"
    if [[ "$rc" -eq 0 ]]; then
      ssh -i "$transfer_key" \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        -o ConnectTimeout=15 \
        "$destination_host" \
        "sha256sum '${remote#*:}' && touch '${remote#*:}.done'"
      printf 'FINALIZE_RC=%s\n' "$?"
    fi
    printf 'FINISH=%s\n' "$(date '+%F %T %Z')"
    return "$rc"
  } >>"$log" 2>&1
}
export -f export_one
export password mysql_bin transfer_key destination work_dir stamp
destination_host="${destination%%:*}"
export destination_host

printf 'COORDINATOR_START=%s DATABASES=%s WORKERS=%s\n' \
  "$(date '+%F %T %Z')" "${#databases[@]}" "$workers" \
  >"$work_dir/coordinator.log"
xargs -r -P "$workers" -n 1 bash -c 'export_one "$1"' _ \
  <"$work_dir/databases.txt"
rc=$?
printf 'COORDINATOR_RC=%s\nCOORDINATOR_FINISH=%s\n' \
  "$rc" "$(date '+%F %T %Z')" >>"$work_dir/coordinator.log"
exit "$rc"
````

#### `01_source_export/bizdb_source_binlog_export.sh`

**中文备注：** 串行从 relay/binlog 导出增量 SQL。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：01_source_export
# 中文备注：串行从 relay/binlog 导出增量 SQL。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
set -uo pipefail

relay_prefix="${PGS_RELAY_PREFIX:-/data/mysql/data/sample-node-22-new-relay-bin}"
relay_index="${PGS_RELAY_INDEX:-${relay_prefix}.index}"
start_file="${PGS_START_FILE:-000003}"
start_position="${PGS_START_POSITION:-33270674}"
stop_file="${PGS_STOP_FILE:-000602}"
stop_datetime="${PGS_STOP_DATETIME:-2026-11-07 00:27:11}"
mysqlbinlog="${PGS_MYSQLBINLOG:-/data/mysql/bin/mysqlbinlog}"
transfer_key="${PGS_TRANSFER_KEY:-/tmp/.bizops-transfer-key}"
destination="${PGS_DESTINATION:-root@192.0.2.38:/root/vendor_a-zips}"
work_dir="${PGS_EXPORT_WORK_DIR:-/data/bizops-bizdb-export}"
output_name="${PGS_BINLOG_OUTPUT:-bizdb-incremental-before-drop-20261107.sql.gz}"

install -d -m 750 "$work_dir"
files=()
while IFS= read -r path; do
  if [[ "$path" != /* ]]; then
    path="$(dirname "$relay_index")/$path"
  fi
  name="$(basename "$path")"
  number="${name##*.}"
  if [[ "$number" =~ ^[0-9]+$ ]] &&
     (( 10#$number >= 10#$start_file && 10#$number <= 10#$stop_file )); then
    files+=("$path")
  fi
done <"$relay_index"

echo "BINLOG_FILES=${#files[@]}"
(( ${#files[@]} > 0 )) || exit 2

destination_host="${destination%%:*}"
remote_path="${destination#*:}/${output_name}"
log="$work_dir/binlog-export.log"
{
  echo "START=$(date '+%F %T %Z')"
  echo "START_FILE=$start_file POSITION=$start_position"
  echo "STOP_FILE=$stop_file DATETIME=$stop_datetime"
  echo "FILE_COUNT=${#files[@]}"
  set -o pipefail
  "$mysqlbinlog" \
    --base64-output=DECODE-ROWS \
    --verbose \
    --skip-gtids \
    --start-position="$start_position" \
    --stop-datetime="$stop_datetime" \
    "${files[@]}" |
    gzip -1 |
    ssh -i "$transfer_key" \
      -o StrictHostKeyChecking=no \
      -o UserKnownHostsFile=/dev/null \
      -o ConnectTimeout=15 \
      "$destination_host" "cat > $remote_path"
  rc=$?
  echo "EXPORT_RC=$rc"
  if [[ "$rc" -eq 0 ]]; then
    ssh -i "$transfer_key" \
      -o StrictHostKeyChecking=no \
      -o UserKnownHostsFile=/dev/null \
      -o ConnectTimeout=15 \
      "$destination_host" "sha256sum '$remote_path'"
  fi
  echo "FINISH=$(date '+%F %T %Z')"
} >>"$log" 2>&1
````

#### `01_source_export/bizdb_source_binlog_parallel.sh`

**中文备注：** 按 relay 文件区间拆分并并行导出增量 SQL。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：01_source_export
# 中文备注：按 relay 文件区间拆分并并行导出增量 SQL。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
set -uo pipefail

relay_prefix="${PGS_RELAY_PREFIX:-/data/mysql/data/sample-node-22-new-relay-bin}"
relay_index="${PGS_RELAY_INDEX:-${relay_prefix}.index}"
start_file="${PGS_START_FILE:-000003}"
start_position="${PGS_START_POSITION:-33270674}"
stop_file="${PGS_STOP_FILE:-000602}"
stop_datetime="${PGS_STOP_DATETIME:-2026-11-07 00:27:11}"
workers="${PGS_BINLOG_WORKERS:-8}"
mysqlbinlog="${PGS_MYSQLBINLOG:-/data/mysql/bin/mysqlbinlog}"
transfer_key="${PGS_TRANSFER_KEY:-/tmp/.bizops-transfer-key}"
destination="${PGS_DESTINATION:-root@192.0.2.38:/root/vendor_a-zips}"
work_dir="${PGS_EXPORT_WORK_DIR:-/data/bizops-bizdb-binlog-parallel}"
output_prefix="${PGS_BINLOG_OUTPUT_PREFIX:-bizdb-incremental-part}"

install -d -m 750 "$work_dir" "$work_dir/ranges" "$work_dir/logs"
selected="$work_dir/selected.tsv"
plan="$work_dir/plan.tsv"
: >"$selected"

while IFS= read -r path; do
  [[ "$path" != /* ]] && path="$(dirname "$relay_index")/$path"
  name="$(basename "$path")"
  number="${name##*.}"
  if [[ "$number" =~ ^[0-9]+$ ]] &&
     (( 10#$number >= 10#$start_file && 10#$number <= 10#$stop_file )); then
    size="$(stat -c %s "$path")"
    printf '%s\t%s\t%s\n' "$number" "$size" "$path" >>"$selected"
  fi
done <"$relay_index"

file_count="$(wc -l <"$selected")"
(( file_count > 0 )) || exit 20
(( workers > file_count )) && workers="$file_count"

awk -F '\t' -v workers="$workers" '
  { size[NR]=$2; files[NR]=$3; total += $2 }
  END {
    target = int((total + workers - 1) / workers)
    range = 1
    used = 0
    for (i = 1; i <= NR; i++) {
      if (i > 1 && range < workers && used >= target) {
        range++
        used = 0
      }
      print range "\t" files[i]
      used += size[i]
    }
  }
' "$selected" >"$plan"

export_one() {
  local index="$1"
  local range_file="$work_dir/ranges/$index.files"
  local output_name="${output_prefix}-$(printf '%02d' "$index")-of-$(printf '%02d' "$workers").sql.gz"
  local remote_path="${destination#*:}/$output_name"
  local log="$work_dir/logs/part-${index}.log"
  local args=(
    --base64-output=DECODE-ROWS
    --verbose
    --skip-gtids
    --stop-datetime="$stop_datetime"
  )
  local first_number
  first_number="$(basename "$(head -1 "$range_file")")"
  first_number="${first_number##*.}"

  if (( 10#$first_number == 10#$start_file )); then
    args+=(--start-position="$start_position")
  fi

  {
    printf 'START=%s PART=%s FILES=%s\n' \
      "$(date '+%F %T %Z')" "$index" "$(wc -l <"$range_file")"
    mapfile -t files <"$range_file"
    set -o pipefail
    "$mysqlbinlog" "${args[@]}" "${files[@]}" |
      gzip -1 |
      ssh -i "$transfer_key" \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        -o ConnectTimeout=15 \
        "$destination_host" "cat > '$remote_path'"
    local rc=$?
    printf 'EXPORT_RC=%s\n' "$rc"
    if [[ "$rc" -eq 0 ]]; then
      ssh -i "$transfer_key" \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        -o ConnectTimeout=15 \
        "$destination_host" \
        "gzip -t '$remote_path' && sha256sum '$remote_path' && touch '$remote_path.done'"
      printf 'VERIFY_RC=%s\n' "$?"
    fi
    printf 'FINISH=%s\n' "$(date '+%F %T %Z')"
    return "$rc"
  } >>"$log" 2>&1
}

destination_host="${destination%%:*}"
export -f export_one
export work_dir output_prefix workers destination destination_host
export transfer_key stop_datetime mysqlbinlog start_file start_position

for index in $(seq 1 "$workers"); do
  awk -F '\t' -v part="$index" '$1 == part { print $2 }' "$plan" \
    >"$work_dir/ranges/$index.files"
done

seq 1 "$workers" |
  xargs -r -P "$workers" -n 1 bash -c 'export_one "$1"' _
rc=$?
printf 'PARALLEL_RC=%s FINISH=%s\n' "$rc" "$(date '+%F %T %Z')" \
  >>"$work_dir/coordinator.log"
exit "$rc"
````

#### `01_source_export/bizdb_user_accounts_my2sql_export.sh`

**中文备注：** 通用 my2sql 并行导出器，支持指定数据库、表、文件区间和输出归档。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：01_source_export
# 中文备注：通用 my2sql 并行导出器，支持指定数据库、表、文件区间和输出归档。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# ============================================================================
# 某业务平台数据库恢复工具：把 relay/binlog 行事件转换成可执行 SQL
# ----------------------------------------------------------------------------
# 运行位置：
#   - 必须在 relay/binlog 所在的源端备份机执行；
#   - my2sql 需要连接一个包含源库表结构的 MySQL 实例来解析 ROW 事件。
#
# 主要职责：
#   1. 按 relay-bin.index 选择指定的 binlog 文件区间；
#   2. 将文件按总字节数尽量均匀切给多个 worker；
#   3. 每个 worker 调用 my2sql，把 ROW 事件导出成 INSERT/UPDATE/DELETE SQL；
#   4. 将每个 worker 的 SQL 打成 tar.gz，并上传到跳板/中转目录。
#
# 关键安全约束：
#   - 截止时间由 PGS_STOP_DATETIME 控制，不得包含删除库事件；
#   - 密码只从 root-only 文件读取，不写日志、不写入仓库；
#   - 可设置 PGS_ALLOW_CONCURRENT=1，允许多种恢复任务并行导出。
#
# 关键环境变量：
#   PGS_DATABASE/PGS_TABLES  目标库与表
#   PGS_START_FILE/STOP_FILE relay 文件范围
#   PGS_STOP_DATETIME        安全恢复截止时间
#   PGS_BINLOG_WORKERS       并行 worker 数
#   PGS_DESTINATION          SQL 包上传目标
# ============================================================================
set -uo pipefail

database="${PGS_DATABASE:-users_db}"
export_name="${PGS_EXPORT_NAME:-$database}"
stamp="${PGS_EXPORT_STAMP:-$(date +%Y%m%d-%H%M%S)}"
relay_index="${PGS_RELAY_INDEX:-/data/mysql/data/sample-node-22-new-relay-bin.index}"
source_dir="${PGS_SOURCE_DATA_DIR:-/data/mysql/data}"
work_dir="${PGS_MY2SQL_WORK_DIR:-/tmp/my2sql-$database-$stamp}"
archive_dir="${PGS_ARCHIVE_WORK_DIR:-/tmp}"
destination="${PGS_DESTINATION:?PGS_DESTINATION is required, for example root@192.0.2.39:/root/vendor_a-zips}"
transfer_key="${PGS_TRANSFER_KEY:-/tmp/.bizops-transfer-key}"
my2sql="${PGS_MY2SQL_BIN:-/tmp/my2sql-relay}"
meta_password_file="${PGS_META_PASSWORD_FILE:?PGS_META_PASSWORD_FILE is required}"
meta_host="${PGS_META_HOST:-192.0.2.40}"
meta_port="${PGS_META_PORT:-13367}"
meta_user="${PGS_META_USER:-bizops_meta}"
start_file="${PGS_START_FILE:-000003}"
start_position="${PGS_START_POSITION:-33270674}"
stop_file="${PGS_STOP_FILE:-000602}"
stop_datetime="${PGS_STOP_DATETIME:-2026-11-07 00:05:00}"
workers="${PGS_BINLOG_WORKERS:-8}"
tables="${PGS_TABLES:-user_account,user_ext,user_level,bank_info,user_payment,new_user,user_code,user_bind}"

install -d -m 750 "$work_dir" "$work_dir/ranges" "$work_dir/logs" "$work_dir/out" "$archive_dir"
: >"$work_dir/selected.tsv"

# 第一遍：只读取 relay 索引，筛出恢复时间范围内的文件及大小。
# 文件大小用于后续按字节均衡分区，避免一个 worker 分到过多大文件。
while IFS= read -r path; do
  [[ "$path" != /* ]] && path="$source_dir/${path#./}"
  number="${path##*.}"
  if [[ "$number" =~ ^[0-9]+$ ]] &&
     (( 10#$number >= 10#$start_file && 10#$number <= 10#$stop_file )); then
    size="$(sudo -n stat -c %s "$path")"
    printf '%s\t%s\t%s\n' "$number" "$size" "$path" >>"$work_dir/selected.tsv"
  fi
done < <(sudo -n cat "$relay_index")

file_count="$(wc -l <"$work_dir/selected.tsv")"
(( file_count > 0 )) || {
  echo "No relay files selected" >&2
  exit 20
}
(( workers > file_count )) && workers="$file_count"

# 第二遍：按总字节数生成分片计划。每个 binlog 文件只分配给一个 worker，
# worker 内部再按文件顺序解析，保证单条业务链的 binlog 顺序不被打乱。
awk -F '\t' -v workers="$workers" '
  { size[NR]=$2; files[NR]=$3; total += $2 }
  END {
    target = int((total + workers - 1) / workers)
    range = 1
    used = 0
    for (i = 1; i <= NR; i++) {
      if (i > 1 && range < workers && used >= target) {
        range++
        used = 0
      }
      print range "\t" files[i]
      used += size[i]
    }
  }
' "$work_dir/selected.tsv" >"$work_dir/plan.tsv"

for index in $(seq 1 "$workers"); do
  awk -F '\t' -v part="$index" '$1 == part { print $2 }' "$work_dir/plan.tsv" \
    >"$work_dir/ranges/$index.files"
done

run_one() {
  # 单个 my2sql worker：
  #   - 第一个分片从业务指定的起点开始；
  #   - 其他分片从文件 position 4 开始，文件之间保持 relay 顺序；
  #   - 输出 SQL 后立即压缩并上传，减少源端磁盘占用。
  local index="$1" first last last_size start_position_for_range output_dir log
  mapfile -t files <"$work_dir/ranges/$index.files"
  first="${files[0]}"
  last="${files[-1]}"
  last_size="$(sudo -n stat -c %s "$last")"
  if (( index == 1 )); then
    start_position_for_range="$start_position"
  else
    start_position_for_range=4
  fi
  output_dir="$work_dir/out/$index"
  log="$work_dir/logs/$index.log"
  mkdir -p "$output_dir"
  local file_per_table=()
  if [[ "${PGS_FILE_PER_TABLE:-0}" == "1" ]]; then
    file_per_table=(-file-per-table)
  fi

  {
    echo "START=$(date '+%F %T %Z') PART=$index FILES=${#files[@]}"
    echo "FIRST=$(basename "$first") LAST=$(basename "$last")"
    sudo -n "$my2sql" \
      -mode file \
      -local-binlog-file "$first" \
      -start-file "$(basename "$first")" \
      -start-pos "$start_position_for_range" \
      -stop-file "$(basename "$last")" \
      -stop-pos "$last_size" \
      -stop-datetime "$stop_datetime" \
      -databases "$database" \
      -tables "$tables" \
      "${file_per_table[@]}" \
      -work-type 2sql \
      -output-dir "$output_dir" \
      -threads 2 \
      -host "$meta_host" \
      -port "$meta_port" \
      -user "$meta_user" \
      -password "$(cat "$meta_password_file")" \
      -mysql-type mysql
    local rc=$?
    echo "MY2SQL_RC=$rc"
    sudo -n chown -R "$(id -u):$(id -g)" "$output_dir"

    local archive="$archive_dir/$export_name-$stamp-part-$(printf '%02d' "$index").tar.gz"
    tar -C "$output_dir" -czf "$archive" .
    scp -q -i "$transfer_key" \
      -o StrictHostKeyChecking=no \
      -o UserKnownHostsFile=/dev/null \
      "$archive" "$destination/"
    echo "ARCHIVE_RC=$?"
    echo "FINISH=$(date '+%F %T %Z')"
    exit "$rc"
  } >"$log" 2>&1
}

export -f run_one
export database stamp work_dir my2sql meta_host meta_port meta_user
export meta_password_file start_position stop_datetime tables archive_dir export_name
export transfer_key destination

# 默认禁止两个 my2sql 任务同时运行，防止源端 CPU/磁盘被重复扫描压垮。
# 本次恢复后期只对明确分离的表组设置 PGS_ALLOW_CONCURRENT=1。
if [[ "${PGS_ALLOW_CONCURRENT:-0}" != "1" ]] &&
   pgrep -f '^/tmp/my2sql-relay' >/dev/null 2>&1; then
  echo "Another my2sql conversion is already running; refusing to start" >&2
  exit 19
fi
pids=()
for index in $(seq 1 "$workers"); do
  bash -c "run_one $index" &
  pids+=("$!")
done

rc=0
for pid in "${pids[@]}"; do
  wait "$pid" || rc=$?
done

if (( rc != 0 )) || find "$work_dir/logs" -type f -name '*.log' \
    -exec grep -L 'MY2SQL_RC=0' {} + | grep -q .; then
  echo "One or more my2sql workers failed" >&2
  exit 21
fi

echo "某业务平台_MY2SQL_EXPORT_OK workers=$workers work_dir=$work_dir"
````

### 8.2 02_baseline_pitr 全量基线与 PITR

下载、校验和导入全量基线，并执行早期 PITR 增量回放。

#### `02_baseline_pitr/bizdb_target_download_parallel.sh`

**中文备注：** 从宝塔中转目录并行下载基线和增量包，并进行 gzip 校验。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：02_baseline_pitr
# 中文备注：从宝塔中转目录并行下载基线和增量包，并进行 gzip 校验。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
set -uo pipefail

transfer_key="${PGS_TRANSFER_KEY:-/tmp/.bizops-transfer-key}"
source_host="${PGS_SOURCE_HOST:-root@192.0.2.38}"
source_file="${PGS_SOURCE_FILE:?PGS_SOURCE_FILE is required}"
destination="${PGS_DESTINATION:?PGS_DESTINATION is required}"
workers="${PGS_DOWNLOAD_WORKERS:-8}"
work_dir="${PGS_DOWNLOAD_WORK_DIR:-/data/bizops-bizdb-restore/downloads}"

install -d -m 750 "$work_dir"
work_name="$(basename "$destination").parallel"
part_dir="$work_dir/$work_name"
install -d -m 750 "$part_dir"
log="$work_dir/${work_name}-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$log") 2>&1

size="$(
  ssh -i "$transfer_key" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o ConnectTimeout=15 \
    "$source_host" "stat -c %s '$source_file'"
)"
[[ "$size" =~ ^[0-9]+$ ]] || exit 20
(( workers > 0 )) || exit 21
chunk=$(( (size + workers - 1) / workers ))

fetch_range() {
  local index="$1"
  local start=$(( (index - 1) * chunk ))
  (( start < size )) || return 0
  local length="$chunk"
  (( start + length <= size )) || length=$(( size - start ))
  local part="$part_dir/$(printf '%02d' "$index").part"
  ssh -i "$transfer_key" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o ConnectTimeout=15 \
    "$source_host" \
    "dd if='$source_file' iflag=skip_bytes,count_bytes skip=$start count=$length bs=4M status=none" \
    >"$part"
  local rc=$?
  echo "RANGE_RC=$rc INDEX=$index START=$start LENGTH=$length SIZE=$(stat -c %s "$part" 2>/dev/null || echo 0)"
  return "$rc"
}

export -f fetch_range
export transfer_key source_host source_file size chunk part_dir

seq 1 "$workers" |
  xargs -r -P "$workers" -n 1 bash -c 'fetch_range "$1"' _
download_rc=$?
echo "DOWNLOAD_PARALLEL_RC=$download_rc"
[[ "$download_rc" -eq 0 ]] || exit "$download_rc"

temporary="$destination.parallel-assemble"
for part in "$part_dir"/*.part; do
  cat "$part"
done >"$temporary"
actual_size="$(stat -c %s "$temporary")"
echo "ASSEMBLED_SIZE=$actual_size EXPECTED_SIZE=$size"
[[ "$actual_size" -eq "$size" ]] || exit 22
gzip -t "$temporary" || exit 23
mv -f "$temporary" "$destination"
rm -f "$part_dir"/*.part
echo "DOWNLOAD_COMPLETE=$(date '+%F %T %Z')"
````

#### `02_baseline_pitr/bizdb_target_import_baseline.sh`

**中文备注：** 按数据库导入全量基线，生成完成标记。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：02_baseline_pitr
# 中文备注：按数据库导入全量基线，生成完成标记。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
set -o pipefail

transfer_key="${PGS_TRANSFER_KEY:-/tmp/.bizops-transfer-key}"
source_host="${PGS_SOURCE_HOST:-root@192.0.2.38}"
source_dir="${PGS_SOURCE_DIR:-/root/vendor_a-zips}"
work_dir="${PGS_TARGET_WORK_DIR:-/data/bizops-bizdb-restore}"
mysql_bin="${PGS_MYSQL_BIN:-/data/mysql/bin/mysql}"
mysql_cnf="${PGS_TARGET_CNF:-/root/.bizops-target.cnf}"
stamp="${PGS_EXPORT_STAMP:-20261107}"
workers="${PGS_IMPORT_WORKERS:-4}"
download_workers="${PGS_DOWNLOAD_WORKERS:-6}"
allow_partial="${PGS_ALLOW_PARTIAL:-0}"
only_done="${PGS_ONLY_DONE:-0}"

install -d -m 750 "$work_dir/base" "$work_dir/logs"
marker_dir="$work_dir/markers"
install -d -m 750 "$marker_dir"
log="$work_dir/logs/baseline-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$log") 2>&1

event_scheduler_was_enabled="$(
  "$mysql_bin" --defaults-extra-file="$mysql_cnf" -N \
    -e "SELECT @@GLOBAL.event_scheduler"
)"
echo "EVENT_SCHEDULER_BEFORE=$event_scheduler_was_enabled"
"$mysql_bin" --defaults-extra-file="$mysql_cnf" \
  -e "SET GLOBAL event_scheduler=OFF"

if [[ "$only_done" == "1" ]]; then
  marker_list="$work_dir/source-done-markers.txt"
  ssh -i "$transfer_key" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$source_host" \
    "find '$source_dir' -maxdepth 1 -type f -name 'bizdb-full-*-$stamp.sql.gz.done' -printf '%f\\n' | sort" \
    >"$marker_list"
  echo "DONE_MARKERS=$(wc -l <"$marker_list")"

  fetch_one() {
    local marker_name="$1"
    local file_name="${marker_name%.done}"
    local target="$work_dir/base/$file_name"
    local temporary="$target.part"
    if [[ -s "$target" && ! -e "$temporary" ]]; then
      echo "SCP_SKIP_EXISTING=$file_name"
      return 0
    fi
    scp -q -i "$transfer_key" \
      -o StrictHostKeyChecking=no \
      -o UserKnownHostsFile=/dev/null \
      "$source_host:$source_dir/$file_name" \
      "$temporary"
    local rc=$?
    if [[ "$rc" -eq 0 ]]; then
      mv -f "$temporary" "$target"
      : >"$target.done"
    else
      rm -f "$temporary"
    fi
    echo "SCP_RC=$rc FILE=$file_name"
    return "$rc"
  }
  export -f fetch_one
  export transfer_key source_host source_dir work_dir

  if [[ -s "$marker_list" ]]; then
    xargs -r -P "$download_workers" -n 1 \
      bash -c 'fetch_one "$1"' _ <"$marker_list"
    echo "DOWNLOAD_PARALLEL_RC=$?"
  fi
else
  scp -q -i "$transfer_key" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$source_host:$source_dir/bizdb-full-*-$stamp.sql.gz" \
    "$work_dir/base/"
  echo "SCP_RC=$?"
fi

files=()
mapfile -t files < <(find "$work_dir/base" -maxdepth 1 -type f -name 'bizdb-full-*.sql.gz' | sort)
if [[ "$only_done" == "1" ]]; then
  selected=()
  for file in "${files[@]}"; do
    [[ -e "$file.done" ]] && selected+=("$file")
  done
  if [[ "${#selected[@]}" -gt 0 ]]; then
    files=("${selected[@]}")
  else
    files=()
  fi
fi
echo "BASELINE_FILES=${#files[@]}"
if [[ "${#files[@]}" -lt 16 && "$allow_partial" != "1" ]]; then
  exit 20
fi

for file in "${files[@]}"; do
  gzip -t "$file" || {
    echo "GZIP_INVALID=$file"
    exit 21
  }
done
echo "GZIP_VERIFY=ok"

import_one() {
  local file="$1"
  local base dblog marker
  base="$(basename "$file" .sql.gz)"
  dblog="$work_dir/logs/${base}.log"
  marker="$marker_dir/${base}.done"
  if [[ -e "$marker" ]]; then
    echo "SKIP_COMPLETED=$base"
    return 0
  fi
  {
    echo "START=$base $(date '+%F %T %Z')"
    gzip -dc "$file" |
      "$mysql_bin" \
        --defaults-extra-file="$mysql_cnf" \
        --max-allowed-packet=268435456 \
        --init-command="SET SESSION sql_log_bin=0; SET SESSION foreign_key_checks=0; SET SESSION unique_checks=0"
    local rc=$?
    echo "IMPORT_RC=$rc"
    echo "FINISH=$(date '+%F %T %Z')"
    if [[ "$rc" -eq 0 ]]; then
      printf 'completed=%s\n' "$(date '+%F %T %Z')" >"$marker"
    fi
    return "$rc"
  } >>"$dblog" 2>&1
}
export -f import_one
export work_dir marker_dir mysql_bin mysql_cnf

declare -a groups=("" "" "" "")
for file in "${files[@]}"; do
  case "$(basename "$file")" in
    *config_db*) continue ;;
  esac
  name="$(basename "$file")"
  if [[ "$name" == *common_log_db* || "$name" == *main_log_db* || "$name" == *agent_db* ]]; then
    groups[0]+="$file"$'\n'
  elif [[ "$name" == *finance_db* || "$name" == *game_db* ]]; then
    groups[1]+="$file"$'\n'
  elif [[ "$name" == *recharge_db* || "$name" == *cms_api_db* ]]; then
    groups[2]+="$file"$'\n'
  else
    groups[3]+="$file"$'\n'
  fi
done

pids=()
for index in 0 1 2 3; do
  group_file="$work_dir/group-$index.txt"
  printf '%s' "${groups[$index]}" >"$group_file"
  (
    while IFS= read -r file; do
      [[ -n "$file" ]] || continue
      import_one "$file" || exit $?
    done <"$group_file"
  ) &
  pids+=("$!")
done

rc=0
for pid in "${pids[@]}"; do
  wait "$pid" || rc=$?
done
echo "BASELINE_PARALLEL_RC=$rc"
[[ "$rc" -eq 0 ]] || exit "$rc"

company_file="$(find "$work_dir/base" -maxdepth 1 -type f -name 'bizdb-full-config_db-*.sql.gz' | head -1)"
if [[ -n "$company_file" && ( "$only_done" != "1" || -e "$company_file.done" ) ]]; then
  import_one "$company_file"
  echo "JLMJ_CONFIG_RC=$?"
fi

echo "BASELINE_COMPLETE=$(date '+%F %T %Z')"
````

#### `02_baseline_pitr/bizdb_target_import_named.sh`

**中文备注：** 按指定数据库导入单个基线包，便于失败后单独重跑。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：02_baseline_pitr
# 中文备注：按指定数据库导入单个基线包，便于失败后单独重跑。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
set -uo pipefail

work_dir="${PGS_TARGET_WORK_DIR:-/data/bizops-bizdb-restore}"
mysql_bin="${PGS_MYSQL_BIN:-/data/mysql/bin/mysql}"
mysql_cnf="${PGS_TARGET_CNF:-/root/.bizops-target.cnf}"
stamp="${PGS_EXPORT_STAMP:-20261107}"
workers="${PGS_IMPORT_WORKERS:-5}"
final_database="${PGS_FINAL_DATABASE:-}"

databases=("$@")
install -d -m 750 "$work_dir/markers" "$work_dir/logs"
log="$work_dir/logs/named-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$log") 2>&1

import_one() {
  local database="$1"
  local file="$work_dir/base/bizdb-full-${database}-${stamp}.sql.gz"
  local marker="$work_dir/markers/bizdb-full-${database}-${stamp}.done"
  local database_log="$work_dir/logs/bizdb-full-${database}-${stamp}.log"
  if [[ -e "$marker" ]]; then
    echo "IMPORT_SKIP_COMPLETED=$database"
    return 0
  fi
  if [[ ! -s "$file" ]]; then
    echo "IMPORT_FILE_MISSING=$database"
    return 25
  fi
  {
    echo "START=$database $(date '+%F %T %Z')"
    gzip -dc "$file" |
      "$mysql_bin" \
        --defaults-extra-file="$mysql_cnf" \
        --max-allowed-packet=268435456 \
        --init-command="SET SESSION sql_log_bin=0; SET SESSION foreign_key_checks=0; SET SESSION unique_checks=0"
    local rc=$?
    echo "IMPORT_RC=$rc"
    echo "FINISH=$(date '+%F %T %Z')"
    if [[ "$rc" -eq 0 ]]; then
      printf 'completed=%s\n' "$(date '+%F %T %Z')" >"$marker"
    fi
    return "$rc"
  } >>"$database_log" 2>&1
}

export -f import_one
export work_dir mysql_bin mysql_cnf stamp

printf '%s\n' "${databases[@]}" |
  xargs -r -P "$workers" -n 1 bash -c 'import_one "$1"' _
rc=$?
echo "IMPORT_PARALLEL_RC=$rc"

if [[ -n "$final_database" ]]; then
  import_one "$final_database"
  final_rc=$?
  echo "FINAL_DATABASE_RC=$final_rc"
  [[ "$final_rc" -eq 0 ]] || rc="$final_rc"
fi

echo "IMPORT_NAMED_COMPLETE=$(date '+%F %T %Z')"
exit "$rc"
````

#### `02_baseline_pitr/bizdb_target_import_remaining.sh`

**中文备注：** 继续导入尚未完成的基线包。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：02_baseline_pitr
# 中文备注：继续导入尚未完成的基线包。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
set -uo pipefail

transfer_key="${PGS_TRANSFER_KEY:-/tmp/.bizops-transfer-key}"
source_host="${PGS_SOURCE_HOST:-root@192.0.2.38}"
source_dir="${PGS_SOURCE_DIR:-/root/vendor_a-zips}"
work_dir="${PGS_TARGET_WORK_DIR:-/data/bizops-bizdb-restore}"
mysql_bin="${PGS_MYSQL_BIN:-/data/mysql/bin/mysql}"
mysql_cnf="${PGS_TARGET_CNF:-/root/.bizops-target.cnf}"
download_workers="${PGS_DOWNLOAD_WORKERS:-6}"
import_workers="${PGS_IMPORT_WORKERS:-5}"
stamp="${PGS_EXPORT_STAMP:-20261107}"

databases=(
  common_log_db
  main_log_db
  recharge_db
  report_db
  merchant_db
)
final_database="config_db"

install -d -m 750 "$work_dir/base" "$work_dir/logs" "$work_dir/markers"
log="$work_dir/logs/remaining-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$log") 2>&1

"$mysql_bin" --defaults-extra-file="$mysql_cnf" \
  -e "SET GLOBAL event_scheduler=OFF"

files_file="$work_dir/remaining-databases.txt"
printf '%s\n' "${databases[@]}" "$final_database" >"$files_file"

fetch_one() {
  local database="$1"
  local file_name="bizdb-full-${database}-${stamp}.sql.gz"
  local target="$work_dir/base/$file_name"
  local temporary="$target.part"
  if [[ -s "$target" ]]; then
    echo "SCP_SKIP_EXISTING=$file_name"
    return 0
  fi
  scp -q -i "$transfer_key" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$source_host:$source_dir/$file_name" \
    "$temporary"
  local rc=$?
  if [[ "$rc" -eq 0 ]]; then
    mv -f "$temporary" "$target"
  else
    rm -f "$temporary"
  fi
  echo "SCP_RC=$rc FILE=$file_name"
  return "$rc"
}

import_parallel() {
  local database="$1"
  local file="$work_dir/base/bizdb-full-${database}-${stamp}.sql.gz"
  local marker="$work_dir/markers/bizdb-full-${database}-${stamp}.done"
  local database_log="$work_dir/logs/bizdb-full-${database}-${stamp}.log"
  if [[ -e "$marker" ]]; then
    echo "IMPORT_SKIP_COMPLETED=$database"
    return 0
  fi
  {
    echo "START=$database $(date '+%F %T %Z')"
    gzip -dc "$file" |
      "$mysql_bin" \
        --defaults-extra-file="$mysql_cnf" \
        --max-allowed-packet=268435456 \
        --init-command="SET SESSION sql_log_bin=0; SET SESSION foreign_key_checks=0; SET SESSION unique_checks=0"
    local rc=$?
    echo "IMPORT_RC=$rc"
    echo "FINISH=$(date '+%F %T %Z')"
    if [[ "$rc" -eq 0 ]]; then
      printf 'completed=%s\n' "$(date '+%F %T %Z')" >"$marker"
    fi
    return "$rc"
  } >>"$database_log" 2>&1
}

export -f fetch_one import_parallel
export transfer_key source_host source_dir work_dir stamp mysql_bin mysql_cnf

xargs -r -P "$download_workers" -n 1 \
  bash -c 'fetch_one "$1"' _ <"$files_file"
download_rc=$?
echo "DOWNLOAD_PARALLEL_RC=$download_rc"
[[ "$download_rc" -eq 0 ]] || exit "$download_rc"

for database in "${databases[@]}" "$final_database"; do
  gzip -t "$work_dir/base/bizdb-full-${database}-${stamp}.sql.gz" || {
    echo "GZIP_INVALID=$database"
    exit 21
  }
done
echo "GZIP_VERIFY=ok"

printf '%s\n' "${databases[@]}" |
  xargs -r -P "$import_workers" -n 1 \
    bash -c 'import_parallel "$1"' _
import_rc=$?
echo "IMPORT_PARALLEL_RC=$import_rc"
[[ "$import_rc" -eq 0 ]] || exit "$import_rc"

import_parallel "$final_database"
final_rc=$?
echo "FINAL_DATABASE_RC=$final_rc"
echo "REMAINING_COMPLETE=$(date '+%F %T %Z')"
exit "$final_rc"
````

#### `02_baseline_pitr/bizdb_finalize_log_baselines.sh`

**中文备注：** 确认日志库基线表数量并写入完成标记。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：02_baseline_pitr
# 中文备注：确认日志库基线表数量并写入完成标记。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
set -uo pipefail

work_root="${PGS_TARGET_WORK_DIR:-/data/bizops-bizdb-restore}"
stamp="${PGS_EXPORT_STAMP:-20261107}"
log_dir="$work_root/logs"
marker_dir="$work_root/markers"

install -d -m 750 "$log_dir" "$marker_dir"
log="$log_dir/finalize-log-baselines-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$log") 2>&1

for database in common_log_db main_log_db; do
  unit="bizdb-live-import-${database}.service"
  while true; do
    active="$(systemctl is-active "$unit" 2>/dev/null || true)"
    result="$(
      systemctl show -p Result --no-page "$unit" 2>/dev/null |
        sed -n 's/^Result=//p'
    )"
    case "$active:$result" in
      inactive:success|unknown:success)
        break
        ;;
      failed:*|inactive:failed|unknown:failed)
        echo "IMPORT_SERVICE_FAILED=$database UNIT=$unit RESULT=$result"
        exit 20
        ;;
    esac
    echo "WAIT_IMPORT=$database ACTIVE=$active RESULT=${result:-unknown} $(date '+%F %T %Z')"
    sleep 30
  done

  failures="$work_root/parallel-import/$database/failures.live.txt"
  failure_count=0
  if [[ -s "$failures" ]]; then
    failure_count="$(wc -l <"$failures")"
  fi
  remaining="$(
    find "$work_root/parallel-import/$database/chunks" \
      -maxdepth 1 -type f -name 'chunk-*.sql' -printf x 2>/dev/null |
      wc -c
  )"
  imported="$(
    find "$work_root/parallel-import/$database/imported" \
      -maxdepth 1 -type f -name 'chunk-*.sql' -printf x 2>/dev/null |
      wc -c
  )"
  echo "IMPORT_RESULT=$database IMPORTED=$imported REMAINING=$remaining FAILURES=$failure_count"
  if (( failure_count > 0 || remaining > 0 || imported == 0 )); then
    echo "IMPORT_RESULT_INCOMPLETE=$database"
    exit 21
  fi
  : >"$marker_dir/bizdb-full-${database}-${stamp}.done"
done

marker_count="$(
  find "$marker_dir" -maxdepth 1 -type f \
    -name "bizdb-full-*-${stamp}.done" -printf x | wc -c
)"
echo "BASELINE_MARKERS=$marker_count/16"
if (( marker_count < 16 )); then
  echo "BASELINE_MARKERS_INCOMPLETE"
  exit 22
fi

systemctl reset-failed bizdb-target-apply-incremental-parallel.service 2>/dev/null || true
systemctl start --no-block bizdb-target-apply-incremental-parallel.service
echo "PITR_APPLY_STARTED=$(date '+%F %T %Z')"
````

#### `02_baseline_pitr/bizdb_target_finish_log_baselines.sh`

**中文备注：** 日志库基线完成后的补收尾流程。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：02_baseline_pitr
# 中文备注：日志库基线完成后的补收尾流程。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
set -eo pipefail

transfer_key="${PGS_TRANSFER_KEY:-/tmp/.bizops-transfer-key}"
source_host="${PGS_SOURCE_HOST:-root@192.0.2.38}"
source_dir="${PGS_SOURCE_DIR:-/root/vendor_a-zips}"
work_dir="${PGS_TARGET_WORK_DIR:-/data/bizops-bizdb-restore}"
stamp="${PGS_EXPORT_STAMP:-20261107}"

install -d -m 750 "$work_dir/logs" "$work_dir/markers"
log="$work_dir/logs/finish-log-baselines-$(date +%Y%m%d-%H%M%S).log"
exec >>"$log" 2>&1

for database in common_log_db main_log_db; do
  file="$work_dir/base/bizdb-full-${database}-${stamp}.sql.gz"
  while [[ ! -s "$file" ]]; do
    systemctl is-active --quiet bizdb-target-download-logcompany.service ||
      {
        echo "DOWNLOAD_SERVICE_STOPPED_WITHOUT_FILE=$file"
        exit 19
      }
    echo "WAIT_DOWNLOAD=$database $(date '+%F %T %Z')"
    sleep 30
  done
  gzip -t "$file"
  remote_hash="$(
    ssh -i "$transfer_key" \
      -o StrictHostKeyChecking=no \
      -o UserKnownHostsFile=/dev/null \
      -o ConnectTimeout=15 \
      "$source_host" "cut -d ' ' -f 1 '$source_dir/$(basename "$file").sha256'"
  )"
  local_hash="$(sha256sum "$file" | cut -d ' ' -f 1)"
  echo "SHA_CHECK=$database REMOTE=$remote_hash LOCAL=$local_hash"
  [[ -n "$remote_hash" && "$remote_hash" == "$local_hash" ]] || exit 21
done

/usr/local/sbin/bizdb_target_import_named.sh common_log_db main_log_db
systemctl start --no-block bizdb-target-apply-incremental-parallel.service
echo "LOG_BASELINES_FINISHED=$(date '+%F %T %Z')"
````

#### `02_baseline_pitr/bizdb_target_apply_incremental.sh`

**中文备注：** 基础增量 SQL 回放器。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：02_baseline_pitr
# 中文备注：基础增量 SQL 回放器。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
set -uo pipefail

transfer_key="${PGS_TRANSFER_KEY:-/tmp/.bizops-transfer-key}"
source_host="${PGS_SOURCE_HOST:-root@192.0.2.38}"
source_dir="${PGS_SOURCE_DIR:-/root/vendor_a-zips}"
work_dir="${PGS_TARGET_WORK_DIR:-/data/bizops-bizdb-restore}"
mysql_bin="${PGS_MYSQL_BIN:-/data/mysql/bin/mysql}"
mysql_cnf="${PGS_TARGET_CNF:-/root/.bizops-target.cnf}"
incremental_name="${PGS_BINLOG_FILE:-bizdb-incremental-before-drop-20261107.sql.gz}"

install -d -m 750 "$work_dir/incremental" "$work_dir/logs"
log="$work_dir/logs/incremental-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$log") 2>&1

scp -q -i "$transfer_key" \
  -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null \
  "$source_host:$source_dir/$incremental_name" \
  "$work_dir/incremental/"
echo "SCP_RC=$?"

file="$work_dir/incremental/$incremental_name"
gzip -t "$file"
echo "GZIP_RC=$?"

event_scheduler_was_enabled="$(
  "$mysql_bin" --defaults-extra-file="$mysql_cnf" -N \
    -e "SELECT @@GLOBAL.event_scheduler"
)"
echo "EVENT_SCHEDULER_BEFORE=$event_scheduler_was_enabled"
"$mysql_bin" --defaults-extra-file="$mysql_cnf" \
  -e "SET GLOBAL event_scheduler=OFF"

set -o pipefail
gzip -dc "$file" |
  "$mysql_bin" \
    --defaults-extra-file="$mysql_cnf" \
    --max-allowed-packet=268435456 \
    --binary-mode \
    --init-command="SET SESSION sql_log_bin=0"
echo "INCREMENTAL_RC=$?"
echo "INCREMENTAL_FINISH=$(date '+%F %T %Z')"
````

#### `02_baseline_pitr/bizdb_target_apply_incremental_parallel.sh`

**中文备注：** 并行增量 SQL 回放器，按表/分片提高吞吐。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：02_baseline_pitr
# 中文备注：并行增量 SQL 回放器，按表/分片提高吞吐。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
set -uo pipefail

transfer_key="${PGS_TRANSFER_KEY:-/tmp/.bizops-transfer-key}"
source_host="${PGS_SOURCE_HOST:-root@192.0.2.38}"
source_dir="${PGS_SOURCE_DIR:-/root/vendor_a-zips}"
work_dir="${PGS_TARGET_WORK_DIR:-/data/bizops-bizdb-restore}"
mysql_bin="${PGS_MYSQL_BIN:-/data/mysql/bin/mysql}"
mysql_cnf="${PGS_TARGET_CNF:-/root/.bizops-target.cnf}"
workers="${PGS_BINLOG_WORKERS:-8}"
prefix="${PGS_BINLOG_OUTPUT_PREFIX:-bizdb-incremental-part}"
stop_datetime="${PGS_STOP_DATETIME:-2026-11-07 00:27:11}"

part_dir="$work_dir/incremental-parallel"
install -d -m 750 "$part_dir" "$work_dir/logs"
log="$work_dir/logs/incremental-parallel-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$log") 2>&1

filename_for() {
  printf '%s-%02d-of-%02d.sql.gz\n' "$prefix" "$1" "$workers"
}

wait_for_remote() {
  local remote_file="$1"
  while ! ssh -i "$transfer_key" \
      -o StrictHostKeyChecking=no \
      -o UserKnownHostsFile=/dev/null \
      -o ConnectTimeout=15 \
      "$source_host" "test -s '$remote_file' && test -e '$remote_file.done'"; do
    echo "WAIT_REMOTE=$(basename "$remote_file") $(date '+%F %T %Z')"
    sleep 20
  done
}

fetch_part() {
  local index="$1"
  local file_name
  local remote_file
  local target
  local temporary
  local remote_sha
  local local_sha
  file_name="$(filename_for "$index")"
  remote_file="$source_dir/$file_name"
  target="$part_dir/$file_name"
  temporary="$target.part"
  wait_for_remote "$remote_file"
  scp -q -i "$transfer_key" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$source_host:$remote_file" \
    "$temporary"
  local rc=$?
  if [[ "$rc" -ne 0 ]]; then
    rm -f "$temporary"
    echo "SCP_FAILED=$file_name RC=$rc"
    return "$rc"
  fi
  gzip -t "$temporary" || {
    echo "GZIP_INVALID=$file_name"
    return 22
  }
  remote_sha="$(
    ssh -i "$transfer_key" \
      -o StrictHostKeyChecking=no \
      -o UserKnownHostsFile=/dev/null \
      -o ConnectTimeout=15 \
      "$source_host" "sha256sum '$remote_file'" |
      awk '{print $1}'
  )"
  local_sha="$(sha256sum "$temporary" | awk '{print $1}')"
  if [[ -z "$remote_sha" || "$remote_sha" != "$local_sha" ]]; then
    echo "SHA_MISMATCH=$file_name REMOTE=$remote_sha LOCAL=$local_sha"
    return 23
  fi
  mv -f "$temporary" "$target"
  printf '%s  %s\n' "$local_sha" "$file_name" >"$target.sha256"
  echo "PART_READY=$file_name SIZE=$(stat -c %s "$target")"
}

export -f filename_for wait_for_remote fetch_part
export transfer_key source_host source_dir part_dir workers prefix

seq 1 "$workers" |
  xargs -r -P "$workers" -n 1 bash -c 'fetch_part "$1"' _
download_rc=$?
echo "DOWNLOAD_PARALLEL_RC=$download_rc"
[[ "$download_rc" -eq 0 ]] || exit "$download_rc"

while true; do
  base_markers="$(
    find "$work_dir/markers" -maxdepth 1 -type f \
      -name 'bizdb-full-*-20261107.done' -printf x | wc -c
  )"
  echo "WAIT_BASELINE_MARKERS=$base_markers/16 $(date '+%F %T %Z')"
  (( base_markers >= 16 )) && break
  sleep 30
done

check_no_drop() {
  local file="$1"
  local hit
  hit="$(
    gzip -dc "$file" |
      grep -m 1 -E '^DROP[[:space:]]+DATABASE' || true
  )"
  if [[ -n "$hit" ]]; then
    echo "DROP_DATABASE_FOUND=$(basename "$file"):$hit"
    return 24
  fi
  echo "NO_DROP=$(basename "$file")"
}

export -f check_no_drop
seq 1 "$workers" |
  xargs -r -P "$workers" -n 1 \
    bash -c 'check_no_drop "$part_dir/$(filename_for "$1")"' _
drop_check_rc=$?
echo "DROP_CHECK_RC=$drop_check_rc"
[[ "$drop_check_rc" -eq 0 ]] || exit "$drop_check_rc"

event_scheduler_before="$(
  "$mysql_bin" --defaults-extra-file="$mysql_cnf" -N \
    -e "SELECT @@GLOBAL.event_scheduler"
)"
echo "EVENT_SCHEDULER_BEFORE=$event_scheduler_before"
"$mysql_bin" --defaults-extra-file="$mysql_cnf" \
  -e "SET GLOBAL event_scheduler=OFF"

echo "INCREMENTAL_START=$(date '+%F %T %Z') STOP_DATETIME=$stop_datetime"
set -o pipefail
for index in $(seq 1 "$workers"); do
  gzip -dc "$part_dir/$(filename_for "$index")"
done |
  "$mysql_bin" \
    --defaults-extra-file="$mysql_cnf" \
    --max-allowed-packet=268435456 \
    --binary-mode \
    --init-command="SET SESSION sql_log_bin=0"
import_rc=$?
echo "INCREMENTAL_RC=$import_rc"
echo "INCREMENTAL_FINISH=$(date '+%F %T %Z')"
exit "$import_rc"
````

#### `02_baseline_pitr/bizdb_filtered_pitr.sh`

**中文备注：** 按时间与对象范围过滤 PITR SQL，排除不允许重放的事件。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：02_baseline_pitr
# 中文备注：按时间与对象范围过滤 PITR SQL，排除不允许重放的事件。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# Export one 某业务平台 database from relay/binlogs up to a safe point in time.
#
# This script runs on the relay-log source host. It filters row events by
# database, splits the selected files into parallel ranges, and writes gzip
# streams to a remote staging host through SSH.
set -uo pipefail

database="${PGS_DATABASE:?PGS_DATABASE is required}"
relay_index="${PGS_RELAY_INDEX:-/data/mysql/data/sample-node-22-new-relay-bin.index}"
start_file="${PGS_START_FILE:-000003}"
start_position="${PGS_START_POSITION:-33270674}"
stop_file="${PGS_STOP_FILE:-000602}"
stop_datetime="${PGS_STOP_DATETIME:-2026-11-07 00:05:00}"
workers="${PGS_BINLOG_WORKERS:-8}"
mysqlbinlog="${PGS_MYSQLBINLOG:-/data/mysql/bin/mysqlbinlog}"
mysqlbinlog_sudo="${PGS_MYSQLBINLOG_SUDO:-1}"
transfer_key="${PGS_TRANSFER_KEY:-/tmp/.bizops-transfer-key}"
destination_host="${PGS_DESTINATION_HOST:?PGS_DESTINATION_HOST is required}"
destination_dir="${PGS_DESTINATION_DIR:?PGS_DESTINATION_DIR is required}"
work_dir="${PGS_FILTERED_WORK_DIR:-/tmp/bizops-filtered-pitr-$database}"
stamp="${PGS_EXPORT_STAMP:-$(date +%Y%m%d-%H%M%S)}"
output_prefix="${PGS_OUTPUT_PREFIX:-bizdb-pitr-bin-$database-$stamp}"

install -d -m 750 "$work_dir" "$work_dir/ranges" "$work_dir/logs"
selected="$work_dir/selected.tsv"
plan="$work_dir/plan.tsv"
: >"$selected"

while IFS= read -r path; do
  [[ "$path" != /* ]] && path="$(dirname "$relay_index")/${path#./}"
  number="${path##*.}"
  if [[ "$number" =~ ^[0-9]+$ ]] &&
     (( 10#$number >= 10#$start_file && 10#$number <= 10#$stop_file )); then
    size="$(
      if [[ "$mysqlbinlog_sudo" == "1" ]]; then
        sudo -n stat -c %s "$path"
      else
        stat -c %s "$path"
      fi
    )"
    printf '%s\t%s\t%s\n' "$number" "$size" "$path" >>"$selected"
  fi
done < <(
  if [[ "$mysqlbinlog_sudo" == "1" ]]; then
    sudo -n cat "$relay_index"
  else
    cat "$relay_index"
  fi
)

file_count="$(wc -l <"$selected")"
if (( file_count == 0 )); then
  echo "No relay files selected" >&2
  exit 20
fi
(( workers > file_count )) && workers="$file_count"

awk -F '\t' -v workers="$workers" '
  { size[NR]=$2; files[NR]=$3; total += $2 }
  END {
    target = int((total + workers - 1) / workers)
    range = 1
    used = 0
    for (i = 1; i <= NR; i++) {
      if (i > 1 && range < workers && used >= target) {
        range++
        used = 0
      }
      print range "\t" files[i]
      used += size[i]
    }
  }
' "$selected" >"$plan"

for index in $(seq 1 "$workers"); do
  awk -F '\t' -v part="$index" '$1 == part { print $2 }' "$plan" \
    >"$work_dir/ranges/$index.files"
done

export_one() {
  local index="$1"
  local output_name
  output_name="${output_prefix}-part-$(printf '%02d' "$index").sql.gz"
  local remote_path="${destination_dir%/}/$output_name"
  local log="$work_dir/logs/part-${index}.log"
  local args=(
    "--database=$database"
    --skip-gtids
    "--stop-datetime=$stop_datetime"
  )
  if (( index == 1 )); then
    args+=("--start-position=$start_position")
  fi

  {
    printf 'START=%s PART=%s FILES=%s\n' \
      "$(date '+%F %T %Z')" "$index" "$(wc -l <"$work_dir/ranges/$index.files")"
    mapfile -t files <"$work_dir/ranges/$index.files"
    set -o pipefail
    if [[ "$mysqlbinlog_sudo" == "1" ]]; then
      sudo -n "$mysqlbinlog" "${args[@]}" "${files[@]}"
    else
      "$mysqlbinlog" "${args[@]}" "${files[@]}"
    fi |
      gzip -1 |
      ssh -i "$transfer_key" \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        -o ConnectTimeout=15 \
        "root@$destination_host" "cat > '$remote_path'"
    local rc=${PIPESTATUS[*]}
    printf 'PIPE_RC=%s\n' "$rc"
    if [[ "${rc// /}" =~ ^0+$ ]]; then
      ssh -i "$transfer_key" \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        -o ConnectTimeout=15 \
        "root@$destination_host" \
        "gzip -t '$remote_path' && sha256sum '$remote_path' && touch '$remote_path.done'"
      printf 'VERIFY_RC=%s\n' "$?"
    fi
    printf 'FINISH=%s\n' "$(date '+%F %T %Z')"
  } >"$log" 2>&1
}

export -f export_one
export database start_position stop_datetime mysqlbinlog mysqlbinlog_sudo
export transfer_key destination_host destination_dir work_dir output_prefix

for index in $(seq 1 "$workers"); do
  export_one "$index" &
done
wait

if find "$work_dir/logs" -type f -name 'part-*.log' -exec grep -L 'VERIFY_RC=0' {} + |
   grep -q .; then
  echo "One or more filtered PITR parts failed verification" >&2
  exit 21
fi

echo "Filtered PITR export complete: $work_dir"
````

#### `02_baseline_pitr/bizdb_user_accounts_my2sql_apply.sh`

**中文备注：** 用户核心表 my2sql 结果的批量回放入口。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：02_baseline_pitr
# 中文备注：用户核心表 my2sql 结果的批量回放入口。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# Replay 某业务平台 core user-table DML into an isolated MySQL database.
#
# Run on the host that owns the recovery MySQL container. The source archives
# must already exist in PGS_ARCHIVE_DIR. The target database name must contain
# "_test_" and must not already exist unless PGS_RECREATE_TEST_DB=1 is set.
set -uo pipefail

container="${PGS_MYSQL_CONTAINER:-bizops-bizdb-pitr57}"
source_database="${PGS_SOURCE_DATABASE:-users_db}"
baseline_archive="${PGS_BASELINE_ARCHIVE:-}"
target_database="${PGS_TARGET_DATABASE:?PGS_TARGET_DATABASE is required}"
archive_dir="${PGS_ARCHIVE_DIR:-/root/vendor_a-zips}"
archive_prefix="${PGS_ARCHIVE_PREFIX:-users_db-20261107-0005-core-sql-part}"
workers="${PGS_BINLOG_WORKERS:-8}"
work_dir="${PGS_APPLY_WORK_DIR:-/data/bizops-bizdb-restore/my2sql-user_accounts-0005}"
parallel_apply="${PGS_PARALLEL_APPLY_SCRIPT:-$work_dir/bizdb_my2sql_apply_parallel.py}"

[[ "$target_database" == *_test_* ]] || {
  echo "Refusing non-test target database: $target_database" >&2
  exit 20
}

install -d -m 750 "$work_dir" "$work_dir/extract"
exec > >(tee -a "$work_dir/apply.log") 2>&1

for index in $(seq 1 "$workers"); do
  archive="$archive_dir/$archive_prefix-$(printf '%02d' "$index").tar.gz"
  [[ -s "$archive" ]] || {
    echo "Missing archive: $archive" >&2
    exit 21
  }
  gzip -t "$archive" || exit 22
done
echo "ARCHIVE_VERIFY_OK count=$workers"

exists="$(
  docker exec "$container" mysql -uadmin -N \
    -e "SHOW DATABASES LIKE '$target_database'"
)"
if [[ -n "$exists" ]]; then
  [[ "${PGS_RECREATE_TEST_DB:-0}" == "1" ]] || {
    echo "Target database already exists: $target_database" >&2
    exit 23
  }
  docker exec "$container" mysql -uadmin \
    -e "DROP DATABASE \`$target_database\`"
fi

docker exec "$container" mysql -uadmin \
  --default-character-set=utf8mb4 \
  -e "CREATE DATABASE \`$target_database\` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
if [[ -n "$baseline_archive" ]]; then
  [[ -s "$baseline_archive" ]] || {
    echo "Missing baseline archive: $baseline_archive" >&2
    exit 26
  }
  gzip -t "$baseline_archive" || exit 27
  gzip -dc "$baseline_archive" |
    sed -E "s/\`$source_database\`/\`$target_database\`/g" |
    docker exec -i "$container" mysql -uadmin --default-character-set=utf8mb4
else
  docker exec "$container" sh -lc \
    "mysqldump -uroot --default-character-set=utf8mb4 --routines --events --triggers '$source_database' | mysql -uadmin --default-character-set=utf8mb4 '$target_database'"
fi
baseline_rc=$?
echo "BASELINE_COPY_RC=$baseline_rc"
(( baseline_rc == 0 )) || exit "$baseline_rc"

# my2sql emits only changed values. Disable implicit ON UPDATE behavior while
# replaying so a statement that did not change its timestamp column keeps the
# baseline value instead of adopting the recovery host's current time.
docker exec "$container" mysql -uadmin --default-character-set=utf8mb4 -e "
  ALTER TABLE \`$target_database\`.\`user_account\`
    MODIFY \`last_update_time\` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP;
  ALTER TABLE \`$target_database\`.\`user_bind\`
    MODIFY \`last_update_time\` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP;
  ALTER TABLE \`$target_database\`.\`user_payment\`
    MODIFY \`update_time\` datetime DEFAULT CURRENT_TIMESTAMP;
  ALTER TABLE \`$target_database\`.\`user_level\`
    MODIFY \`update_time\` timestamp NULL DEFAULT NULL;
"
echo "TIMESTAMP_AUTOUPDATE_DISABLED_RC=$?"

rm -rf "$work_dir/extract"
install -d -m 750 "$work_dir/extract"
for index in $(seq 1 "$workers"); do
  archive="$archive_dir/$archive_prefix-$(printf '%02d' "$index").tar.gz"
  part_dir="$work_dir/extract/$index"
  install -d -m 750 "$part_dir"
  tar -C "$part_dir" -xzf "$archive"
done

mapfile -t sql_files < <(
  find "$work_dir/extract" -type f -name 'forward.*.sql' -printf '%f\t%p\n' |
    sort -t. -k2,2n
)
(( ${#sql_files[@]} > 0 )) || {
  echo "No DML files found" >&2
  exit 24
}

ddl_hits="$(
  while IFS=$'\t' read -r _ path; do
    grep -Ei '^(CREATE|ALTER|DROP|TRUNCATE)[[:space:]]' "$path" || true
  done < <(printf '%s\n' "${sql_files[@]}") |
    head -1
)"
[[ -z "$ddl_hits" ]] || {
  echo "Unexpected DDL in DML input: $ddl_hits" >&2
  exit 25
}
echo "DML_FILES=${#sql_files[@]} DDL_CHECK=ok"

[[ -s "$parallel_apply" ]] || {
  echo "Missing parallel apply script: $parallel_apply" >&2
  exit 28
}
python3 "$parallel_apply" \
  --input-dir "$work_dir/extract" \
  --source-db "$source_database" \
  --target-db "$target_database" \
  --container "$container" \
  --workers "$workers"
replay_rc=$?
echo "DML_REPLAY_RC=$replay_rc"
(( replay_rc == 0 )) || exit "$replay_rc"

docker exec "$container" mysql -uadmin --default-character-set=utf8mb4 -e "
  ALTER TABLE \`$target_database\`.\`user_account\`
    MODIFY \`last_update_time\` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP;
  ALTER TABLE \`$target_database\`.\`user_bind\`
    MODIFY \`last_update_time\` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP;
  ALTER TABLE \`$target_database\`.\`user_payment\`
    MODIFY \`update_time\` datetime DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP;
  ALTER TABLE \`$target_database\`.\`user_level\`
    MODIFY \`update_time\` timestamp NULL DEFAULT NULL
    ON UPDATE CURRENT_TIMESTAMP;
"
restore_rc=$?
echo "TIMESTAMP_AUTOUPDATE_RESTORED_RC=$restore_rc"
exit "$restore_rc"
````

#### `02_baseline_pitr/bizdb_my2sql_apply_parallel.py`

**中文备注：** 用户核心表按 UID 稳定分片并并行回放。

````python
#!/usr/bin/env python3
# ============================================================================
# 平台：某业务平台
# 恢复阶段：02_baseline_pitr
# 中文备注：用户核心表按 UID 稳定分片并并行回放。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
"""Apply time-ordered my2sql DML with per-UID parallelism."""

from __future__ import annotations

import argparse
import collections
import csv
import io
import os
import re
import subprocess
import sys
import time
from pathlib import Path


INSERT_RE = re.compile(
    r"^INSERT INTO `([^`]+)`\.`([^`]+)` \((.*?)\) VALUES \((.*)\);\s*$"
)
UPDATE_RE = re.compile(r"^UPDATE `([^`]+)`\.`([^`]+)` ")
DELETE_RE = re.compile(r"^DELETE FROM `([^`]+)`\.`([^`]+)` ")
UID_WHERE_RE = re.compile(r" WHERE `uid`=(\d+)\s*;\s*$")
ID_WHERE_RE = re.compile(r" WHERE `id`=(\d+)\s*;\s*$")


def statement_identity(sql: str) -> tuple[str, str]:
    for operation, pattern in (
        ("INSERT", INSERT_RE),
        ("UPDATE", UPDATE_RE),
        ("DELETE", DELETE_RE),
    ):
        match = pattern.match(sql)
        if match:
            return operation, match.group(2)
    raise ValueError("unrecognized SQL statement")


def split_sql_list(value: str) -> list[str]:
    rows = next(csv.reader(io.StringIO(value), quotechar="'", escapechar="\\"))
    return [row.strip() for row in rows]


def shard_for(sql: str, source_db: str, workers: int) -> int:
    match = INSERT_RE.match(sql)
    if match:
        schema, _table, columns_raw, values_raw = match.groups()
        if schema != source_db:
            raise ValueError(f"unexpected INSERT schema: {schema}")
        columns = [item.strip("` ") for item in split_sql_list(columns_raw)]
        values = split_sql_list(values_raw)
        if len(columns) != len(values):
            raise ValueError("INSERT column/value count mismatch")
        try:
            uid = int(values[columns.index("uid")])
        except (ValueError, IndexError) as exc:
            raise ValueError("INSERT without numeric uid") from exc
        return uid % workers

    match = UPDATE_RE.match(sql) or DELETE_RE.match(sql)
    if match:
        schema, _table = match.groups()
        if schema != source_db:
            raise ValueError(f"unexpected UPDATE/DELETE schema: {schema}")
        match_uid = UID_WHERE_RE.search(sql)
        if match_uid:
            return int(match_uid.group(1)) % workers
        match_id = ID_WHERE_RE.search(sql)
        if match_id:
            return int(match_id.group(1)) % workers
        raise ValueError("DML without uid/id predicate")
    raise ValueError("unexpected SQL statement")


def sql_files(root: Path) -> list[Path]:
    files = list(root.rglob("forward.*.sql"))
    files.sort(key=lambda path: int(path.stem.split(".")[1]))
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--source-db", default="users_db")
    parser.add_argument("--target-db", required=True)
    parser.add_argument("--container", default="bizops-bizdb-pitr57")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--commit-every", type=int, default=5000)
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Validate and summarize DML without opening MySQL workers.",
    )
    args = parser.parse_args()

    if args.workers < 1:
        raise SystemExit("workers must be positive")
    if "_test_" not in args.target_db:
        raise SystemExit("refusing non-test target database")

    files = sql_files(args.input_dir)
    if not files:
        raise SystemExit("no forward SQL files found")

    # Verify the complete input before sending any statement.
    statement_count = 0
    operation_counts: collections.Counter = collections.Counter()
    for path in files:
        with path.open("r", encoding="utf-8", errors="strict") as stream:
            for line_no, raw in enumerate(stream, 1):
                sql = raw.rstrip("\n")
                if not sql or sql.startswith("--"):
                    continue
                if re.match(r"^(CREATE|ALTER|DROP|TRUNCATE)\b", sql, re.I):
                    raise SystemExit(f"unexpected DDL at {path}:{line_no}")
                if not (sql.startswith("INSERT ") or sql.startswith("UPDATE ")
                        or sql.startswith("DELETE ")):
                    raise SystemExit(f"unexpected statement at {path}:{line_no}")
                shard_for(sql, args.source_db, args.workers)
                operation_counts[statement_identity(sql)] += 1
                statement_count += 1
    print(f"INPUT_VERIFY_OK files={len(files)} statements={statement_count}", flush=True)
    for (operation, table), count in sorted(operation_counts.items()):
        print(f"INPUT_TABLE {operation} {table} {count}", flush=True)
    if args.verify_only:
        return 0

    command = [
        "docker",
        "exec",
        "-i",
        args.container,
        "mysql",
        "-uroot",
        "--default-character-set=utf8mb4",
        "--max-allowed-packet=268435456",
        "--binary-mode",
        "--init-command=SET SESSION sql_log_bin=0; SET SESSION foreign_key_checks=0; SET autocommit=0;",
    ]
    children: list[subprocess.Popen[bytes]] = []
    logs = []
    for index in range(args.workers):
        log_path = Path(f"/tmp/bizdb-my2sql-apply-worker-{index}.log")
        log = log_path.open("wb")
        logs.append(log)
        child = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        children.append(child)

    def write(index: int, sql: str) -> None:
        child = children[index]
        assert child.stdin is not None
        transformed = sql.replace(
            f"`{args.source_db}`.", f"`{args.target_db}`.", 1
        )
        if transformed.startswith("INSERT INTO "):
            transformed = transformed.replace("INSERT INTO ", "INSERT IGNORE INTO ", 1)
        child.stdin.write((transformed + "\n").encode("utf-8"))

    sent = 0
    pending = [0] * args.workers
    started = time.time()
    try:
        for path in files:
            with path.open("r", encoding="utf-8", errors="strict") as stream:
                for raw in stream:
                    sql = raw.rstrip("\n")
                    if not sql or sql.startswith("--"):
                        continue
                    index = shard_for(sql, args.source_db, args.workers)
                    write(index, sql)
                    pending[index] += 1
                    sent += 1
                    if pending[index] >= args.commit_every:
                        assert children[index].stdin is not None
                        children[index].stdin.write(b"COMMIT;\n")
                        pending[index] = 0
                    if sent % 100000 == 0:
                        elapsed = max(time.time() - started, 1)
                        print(
                            f"REPLAY_PROGRESS {sent}/{statement_count} "
                            f"({sent / statement_count * 100:.1f}%) "
                            f"rate={sent / elapsed:.0f}/s",
                            flush=True,
                        )
        for index, child in enumerate(children):
            assert child.stdin is not None
            child.stdin.write(b"COMMIT;\n")
            child.stdin.close()

        failed = []
        for index, child in enumerate(children):
            rc = child.wait()
            if rc:
                failed.append((index, rc))
            logs[index].close()
        if failed:
            raise SystemExit(f"MySQL worker failures: {failed}")
    except Exception:
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
        raise

    print(
        f"REPLAY_OK files={len(files)} statements={sent} "
        f"seconds={time.time() - started:.1f}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
````

### 8.3 03_table_parallel 小表与表级并行

按表组装 SQL、备份、按表并发回放，并支持 done 标记断点续跑。

#### `03_table_parallel/bizdb_small_table_backup.sh`

**中文备注：** 回放前逐表 mysqldump 备份，失败时禁止继续写库。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：03_table_parallel
# 中文备注：回放前逐表 mysqldump 备份，失败时禁止继续写库。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# ============================================================================
# 某业务平台数据库恢复工具：回放前逐表备份
# ----------------------------------------------------------------------------
# 输入 tables.tsv 每行两列：数据库名、表名。
# 使用 mysqldump --single-transaction 获取一致性快照，并立即 gzip。
# 只有压缩包非空且 gzip -t 校验成功，才写入 BACKUP_OK；
# 失败会写 BACKUP_FAIL，调用方应停止后续写库。
# ============================================================================
set -uo pipefail

base="${PGS_SMALL_BACKUP_DIR:-/data/bizops-small-export/backups/pre-apply-20261109}"
tables_tsv="${PGS_SMALL_TABLE_LIST:-$base/tables.tsv}"
workers="${PGS_SMALL_BACKUP_WORKERS:-4}"
dump_bin="${PGS_MYSQLDUMP_BIN:-/data/mysql/bin/mysqldump}"
defaults_file="${PGS_TARGET_CNF:-/root/.bizops-target.cnf}"
log="$base/backup.log"

install -d -m 750 "$base"
printf 'START=%s WORKERS=%s\n' "$(date '+%F %T %Z')" "$workers" >"$log"

backup_one() {
  # 单表备份；先写 .part，校验成功后再原子改名，避免留下“看似成功”的坏文件。
  local database="$1"
  local table="$2"
  local output="$base/${database}.${table}.sql.gz"
  local temporary="${output}.part"
  local rc

  sudo -n "$dump_bin" \
    --defaults-extra-file="$defaults_file" \
    --single-transaction --quick --skip-lock-tables \
    --routines --triggers --hex-blob --set-gtid-purged=OFF \
    --add-drop-table "$database" "$table" |
    gzip -1 >"$temporary"
  rc=$?
  if (( rc == 0 )) && [[ -s "$temporary" ]] && gzip -t "$temporary"; then
    mv -f "$temporary" "$output"
    printf 'BACKUP_OK=%s.%s SIZE=%s\n' \
      "$database" "$table" "$(stat -c %s "$output")" >>"$log"
  else
    rm -f "$temporary"
    printf 'BACKUP_FAIL=%s.%s RC=%s\n' "$database" "$table" "$rc" >>"$log"
  fi
}

export -f backup_one
export base dump_bin defaults_file log

awk -F '\t' 'NF == 2 { print $1 "\t" $2 }' "$tables_tsv" |
  xargs -r -P "$workers" -n 2 bash -c 'backup_one "$1" "$2"' _
rc=$?
printf 'FINISH=%s RC=%s\n' "$(date '+%F %T %Z')" "$rc" >>"$log"
exit "$rc"
````

#### `03_table_parallel/bizdb_wait_and_apply_small.sh`

**中文备注：** 等待源端导出完成、下载校验、解压并自动启动表级回放。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：03_table_parallel
# 中文备注：等待源端导出完成、下载校验、解压并自动启动表级回放。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# ============================================================================
# 某业务平台数据库恢复工具：等待导出、下载校验、解压并启动表级回放
# ----------------------------------------------------------------------------
# 执行链：
#   1. 等待中转机上的 COMPLETE/FAILED 标记；
#   2. 下载 exported_archive_part-*.tar.gz；
#   3. 对每个包执行 gzip 校验；
#   4. 解压到 extracted/part-*；
#   5. 调用统一表级回放脚本。
# 本脚本只负责搬运和编排，不直接解释 SQL。
# ============================================================================
set -uo pipefail

stamp="${某业务平台_SMALL_STAMP:-20261109-p3}"
base="${某业务平台_SMALL_INCOMING_DIR:-/data/bizops-small-export/incoming/$stamp}"
ops_host="${PGS_TRANSFER_HOST:-root@192.0.2.38}"
ops_dir="${PGS_TRANSFER_DIR:-/root/vendor_a-zips}"
key="${PGS_TRANSFER_KEY:-/tmp/.bizops-transfer-key}"
workers="${某业务平台_SMALL_EXPORT_WORKERS:-8}"
apply_script="${某业务平台_SMALL_APPLY_SCRIPT:-/tmp/bizdb_apply_small_table_sql.sh}"
export_name="${某业务平台_SMALL_EXPORT_NAME:-bizdb-small-multidb}"
marker_prefix="$ops_dir/$export_name-$stamp"
archive_prefix="$export_name-$stamp-part"
log="$base/wait-apply.log"

install -d -m 750 "$base"
if [[ -e "$base/pipeline.pid" ]] &&
   kill -0 "$(cat "$base/pipeline.pid")" 2>/dev/null; then
  echo "pipeline already running"
  exit 0
fi
printf '%s\n' "$$" >"$base/pipeline.pid"
printf 'WAIT_START=%s STAMP=%s\n' "$(date '+%F %T %Z')" "$stamp" >"$log"

ssh_opts=(
  -i "$key"
  -o BatchMode=yes
  -o StrictHostKeyChecking=no
  -o UserKnownHostsFile=/dev/null
  -o ConnectTimeout=15
)

while true; do
  # 失败标记优先退出；只有 COMPLETE 且包数量完整才进入下载阶段。
  if ssh "${ssh_opts[@]}" "$ops_host" "test -e '$marker_prefix.FAILED'" \
       >/dev/null 2>&1; then
    printf 'EXPORT_FAILED_MARKER=%s\n' "$(date '+%F %T %Z')" >>"$log"
    exit 30
  fi
  if ssh "${ssh_opts[@]}" "$ops_host" "test -e '$marker_prefix.COMPLETE'" \
       >/dev/null 2>&1; then
    count="$(
      ssh "${ssh_opts[@]}" "$ops_host" \
        "ls -1 '$ops_dir/$archive_prefix-'*.tar.gz 2>/dev/null | wc -l" \
        2>/dev/null | tail -n 1 | tr -cd '0-9'
    )"
    count="${count:-0}"
    printf 'EXPORT_COMPLETE=%s ARCHIVES=%s/%s\n' \
      "$(date '+%F %T %Z')" "$count" "$workers" >>"$log"
    [[ "$count" -eq "$workers" ]] && break
  fi
  printf 'WAITING=%s\n' "$(date '+%F %T %Z')" >>"$log"
  sleep 30
done

extract_root="$base/extracted"
install -d -m 750 "$extract_root"
for raw_index in $(seq 1 "$workers"); do
  # 每个分片独立下载并校验，避免一个坏包被静默解压。
  printf -v index '%02d' "$raw_index"
  archive="$archive_prefix-$index.tar.gz"
  local_archive="$base/$archive"
  part_dir="$extract_root/part-$index"
  install -d -m 750 "$part_dir"
  if [[ ! -s "$local_archive" ]]; then
    scp "${ssh_opts[@]}" "$ops_host:$ops_dir/$archive" "$local_archive"
    rc=$?
    printf 'DOWNLOAD=%s RC=%s\n' "$archive" "$rc" >>"$log"
    (( rc == 0 )) || exit 31
  fi
  gzip -t "$local_archive"
  rc=$?
  printf 'GZIP=%s RC=%s\n' "$archive" "$rc" >>"$log"
  (( rc == 0 )) || exit 32
  tar -C "$part_dir" -xzf "$local_archive"
  rc=$?
  printf 'EXTRACT=%s RC=%s\n' "$archive" "$rc" >>"$log"
  (( rc == 0 )) || exit 33
done

printf 'REPLAY_START=%s\n' "$(date '+%F %T %Z')" >>"$log"
# 后续交给表级回放器；锁、备份、SQL 黑名单和参数恢复均在该脚本中完成。
某业务平台_SMALL_APPLY_ROOT="$base/apply" \
某业务平台_SMALL_EXTRACT_ROOT="$extract_root" \
某业务平台_SMALL_APPLY_WORKERS="${某业务平台_SMALL_APPLY_WORKERS:-8}" \
  "$apply_script" >>"$log" 2>&1
rc=$?
printf 'REPLAY_FINISH=%s RC=%s\n' "$(date '+%F %T %Z')" "$rc" >>"$log"
exit "$rc"
````

#### `03_table_parallel/bizdb_apply_small_table_sql.sh`

**中文备注：** 主表级并发回放器；小表优先、同表保序、INSERT IGNORE、事务参数自动恢复。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：03_table_parallel
# 中文备注：主表级并发回放器；小表优先、同表保序、INSERT IGNORE、事务参数自动恢复。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# ============================================================================
# 某业务平台数据库恢复工具：多表并发回放
# ----------------------------------------------------------------------------
# 用途：
#   将 my2sql 按 relay 文件切出的 SQL 片段，按“数据库.表”重新拼成单表文件，
#   然后让不同表并发回放。每张表内部严格保持 binlog 顺序。
#
# 关键行为：
#   1. 自动排除 YYYYMMDD 日期分区表和指定历史表；
#   2. 先备份、再回放，支持断点 done 标记；
#   3. INSERT 改成 INSERT IGNORE；UPDATE/DELETE 按原顺序执行；
#   4. 回放前临时移除 ON UPDATE CURRENT_TIMESTAMP，避免历史时间被刷新；
#   5. 回放期间临时 flush=2、关闭 event_scheduler，退出时恢复原值；
#   6. 支持复用已拼好的 SQL，断点续跑时不用重复组装几十 GB 文件。
#
# 输入目录通常为：
#   /data/bizops-small-export/incoming/<stamp>/extracted/part-*
# 输出目录通常为：
#   /data/bizops-small-export/incoming/<stamp>/apply/{combined,runs}
# ============================================================================
set -uo pipefail

# ---- 路径、并发和数据库客户端配置 ----
root="${某业务平台_SMALL_APPLY_ROOT:-/data/bizops-small-export/apply}"
extract_root="${某业务平台_SMALL_EXTRACT_ROOT:-$root/extracted}"
combined_dir="${某业务平台_SMALL_COMBINED_DIR:-$root/combined}"
run_dir="${某业务平台_SMALL_RUN_DIR:-$root/runs}"
workers="${某业务平台_SMALL_APPLY_WORKERS:-8}"
case "$root" in
  */20261109-p5/apply|*/20261109-p6/apply)
    workers="${某业务平台_SMALL_HIGH_CONCURRENCY_WORKERS:-16}"
    ;;
esac
mysql_bin="${PGS_MYSQL_BIN:-/data/mysql/bin/mysql}"
defaults_file="${PGS_TARGET_CNF:-/root/.bizops-target.cnf}"
backup_dir="${某业务平台_SMALL_BACKUP_DIR:-}"
restore_before_replay="${某业务平台_SMALL_RESTORE_BEFORE_REPLAY:-0}"
log="$root/apply.log"

install -d -m 750 "$root" "$combined_dir" "$run_dir"
printf 'ASSEMBLE_START=%s\n' "$(date '+%F %T %Z')" >"$log"

# 全局 flock：同一时刻只允许一个写库任务操作同一个恢复目标，
# 避免多个回放器同时改 ON UPDATE/event_scheduler 等全局参数。
lock_file="${某业务平台_SMALL_APPLY_LOCK:-/data/bizops-small-export/apply.lock}"
exec 9>"$lock_file"
flock 9
printf 'APPLY_LOCK_ACQUIRED=%s\n' "$(date '+%F %T %Z')" >>"$log"

# ---- 生成待回放表清单 ----
# 日期分区表（表名包含 8 位日期）不进入本次恢复；
# contest、record_log 默认延后，由专用追加入口处理。
manifest="$root/tables.list"
find "$extract_root" -type f -name '*.forward.[0-9]*.sql' -printf '%f\n' |
  sed -E 's/\.forward\.[0-9]+\.sql$//' |
  sort -u |
  grep -Ev '[0-9]{8}|_bak_[0-9]{4}$' |
  { if [[ "${某业务平台_SMALL_ALLOW_DEFERRED:-0}" == "1" ]]; then
      cat
    else
      grep -Ev '(^|\.)contest$|(^|\.)record_log$'
    fi; } \
  >"$manifest"

[[ -s "$manifest" ]] || {
  echo "No replayable table files found under $extract_root" >&2
  exit 20
}

while IFS= read -r table; do
  target="$combined_dir/$table.sql"
  temporary="$target.part"
  # 续跑时可直接复用完整 SQL；避免重新拼接上百 GB 数据。
  if [[ "${某业务平台_SMALL_REUSE_COMBINED:-0}" == "1" && -s "$target" ]]; then
    printf 'TABLE_REUSED=%s SIZE=%s\n' \
      "$table" "$(stat -c %s "$target")" >>"$log"
    continue
  fi
  : >"$temporary"
  for part_dir in "$extract_root"/part-*; do
    [[ -d "$part_dir" ]] || continue
    find "$part_dir" -maxdepth 1 -type f -name "$table.forward.[0-9]*.sql" \
      -print0 |
      sort -z -V |
      xargs -0 -r cat >>"$temporary"
  done
  if [[ -s "$temporary" ]]; then
    mv -f "$temporary" "$target"
    printf 'TABLE_ASSEMBLED=%s SIZE=%s\n' \
      "$table" "$(stat -c %s "$target")" >>"$log"
  else
    rm -f "$temporary"
  fi
done <"$manifest"

# ---- 小表优先，缩短首批可用数据的等待时间 ----
ordered="$root/tables-by-size.list"
while IFS= read -r table; do
  file="$combined_dir/$table.sql"
  [[ -s "$file" ]] || continue
  size="$(stat -c %s "$file")"
  printf '%020d\t%s\n' "$size" "$table"
done <"$manifest" |
  sort -n |
  cut -f2- >"$ordered"

(( $(wc -l <"$ordered") > 0 )) || {
  echo "No non-empty table SQL produced" >&2
  exit 21
}

# 回放前做 DDL/DROP/TRUNCATE 黑名单检查；复用模式假定首次组装时已检查。
if [[ "${某业务平台_SMALL_REUSE_COMBINED:-0}" == "1" ]]; then
  printf 'DDL_SCAN_REUSED=1\n' >>"$log"
else
  if grep -Il -E '^[[:space:]]*(CREATE|ALTER|DROP|TRUNCATE)[[:space:]]' \
      "$combined_dir"/*.sql >/dev/null; then
    echo "DDL/DROP/TRUNCATE statement found; refusing to replay" >&2
    exit 22
  fi
fi

apply_one() {
  # 单表回放函数：
  #   - 同一张表只由一个 worker 处理，因此表内事件顺序绝对不变；
  #   - INSERT IGNORE 用于重复执行时安全跳过已有行；
  #   - 只要出现任何 SQL ERROR，就不写 done 标记，交由后续核验重跑。
  local table="$1"
  local sql_file="$combined_dir/$table.sql"
  local table_log="$run_dir/$table.log"
  local done_file="$run_dir/$table.done"

  [[ -s "$sql_file" ]] || return 0
  [[ -e "$done_file" ]] && return 0

  printf 'TABLE_START=%s TIME=%s\n' \
    "$table" "$(date '+%F %T %Z')" >"$table_log"
  awk '
    substr($0, 1, 12) == "INSERT INTO " {
      print "INSERT IGNORE INTO " substr($0, 13)
      next
    }
    { print }
  ' "$sql_file" |
    sudo -n "$mysql_bin" \
      --defaults-extra-file="$defaults_file" \
      --max-allowed-packet=1073741824 \
      --binary-mode \
      --force \
      --init-command='SET SESSION sql_log_bin=0; SET SESSION foreign_key_checks=0; SET SESSION unique_checks=0; SET SESSION autocommit=1' \
      >>"$table_log" 2>&1
  local rc=$?
  local error_count
  error_count="$(grep -c '^ERROR ' "$table_log" 2>/dev/null || true)"
  error_count="${error_count:-0}"
  printf 'TABLE_RC=%s TABLE=%s SQL_ERRORS=%s TIME=%s\n' \
    "$rc" "$table" "$error_count" "$(date '+%F %T %Z')" >>"$table_log"
  if (( rc == 0 && error_count == 0 )); then
    printf '%s\n' "$(date '+%F %T %Z')" >"$done_file"
  else
    (( rc != 0 )) || rc=40
  fi
  return "$rc"
}

export -f apply_one
export combined_dir run_dir mysql_bin defaults_file

table_values="$(
  awk 'BEGIN { first=1 } {
    if (!first) printf ","
    printf "\047%s\047", $0
    first=0
  } END { print "" }' "$manifest"
)"
guard_generator="$root/on-update-generator.sql"
drop_guard="$root/drop-on-update.sql"
restore_guard="$root/restore-on-update.sql"
cat >"$guard_generator" <<'SQL'
SELECT
 CONCAT('ALTER TABLE `',TABLE_SCHEMA,'`.`',TABLE_NAME,
        '` MODIFY COLUMN `',COLUMN_NAME,'` ',COLUMN_TYPE,
   IF(IS_NULLABLE='YES',' NULL',' NOT NULL'),
   CASE WHEN COLUMN_DEFAULT IS NULL AND IS_NULLABLE='YES' THEN ' DEFAULT NULL'
        WHEN COLUMN_DEFAULT IS NULL THEN ''
        WHEN COLUMN_DEFAULT LIKE 'CURRENT_TIMESTAMP%'
          THEN CONCAT(' DEFAULT ',COLUMN_DEFAULT)
        ELSE CONCAT(' DEFAULT ',QUOTE(COLUMN_DEFAULT)) END,
   IF(COLUMN_COMMENT='','',CONCAT(' COMMENT ',QUOTE(COLUMN_COMMENT))),
   ';'),
 CONCAT('ALTER TABLE `',TABLE_SCHEMA,'`.`',TABLE_NAME,
        '` MODIFY COLUMN `',COLUMN_NAME,'` ',COLUMN_TYPE,
   IF(IS_NULLABLE='YES',' NULL',' NOT NULL'),
   CASE WHEN COLUMN_DEFAULT IS NULL AND IS_NULLABLE='YES' THEN ' DEFAULT NULL'
        WHEN COLUMN_DEFAULT IS NULL THEN ''
        WHEN COLUMN_DEFAULT LIKE 'CURRENT_TIMESTAMP%'
          THEN CONCAT(' DEFAULT ',COLUMN_DEFAULT)
        ELSE CONCAT(' DEFAULT ',QUOTE(COLUMN_DEFAULT)) END,
   ' ON UPDATE ',SUBSTRING_INDEX(EXTRA,'on update ',-1),
   IF(COLUMN_COMMENT='','',CONCAT(' COMMENT ',QUOTE(COLUMN_COMMENT))),
   ';')
FROM information_schema.columns
WHERE CONCAT(TABLE_SCHEMA,'.',TABLE_NAME) IN (__TABLES__)
  AND EXTRA LIKE '%on update%'
ORDER BY TABLE_SCHEMA,TABLE_NAME,ORDINAL_POSITION;
SQL
sed -i "s|__TABLES__|$table_values|" "$guard_generator"
sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" -N --batch \
  <"$guard_generator" |
  awk -F '\t' '{ print $1 }' >"$drop_guard"
sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" -N --batch \
  <"$guard_generator" |
  awk -F '\t' '{ print $2 }' >"$restore_guard"
printf 'ON_UPDATE_GUARD_COLUMNS=%s\n' \
  "$(wc -l <"$drop_guard")" >>"$log"

restore_one() {
  # 从回放前 mysqldump 备份恢复单表，用于失败的未完成表重新开始。
  local table="$1"
  local database="${table%%.*}"
  local table_name="${table#*.}"
  local archive="$backup_dir/$table.sql.gz"

  [[ -s "$archive" ]] || {
    printf 'BACKUP_MISSING=%s\n' "$table" >>"$log"
    return 41
  }
  gzip -dc "$archive" |
    sudo -n "$mysql_bin" \
      --defaults-extra-file="$defaults_file" \
      --max-allowed-packet=1073741824 \
      --init-command='SET SESSION sql_log_bin=0; SET SESSION foreign_key_checks=0' \
      "$database" >>"$log" 2>&1
}

export -f restore_one
export backup_dir log

if [[ "$restore_before_replay" == "1" ]]; then
  [[ -n "$backup_dir" && -d "$backup_dir" ]] || {
    echo "Backup directory is required before replay" >&2
    exit 23
  }
  printf 'RESTORE_START=%s TABLES=%s\n' \
    "$(date '+%F %T %Z')" "$(wc -l <"$ordered")" >>"$log"
  xargs -r -P "$workers" -n 1 bash -c 'restore_one "$1"' _ <"$ordered"
  rc=$?
  printf 'RESTORE_FINISH=%s RC=%s\n' "$(date '+%F %T %Z')" "$rc" >>"$log"
  (( rc == 0 )) || exit "$rc"
fi

printf 'APPLY_START=%s WORKERS=%s TABLES=%s\n' \
  "$(date '+%F %T %Z')" "$workers" "$(wc -l <"$ordered")" >>"$log"
printf '• 回放开始：%s 张表，%s 并发\n' \
  "$(wc -l <"$ordered")" "$workers"

flush_before="$(
  sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" -N \
    -e 'SELECT @@GLOBAL.innodb_flush_log_at_trx_commit'
)"
event_scheduler_before="$(
  sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" -N \
    -e 'SELECT @@GLOBAL.event_scheduler'
)"
printf 'FLUSH_BEFORE=%s\n' "$flush_before" >>"$log"
printf 'EVENT_SCHEDULER_BEFORE=%s\n' "$event_scheduler_before" >>"$log"
restore_runtime_settings() {
  # 无论正常完成、异常退出还是人工中断，都恢复原表结构和服务参数。
  sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" \
    <"$restore_guard" >>"$log" 2>&1
  sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" \
    -e "SET GLOBAL innodb_flush_log_at_trx_commit=$flush_before" \
    >>"$log" 2>&1
  sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" \
    -e "SET GLOBAL event_scheduler=$event_scheduler_before" \
    >>"$log" 2>&1
  printf 'FLUSH_RESTORED=%s TIME=%s\n' \
    "$flush_before" "$(date '+%F %T %Z')" >>"$log"
  printf 'EVENT_SCHEDULER_RESTORED=%s TIME=%s\n' \
    "$event_scheduler_before" "$(date '+%F %T %Z')" >>"$log"
  printf 'ON_UPDATE_GUARD_RESTORED=%s\n' \
    "$(date '+%F %T %Z')" >>"$log"
}
trap restore_runtime_settings EXIT
sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" \
  -e 'SET GLOBAL innodb_flush_log_at_trx_commit=2' >>"$log" 2>&1
sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" \
  -e 'SET GLOBAL event_scheduler=OFF' >>"$log" 2>&1
printf 'FLUSH_DURING_APPLY=2\n' >>"$log"
printf 'EVENT_SCHEDULER_DURING_APPLY=OFF\n' >>"$log"

sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" \
  <"$drop_guard" >>"$log" 2>&1
printf 'ON_UPDATE_GUARD_APPLIED=%s\n' "$(date '+%F %T %Z')" >>"$log"

xargs -r -P "$workers" -n 1 bash -c 'apply_one "$1"' _ <"$ordered"
rc=$?
printf 'APPLY_FINISH=%s RC=%s DONE=%s FAILED=%s\n' \
  "$(date '+%F %T %Z')" "$rc" \
  "$(find "$run_dir" -maxdepth 1 -name '*.done' -printf x | wc -c)" \
  "$(grep -l '^TABLE_RC=[1-9]' "$run_dir"/*.log 2>/dev/null | wc -l)" \
  >>"$log"
exit "$rc"
````

#### `03_table_parallel/bizdb_import_closed_chunks.sh`

**中文备注：** 导入已封包的 SQL 分片并维护完成状态。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：03_table_parallel
# 中文备注：导入已封包的 SQL 分片并维护完成状态。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
set -uo pipefail

database="${PGS_DATABASE:?PGS_DATABASE is required}"
workers="${PGS_IMPORT_WORKERS:-12}"
minimum_age_minutes="${PGS_MIN_CHUNK_AGE_MINUTES:-1}"
mysql_cnf="${PGS_TARGET_CNF:-/root/.bizops-target.cnf}"
work_root="${PGS_PARALLEL_WORK_ROOT:-/data/bizops-bizdb-restore/parallel-import}"

work_dir="$work_root/$database"
chunk_dir="$work_dir/chunks"
done_dir="$work_dir/imported"
log_dir="$work_dir/logs"
marker_dir="$work_dir/markers"
failures="$work_dir/failures.live.txt"

install -d -m 750 "$chunk_dir" "$done_dir" "$log_dir" "$marker_dir"
: >"$failures"

mapfile -t chunks < <(
  find "$chunk_dir" -maxdepth 1 -type f -name 'chunk-*.sql' \
    -mmin "+$minimum_age_minutes" \
    ! -name 'chunk-000000.sql' |
    sort
)

echo "CLOSED_TABLE_CHUNKS=${#chunks[@]} WORKERS=$workers"
(( ${#chunks[@]} > 0 )) || exit 0

import_one() {
  local file="$1"
  local name
  local marker
  local log
  name="$(basename "$file")"
  marker="$marker_dir/$name.done"
  log="$log_dir/$name.live.log"

  if [[ -e "$marker" ]]; then
    mv -f -- "$file" "$done_dir/$name"
    return 0
  fi
  if /data/mysql/bin/mysql \
      --defaults-extra-file="$mysql_cnf" \
      --max-allowed-packet=268435456 \
      --init-command="SET SESSION sql_log_bin=0; SET SESSION foreign_key_checks=0; SET SESSION unique_checks=0" \
      "$database" <"$file" >"$log" 2>&1; then
    : >"$marker"
    mv -f -- "$file" "$done_dir/$name"
    echo "TABLE_OK=$name"
  else
    echo "$file" >>"$failures"
    echo "TABLE_FAILED=$name"
  fi
}

export -f import_one
export database mysql_cnf log_dir marker_dir done_dir failures

printf '%s\0' "${chunks[@]}" |
  xargs -0 -r -P "$workers" -n 1 bash -c 'import_one "$1"' _

mapfile -t failed_files <"$failures"
echo "IMPORT_FAILURES=${#failed_files[@]}"
echo "CLOSED_CHUNK_BATCH_COMPLETE=$(date '+%F %T %Z')"
(( ${#failed_files[@]} == 0 ))
````

#### `03_table_parallel/bizdb_replay_uid_sharded.sh`

**中文备注：** 按 UID 分片执行单张大表，同一 UID 保持顺序。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：03_table_parallel
# 中文备注：按 UID 分片执行单张大表，同一 UID 保持顺序。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# ============================================================================
# 某业务平台数据库恢复工具：按 UID 分片回放大表
# ----------------------------------------------------------------------------
# 适用场景：同一 UID 的事件必须严格按时间顺序，但不同 UID 可以并行。
# 本脚本先按 key_column（默认 uid）把 SQL 分到多个 shard，再并行执行。
# 恢复前可从备份还原单表，退出时恢复 ON UPDATE 和 MySQL 全局参数。
# ============================================================================
set -uo pipefail

input="${某业务平台_SHARD_INPUT:?某业务平台_SHARD_INPUT is required}"
database="${某业务平台_SHARD_DATABASE:?某业务平台_SHARD_DATABASE is required}"
table_name="${某业务平台_SHARD_TABLE:?某业务平台_SHARD_TABLE is required}"
key_column="${某业务平台_SHARD_KEY_COLUMN:-uid}"
workers="${某业务平台_SHARD_WORKERS:-8}"
work_dir="${某业务平台_SHARD_WORK_DIR:-/data/bizops-small-export/shard-$database-$table_name}"
backup_file="${某业务平台_SHARD_BACKUP_FILE:-}"
drop_guard_source="${某业务平台_SHARD_DROP_GUARD_SOURCE:-}"
restore_guard_source="${某业务平台_SHARD_RESTORE_GUARD_SOURCE:-}"
mysql_bin="${PGS_MYSQL_BIN:-/data/mysql/bin/mysql}"
defaults_file="${PGS_TARGET_CNF:-/root/.bizops-target.cnf}"
log="$work_dir/apply.log"

install -d -m 750 "$work_dir" "$work_dir/parts"
printf 'SHARD_START=%s TABLE=%s.%s KEY=%s WORKERS=%s\n' \
  "$(date '+%F %T %Z')" "$database" "$table_name" "$key_column" "$workers" \
  >"$log"

if [[ -n "$backup_file" ]]; then
  # 可选：先还原该表的回放前备份，用于失败后从干净基线重跑。
  [[ -s "$backup_file" ]] || {
    echo "backup file missing: $backup_file" >&2
    exit 20
  }
  gzip -dc "$backup_file" |
    sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" \
      --max-allowed-packet=1073741824 \
      --force \
      --init-command='SET SESSION sql_log_bin=0; SET SESSION foreign_key_checks=0' \
      "$database" >>"$log" 2>&1
  restore_rc="${PIPESTATUS[1]}"
  unexpected_errors="$(
    grep '^ERROR ' "$log" 2>/dev/null |
      grep -Ev '^ERROR 1304 ' || true
  )"
  printf 'BACKUP_RESTORED=%s RC=%s\n' \
    "$(date '+%F %T %Z')" "$restore_rc" >>"$log"
  if [[ -n "$unexpected_errors" ]]; then
    printf 'BACKUP_UNEXPECTED_ERROR=%s\n' "$unexpected_errors" >>"$log"
    exit 21
  fi
fi

table_ref="\`$database\`.\`$table_name\`"
drop_guard="$work_dir/drop-guard.sql"
restore_guard="$work_dir/restore-guard.sql"
if [[ -n "$drop_guard_source" && -n "$restore_guard_source" ]]; then
  grep -F "ALTER TABLE $table_ref" "$drop_guard_source" >"$drop_guard"
  grep -F "ALTER TABLE $table_ref" "$restore_guard_source" >"$restore_guard"
  sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" \
    <"$drop_guard" >>"$log" 2>&1
  printf 'TIMESTAMP_GUARD=OFF\n' >>"$log"
fi

flush_before="$(
  sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" -N \
    -e 'SELECT @@GLOBAL.innodb_flush_log_at_trx_commit'
)"
event_scheduler_before="$(
  sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" -N \
    -e 'SELECT @@GLOBAL.event_scheduler'
)"
restore_runtime() {
  # 即使脚本被中断，也尽力恢复表结构和临时性能参数。
  if [[ -s "$restore_guard" ]]; then
    sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" \
      <"$restore_guard" >>"$log" 2>&1
  fi
  sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" \
    -e "SET GLOBAL innodb_flush_log_at_trx_commit=$flush_before; SET GLOBAL event_scheduler=$event_scheduler_before" \
    >>"$log" 2>&1
  printf 'RUNTIME_RESTORED=%s FLUSH=%s EVENT=%s\n' \
    "$(date '+%F %T %Z')" "$flush_before" "$event_scheduler_before" >>"$log"
}
trap restore_runtime EXIT
sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" \
  -e 'SET GLOBAL innodb_flush_log_at_trx_commit=2; SET GLOBAL event_scheduler=OFF' \
  >>"$log" 2>&1

cat >"$work_dir/shard.pl" <<'PERL'
use strict;
use warnings;
my ($input, $dir, $key, $workers) = @ARGV;
my @fh;
for my $i (0 .. $workers - 1) {
  open($fh[$i], '>', sprintf('%s/%02d.sql', $dir, $i)) or die "$!";
}
open(my $in, '<', $input) or die "$!";
my $bad = 0;
my $count = 0;
while (my $line = <$in>) {
  if ($line =~ /WHERE `\Q$key\E`=(\d+);\s*$/) {
    print {$fh[$1 % $workers]} $line;
    $count++;
  } elsif ($line =~ /^INSERT INTO `[^`]+`\.`[^`]+` \([^)]*`\Q$key\E`[^)]*\) VALUES \((\d+),/) {
    print {$fh[$1 % $workers]} $line;
    $count++;
  } else {
    $bad++;
  }
}
close($in);
close($_) for @fh;
print STDERR "SHARDED=$count UNSHARDED=$bad\n";
exit($bad ? 22 : 0);
PERL

perl "$work_dir/shard.pl" "$input" "$work_dir/parts" "$key_column" "$workers" \
  2>>"$log"
rc=$?
printf 'SHARD_FINISH=%s RC=%s\n' "$(date '+%F %T %Z')" "$rc" >>"$log"
(( rc == 0 )) || exit "$rc"

apply_shard() {
  local part="$1"
  local part_log="$work_dir/$(basename "$part").log"
  sudo -n "$mysql_bin" \
    --defaults-extra-file="$defaults_file" \
    --max-allowed-packet=1073741824 \
    --binary-mode \
    --force \
    --init-command='SET SESSION sql_log_bin=0; SET SESSION foreign_key_checks=0; SET SESSION unique_checks=0; SET SESSION autocommit=1' \
    "$database" <"$part" >"$part_log" 2>&1
  local rc=$?
  local errors
  errors="$(grep -c '^ERROR ' "$part_log" 2>/dev/null || true)"
  printf 'SHARD_RC=%s ERRORS=%s PART=%s TIME=%s\n' \
    "$rc" "${errors:-0}" "$(basename "$part")" \
    "$(date '+%F %T %Z')" >>"$log"
  (( rc == 0 && ${errors:-0} == 0 )) || return 40
}
export -f apply_shard
export database mysql_bin defaults_file work_dir

printf 'REPLAY_START=%s\n' "$(date '+%F %T %Z')" >>"$log"
find "$work_dir/parts" -type f -name '*.sql' -print0 |
  xargs -0 -r -P "$workers" -n 1 bash -c 'apply_shard "$1"' _
rc=$?
printf 'REPLAY_FINISH=%s RC=%s\n' "$(date '+%F %T %Z')" "$rc" >>"$log"
exit "$rc"
````

### 8.4 04_large_log_tables 超大日志表专项

处理 contest、record_log 等超大日志表的倒序 INSERT 与主键分片。

#### `04_large_log_tables/bizdb_apply_append_only_desc.sh`

**中文备注：** 仅回放 INSERT，最新 binlog 优先、单文件倒序、INSERT IGNORE 并发执行。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：04_large_log_tables
# 中文备注：仅回放 INSERT，最新 binlog 优先、单文件倒序、INSERT IGNORE 并发执行。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# ============================================================================
# 某业务平台数据库恢复工具：两张大日志表的“倒序 + 仅 INSERT”回放
# ----------------------------------------------------------------------------
# 适用表：
#   - main_log_db.contest
#   - finance_db.record_log
#
# 业务口径：
#   1. 这两张表只补历史缺失的 INSERT；
#   2. 已有行直接跳过，不执行 UPDATE/DELETE；
#   3. 最新 binlog 文件先处理，单文件内部也从最后一行向前处理，
#      因此优先写入最大 ID 附近的记录；
#   4. 可从指定 relay 文件号开始，避免重复跑不需要的月份。
#
# 安全措施：
#   - 写库前先独立备份两表；
#   - 所有 INSERT 改为 INSERT IGNORE；
#   - 使用全局 flock，避免与其他回放任务并发改全局数据库参数；
#   - 退出时恢复 innodb_flush_log_at_trx_commit 和 event_scheduler。
# ============================================================================
set -uo pipefail

root="${某业务平台_APPEND_ONLY_ROOT:-/data/bizops-small-export/incoming/20261109-p6/apply}"
extract_root="${某业务平台_APPEND_ONLY_EXTRACT_ROOT:-$root/extracted}"
run_dir="${某业务平台_APPEND_ONLY_RUN_DIR:-$root/runs}"
backup_dir="${某业务平台_APPEND_ONLY_BACKUP_DIR:-$root/backups/pre-apply-20261109}"
workers="${某业务平台_APPEND_ONLY_WORKERS:-16}"
start_file_number="${某业务平台_APPEND_ONLY_START_FILE:-0}"
mysql_bin="${PGS_MYSQL_BIN:-/data/mysql/bin/mysql}"
defaults_file="${PGS_TARGET_CNF:-/root/.bizops-target.cnf}"
backup_script="${某业务平台_SMALL_BACKUP_SCRIPT:-/tmp/bizdb_small_table_backup.sh}"
log="$root/apply.log"
lock_file="${某业务平台_APPEND_ONLY_LOCK:-/data/bizops-small-export/apply.lock}"
tables=("main_log_db.contest" "finance_db.record_log")

# 与普通多表回放共享同一把锁，防止两套写入流程同时改全局参数。
install -d -m 750 "$root" "$run_dir" "$backup_dir"
exec 9>"$lock_file"
flock 9

printf 'APPLY_START=%s WORKERS=%s\n' "$(date '+%F %T %Z')" "$workers" >"$log"

files_list="$root/files.desc"
: >"$files_list"
# 生成“新文件在前”的文件列表，并过滤掉起始 relay 文件号之前的文件。
for table in "${tables[@]}"; do
  find "$extract_root" -type f -name "$table.forward.[0-9]*.sql" -print |
    while IFS= read -r file; do
      stem="${file%.sql}"
      number="${stem##*.}"
      if (( 10#$number >= 10#$start_file_number )); then
        printf '%s\n' "$file"
      fi
    done
done |
  sort -rV >"$files_list"

file_count="$(wc -l <"$files_list")"
total_bytes="$(
  while IFS= read -r file; do
    stat -c %s "$file"
  done <"$files_list" |
    awk '{ total += $1 } END { printf "%.0f", total }'
)"
(( file_count > 0 )) || {
  echo "No append-only SQL files found under $extract_root" >&2
  exit 20
}
printf 'FILES=%s BYTES=%s\n' "$file_count" "$total_bytes" >>"$log"
printf 'START_FILE_NUMBER=%s\n' "$start_file_number" >>"$log"

if [[ "${某业务平台_APPEND_ONLY_DRY_RUN:-0}" == "1" ]]; then
  printf 'DRY_RUN_FILES=%s\n' "$file_count"
  exit 0
fi

# 写库前对两张超大表做独立备份；备份失败则拒绝继续。
printf '%s\n' \
  $'main_log_db\tcontest' \
  $'finance_db\trecord_log' >"$backup_dir/tables.tsv"
PGS_SMALL_BACKUP_DIR="$backup_dir" \
PGS_SMALL_TABLE_LIST="$backup_dir/tables.tsv" \
PGS_SMALL_BACKUP_WORKERS=2 \
  "$backup_script" || {
  echo "Pre-apply backup failed; refusing to replay" >&2
  exit 21
}
printf 'BACKUP_READY=%s\n' "$backup_dir" >>"$log"

query_scalar() {
  sudo -n "$mysql_bin" --defaults-extra-file="$defaults_file" -N \
    -e "$1"
}

contest_max_before="$(query_scalar 'SELECT MAX(id) FROM main_log_db.contest')"
sx_max_before="$(
  query_scalar 'SELECT MAX(id) FROM finance_db.record_log'
)"
printf 'BASELINE_MAX_ID=main_log_db.contest:%s finance_db.record_log:%s\n' \
  "$contest_max_before" "$sx_max_before" >>"$log"

flush_before="$(query_scalar 'SELECT @@GLOBAL.innodb_flush_log_at_trx_commit')"
event_scheduler_before="$(query_scalar 'SELECT @@GLOBAL.event_scheduler')"
printf 'FLUSH_BEFORE=%s\nEVENT_SCHEDULER_BEFORE=%s\n' \
  "$flush_before" "$event_scheduler_before" >>"$log"

restore_runtime_settings() {
  query_scalar \
    "SET GLOBAL innodb_flush_log_at_trx_commit=$flush_before" >>"$log" 2>&1
  query_scalar \
    "SET GLOBAL event_scheduler=$event_scheduler_before" >>"$log" 2>&1
  printf 'FLUSH_RESTORED=%s TIME=%s\n' \
    "$flush_before" "$(date '+%F %T %Z')" >>"$log"
  printf 'EVENT_SCHEDULER_RESTORED=%s TIME=%s\n' \
    "$event_scheduler_before" "$(date '+%F %T %Z')" >>"$log"
}
trap restore_runtime_settings EXIT

query_scalar 'SET GLOBAL innodb_flush_log_at_trx_commit=2' >>"$log" 2>&1
query_scalar 'SET GLOBAL event_scheduler=OFF' >>"$log" 2>&1
printf 'FLUSH_DURING_APPLY=2\nEVENT_SCHEDULER_DURING_APPLY=OFF\n' >>"$log"

apply_file() {
  # 单文件倒序过滤：
  #   tac 让同一个 binlog 文件中 ID 更大的 INSERT 优先执行；
  #   awk 只保留 INSERT，并改为 INSERT IGNORE。
  local sql_file="$1"
  local base
  local done_file
  local table_log
  local rc

  base="$(basename "$sql_file" .sql)"
  done_file="$run_dir/$base.done"
  table_log="$run_dir/$base.log"
  [[ -e "$done_file" ]] && return 0

  printf 'FILE_START=%s TIME=%s\n' \
    "$base" "$(date '+%F %T %Z')" >"$table_log"
  (
    tac "$sql_file" |
      LC_ALL=C awk '
        /^INSERT INTO / {
          sub(/^INSERT INTO /, "INSERT IGNORE INTO ")
          print
          count++
        }
        END {
          printf "FILTERED_INSERTS=%d\n", count > "/dev/stderr"
        }
      ' |
      sudo -n "$mysql_bin" \
        --defaults-extra-file="$defaults_file" \
        --max-allowed-packet=1073741824 \
        --binary-mode \
        --init-command='SET SESSION sql_log_bin=0; SET SESSION foreign_key_checks=0; SET SESSION autocommit=1; SET SESSION net_read_timeout=600; SET SESSION net_write_timeout=600'
  ) >>"$table_log" 2>&1
  rc=$?

  printf 'FILE_RC=%s FILE=%s TIME=%s\n' \
    "$rc" "$base" "$(date '+%F %T %Z')" >>"$table_log"
  if (( rc == 0 )); then
    printf '%s\n' "$(date '+%F %T %Z')" >"$done_file"
  fi
  return "$rc"
}

export -f apply_file
export run_dir mysql_bin defaults_file

printf 'APPLY_ORDER=NEWEST_BINLOG_FIRST_REVERSE_LINES\n' >>"$log"
printf 'APPLY_POLICY=INSERT_IGNORE_ONLY_IGNORE_UPDATE_DELETE\n' >>"$log"

xargs -r -P "$workers" -n 1 bash -c 'apply_file "$1"' _ <"$files_list"
rc=$?

done_count="$(
  find "$run_dir" -maxdepth 1 -type f -name '*.done' -printf x |
    wc -c
)"
failed_count="$(
  grep -l '^FILE_RC=[1-9]' "$run_dir"/*.log 2>/dev/null |
    wc -l
)"
printf 'APPLY_FINISH=%s RC=%s DONE=%s/%s FAILED=%s\n' \
  "$(date '+%F %T %Z')" "$rc" "$done_count" "$file_count" \
  "$failed_count" >>"$log"

if (( rc != 0 || done_count != file_count || failed_count != 0 )); then
  exit 22
fi

exit 0
````

#### `04_large_log_tables/bizdb_resume_key_sharded.py`

**中文备注：** 按主键稳定分片并行回放 INSERT/DELETE，支持跨行 JSON 完整语句解析和批量提交。

````python
#!/usr/bin/env python3
# ============================================================================
# 平台：某业务平台
# 恢复阶段：04_large_log_tables
# 中文备注：按主键稳定分片并行回放 INSERT/DELETE，支持跨行 JSON 完整语句解析和批量提交。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
"""某业务平台数据库恢复工具：按主键稳定分片续跑大表 SQL。

核心目标：
1. 同一主键的所有 INSERT/DELETE 永远进入同一个 worker；
2. 每个 worker 按 SQL 文件原始顺序执行，保证同主键事件顺序；
3. 不同主键分片并行，提高超大表的恢复速度；
4. 使用完整 SQL 语句边界解析，避免把含换行的 JSON/longtext 截断；
5. 每约 4MB 提交一次事务，降低逐条 autocommit 的写入开销；
6. 进程退出时恢复 MySQL 全局参数。
"""

import argparse
import os
import re
import subprocess
import threading
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


RUNTIME_LOCK = threading.Lock()


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")


def mysql_command(
    mysql_bin: str,
    defaults_file: str,
) -> List[str]:
    """构造只用于恢复回放的 mysql 客户端参数。

    sql_log_bin=0 避免恢复流量继续生成 binlog；
    unique_checks/foreign_key_checks=0 降低回放约束开销；
    autocommit=0 配合 COMMIT 批量提交。
    """
    return [
        "sudo",
        "-n",
        mysql_bin,
        "--defaults-extra-file=" + defaults_file,
        "--max-allowed-packet=1073741824",
        "--binary-mode",
        "--init-command="
        "SET SESSION sql_log_bin=0; "
        "SET SESSION foreign_key_checks=0; "
        "SET SESSION unique_checks=0; "
        "SET SESSION autocommit=0; "
        "SET SESSION net_read_timeout=600; "
        "SET SESSION net_write_timeout=600",
    ]


def query_scalar(mysql: List[str], sql: str) -> str:
    proc = subprocess.run(
        mysql + ["-N", "--batch", "-e", sql],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError(proc.stderr.strip() or "mysql query failed")
    return proc.stdout.strip()


def next_line_offset(path: Path, offset: int) -> int:
    """从中断字节位置前进到下一条完整 SQL 行，避免从半行开始。"""
    if offset <= 0:
        return 0
    with path.open("rb") as handle:
        handle.seek(offset)
        handle.readline()
        return handle.tell()


def iter_sql_statements(handle, start_offset: int):
    """按 `;\n` 边界产出完整 SQL 语句。

    这里不按物理行处理，因为 my2sql 生成的 longtext/JSON 值可能跨多行。
    一次读取 4MB，不足一条语句时留在 buffer，直到遇到完整语句结束符。
    """
    buffer = bytearray()
    consumed = start_offset
    while True:
        chunk = handle.read(4 * 1024 * 1024)
        if not chunk:
            break
        buffer.extend(chunk)
        search_from = 0
        while True:
            end = buffer.find(b";\n", search_from)
            if end < 0:
                break
            statement = bytes(buffer[search_from:end + 2])
            consumed += len(statement)
            yield statement, consumed
            search_from = end + 2
        if search_from:
            del buffer[:search_from]
    if buffer.strip():
        statement = bytes(buffer)
        consumed += len(statement)
        yield statement, consumed


def line_shard(line: bytes, key_name: str, shards: int) -> int:
    """从 INSERT/DELETE 中提取主键，并计算稳定的 shard 编号。"""
    if line.startswith(b"INSERT INTO "):
        if key_name == "balance_id":
            match = re.search(
                rb"VALUES \(\s*'(?:\\.|[^'])*'\s*,\s*([0-9]+)\s*,",
                line,
            )
        else:
            match = re.search(rb"VALUES \(\s*([0-9]+)\s*,", line)
    elif line.startswith(b"DELETE FROM "):
        escaped = re.escape(key_name.encode())
        match = re.search(rb"`" + escaped + rb"`\s*=\s*([0-9]+)", line)
    else:
        raise ValueError(
            "unsupported SQL statement: "
            + line[:100].decode("utf-8", "replace")
        )
    if not match:
        raise ValueError(
            f"cannot extract {key_name}: "
            + line[:180].decode("utf-8", "replace")
        )
    return int(match.group(1)) % shards


def replay_table(
    table: str,
    key_name: str,
    sql_file: Path,
    start_offset: int,
    shards: int,
    root: Path,
    mysql: List[str],
) -> int:
    """并行回放一张表，并在所有 shard 成功后写 done 标记。"""
    run_dir = root / "runs-sharded"
    progress_dir = root / "progress"
    run_dir.mkdir(parents=True, exist_ok=True)
    progress_dir.mkdir(parents=True, exist_ok=True)

    safe = table.replace(".", "__")
    table_log = root / "runs" / f"{table}.log"
    done_file = root / "runs" / f"{table}.done"
    progress_file = progress_dir / f"{table}.pos"
    if done_file.exists():
        return 0

    with table_log.open("a", encoding="utf-8") as log:
        log.write(
            f"SHARD_RESUME_START={now()} START_OFFSET={start_offset} "
            f"SHARDS={shards} KEY={key_name}\n"
        )

    workers: List[Tuple[subprocess.Popen, Any]] = []
    shard_logs: List[Path] = []
    for index in range(shards):
        # 每个 shard 使用独立 MySQL 会话，避免多个线程共用一个连接。
        shard_log = run_dir / f"{safe}.shard{index}.log"
        shard_logs.append(shard_log)
        output = shard_log.open("wb")
        worker = subprocess.Popen(
            mysql,
            stdin=subprocess.PIPE,
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        workers.append((worker, output))

    position = next_line_offset(sql_file, start_offset)
    progress_file.write_text(str(position) + "\n", encoding="ascii")
    buffers: Dict[int, bytearray] = defaultdict(bytearray)
    buffer_total = 0
    lines_since_flush = 0
    error = None  # type: Optional[Exception]

    try:
        with sql_file.open("rb") as source:
            source.seek(position)
            for line, statement_end in iter_sql_statements(source, position):
                position = statement_end
                index = line_shard(line, key_name, shards)
                if line.startswith(b"INSERT INTO "):
                    line = b"INSERT IGNORE INTO " + line[len(b"INSERT INTO "):]
                buffers[index].extend(line)
                buffer_total += len(line)
                lines_since_flush += 1
                if buffer_total >= 4 * 1024 * 1024 or lines_since_flush >= 20000:
                    # 批量提交：同 shard 保持顺序，同时显著减少事务提交次数。
                    for shard_index, buffer in buffers.items():
                        if buffer:
                            workers[shard_index][0].stdin.write(buffer)
                            workers[shard_index][0].stdin.write(b"COMMIT;\n")
                            workers[shard_index][0].stdin.flush()
                            buffer.clear()
                    buffer_total = 0
                    lines_since_flush = 0
                    progress_file.write_text(str(position) + "\n", encoding="ascii")
        for shard_index, buffer in buffers.items():
            if buffer:
                workers[shard_index][0].stdin.write(buffer)
                workers[shard_index][0].stdin.write(b"COMMIT;\n")
                workers[shard_index][0].stdin.flush()
                buffer.clear()
        progress_file.write_text(str(position) + "\n", encoding="ascii")
    except Exception as exc:
        error = exc
    finally:
        for worker, _ in workers:
            if worker.stdin:
                worker.stdin.close()
        for worker, output in workers:
            worker.wait()
            output.close()

    errors = 0
    for shard_log in shard_logs:
        text = shard_log.read_text(encoding="utf-8", errors="replace")
        errors += len(re.findall(r"^ERROR ", text, re.M))
    failed_workers = sum(1 for worker, _ in workers if worker.returncode != 0)
    with table_log.open("a", encoding="utf-8") as log:
        log.write(
            f"SHARD_RESUME_FINISH={now()} END_OFFSET={position} "
            f"WORKER_FAILED={failed_workers} SQL_ERRORS={errors}"
        )
        if error:
            log.write(
                " PARSE_ERROR="
                + str(error).replace("\n", " ")[:500]
            )
        log.write("\n")
        if error is None and failed_workers == 0 and errors == 0:
            log.write(f"TABLE_RC=0 TABLE={table} SQL_ERRORS=0 TIME={now()}\n")
            done_file.write_text(now() + "\n", encoding="utf-8")
            return 0
        log.write(f"TABLE_RC=1 TABLE={table} SQL_ERRORS={errors} TIME={now()}\n")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--combined-dir", required=True)
    parser.add_argument("--offsets", required=True)
    parser.add_argument("--shards", type=int, default=4)
    parser.add_argument("--mysql-bin", default="/data/mysql/bin/mysql")
    parser.add_argument(
        "--defaults-file", default="/root/.bizops-target.cnf"
    )
    args = parser.parse_args()

    root = Path(args.root)
    combined_dir = Path(args.combined_dir)
    specs = {
        # 各表用于分片的主键：
        # - 普通日志表：id % N
        # - 复合主键关系表：balance_id % N，同一余额关系仍进入同一 shard
        "finance_db.record_log_bak": "id",
        "main_log_db.contest_list": "id",
        "main_log_db.balance_relation": "balance_id",
    }
    offsets = {}  # type: Dict[str, int]
    for raw in Path(args.offsets).read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        table, value = raw.split("\t", 1)
        offsets[table] = int(value)

    missing = set(specs) - set(offsets)
    if missing:
        raise SystemExit(f"missing offsets: {sorted(missing)}")

    mysql = mysql_command(args.mysql_bin, args.defaults_file)
    flush_before = query_scalar(
        mysql, "SELECT @@GLOBAL.innodb_flush_log_at_trx_commit"
    )
    scheduler_before = query_scalar(mysql, "SELECT @@GLOBAL.event_scheduler")
    query_scalar(mysql, "SET GLOBAL innodb_flush_log_at_trx_commit=2")
    query_scalar(mysql, "SET GLOBAL event_scheduler=OFF")

    results = {}  # type: Dict[str, int]
    try:
        threads = []  # type: List[threading.Thread]

        def run(table: str, key_name: str) -> None:
            results[table] = replay_table(
                table=table,
                key_name=key_name,
                sql_file=combined_dir / f"{table}.sql",
                start_offset=offsets[table],
                shards=args.shards,
                root=root,
                mysql=mysql,
            )

        for table, key_name in specs.items():
            thread = threading.Thread(
                target=run,
                args=(table, key_name),
                daemon=False,
            )
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
    finally:
        query_scalar(
            mysql,
            f"SET GLOBAL innodb_flush_log_at_trx_commit={flush_before}",
        )
        query_scalar(
            mysql,
            f"SET GLOBAL event_scheduler={scheduler_before}",
        )

    return 0 if all(code == 0 for code in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
````

### 8.5 05_monitoring_verify 监控、核验与参数保护

恢复期间采样真实字节进度、失败数、ETA，并通过群机器人通知。

#### `05_monitoring_verify/bizdb_restore_monitor.py`

**中文备注：** 每 5 分钟群播报进行中任务、表级完成度、尾部补跑进度、失败数和预计北京时间。

````python
#!/usr/bin/env python3
# ============================================================================
# 平台：某业务平台
# 恢复阶段：05_monitoring_verify
# 中文备注：每 5 分钟群播报进行中任务、表级完成度、尾部补跑进度、失败数和预计北京时间。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
"""某业务平台数据库恢复监控与群播报。

数据来源：
1. 已完成表的 .done 标记；
2. 正在读取 SQL 文件的真实文件偏移；
3. 分片回放器写入的进度文件；
4. 表级/文件级失败日志；
5. MySQL 当前全局恢复参数。

通知原则：
- 只播报进行中任务和数据断层，不逐条播报已完成表；
- 百分比按真实 SQL 字节加权，不用表数量冒充总体进度；
- 预计完成时间统一换算为北京时间；
- 回放全部完成时只发一次独立通知；
- 业务验收和开服仍由四组人工确认，不由监控器自动放行。
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bizops_live_progress_loop import 某业务平台_DATABASES, bizdb_export_status
from emergency_bastion_exec import run_asset


ASSETS = Path("scripts/emergency_bastion_assets.txt")
STATE = Path("/tmp/bizdb-restore-monitor-state.json")
BASELINE_TIME = datetime.fromisoformat("2026-05-10 17:57:49")
TARGET_TIME = datetime.fromisoformat("2026-11-07 00:27:11")
USER_DATA_END = datetime.fromisoformat("2026-11-07 00:05:00")

DATABASE_ORDER = (
    "users_db",
    "game_db",
    "recharge_db",
    "config_db",
    "finance_db",
    "cms_api_db",
    "report_db",
    "merchant_db",
    "common_log_db",
    "main_log_db",
    "diff_log_db",
    "data_db",
    "monitor_db",
    "geoip",
    "history_partition_db",
    "agent_db",
    "market_db",
)

SAMPLE_TIME_COLUMNS = {
    "users_db": ("user_account.last_update_time", "user_account", "last_update_time"),
    "game_db": ("user_info.last_update_time", "user_info", "last_update_time"),
    "recharge_db": ("order.updated", "order", "updated"),
    "config_db": ("system_log.create_time", "system_log", "create_time"),
    "finance_db": ("record_log.create_time", "record_log", "create_time"),
    "cms_api_db": ("t_addmoney_logs.addtime", "t_addmoney_logs", "addtime"),
    "report_db": ("rpt_channel.update_time", "rpt_channel", "update_time"),
    "merchant_db": ("admin_optlog.rtime", "admin_optlog", "rtime"),
    "common_log_db": ("gold.post_time", "gold", "post_time"),
    "main_log_db": ("contest.post_time", "contest", "post_time"),
    "diff_log_db": ("roulette_point.post_time", "roulette_point", "post_time"),
    "data_db": ("income_main.f_date", "income_main", "f_date"),
    "monitor_db": ("monitor_warn_log.warn_time", "monitor_warn_log", "warn_time"),
    "history_partition_db": ("gold_hist.post_time", "gold_hist", "post_time"),
    "agent_db": ("spread.update_time", "spread", "update_time"),
}


def run(name: str, command: str) -> str:
    script = (
        "printf '__MON_BEGIN__\\n'\n"
        + command
        + "\nprintf '__MON_END__\\n'\n"
    )
    result = run_asset(name, script, "__MON_BEGIN__", "__MON_END__")
    return str(result.get("transcript", "")).replace("\r", "")


def query_db2() -> dict[str, object]:
    command = r"""
set +e
password=$(sudo -n sed -nE "s/.* -p'([^']+)'.*/\1/p" /root/mysql.sh | head -1)
[ -n "$password" ] || password=$(sudo -n sed -nE 's/.* -p"([^"]+)".*/\1/p' /root/mysql.sh | head -1)
MYSQL_PWD="$password" /data/mysql/bin/mysql -uadmin -N --batch -e "
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='common_log_db';
SELECT table_name,table_rows,ROUND((data_length+index_length)/1024/1024,1)
  FROM information_schema.tables WHERE table_schema='common_log_db'
  ORDER BY table_name DESC LIMIT 2;
"
unset password
cat /tmp/log-comm-base-import.log
"""
    text = run("sample-node-06", command)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    count_line = next((line for line in lines if line.isdigit()), "")
    table_lines = [line.split("\t") for line in lines if "\t" in line]
    if not count_line or not table_lines:
        raise RuntimeError("备份节点 progress unavailable")
    current = table_lines[0]
    import_rc = re.search(r"^IMPORT_RC=(\d+)$", text, re.M)
    import_end = re.search(r"^END=(.+)$", text, re.M)
    return {
        "tables": int(count_line),
        "table": current[0],
        "rows": int(current[1]),
        "size_gb": float(current[2]) / 1024,
        "import_rc": int(import_rc.group(1)) if import_rc else None,
        "import_end": import_end.group(1).strip() if import_end else "",
        "baseline_complete": bool(import_rc and import_rc.group(1) == "0"),
        "raw": text,
    }


def query_db1() -> dict[str, object]:
    command = r"""
set +e
if pgrep -f '^/bin/bash /tmp/apply-logcomm-all.sh' >/dev/null; then echo RUNNING=1; else echo RUNNING=0; fi
last=$(tail -1 /tmp/apply-logcomm-all.log 2>/dev/null)
echo "TAIL=$last"
line=$(grep -oE 'at line [0-9]+' /tmp/apply-logcomm-all.log 2>/dev/null | tail -1 | awk '{print $3}')
echo "STATEMENTS=${line:-0}"
password=$(sudo -n sed -nE 's/.* -p"([^"]+)".*/\1/p' /root/mysql.sh | head -1)
[ -n "$password" ] || password=$(sudo -n sed -nE "s/.* -p'([^']+)'.*/\1/p" /root/mysql.sh | head -1)
MYSQL_PWD="$password" timeout 20 /data/mysql/bin/mysql -uadmin -N -e "
SELECT 'gold',MAX(post_time),COUNT(*) FROM common_log_db.gold;
SELECT 'logon',MAX(create_time),COUNT(*) FROM common_log_db.logon;
SELECT 'contest',MAX(post_time),COUNT(*) FROM main_log_db.contest;
SELECT 'flush_mode',@@GLOBAL.innodb_flush_log_at_trx_commit;
"
unset password
"""
    text = run("sample-node-05", command)
    running = bool(re.search(r"^RUNNING=1$", text, re.M))
    statement_match = re.search(r"^STATEMENTS=(\d+)", text, re.M)
    gold = re.search(r"^gold\t([^\t]+)\t(\d+)$", text, re.M)
    logon = re.search(r"^logon\t([^\t]+)\t(\d+)$", text, re.M)
    contest = re.search(r"^contest\t([^\t]+)\t(\d+)$", text, re.M)
    flush_mode = re.search(r"^flush_mode\t([012])$", text, re.M)
    return {
        "running": running,
        "statements": int(statement_match.group(1)) if statement_match else 0,
        "gold_max": gold.group(1) if gold else "",
        "gold_rows": int(gold.group(2)) if gold else 0,
        "logon_max": logon.group(1) if logon else "",
        "logon_rows": int(logon.group(2)) if logon else 0,
        "contest_max": contest.group(1) if contest else "",
        "contest_rows": int(contest.group(2)) if contest else 0,
        "flush_mode": flush_mode.group(1) if flush_mode else "unknown",
        "raw": text,
    }


def query_database_snapshot() -> dict[str, object]:
    """Return a compact, live per-database recovery inventory.

    The maximum-time sample is intentionally small. It proves whether a
    database contains post-baseline activity without scanning every large
    partition table on each monitoring tick.
    """

    database_list = ",".join(f"'{name}'" for name in DATABASE_ORDER)
    time_queries = []
    for database, (label, table, column) in SAMPLE_TIME_COLUMNS.items():
        if (database, column) in {
            ("cms_api_db", "addtime"),
            ("config_db", "create_time"),
        }:
            value = f"IFNULL(FROM_UNIXTIME(MAX(`{column}`)),'NULL')"
        else:
            value = f"IFNULL(DATE_FORMAT(MAX(`{column}`),'%Y-%m-%d %H:%i:%s'),'NULL')"
        time_queries.append(
            f"SELECT 'TM','{database}','{label}',{value} "
            f"FROM `{database}`.`{table}`;"
        )

    command = f"""
set +e
password=$(sudo -n sed -nE 's/.* -p"([^"]+)".*/\\1/p' /root/mysql.sh | head -1)
[ -n "$password" ] || password=$(sudo -n sed -nE "s/.* -p'([^']+)'.*/\\1/p" /root/mysql.sh | head -1)
MYSQL_PWD="$password" timeout 100 /data/mysql/bin/mysql -uadmin -N --batch <<'SQL'
SET time_zone = '+08:00';
SELECT 'META','sample-node-05',DATE_FORMAT(NOW(),'%Y-%m-%d %H:%i:%s');
SELECT 'DB',TABLE_SCHEMA,COUNT(*),
       ROUND(SUM(data_length+index_length)/1024/1024,1),
       SUM(table_rows),
       SUM(CASE WHEN table_name REGEXP '[0-9]{{8}}' THEN 1 ELSE 0 END)
  FROM information_schema.tables
 WHERE table_schema IN ({database_list})
   AND table_type='BASE TABLE'
 GROUP BY table_schema
 ORDER BY table_schema;
{''.join(time_queries)}
SQL
mysql_rc=$?
unset password
printf 'MYSQL_RC=%s\\n' "$mysql_rc"
active=$(
  ps -eo pid,etime,args |
    grep -E '[m]y2sql|[a]pply-logcomm|[b]sqp.*(replay|import)|[p]arallel-import' |
    grep -v 'bizdb_restore_monitor.py' |
    head -5
)
if [ -n "$active" ]; then
  printf 'ACTIVE=1\\n%s\\n' "$active"
else
  printf 'ACTIVE=0\\n'
fi
printf 'MARKERS='
find /data/bizops-bizdb-restore/markers -maxdepth 1 -type f \\
  -name 'bizdb-full-*-20261107.done' -printf x 2>/dev/null | wc -c
printf 'APPLY_RUNNING='
pgrep -fc '[b]sqp_apply_small_table_sql.sh|[a]pply_one|[b]sqp_apply_append_only_desc.sh' 2>/dev/null || true
apply_tables=0
apply_done=0
apply_failed=0
for apply_root in $(
  find /data/bizops-small-export/incoming -maxdepth 3 -type f \
    -name 'tables.list' -printf '%h\n' 2>/dev/null |
    grep -E '/(apply|safe-apply[^/]*)$' |
    sort -u
); do
  apply_tables=$((apply_tables + $(wc -l < "$apply_root/tables.list")))
  apply_done=$((apply_done + $(find "$apply_root/runs" -maxdepth 1 \\
    -type f -name '*.done' -printf x 2>/dev/null | wc -c)))
  apply_failed=$((apply_failed + $(grep -l '^TABLE_RC=[1-9]' \\
    "$apply_root/runs"/*.log 2>/dev/null | grep -v '\\.superseded-' | wc -l)))
  for db in $(cut -d. -f1 "$apply_root/tables.list" | sort -u); do
    expected=$(grep -c "^$db\\." "$apply_root/tables.list")
    done_count=$(find "$apply_root/runs" -maxdepth 1 -type f \\
      -name "$db.*.done" -printf x 2>/dev/null | wc -c)
    if test "$expected" -gt 0 && test "$done_count" -eq "$expected"; then
      printf 'APPLY_DB_DONE=%s\\n' "$db"
    elif test "$done_count" -gt 0; then
      printf 'APPLY_DB_PARTIAL=%s\\n' "$db"
    fi
    if test "$done_count" -lt "$expected"; then
      printf 'APPLY_DB_PENDING=%s\\n' "$db"
    fi
  done
done
printf 'APPLY_TABLES=%s\\n' "$apply_tables"
printf 'APPLY_DONE=%s\\n' "$apply_done"
printf 'APPLY_FAILED=%s\\n' "$apply_failed"
p5_root=/data/bizops-small-export/incoming/20261109-p5/apply
p5_total_bytes=0
p5_done_bytes=0
while IFS= read -r table; do
  table_size=$(stat -c %s "$p5_root/combined/$table.sql" 2>/dev/null || echo 0)
  p5_total_bytes=$((p5_total_bytes + table_size))
  if [ -e "$p5_root/runs/$table.done" ]; then
    p5_done_bytes=$((p5_done_bytes + table_size))
  fi
done <"$p5_root/tables.list"
p5_running_bytes=0
shard_current_bytes=0
shard_total_bytes=0
for process in $(pgrep -x awk 2>/dev/null); do
  source_file=$(sudo -n readlink "/proc/$process/fd/3" 2>/dev/null)
  case "$source_file" in
    "$p5_root"/combined/*.sql|"$p5_root"/combined-tail/*.sql|"$p5_root"/apply-tail-sx/combined/*.sql)
      position=$(sudo -n awk '/^pos:/{{print $2}}' \
        "/proc/$process/fdinfo/3" 2>/dev/null)
      table=$(basename "$source_file" .sql)
      original_size=$(stat -c %s "$p5_root/combined/$table.sql" 2>/dev/null || echo 0)
      baseline=$(
        awk -F '\t' -v table="$table" '$1 == table {{print $2}}' \
          "$p5_root/shard-baselines.tsv" 2>/dev/null |
          head -1
      )
      baseline=${{baseline:-0}}
      position=${{position:-0}}
      effective_position=$position
      shard_size=$original_size
      is_tail=0
      case "$source_file" in
        "$p5_root"/combined-tail/*.sql|"$p5_root"/apply-tail-sx/combined/*.sql)
          is_tail=1
          effective_position=$baseline
          shard_size=$(
            awk -F '\t' -v table="$table" '$1 == table {{print $2}}' \
              "$p5_root/tail-sizes.tsv" 2>/dev/null |
              head -1
          )
          shard_size=${{shard_size:-0}}
          ;;
      esac
      p5_running_bytes=$((p5_running_bytes + effective_position))
      percent=$(awk -v p="$effective_position" -v s="$original_size" \
        'BEGIN{{if(s>0)printf "%.2f",p*100/s;else printf "0"}}')
      printf 'P5_PROGRESS=%s|%s|%s|%s\\n' \
        "$table" "$position" "$original_size" "$percent"
      if [ "$is_tail" -eq 1 ]; then
        shard_percent=$(awk -v p="$position" -v s="$shard_size" \
          'BEGIN{{if(s>0)printf "%.2f",p*100/s;else printf "0"}}')
        printf 'P5_SHARD_PROGRESS=%s|%s|%s|%s\\n' \
          "$table" "$position" "$shard_size" "$shard_percent"
        shard_current_bytes=$((shard_current_bytes + position))
        shard_total_bytes=$((shard_total_bytes + shard_size))
      fi
      ;;
  esac
done
for progress_file in "$p5_root"/progress/*.pos; do
  [ -s "$progress_file" ] || continue
  table=$(basename "$progress_file" .pos)
  [ -e "$p5_root/runs/$table.done" ] && continue
  position=$(cat "$progress_file" 2>/dev/null)
  baseline=$(
    awk -F '\t' -v table="$table" '$1 == table {{print $2}}' \
      "$p5_root/shard-baselines.tsv" 2>/dev/null |
      head -1
  )
  baseline=${{baseline:-0}}
  effective_position=$baseline
  original_size=$(stat -c %s "$p5_root/combined/$table.sql" 2>/dev/null || echo 0)
  tail_size=$(
    awk -F '\t' -v table="$table" '$1 == table {{print $2}}' \
      "$p5_root/tail-sizes.tsv" 2>/dev/null |
      head -1
  )
  tail_size=${{tail_size:-0}}
  position=${{position:-0}}
  p5_running_bytes=$((p5_running_bytes + effective_position))
  percent=$(awk -v p="$effective_position" -v s="$original_size" \
    'BEGIN{{if(s>0)printf "%.2f",p*100/s;else printf "0"}}')
  shard_size=$tail_size
  if [ "$shard_size" -le 0 ]; then
    shard_size=$original_size
  fi
  shard_percent=$(awk -v p="$position" -v s="$shard_size" \
    'BEGIN{{if(s>0)printf "%.2f",p*100/s;else printf "0"}}')
  printf 'P5_PROGRESS=%s|%s|%s|%s\n' \
    "$table" "$position" "$original_size" "$percent"
  printf 'P5_SHARD_PROGRESS=%s|%s|%s|%s\n' \
    "$table" "$position" "$shard_size" "$shard_percent"
  shard_current_bytes=$((shard_current_bytes + position))
  shard_total_bytes=$((shard_total_bytes + shard_size))
done
if [ -s "$p5_root/tail-sizes.tsv" ]; then
  while IFS=$'\t' read -r table tail_size; do
    if [ -e "$p5_root/runs/$table.done" ]; then
      shard_current_bytes=$((shard_current_bytes + tail_size))
      shard_total_bytes=$((shard_total_bytes + tail_size))
    fi
  done <"$p5_root/tail-sizes.tsv"
fi
printf 'P5_JOB_TABLES=%s\\n' "$(wc -l <"$p5_root/tables.list")"
printf 'P5_JOB_DONE_TABLES='
find "$p5_root/runs" -maxdepth 1 -type f -name '*.done' -printf x 2>/dev/null |
  wc -c
printf 'P5_JOB_TOTAL_BYTES=%s\\n' "$p5_total_bytes"
printf 'P5_JOB_DONE_BYTES=%s\\n' "$p5_done_bytes"
printf 'P5_JOB_RUNNING_BYTES=%s\\n' "$p5_running_bytes"
printf 'P5_SHARD_CURRENT_BYTES=%s\\n' "${{shard_current_bytes:-0}}"
printf 'P5_SHARD_TOTAL_BYTES=%s\\n' "${{shard_total_bytes:-0}}"
printf 'P5_JOB_RUNNING='
pgrep -fc \
  '^/bin/bash /tmp/bizdb_apply_small_table_sql.sh|^[^ ]*python3 /tmp/bizdb_resume_key_sharded.py' \
  2>/dev/null || true
printf 'P5_JOB_FAILED='
grep -l '^TABLE_RC=[1-9]' "$p5_root/runs"/*.log 2>/dev/null |
  grep -v '\\.superseded-' | wc -l
append_root=/data/bizops-small-export/incoming/20261109-p6/apply
p6_total_bytes=0
p6_done_bytes=0
if [ -s "$append_root/files.desc" ]; then
  while IFS= read -r file; do
    file_size=$(stat -c %s "$file" 2>/dev/null || echo 0)
    p6_total_bytes=$((p6_total_bytes + file_size))
    marker="$append_root/runs/$(basename "$file" .sql).done"
    if [ -e "$marker" ]; then
      p6_done_bytes=$((p6_done_bytes + file_size))
    fi
  done <"$append_root/files.desc"
fi
printf 'P6_JOB_FILES='; wc -l <"$append_root/files.desc" 2>/dev/null || true
printf 'P6_JOB_DONE='
find "$append_root/runs" -maxdepth 1 -type f -name '*.done' -printf x 2>/dev/null |
  wc -c
printf 'APPEND_FAILED='
grep -l '^FILE_RC=[1-9]' "$append_root/runs"/*.log 2>/dev/null | wc -l
printf 'P6_JOB_TOTAL_BYTES=%s\n' "$p6_total_bytes"
printf 'P6_JOB_DONE_BYTES=%s\n' "$p6_done_bytes"
printf 'P6_JOB_RUNNING='
pgrep -fc '^/bin/bash /tmp/bizdb_apply_append_only_desc.sh' 2>/dev/null || true
backup_log=/data/bizops-small-export/backups/pre-apply-20261109/backup.log
printf 'BACKUP_OK='
grep -c '^BACKUP_OK=' "$backup_log" 2>/dev/null || true
printf 'BACKUP_FAILED='
grep -c '^BACKUP_FAIL=' "$backup_log" 2>/dev/null || true
pipeline_running=0
for pid_file in $(find /data/bizops-small-export/incoming -mindepth 2 \
  -maxdepth 2 -type f -name 'pipeline.pid' 2>/dev/null); do
  pipeline_pid=$(cat "$pid_file" 2>/dev/null)
  if [ -n "$pipeline_pid" ] && kill -0 "$pipeline_pid" 2>/dev/null; then
    pipeline_running=1
    pipeline_dir=$(dirname "$pid_file")
    stamp=$(basename "$pipeline_dir")
    stage=$(awk '!/^WAITING=/ && NF {{ last=$0 }} END {{ print last }}' \
      "$pipeline_dir/wait-apply.log" 2>/dev/null)
    printf 'PIPELINE_ACTIVE=%s|%s\n' "$stamp" "${{stage:-准备中}}"
  fi
done
if [ "$pipeline_running" -eq 1 ]; then
  printf 'ACTIVE=1\n'
fi
"""
    text = run("sample-node-05", command)
    inventory: dict[str, dict[str, int | float]] = {}
    sampled: dict[str, dict[str, str]] = {}
    active_lines: list[str] = []
    marker_count = 0
    apply_values: dict[str, int] = {}
    backup_values: dict[str, int] = {}
    append_values: dict[str, int] = {}
    job_values: dict[str, int] = {}
    p5_progress: list[dict[str, int | str]] = []
    p5_shard_progress: list[dict[str, int | str]] = []
    apply_done_databases: set[str] = set()
    apply_partial_databases: set[str] = set()
    apply_pending_databases: set[str] = set()
    pipeline_runs: list[dict[str, str]] = []

    for line in text.splitlines():
        fields = line.split("\t")
        if fields[0] == "DB" and len(fields) == 6:
            try:
                inventory[fields[1]] = {
                    "tables": int(fields[2]),
                    "size_mb": float(fields[3] or 0),
                    "rows": int(fields[4] or 0),
                    "dated_tables": int(fields[5] or 0),
                }
            except ValueError:
                continue
        elif fields[0] == "TM" and len(fields) == 4:
            sampled.setdefault(fields[1], {})[fields[2]] = fields[3]
        elif line.startswith("MARKERS=") and line[8:].strip().isdigit():
            marker_count = int(line[8:].strip())
        elif line.startswith("APPLY_") and "=" in line:
            key, value = line.split("=", 1)
            if key in {
                "APPLY_RUNNING",
                "APPLY_TABLES",
                "APPLY_DONE",
                "APPLY_FAILED",
            } and value.strip().isdigit():
                apply_values[key] = int(value.strip())
            elif key == "APPLY_DB_DONE":
                apply_done_databases.add(value.strip())
            elif key == "APPLY_DB_PARTIAL":
                apply_partial_databases.add(value.strip())
            elif key == "APPLY_DB_PENDING":
                apply_pending_databases.add(value.strip())
        elif line.startswith("PIPELINE_ACTIVE=") and "|" in line:
            stamp, stage = line.split("=", 1)[1].split("|", 1)
            pipeline_runs.append(
                {
                    "stamp": stamp.strip(),
                    "stage": stage.strip() or "准备中",
                }
            )
        elif line.startswith("BACKUP_") and "=" in line:
            key, value = line.split("=", 1)
            if value.strip().isdigit():
                backup_values[key] = int(value.strip())
        elif line.startswith("APPEND_") and "=" in line:
            key, value = line.split("=", 1)
            if value.strip().isdigit():
                append_values[key] = int(value.strip())
        elif line.startswith("P5_PROGRESS="):
            table, position, size, percent = line.split("=", 1)[1].split("|", 3)
            try:
                p5_progress.append(
                    {
                        "table": table,
                        "position": int(position),
                        "size": int(size),
                        "percent": float(percent),
                    }
                )
            except ValueError:
                continue
        elif line.startswith("P5_SHARD_PROGRESS="):
            table, position, size, percent = line.split("=", 1)[1].split("|", 3)
            try:
                p5_shard_progress.append(
                    {
                        "table": table,
                        "position": int(position),
                        "size": int(size),
                        "percent": float(percent),
                    }
                )
            except ValueError:
                continue
        elif (
            line.startswith("P5_JOB_")
            or line.startswith("P5_SHARD_")
            or line.startswith("P6_JOB_")
        ):
            key, value = line.split("=", 1)
            if value.strip().isdigit():
                job_values[key] = int(value.strip())
        elif line.startswith("ACTIVE="):
            continue
        elif " apply-" in f" {line} " or "bizdb" in line.lower():
            if "grep" not in line and "bizdb_restore_monitor.py" not in line:
                active_lines.append(line.strip())

    return {
        "inventory": inventory,
        "sampled": sampled,
        "active": bool(
            re.search(r"^ACTIVE=1$", text, re.M)
        ),
        "active_lines": active_lines,
        "markers": marker_count,
        "apply_running": apply_values.get("APPLY_RUNNING", 0),
        "apply_tables": apply_values.get("APPLY_TABLES", 0),
        "apply_done": apply_values.get("APPLY_DONE", 0),
        "apply_failed": apply_values.get("APPLY_FAILED", 0),
        "apply_done_databases": sorted(apply_done_databases),
        "apply_partial_databases": sorted(apply_partial_databases),
        "apply_pending_databases": sorted(apply_pending_databases),
        "pipeline_active": bool(pipeline_runs),
        "pipeline_runs": pipeline_runs,
        "backup_ok": backup_values.get("BACKUP_OK", 0),
        "backup_failed": backup_values.get("BACKUP_FAILED", 0),
        "append_tables": append_values.get("APPEND_FILES", 0),
        "append_done": append_values.get("APPEND_DONE", 0),
        "append_failed": append_values.get("APPEND_FAILED", 0),
        "p5_progress": sorted(
            p5_progress, key=lambda item: float(item["percent"])
        ),
        "p5_shard_progress": sorted(
            p5_shard_progress, key=lambda item: float(item["percent"])
        ),
        "p5_job_tables": job_values.get("P5_JOB_TABLES", 0),
        "p5_job_done_tables": job_values.get("P5_JOB_DONE_TABLES", 0),
        "p5_job_total_bytes": job_values.get("P5_JOB_TOTAL_BYTES", 0),
        "p5_job_done_bytes": job_values.get("P5_JOB_DONE_BYTES", 0),
        "p5_job_running_bytes": job_values.get("P5_JOB_RUNNING_BYTES", 0),
        "p5_shard_current_bytes": job_values.get("P5_SHARD_CURRENT_BYTES", 0),
        "p5_shard_total_bytes": job_values.get("P5_SHARD_TOTAL_BYTES", 0),
        "p5_job_running": job_values.get("P5_JOB_RUNNING", 0),
        "p5_job_failed": job_values.get("P5_JOB_FAILED", 0),
        "p6_job_files": job_values.get("P6_JOB_FILES", 0),
        "p6_job_done": job_values.get("P6_JOB_DONE", 0),
        "p6_job_total_bytes": job_values.get("P6_JOB_TOTAL_BYTES", 0),
        "p6_job_done_bytes": job_values.get("P6_JOB_DONE_BYTES", 0),
        "p6_job_running": job_values.get("P6_JOB_RUNNING", 0),
    }


def query_source_export_status() -> dict[str, object]:
    """Read active small-table extraction databases without exposing argv."""

    script = r"""
printf '__EXPORT_BEGIN__\n'
for pid in $(pgrep -f '^/tmp/my2sql-relay' 2>/dev/null); do
  db="$(sudo -n tr '\0' '\n' < "/proc/$pid/cmdline" 2>/dev/null |
    awk '$0 == "-databases" { getline; print; exit }')"
  start_file="$(sudo -n tr '\0' '\n' < "/proc/$pid/cmdline" 2>/dev/null |
    awk '$0 == "-start-file" { getline; print; exit }')"
  stop_file="$(sudo -n tr '\0' '\n' < "/proc/$pid/cmdline" 2>/dev/null |
    awk '$0 == "-stop-file" { getline; print; exit }')"
  current_file="$(sudo -n ls -l "/proc/$pid/fd" 2>/dev/null |
    sed -nE 's#.* -> .*relay-bin\.([0-9]+)$#\1#p' |
    tail -1)"
  printf 'ACTIVE_PROGRESS=%s|%s|%s|%s\n' \
    "$db" "$start_file" "$current_file" "$stop_file"
done
printf 'RUNNING=%s\n' "$(pgrep -fc '^/tmp/my2sql-relay' 2>/dev/null || true)"
printf 'ARCHIVE_COUNT='
find /data/bizops-small-export/archives -maxdepth 1 -type f \
  -name 'bizdb-small-*-part-*.tar.gz' -printf x 2>/dev/null | wc -c
printf '__EXPORT_END__\n'
"""
    result = run_asset(
        "sample-node-22",
        script,
        "__EXPORT_BEGIN__",
        "__EXPORT_END__",
    )
    if result.get("status") != "scanned":
        raise RuntimeError(
            f"source export status unavailable: {result.get('status')}"
        )
    transcript = str(result.get("transcript", ""))
    progress_by_database: dict[str, list[float]] = {}
    for line in transcript.splitlines():
        if not line.startswith("ACTIVE_PROGRESS="):
            continue
        fields = line.split("=", 1)[1].split("|")
        if len(fields) != 4:
            continue
        databases_text, start_text, current_text, stop_text = fields
        numbers = []
        for text in (start_text, current_text, stop_text):
            match = re.search(r"([0-9]+)$", text)
            numbers.append(int(match.group(1)) if match else 0)
        start_number, current_number, stop_number = numbers
        if stop_number > start_number and current_number:
            percentage = max(
                0.0,
                min(
                    99.9,
                    (current_number - start_number)
                    * 100.0
                    / (stop_number - start_number),
                ),
            )
            for database in databases_text.split(","):
                if database.strip():
                    progress_by_database.setdefault(database.strip(), []).append(
                        percentage
                    )
    active_databases = sorted(progress_by_database)
    running_match = re.search(r"^RUNNING=(\d+)$", transcript, re.M)
    archive_match = re.search(r"^ARCHIVE_COUNT=(\d+)$", transcript, re.M)
    return {
        "active_databases": active_databases,
        "progress": {
            database: sum(values) / len(values)
            for database, values in progress_by_database.items()
            if values
        },
        "running_workers": int(running_match.group(1)) if running_match else 0,
        "archive_count": int(archive_match.group(1)) if archive_match else 0,
    }


def format_sampled_time(value: str) -> str:
    if not value or value == "NULL":
        return "无有效时间"
    return value


def human_rows(value: int | float) -> str:
    value = float(value)
    if value >= 100_000_000:
        return f"{value / 100_000_000:.2f}亿"
    if value >= 10_000:
        return f"{value / 10_000:.1f}万"
    return f"{value:.0f}"


def format_pipeline_stage(stage: str) -> str:
    if stage.startswith("DOWNLOAD="):
        archive = stage.split("=", 1)[1].split()[0]
        return f"下载 {archive}"
    if stage.startswith("EXTRACT="):
        archive = stage.split("=", 1)[1].split()[0]
        match = re.search(r"-part-([0-9]+)\.tar\.gz$", archive)
        suffix = f" part-{match.group(1)}" if match else ""
        return f"解压数据包{suffix}"
    if stage.startswith("GZIP="):
        archive = stage.split("=", 1)[1].split()[0]
        match = re.search(r"-part-([0-9]+)\.tar\.gz$", archive)
        suffix = f" part-{match.group(1)}" if match else ""
        return f"校验数据包{suffix}"
    if stage.startswith("REPLAY_START="):
        return "8 路表级回放已开始"
    if stage.startswith("REPLAY_FINISH="):
        return "8 路表级回放已结束，等待核验"
    return stage


def parse_time(value: object) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    days, seconds = divmod(seconds, 86_400)
    hours, seconds = divmod(seconds, 3_600)
    minutes = seconds // 60
    if days:
        return f"{days}天{hours}小时{minutes}分"
    if hours:
        return f"{hours}小时{minutes}分"
    return f"{minutes}分"


def send(text: str) -> None:
    formatted = f"<pre>{html.escape(text)}</pre>"
    proc = subprocess.run(
        [
            "python3",
            "scripts/bizops_notify.py",
            "--quiet",
            "--parse-mode",
            "HTML",
            formatted,
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode:
        raise RuntimeError(proc.stderr.strip())


def send_completion_handoff(
    db1: dict[str, object],
    db2: dict[str, object],
) -> None:
    summary = (
        "【某业务平台数据恢复｜到达 100% 截止点】\n\n"
        "@Ben_Bird 请立即查看并决定是否进入业务切换。\n"
        f"备份节点 基线：已完成（IMPORT_RC={db2.get('import_rc')}，"
        f"{db2.get('import_end') or '完成时间已记录'}）\n"
        f"主节点 回放：已停止\n"
        f"gold 最新：{db1.get('gold_max') or '暂不可读'}\n"
        f"logon 最新：{db1.get('logon_max') or '暂不可读'}\n"
        f"contest 最新：{db1.get('contest_max') or '暂不可读'}\n"
        "恢复截止点：2026-11-07 00:27:11\n\n"
        "以下移交按顺序执行，未完成前不要提前开放网站。"
    )
    messages = [
        summary,
        "@benb6879 @Henry91888 请上某业务平台数据库核验用户、账务、日志表数据完整性与业务可用性。",
        "@louis338888 请在开发数据核验通知后恢复某业务平台主从关系，并核对复制延迟与错误。",
        "@gandalf_dabo 请在 DBA 确认主从正常后开启网站及相关服务。",
        "@Danny66889 请在网站开启后进入后台检查用户、充值、提款、注单、报表及其他数据功能。",
        (
            "@gandalf_dabo @louis338888 今天上班后还需更换除某业务平台外全部盘口的数据库账号密码。"
            "禁止在群聊、脚本输出、截图或工单中放明文密码；密码分段保存、分段交接，"
            "并同步清理 shell history 与遗留配置文件。"
        ),
    ]
    for index, message in enumerate(messages):
        if index:
            time.sleep(3)
        send(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=300)
    parser.add_argument("--periodic", type=int, default=1800)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    state: dict[str, object] = {}
    if STATE.exists():
        try:
            state = json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            state = {}

    while True:
        now = time.time()
        try:
            db2 = {
                "tables": int(state.get("tables", 0)),
                "table": str(state.get("table", "yuanbao")),
                "rows": int(state.get("rows", 0)),
                "size_gb": 0.0,
                "import_rc": state.get("import_rc"),
                "import_end": state.get("import_end", ""),
                "baseline_complete": bool(state.get("baseline_complete")),
            }
            db1 = {
                "running": not bool(state.get("replay_stopped", False)),
                "statements": int(state.get("statements", 0)),
                "gold_max": state.get("gold_max", ""),
                "logon_max": state.get("logon_max", ""),
                "contest_max": state.get("contest_max", ""),
                "flush_mode": state.get("flush_mode", "unknown"),
            }
            total_rows = int(state.get("total_rows", 0))
            if db2["table"] != state.get("table"):
                try:
                    command = (
                        "set +e; password=$(sudo -n sed -nE "
                        "'s/.* -p\"([^\"]+)\".*/\\1/p' /root/mysql.sh | head -1); "
                        "MYSQL_PWD=\"$password\" /data/mysql/bin/mysql -uadmin -N -e "
                        f"\"SELECT table_rows FROM information_schema.tables "
                        f"WHERE table_schema='common_log_db' AND table_name='{db2['table']}'\""
                    )
                    value = run("sample-node-05", command).strip()
                    total_rows = int(value) if value.isdigit() else 0
                except Exception:
                    total_rows = 0

            pct = (
                min(100.0, db2["rows"] * 100.0 / total_rows)
                if total_rows
                else 0.0
            )
            changed_table = db2["table"] != state.get("table")
            baseline_completed_new = bool(db2.get("baseline_complete")) and not bool(
                state.get("baseline_complete")
            )
            current_data_time = max(
                filter(
                    None,
                    [
                        parse_time(db1.get("gold_max")),
                        parse_time(db1.get("logon_max")),
                    ],
                ),
                default=None,
            )
            data_time_pct = (
                max(
                    0.0,
                    min(
                        100.0,
                        (current_data_time - BASELINE_TIME).total_seconds()
                        * 100.0
                        / (USER_DATA_END - BASELINE_TIME).total_seconds(),
                    ),
                )
                if current_data_time
                else float(state.get("data_time_pct", 0.0))
            )
            previous_data_time = parse_time(state.get("current_data_time")) or max(
                filter(
                    None,
                    [
                        parse_time(state.get("gold_max")),
                        parse_time(state.get("logon_max")),
                    ],
                ),
                default=None,
            )
            previous_updated = parse_time(state.get("updated_at"))
            replay_rate = None
            eta_hours = None
            if (
                current_data_time
                and previous_data_time
                and previous_updated
                and current_data_time > previous_data_time
            ):
                data_delta = (current_data_time - previous_data_time).total_seconds()
                wall_delta = (
                    datetime.now().astimezone() - previous_updated
                ).total_seconds()
                if wall_delta > 0:
                    replay_rate = data_delta / wall_delta
                    remaining_data = max(
                        0.0, (TARGET_TIME - current_data_time).total_seconds()
                    )
                    eta_hours = remaining_data / replay_rate / 3_600
                    if not 0 < eta_hours < 24 * 30:
                        eta_hours = None
            periodic = now - float(state.get("last_notify", 0)) >= args.periodic
            should_send = (
                args.force
                or periodic
                or args.once
            )

            gold_time = parse_time(db1.get("gold_max"))
            logon_time = parse_time(db1.get("logon_max"))
            user_data_complete = bool(
                db2.get("baseline_complete")
                and not db1.get("running", True)
                and gold_time
                and logon_time
                and gold_time >= datetime.fromisoformat("2026-11-07 00:04:59")
                and logon_time >= datetime.fromisoformat("2026-11-07 00:02:57")
            )
            export_snapshot: dict[str, object] = {
                "active_databases": state.get("active_databases") or [],
                "running_workers": state.get("source_export_workers") or 0,
                "archive_count": state.get("source_export_archives") or 0,
            }

            if should_send:
                try:
                    database_snapshot = query_database_snapshot()
                    state["database_snapshot"] = database_snapshot
                except Exception as exc:
                    database_snapshot = state.get("database_snapshot", {})
                    database_snapshot["error"] = str(exc)
                try:
                    export_total, export_bytes, part_count, part_bytes, parts_done = (
                        bizdb_export_status()
                    )
                    part_total = max(part_count, parts_done)
                except Exception:
                    export_total, export_bytes = 0, 0
                    part_total, part_bytes, parts_done = 0, 0, 0
                try:
                    export_snapshot = query_source_export_status()
                except Exception:
                    export_snapshot = {
                        "active_databases": state.get(
                            "active_databases", []
                        ),
                        "running_workers": 0,
                        "archive_count": 0,
                    }
                p5_total_bytes = int(
                    database_snapshot.get("p5_job_total_bytes", 0) or 0
                )
                p5_done_bytes = int(
                    database_snapshot.get("p5_job_done_bytes", 0) or 0
                )
                p5_running_bytes = int(
                    database_snapshot.get("p5_job_running_bytes", 0) or 0
                )
                p6_total_bytes = int(
                    database_snapshot.get("p6_job_total_bytes", 0) or 0
                )
                p6_done_bytes = int(
                    database_snapshot.get("p6_job_done_bytes", 0) or 0
                )
                p5_progress = database_snapshot.get("p5_progress", [])
                p5_shard_progress = database_snapshot.get(
                    "p5_shard_progress", []
                )
                shard_current_bytes = int(
                    database_snapshot.get("p5_shard_current_bytes", 0) or 0
                )
                shard_total_bytes = int(
                    database_snapshot.get("p5_shard_total_bytes", 0) or 0
                )
                queue_total_bytes = p5_total_bytes + p6_total_bytes
                queue_progress_bytes = (
                    p5_done_bytes + p5_running_bytes + p6_done_bytes
                )
                queue_pct = (
                    min(100.0, queue_progress_bytes * 100.0 / queue_total_bytes)
                    if queue_total_bytes
                    else 0.0
                )
                queue_rate = None
                queue_eta = None
                previous_queue_bytes = state.get("queue_progress_bytes")
                previous_queue_at = parse_time(state.get("queue_updated_at"))
                current_beijing = datetime.now(
                    timezone(timedelta(hours=8))
                )
                shard_rate = None
                shard_eta = None
                previous_shard_bytes = state.get("shard_progress_bytes")
                previous_shard_at = parse_time(state.get("shard_updated_at"))
                if previous_shard_bytes is not None and previous_shard_at:
                    shard_delta = shard_current_bytes - int(previous_shard_bytes)
                    shard_wall_delta = (
                        current_beijing.replace(tzinfo=None)
                        - previous_shard_at.replace(tzinfo=None)
                    ).total_seconds()
                    if shard_delta > 0 and shard_wall_delta > 0:
                        shard_rate = shard_delta / shard_wall_delta
                        shard_eta = (
                            max(0, shard_total_bytes - shard_current_bytes)
                            / shard_rate
                        )
                if previous_queue_bytes is not None and previous_queue_at:
                    byte_delta = queue_progress_bytes - int(previous_queue_bytes)
                    wall_delta = (
                        current_beijing.replace(tzinfo=None)
                        - previous_queue_at.replace(tzinfo=None)
                    ).total_seconds()
                    if byte_delta > 0 and wall_delta > 0:
                        queue_rate = byte_delta / wall_delta
                        queue_eta = (
                            max(0, queue_total_bytes - queue_progress_bytes)
                            / queue_rate
                        )

                if db1.get("running", True):
                    replay_status = "进行中"
                elif user_data_complete:
                    replay_status = "用户数据已完成；其他库继续排程"
                else:
                    replay_status = "异常停止，尚未完成"
                baseline_state = (
                    f"已完成（IMPORT_RC={db2.get('import_rc')}，"
                    f"{db2.get('import_end') or '完成时间已记录'}）"
                    if db2.get("baseline_complete")
                    else f"进行中（{max(0, db2['tables'] - 1)}/"
                    f"{max(db2['tables'], 103)} 张表已检测）"
                )
                data_time_remaining = (
                    format_duration((USER_DATA_END - current_data_time).total_seconds())
                    if current_data_time
                    else "待核对"
                )
                eta = (
                    f"约 {eta_hours:.1f} 小时"
                    if eta_hours is not None
                    else "样本不足，下一轮更新"
                )
                snapshot_inventory = database_snapshot.get("inventory", {})
                snapshot_times = database_snapshot.get("sampled", {})
                active_databases = set(export_snapshot.get("active_databases", []))
                export_progress = export_snapshot.get("progress", {})
                apply_running = int(database_snapshot.get("apply_running", 0) or 0)
                apply_tables = int(database_snapshot.get("apply_tables", 0) or 0)
                apply_done = int(database_snapshot.get("apply_done", 0) or 0)
                apply_failed = int(database_snapshot.get("apply_failed", 0) or 0)
                apply_done_databases = set(
                    database_snapshot.get("apply_done_databases", [])
                )
                apply_pending_databases = set(
                    database_snapshot.get("apply_pending_databases", [])
                )
                pipeline_runs = database_snapshot.get("pipeline_runs", [])
                pipeline_active = bool(database_snapshot.get("pipeline_active"))
                pipeline_stamps = {
                    str(run.get("stamp", "")) for run in pipeline_runs
                }
                if pipeline_active and any(
                    "p5" in stamp or "p6" in stamp for stamp in pipeline_stamps
                ):
                    active_databases.update({"main_log_db", "finance_db"})
                completed_databases = {"users_db", "common_log_db"}
                replay_completed_lines = []
                recovering_lines = []
                no_increment_lines = []
                pending_lines = []
                no_increment_databases = {
                    "data_db",
                    "geoip",
                    "history_partition_db",
                    "market_db",
                }
                for database in DATABASE_ORDER:
                    if database in completed_databases:
                        continue
                    metrics = snapshot_inventory.get(database, {})
                    tables = metrics.get("tables", "?")
                    size_mb = metrics.get("size_mb")
                    size_text = (
                        f"{float(size_mb) / 1024:.2f} GB"
                        if isinstance(size_mb, (int, float)) and size_mb >= 1024
                        else f"{float(size_mb):.0f} MB"
                        if isinstance(size_mb, (int, float))
                        else "体积待读"
                    )
                    times = snapshot_times.get(database, {})
                    time_text = "、".join(
                        f"{label}={format_sampled_time(value)}"
                        for label, value in times.items()
                    ) or "无时间字段，按表数核对"
                    if database in active_databases:
                        defer_note = ""
                        if database == "main_log_db":
                            defer_note = "；contest 按指示最后处理"
                        elif database == "finance_db":
                            defer_note = "；record_log 按指示最后处理"
                        recovering_lines.append(
                            f"• {database}｜其他表恢复中{defer_note}"
                            f"｜当前库内时间 {time_text}"
                        )
                    elif database in apply_done_databases:
                        replay_completed_lines.append(
                            f"• {database}｜增量表回放完成，待最终核验"
                            f"｜当前库内时间 {time_text}"
                        )
                    elif apply_running and database in apply_pending_databases:
                        recovering_lines.append(
                            f"• {database}｜逐表并发回放中/排队中"
                            f"｜当前库内时间 {time_text}"
                        )
                    elif database in {"main_log_db", "finance_db"}:
                        deferred_table = (
                            "contest"
                            if database == "main_log_db"
                            else "record_log"
                        )
                        pending_lines.append(
                            f"• {database}｜其他表排队中，"
                            f"{deferred_table} 最后处理｜当前库内时间 {time_text}"
                        )
                    elif database in no_increment_databases:
                        no_increment_lines.append(
                            f"• {database}｜本轮未发现可回放增量，待源端终验"
                            f"｜当前库内时间 {time_text}"
                        )
                    else:
                        pending_lines.append(
                            f"• {database}｜{tables} 表 / {size_text}｜"
                            f"当前库内时间 {time_text}"
                        )
                active_state = (
                    f"源端小库抽取运行中，{export_snapshot.get('running_workers', 0)} 个 worker"
                    if export_snapshot.get("active_databases")
                    else f"主节点 逐表并发回放中，{apply_running} 个 worker"
                    if apply_running
                    else "P5 后续队列处理中："
                    + "；".join(
                        f"{run.get('stamp')} "
                        f"{format_pipeline_stage(str(run.get('stage', '')))}"
                        for run in pipeline_runs
                    )
                    if pipeline_active
                    else "当前无补回放进程"
                )
                marker_count = len(
                    set(snapshot_inventory).intersection(某业务平台_DATABASES)
                )
                eta_text = "样本不足，下一轮更新"
                end_text = "待计算"
                estimated_remaining = (
                    shard_eta if shard_eta is not None else queue_eta
                )
                if estimated_remaining is not None:
                    eta_text = format_duration(estimated_remaining)
                    finish_beijing = current_beijing + timedelta(
                        seconds=estimated_remaining
                    )
                    end_text = finish_beijing.strftime("%H:%M")
                active_lines = []
                p5_table_pct = (
                    int(database_snapshot.get("p5_job_done_tables", 0) or 0)
                    * 100.0
                    / int(database_snapshot.get("p5_job_tables", 0) or 1)
                )
                shard_pct = (
                    shard_current_bytes * 100.0 / shard_total_bytes
                    if shard_total_bytes
                    else 0.0
                )
                if int(database_snapshot.get("p6_job_running", 0) or 0):
                    p6_files = int(database_snapshot.get("p6_job_files", 0) or 0)
                    p6_done = int(database_snapshot.get("p6_job_done", 0) or 0)
                    p6_pct = p6_done * 100.0 / p6_files if p6_files else 0.0
                    active_lines.append(
                        f"• P6｜contest、record_log（10–11 月）｜"
                        f"{p6_pct:.2f}%｜{p6_done}/{p6_files} 文件"
                    )
                if int(database_snapshot.get("p5_job_running", 0) or 0):
                    active_lines.append(
                        f"• P5｜main_log_db、finance_db 其他表｜"
                        f"表级 {p5_table_pct:.1f}%｜"
                        f"{database_snapshot.get('p5_job_done_tables', 0)}/"
                        f"{database_snapshot.get('p5_job_tables', 0)} 表完成"
                    )
                    if p5_shard_progress:
                        active_lines.append(
                            f"  - 当前分片补跑：{shard_pct:.2f}%"
                            f"（{shard_current_bytes / 1024**3:.2f}/"
                            f"{shard_total_bytes / 1024**3:.2f} GB）"
                        )
                        effective = {
                            str(item["table"]): float(item["percent"])
                            for item in p5_progress
                        }
                        for item in p5_shard_progress:
                            table_name = str(item["table"])
                            active_lines.append(
                                f"  - {table_name}｜分片 "
                                f"{float(item['percent']):.2f}%"
                                f"｜总覆盖 "
                                f"{effective.get(table_name, 0.0):.2f}%"
                            )
                    else:
                        for item in p5_progress:
                            active_lines.append(
                                f"  - {item['table']}｜"
                                f"{float(item['percent']):.2f}%"
                            )
                if not active_lines:
                    active_lines.append("• 当前无执行中的回放任务")
                gap_lines = (
                    "• report_db：rpt_user 等报表表缺少 2025-06～2026-04",
                    "• game_db、recharge_db、cms_api_db、merchant_db、"
                    "diff_log_db、config_db：动态历史表存在同源年度断层",
                    "• 业务确认：该历史段不重要，暂不继续修复，不阻塞当前开服",
                )
                message = (
                    "【某业务平台 数据恢复｜进行中】\n\n"
                    f"更新时间：{current_beijing:%Y-%m-%d %H:%M}（北京时间）\n"
                    f"表级完成：{database_snapshot.get('p5_job_done_tables', 0)}/"
                    f"{database_snapshot.get('p5_job_tables', 0)}"
                    f"（{p5_table_pct:.1f}%）\n"
                    f"当前最近3个月尾部补跑：{shard_pct:.2f}%"
                    f"（{shard_current_bytes / 1024**3:.2f}/"
                    f"{shard_total_bytes / 1024**3:.2f} GB）\n"
                    f"预计剩余：{eta_text}｜预计完成：北京时间 {end_text}\n\n"
                    "一、正在恢复\n"
                    + "\n".join(active_lines)
                    + "\n\n二、数据断层\n"
                    + "\n".join(gap_lines)
                    + "\n\n三、校验口径\n"
                    "• 同表严格保序，不同表并发\n"
                    "• 完成后核对行数、最大时间、主键和 DROP/TRUNCATE\n"
                    "• 全库核验通过前，不恢复主从、不开放网站"
                )
                replay_complete = bool(
                    int(database_snapshot.get("p5_job_tables", 0) or 0)
                    > 0
                    and int(database_snapshot.get("p5_job_done_tables", 0) or 0)
                    == int(database_snapshot.get("p5_job_tables", 0) or 0)
                    and int(database_snapshot.get("p6_job_files", 0) or 0)
                    > 0
                    and int(database_snapshot.get("p6_job_done", 0) or 0)
                    == int(database_snapshot.get("p6_job_files", 0) or 0)
                    and not int(database_snapshot.get("p5_job_running", 0) or 0)
                    and not int(database_snapshot.get("p6_job_running", 0) or 0)
                    and not int(database_snapshot.get("p5_job_failed", 0) or 0)
                    and not int(database_snapshot.get("append_failed", 0) or 0)
                )
                if replay_complete:
                    if not state.get("replay_completion_notified"):
                        completion_message = (
                            "【某业务平台 数据恢复｜回放全部完成】\n\n"
                            f"完成时间：{current_beijing:%Y-%m-%d %H:%M}"
                            "（北京时间）\n"
                            f"P5：{database_snapshot.get('p5_job_done_tables')}/"
                            f"{database_snapshot.get('p5_job_tables')} 表完成\n"
                            f"P6：{database_snapshot.get('p6_job_done')}/"
                            f"{database_snapshot.get('p6_job_files')} 文件完成\n"
                            "失败数：0\n\n"
                            "当前进入行数、最大时间、主键、1032 差异及 "
                            "DROP/TRUNCATE 最终核验。\n"
                            "历史断层已按业务口径接受，不阻塞开服。\n"
                            "核验通过前仍不恢复主从、不开放网站。"
                        )
                        send(completion_message)
                        state["replay_completion_notified"] = True
                        state["replay_completed_at"] = current_beijing.isoformat()
                elif not state.get("replay_completion_notified"):
                    send(message)
                state["last_notify"] = now

            # 用户数据完成不等于全部 17 个业务库及日志对象完成。
            # 四组移交通知仍需显式设置 all_databases_verified=true 后才发送。
            completed = bool(
                state.get("all_databases_verified")
                and user_data_complete
                and not state.get("completion_notified")
            )
            if completed:
                send_completion_handoff(db1, db2)
                state["completion_notified"] = True
                state["completed_at"] = datetime.now().astimezone().isoformat()

            state.update(
                {
                    "table": db2["table"],
                    "tables": db2["tables"],
                    "rows": db2["rows"],
                    "total_rows": total_rows,
                    "pct": pct,
                    "baseline_complete": bool(db2.get("baseline_complete")),
                    "import_rc": db2.get("import_rc"),
                    "import_end": db2.get("import_end", ""),
                    "statements": db1.get("statements", 0),
                    "gold_max": db1.get("gold_max", ""),
                    "logon_max": db1.get("logon_max", ""),
                    "contest_max": db1.get("contest_max", ""),
                    "flush_mode": db1.get("flush_mode", "unknown"),
                    "replay_stopped": not bool(db1.get("running", True)),
                    "user_data_complete": user_data_complete,
                    "full_recovery_complete": completed,
                    "current_data_time": (
                        current_data_time.isoformat() if current_data_time else ""
                    ),
                    "data_time_pct": data_time_pct,
                    "replay_rate": replay_rate,
                    "eta_hours": eta_hours,
                    "queue_progress_bytes": queue_progress_bytes
                    if should_send
                    else state.get("queue_progress_bytes", 0),
                    "queue_updated_at": current_beijing.isoformat()
                    if should_send
                    else state.get("queue_updated_at", ""),
                    "shard_progress_bytes": shard_current_bytes
                    if should_send
                    else state.get("shard_progress_bytes", 0),
                    "shard_updated_at": current_beijing.isoformat()
                    if should_send
                    else state.get("shard_updated_at", ""),
                    "active_databases": export_snapshot.get(
                        "active_databases", []
                    ),
                    "source_export_workers": export_snapshot.get(
                        "running_workers", 0
                    ),
                    "source_export_archives": export_snapshot.get(
                        "archive_count", 0
                    ),
                    "updated_at": datetime.now().astimezone().isoformat(),
                }
            )
            STATE.write_text(
                json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            if args.once:
                return 0
            if completed:
                return 0
        except Exception as exc:
            print(f"{datetime.now().astimezone().isoformat()} ERROR {exc}", flush=True)
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
````

#### `05_monitoring_verify/run_bizdb_restore_monitor.sh`

**中文备注：** 监控器常驻启动包装，负责读取跳板密钥环境并自动重启。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：05_monitoring_verify
# 中文备注：监控器常驻启动包装，负责读取跳板密钥环境并自动重启。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
# ============================================================================
# 某业务平台数据库恢复工具：常驻监控启动器
# ----------------------------------------------------------------------------
# 从宝塔运维机读取堡垒机跳板密码（只在进程环境中使用，不打印）。
# 每 2 分钟采样一次，每 5 分钟向群发送一次进行中状态。
# 监控脚本异常退出后 30 秒自动重启。
# ============================================================================
set -u

repo="/Users/operator/Projects/ops/private-notes/master"
ops_host="root@192.0.2.38"
ops_key="$repo/infrastructure/brazil/access/192.0.2.38_id_ed25519"

cd "$repo" || exit 1
export PATH="/Users/operator/.local/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export PYTHONPATH="$repo/scripts"
export 某业务公司_BASTION_EXEC_TIMEOUT=75
export BASTION_BOOTSTRAP_PASSWORD="$(
  ssh -i "$ops_key" -o BatchMode=yes -o ConnectTimeout=15 \
    "$ops_host" 'cat /opt/bizops-ops-console/secrets/pgs_deploy_pass'
)"

while true; do
  python3 scripts/bizdb_restore_monitor.py --interval 120 --periodic 300
  rc=$?
  if python3 - <<'PY'
import json
from pathlib import Path
path = Path("/tmp/bizdb-restore-monitor-state.json")
try:
    state = json.loads(path.read_text(encoding="utf-8"))
except Exception:
    raise SystemExit(1)
raise SystemExit(0 if state.get("completion_notified") is True else 1)
PY
  then
    echo "$(date '+%F %T %Z') completion handoff sent; monitor stopped" >&2
    exit 0
  fi
  echo "$(date '+%F %T %Z') monitor exited; restarting in 30 seconds" >&2
  sleep 30
done
````

#### `05_monitoring_verify/emergency_bastion_exec.py`

**中文备注：** 通过新堡垒机执行只读采集脚本，可配置超时。

````python
#!/usr/bin/env python3
# ============================================================================
# 平台：某业务平台
# 恢复阶段：05_monitoring_verify
# 中文备注：通过新堡垒机执行只读采集脚本，可配置超时。
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

#### `05_monitoring_verify/bizdb_online_verify.sql`

**中文备注：** 恢复后在线数据与关键表时间边界的 SQL 核验模板。

````sql
-- 平台：某业务平台
-- 恢复阶段：05_monitoring_verify
-- 中文备注：恢复后在线数据与关键表时间边界的 SQL 核验模板。
-- 安全说明：本文件不包含密码、Token 或私钥。
-- 某业务平台 online verification queries.
-- 主节点: sample-node-05 (192.0.2.14)
-- 备份节点: sample-node-06 (192.0.2.15)
-- Application user_accounts: app_service@198.51.100.% or app_user@198.51.100.%

USE users_db;

SELECT MIN(uid) AS min_user_account_uid FROM user_account;
SELECT COUNT(uid) AS user_account_count FROM user_account;
SELECT MAX(last_update_time) AS max_user_account_update FROM user_account;

SELECT MIN(uid) AS min_user_ext_uid FROM user_ext;
SELECT COUNT(uid) AS user_ext_count FROM user_ext;
SELECT MAX(last_logon_time) AS max_user_account_login FROM user_ext;

-- Log databases are restored separately from users_db.
SELECT MAX(post_time) AS max_comm_gold_time FROM common_log_db.gold;
SELECT MAX(post_time) AS max_contest_time FROM main_log_db.contest;
SELECT MAX(create_time) AS max_comm_logon_time FROM common_log_db.logon;
````

#### `05_monitoring_verify/bizdb_restore_flush_guard.sh`

**中文备注：** 回放期间记录并恢复 MySQL 临时性能参数。

````bash
#!/bin/bash
# ============================================================================
# 平台：某业务平台
# 恢复阶段：05_monitoring_verify
# 中文备注：回放期间记录并恢复 MySQL 临时性能参数。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
set -uo pipefail

log=/tmp/bizdb-restore-flush-guard.log
mysql_bin=/data/mysql/bin/mysql
apply_pid_file=/tmp/bizdb-restore-flush-guard.pid
original_file=/tmp/bizdb-restore-flush-original

printf '%s\n' "$$" >"$apply_pid_file"
echo "$(date '+%F %T %Z') guard_start pid=$$" >>"$log"

mysql_password() {
  local password
  password="$(sudo -n sed -nE 's/.* -p"([^"]+)".*/\1/p' /root/mysql.sh | head -1)"
  [ -n "$password" ] || password="$(sudo -n sed -nE "s/.* -p'([^']+)'.*/\1/p" /root/mysql.sh | head -1)"
  printf '%s' "$password"
}

mysql_query() {
  local password
  password="$(mysql_password)"
  MYSQL_PWD="$password" "$mysql_bin" -uroot -N --batch -e "$1"
}

restore_flush_mode() {
  local original="1"
  [ -s "$original_file" ] && original="$(cat "$original_file")"
  local password
  password="$(mysql_password)"
  if MYSQL_PWD="$password" "$mysql_bin" -uroot -e \
      "SET GLOBAL innodb_flush_log_at_trx_commit=$original" 2>>"$log"; then
    echo "$(date '+%F %T %Z') flush_mode_restored=$original" >>"$log"
  else
    echo "$(date '+%F %T %Z') flush_mode_restore_failed original=$original" >>"$log"
  fi
}

trap restore_flush_mode EXIT INT TERM

original="$(mysql_query 'SELECT @@GLOBAL.innodb_flush_log_at_trx_commit')"
case "$original" in
  0|1|2) printf '%s\n' "$original" >"$original_file" ;;
  *)
    echo "$(date '+%F %T %Z') invalid_original=$original" >>"$log"
    exit 2
    ;;
esac

echo "$(date '+%F %T %Z') original=$original waiting_for_replay" >>"$log"
while pgrep -f '^/bin/bash /tmp/apply-logcomm-all.sh' >/dev/null; do
  sleep 15
done

echo "$(date '+%F %T %Z') replay_process_finished" >>"$log"
restore_flush_mode
trap - EXIT INT TERM
echo "$(date '+%F %T %Z') guard_complete" >>"$log"
````

### 8.6 06_rebuild_docs 工具包重建

一键重建本说明文档、脚本分类目录、SHA256 清单和 zip 工具包。

#### `06_rebuild_docs/build_bizdb_recovery_toolkit.py`

**中文备注：** 工具包构建器；修改脚本或备注后重新运行即可生成新文档和压缩包。

````python
#!/usr/bin/env python3
# ============================================================================
# 平台：某业务平台
# 恢复阶段：06_rebuild_docs
# 中文备注：工具包构建器；修改脚本或备注后重新运行即可生成新文档和压缩包。
# 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。
# ============================================================================
"""生成 某业务平台数据库恢复脚本与工具包。

输出内容：
1. 一份中文 Markdown 总说明，包含目录树、操作顺序和全部脚本源码；
2. 按恢复阶段分类的脚本副本；
3. SHA256SUMS；
4. 可直接发群下载的 zip 压缩包。

脚本副本会额外加入中文头注释。生产脚本本身不会被这份构建器改写。
"""

from __future__ import annotations

import hashlib
import shutil
import zipfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261110"
OUT_DIR = ROOT / "deliverables" / f"bizdb-recovery-toolkit-{STAMP}"
DOC_NAME = "某业务平台数据库恢复脚本与工具说明.md"
DOC_PATH = ROOT / "docs" / "history" / f"2026-11-10-0420-【恢复工具】{DOC_NAME}"


GROUPS = [
    (
        "01_source_export",
        "从源端 relay/binlog 生成带表名和主键条件的可执行 SQL。",
        [
            (
                "bizdb_source_export_full.sh",
                "导出整库全量 SQL 基线，供目标机恢复 2026-05-10 基线。",
            ),
            (
                "bizdb_source_binlog_export.sh",
                "串行从 relay/binlog 导出增量 SQL。",
            ),
            (
                "bizdb_source_binlog_parallel.sh",
                "按 relay 文件区间拆分并并行导出增量 SQL。",
            ),
            (
                "bizdb_user_accounts_my2sql_export.sh",
                "通用 my2sql 并行导出器，支持指定数据库、表、文件区间和输出归档。",
            ),
        ],
    ),
    (
        "02_baseline_pitr",
        "下载、校验和导入全量基线，并执行早期 PITR 增量回放。",
        [
            (
                "bizdb_target_download_parallel.sh",
                "从宝塔中转目录并行下载基线和增量包，并进行 gzip 校验。",
            ),
            (
                "bizdb_target_import_baseline.sh",
                "按数据库导入全量基线，生成完成标记。",
            ),
            (
                "bizdb_target_import_named.sh",
                "按指定数据库导入单个基线包，便于失败后单独重跑。",
            ),
            (
                "bizdb_target_import_remaining.sh",
                "继续导入尚未完成的基线包。",
            ),
            (
                "bizdb_finalize_log_baselines.sh",
                "确认日志库基线表数量并写入完成标记。",
            ),
            (
                "bizdb_target_finish_log_baselines.sh",
                "日志库基线完成后的补收尾流程。",
            ),
            (
                "bizdb_target_apply_incremental.sh",
                "基础增量 SQL 回放器。",
            ),
            (
                "bizdb_target_apply_incremental_parallel.sh",
                "并行增量 SQL 回放器，按表/分片提高吞吐。",
            ),
            (
                "bizdb_filtered_pitr.sh",
                "按时间与对象范围过滤 PITR SQL，排除不允许重放的事件。",
            ),
            (
                "bizdb_user_accounts_my2sql_apply.sh",
                "用户核心表 my2sql 结果的批量回放入口。",
            ),
            (
                "bizdb_my2sql_apply_parallel.py",
                "用户核心表按 UID 稳定分片并并行回放。",
            ),
        ],
    ),
    (
        "03_table_parallel",
        "按表组装 SQL、备份、按表并发回放，并支持 done 标记断点续跑。",
        [
            (
                "bizdb_small_table_backup.sh",
                "回放前逐表 mysqldump 备份，失败时禁止继续写库。",
            ),
            (
                "bizdb_wait_and_apply_small.sh",
                "等待源端导出完成、下载校验、解压并自动启动表级回放。",
            ),
            (
                "bizdb_apply_small_table_sql.sh",
                "主表级并发回放器；小表优先、同表保序、INSERT IGNORE、事务参数自动恢复。",
            ),
            (
                "bizdb_import_closed_chunks.sh",
                "导入已封包的 SQL 分片并维护完成状态。",
            ),
            (
                "bizdb_replay_uid_sharded.sh",
                "按 UID 分片执行单张大表，同一 UID 保持顺序。",
            ),
        ],
    ),
    (
        "04_large_log_tables",
        "处理 contest、record_log 等超大日志表的倒序 INSERT 与主键分片。",
        [
            (
                "bizdb_apply_append_only_desc.sh",
                "仅回放 INSERT，最新 binlog 优先、单文件倒序、INSERT IGNORE 并发执行。",
            ),
            (
                "bizdb_resume_key_sharded.py",
                "按主键稳定分片并行回放 INSERT/DELETE，支持跨行 JSON 完整语句解析和批量提交。",
            ),
        ],
    ),
    (
        "05_monitoring_verify",
        "恢复期间采样真实字节进度、失败数、ETA，并通过群机器人通知。",
        [
            (
                "bizdb_restore_monitor.py",
                "每 5 分钟群播报进行中任务、表级完成度、尾部补跑进度、失败数和预计北京时间。",
            ),
            (
                "run_bizdb_restore_monitor.sh",
                "监控器常驻启动包装，负责读取跳板密钥环境并自动重启。",
            ),
            (
                "emergency_bastion_exec.py",
                "通过新堡垒机执行只读采集脚本，可配置超时。",
            ),
            (
                "bizdb_online_verify.sql",
                "恢复后在线数据与关键表时间边界的 SQL 核验模板。",
            ),
            (
                "bizdb_restore_flush_guard.sh",
                "回放期间记录并恢复 MySQL 临时性能参数。",
            ),
        ],
    ),
    (
        "06_rebuild_docs",
        "一键重建本说明文档、脚本分类目录、SHA256 清单和 zip 工具包。",
        [
            (
                "build_bizdb_recovery_toolkit.py",
                "工具包构建器；修改脚本或备注后重新运行即可生成新文档和压缩包。",
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
            f"-- 平台：某业务平台",
            f"-- 恢复阶段：{stage}",
            f"-- 中文备注：{note}",
            "-- 安全说明：本文件不包含密码、Token 或私钥。",
            "",
        ]
        return "\n".join(header) + source

    marker = "#"
    header = [
        f"{marker} ============================================================================",
        f"{marker} 平台：某业务平台",
        f"{marker} 恢复阶段：{stage}",
        f"{marker} 中文备注：{note}",
        f"{marker} 安全说明：本文件不包含密码、Token 或私钥；运行时从受限环境读取。",
        f"{marker} ============================================================================",
        "",
    ]
    shebang, separator, body = source.partition("\n")
    if separator and shebang.startswith("#!"):
        return shebang + "\n" + "\n".join(header) + body.lstrip("\n")
    return "\n".join(header) + source


def tree_lines() -> list[str]:
    lines = [
        f"bizdb-recovery-toolkit-{STAMP}/",
        f"├── README.md",
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
    copied_files: list[Path] = []

    for group, group_note, files in GROUPS:
        target_dir = OUT_DIR / group
        target_dir.mkdir()
        sections.append(f"## {group}\n\n{group_note}\n")
        for name, note in files:
            source = read_source(name)
            bundled = add_chinese_header(name, group, note, source)
            target = target_dir / name
            target.write_text(bundled, encoding="utf-8")
            copied_files.append(target)

            language = "python" if name.endswith(".py") else "sql" if name.endswith(".sql") else "bash"
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
    document = f"""# 某业务平台数据库恢复脚本与工具说明

> **平台标识：某业务平台**  
> 生成时间：2026-11-10（Asia/Manila，UTC+8）  
> 适用场景：数据库误删后的全量基线恢复、binlog/PITR 增量回放、超大表专项恢复与进度通知。

## 一、本次恢复结果

- P5：27/27 张表回放完成，失败 0。
- P6：96/96 个 SQL 文件完成，失败 0。
- `contest_list`、`balance_relation`、`contest`、`record_log` 最后数据时间为 `2026-11-07 00:04:59`。
- 相关表主键数量均等于行数，`CHECK TABLE` 全部为 `OK`。
- 回放结束后 `innodb_flush_log_at_trx_commit=1`，`event_scheduler=ON`。
- 历史断层 `2025-06～2026-04` 已由业务确认不处理，不阻塞本次开服。

## 二、目录树

```text
{tree}
```

## 三、恢复流程

1. **源端全量导出**：从源库或备份机导出各业务库基线。
2. **源端 binlog 导出**：按 relay 文件区间和恢复截止时间生成表级 DML。
3. **目标机基线导入**：逐库导入全量 SQL，并写完成标记。
4. **早期 PITR**：按 UID 或表进行增量回放，恢复用户和日志主链路。
5. **小表优先回放**：按表并发；同一张表保持 binlog 顺序。
6. **超大表专项**：
   - `contest`、`record_log`：按最新 binlog 优先、仅回放 INSERT。
   - 剩余大表：按主键稳定分片，同一主键只进入一个 shard。
7. **持续核验**：检查行数、主键、最大时间、SQL 错误和 `CHECK TABLE`。
8. **自动化通知**：每 5 分钟播报进行中任务；全部回放完成后只发一次完成通知。

## 四、安全边界

- 脚本不包含数据库密码、Telegram Token、SSH 私钥或云 API 密钥。
- 凭据只从 root-only 配置文件或进程环境读取。
- 写库前必须完成备份；备份失败时脚本拒绝继续。
- 默认拒绝 DDL、DROP、TRUNCATE 和 YYYYMMDD 日期分区表。
- 同一张表只能由一个 worker 顺序处理；不同表或不同主键 shard 才允许并发。
- 临时性能参数在脚本退出时恢复。
- 回放完成不等于业务验收完成；主从切换和开放网站必须由人工确认。

## 五、关键环境变量

| 变量 | 用途 |
|---|---|
| `PGS_DATABASE` / `PGS_TABLES` | 源端导出的数据库与表 |
| `PGS_START_FILE` / `PGS_STOP_FILE` | relay/binlog 文件范围 |
| `PGS_STOP_DATETIME` | 安全恢复截止时间 |
| `PGS_DESTINATION` | SQL 包上传目标 |
| `某业务平台_SMALL_APPLY_WORKERS` | 表级回放并发数 |
| `某业务平台_SMALL_REUSE_COMBINED` | 复用已组装 SQL，断点续跑 |
| `某业务平台_APPEND_ONLY_START_FILE` | 超大日志表起始 relay 文件号 |
| `某业务平台_APPEND_ONLY_WORKERS` | 文件级并发数 |
| `某业务公司_BASTION_EXEC_TIMEOUT` | 堡垒机只读采集超时 |

## 六、脚本与完整源码

以下源码是本次在 某业务平台恢复中使用的工具副本。压缩包中的副本额外加入了
“平台、恢复阶段、中文备注、安全说明”头注释。

{chr(10).join(sections)}
"""
    readme = document
    (OUT_DIR / "README.md").write_text(readme, encoding="utf-8")
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

    archive = ROOT / "deliverables" / f"bizdb-recovery-toolkit-{STAMP}.zip"
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

## 九、归档复核结论

本次某业务平台恢复工具链已完成文档化归档。29 个归档内容文件、17 个业务库基线导出、relay/binlog PITR、表级并发、超大日志表专项回放、回放前备份、在线核验和通知脚本均有对应说明；脚本源码在本文中完整保留。

P5 的 27/27 张表和 P6 的 96/96 个 SQL 文件均完成回放且失败数为 0。`contest_list`、`balance_relation`、`contest`、`record_log` 的最后数据时间均为 `2026-11-07 00:04:59`；相关表主键数量等于行数，`CHECK TABLE` 全部返回 `OK`。回放结束后 `innodb_flush_log_at_trx_commit=1`、`event_scheduler=ON`。历史断层 `2025-06～2026-04` 已由业务确认不处理，不阻塞本次开服。

后续复用本工具包时，应先确认恢复对象、截止时间、业务库范围和备份可用性，再按目录顺序执行。回放完成只代表数据任务结束，主从切换、业务验收和网站开放仍需人工确认。所有脚本仅用于本次某业务平台恢复审计与复盘。
