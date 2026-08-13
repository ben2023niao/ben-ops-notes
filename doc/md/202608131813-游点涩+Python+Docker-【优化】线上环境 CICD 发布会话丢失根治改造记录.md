---
id: "doc-713c63474d24"
title: "【优化】线上环境 CICD 发布会话丢失根治改造记录"
date: "2026-08-13T18:13:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Python", "Docker", "自动化", "安全运维", "故障排查", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-13-1813-%E3%80%90%E4%BC%98%E5%8C%96%E3%80%91%E7%BA%BF%E4%B8%8A%E7%8E%AF%E5%A2%83CICD%E5%8F%91%E5%B8%83%E4%BC%9A%E8%AF%9D%E4%B8%A2%E5%A4%B1%E6%A0%B9%E6%B2%BB%E6%94%B9%E9%80%A0%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-13-1813-【优化】线上环境CICD发布会话丢失根治改造记录.md"
sourceSha256: "062cbe8dec8dfa6c857273ef4bc878a030d8be8b1f84495580645eb679245df6"
sourceSystem: "project-doc"
---

# 【优化】线上环境 CICD 发布会话丢失根治改造记录

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-08-13-1813-【优化】线上环境CICD发布会话丢失根治改造记录.md`

> 整理日期：2026-08-13 18:13｜日期依据：文件名日期

文档日期：2026-08-13 18:13
环境：游点涩线上环境（main 分支）
分类：优化
标签：线上环境、后端、CICD、发布稳定性、SessionNotFoundException、WebLogger

## 背景

2026-08-13 线上后端发布 45af8d1487af 时再次因 `pywebio SessionNotFoundException` 中断（详见
`docs/2026-08-13-1808-【问题排查+发布】线上环境后端发布会话丢失异常定位与恢复记录.md`）。
本次对 `cicd-web/logs` 全部发布日志做了扫描，确认这不是偶发：

```text
发布异常次数：8 次（07-30、08-01、08-03、08-05 x2、08-07、08-11、08-13）
异常类型：全部为 pywebio.exceptions.SessionNotFoundException（2 处输出/次）
发生阶段：全部在 Web 页面发起的 Docker 构建阶段（Phalcon 编译约 4 分钟）
共同影响：发布中断在 up 之前，生产容器未受影响；发布锁自动释放
CLI 发布：同期 CLI 发布全部成功，未出现该问题
```

## 根因

CICD Web 基于 PyWebIO 会话模型。发布流程把 Docker 构建长日志实时渲染到浏览器会话 scope：

```text
run_stream -> logger.log -> CompositeLogger -> WebLogger.log
  -> with use_scope(deploy_log) -> get_current_session
  -> 会话丢失时抛 SessionNotFoundException
```

浏览器关闭/刷新/切后台超时/网络切换都会导致会话失效；日志输出一旦失败，
异常沿 run_stream -> build_image -> run_deploy 向上传播，整个发布流程被中断。

## 改造内容

### 1. WebLogger 会话安全（cicd-web/command.py）

`WebLogger` 的所有页面输出（log / write_html / force_scroll_bottom）统一走 `_render` 保护：

- 正常时行为不变：实时输出到页面并滚动到底部；
- 会话失效时捕获异常，降级为控制台输出并打印 `[web-session-lost]` 标记；
- 绝不向外抛异常，发布主流程（git -> build -> up -> health）可继续执行；
- 文件日志与 Telegram 通知不受影响，最终结果仍完整送达。

### 2. 发布页提示与成功后渲染保护（cicd-web/steps/publish.py）

- 发布开始前增加提示：发布开始后请勿关闭或刷新页面；即使浏览器会话中断，发布仍会继续，
  最终结果以 Telegram 通知为准。
- 发布成功后页面渲染（第五步容器状态、成功/警告/失败提示、自动刷新）包裹 try/except：
  会话已失效时只降级，不改变发布结果；成功通知与发布日志文档已在渲染前发送。

## 验证结果

```text
语法：本地 python3 与线上生产 venv（Python 3.10.12）py_compile 均通过
模拟测试：monkeypatch use_scope/put_html/scroll_to 抛 SessionNotFoundException 后，
  WebLogger.log / write_html / force_scroll_bottom 全部降级成功，无异常抛出
上线：运维仓库提交 a886838 推送 main，线上仓库同步后 ./cicd-web.sh restart
  CICD Web 新进程 PID 2116151 运行中，页面 HTTP 200，线上文件已含修复代码
```

## 发布信息

```text
运维仓库提交：a886838（fix(cicd): WebLogger会话丢失降级，发布不再因SessionNotFoundException中断）
改动文件：cicd-web/command.py（+44/-?）、cicd-web/steps/publish.py（+33/-?）
线上生效：2026-08-13 18:13 已重启 CICD Web
```

## 效果预期与后续建议

```text
1. 浏览器会话丢失不再中断发布：构建/拉起/健康检查会继续完成，结果以 Telegram 与文件日志为准。
2. 仍推荐长时间构建优先用 CLI 发布（cicd-web.py deploy --git-id <sha> --with-cron --json）。
3. 可选治本方向（后续排期）：把发布长任务改为独立后台进程/线程，页面只订阅展示状态，
   日志输出完全不依赖活动会话；本次“降级不中断”已覆盖故障面，后台化是体验增强。
```

## 回滚

```text
git revert a886838 并推送 main；线上自动更新或 ./cicd-web.sh restart 后恢复旧行为。
```

## 通知记录

```text
步骤 1 文档与 workbench 就绪          message_id 9287
步骤 2 最近发布失败日志分析           message_id 9289
步骤 3 CICD 发布稳定性代码改造         message_id 9292
步骤 4 线上验证与 CICD 重启上线        message_id 9293
最终总结                             见群内后续消息
```

## 安全与敏感内容

本记录不输出 Telegram token/chat_id、私钥、Git 凭据。
