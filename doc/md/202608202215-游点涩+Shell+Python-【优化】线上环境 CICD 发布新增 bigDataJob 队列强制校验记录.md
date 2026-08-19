---
id: "doc-372e3af79abf"
title: "【优化】线上环境 CICD 发布新增 bigDataJob 队列强制校验记录"
date: "2026-08-20T22:15:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Python", "Docker", "自动化", "安全运维", "故障排查", "数据库恢复"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-2215-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83CICD%E5%8F%91%E5%B8%83%E6%96%B0%E5%A2%9EbigDataJob%E9%98%9F%E5%88%97%E5%BC%BA%E5%88%B6%E6%A0%A1%E9%AA%8C%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-2215-【优化】线上环境CICD发布新增bigDataJob队列强制校验记录.md"
sourceSha256: "fe8a7000614375427ca882113525f015887cb3e78ca6e7af3ea9d249fbda8561"
sourceSystem: "project-doc"
---

# 【优化】线上环境 CICD 发布新增 bigDataJob 队列强制校验记录

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-20-2215-【优化】线上环境CICD发布新增bigDataJob队列强制校验记录.md`

> 整理日期：2026-08-20 22:15｜日期依据：文件名日期

文档日期：2026-08-20 22:15
环境：游点涩线上环境（main 分支）
分类：优化 / 发布流程
标签：线上环境、CICD、发布健康检查、bigDataJob、队列守护、强制校验

## 背景

2026-08-20 修复线上大数据上报队列 `bigDataJob queue` 未启动问题后，
用户要求：后续每次发布代码 / 更新代码，该队列都必须启动起来，避免
`big_data_job` 再次积压。为此将“队列守护存在”固化为 CICD 发布健康检查
的强制校验项。

## 调整内容

```text
cicd-web/core.py：
1. HealthResult 新增 queue 字段；
2. HealthResult.ok 增加判定：cron 模式下 queue 必须为 ok，
   否则发布结果不通过（SUCCESS 必要条件）；纯 Web 模式为 n/a 不判定；
3. 新增 check_bigdata_queue_worker()：在 cron 容器内通过 /proc 遍历
   校验 shell.php bigDataJob queue 进程是否存在；
4. check_services() 在 with_cron=True 时执行队列校验；
5. 发布成功 / 健康检查通知新增“队列：ok/missing”行；
6. DeployResult.to_json_dict 同步新增 queue 字段。
```

队列校验命令（容器内）：

```sh
found=0; for p in /proc/[0-9]*; do
  tr "\0" " " < "$p/cmdline" 2>/dev/null | grep -qE "shell\.php bigDataJob queue" && found=1
done; echo $found
```

线上同步：

```text
/opt/docker-youdianse-php/cicd-web/core.py 已同步
原文件备份：cicd-web/core.py.bak.20260820-bigdata
cicd-web 服务已重启（cicd-web.py --host 0.0.0.0 --port 18090）
```

## 验证

```text
1. 本地 python3 -m py_compile core.py 语法通过；
2. 线上 runtime/venv/bin/python -m py_compile core.py 语法通过；
3. 线上 cron 容器实测检查命令输出 found=1（bigDataJob queue 在跑）；
4. cicd-web 新进程 PID 4174274 运行中，端口 18090 监听正常，启动日志无报错；
5. big_data_job 积压最终确认：121088 -> 2（基本清空），failed=0，
   剩余为瞬时新写入任务，由守护进程持续消费。
```

## 后续

```text
1. 每次发布/更新代码，发布通知将包含“队列：ok/missing”，
   missing 时发布判定 WARNING，需先修复再发布；
2. 若新增其他必须常驻的队列，同步维护 docker-compose.yml 的
   QUEUE_WORKERS 与本校验函数；
3. 观察 bigDataJob queue 长期稳定性与 big_data_job 积压水位。
```

## 通知记录

```text
步骤 1：Mongo big_data_job 积压继续下降（23867 -> 9105）
步骤 2：Mongo big_data_job 积压已基本清空（121088 -> 2，failed=0）
步骤 3：CICD 发布流程新增 bigDataJob 队列强制校验（本地代码）
步骤 4：线上 CICD 已同步并重启，队列校验生效
步骤 5：doc 更新与本地提交
汇总：见群内最终总结
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据。
