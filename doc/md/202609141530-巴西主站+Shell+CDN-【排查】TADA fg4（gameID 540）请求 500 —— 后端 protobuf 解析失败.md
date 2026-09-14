---
id: "doc-62572f661b0f"
title: "【排查】TADA fg4（gameID 540）请求 500 —— 后端 protobuf 解析失败"
date: "2026-09-14T15:30:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Shell", "CDN", "故障排查"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-09-14-1530-%E3%80%90%E6%8E%92%E6%9F%A5%E3%80%91TADA-fg4-540%E6%B8%B8%E6%88%8F%E8%AF%B7%E6%B1%82-protobuf%E8%A7%A3%E6%9E%90%E5%A4%B1%E8%B4%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-09-14-1530-【排查】TADA-fg4-540游戏请求-protobuf解析失败记录.md"
sourceSha256: "7d45b57e8124088e8df8af93c7778413034fb3a009fa333a470d177920fc0308"
sourceSystem: "project-doc"
---

# 【排查】TADA fg4（gameID 540）请求 500 —— 后端 protobuf 解析失败

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-09-14-1530-【排查】TADA-fg4-540游戏请求-protobuf解析失败记录.md`

> 整理日期：2026-09-14 15:30｜日期依据：文件名日期

时间：2026-09-14 15:30（Asia/Manila）
提出人：Ben（开发）
执行人：Codex（运维）
状态：已定位到后端代码位置，待开发按协议修复

## 一、现象

```text
游戏 fg4（gameID=540）打不开；前端发起的接口请求返回 500。
入口静态页与动态域都正常，问题只出现在「后端解析这条游戏请求」。
```

## 二、复现与实测结果

### 2.1 原样请求（开发提供）

```bash
curl --url 'https://tada-games.tada-cdn-2026.icu/fg4/' \
  -H 'accept: application/json, text/javascript, text/plain' \
  -H 'origin: https://tada-statics1.xqv9m8.icu' \
  -H 'referer: https://tada-statics1.xqv9m8.icu/' \
  -H 'user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) ...' \
  -H 'x-front-page: https://tada-statics1.xqv9m8.icu/fg4/index.html?...&gameID=540&...'
```

结果：`404 File Not Found`（14B / text/plain）——`/fg4/` 不是真实接口路径。

### 2.2 真实接口路径对比（同一台后端）

| 请求 | 结果 | 说明 |
| --- | --- | --- |
| `GET  /fg4/req` | **405 Method Not Allowed** | 后端在响应，只是该用 POST |
| `GET  /c7d/req` | 405 | 同上 |
| `GET  /lm/req` | 405 | 同上 |
| `POST /fg4/req`（空 `{}`） | **500 Internal Server Error** | 后端抛异常 |

结论：**动态域与后端连通正常**（405 说明路由命中、处理链路在），不是 CDN/静态/网络问题。

### 2.3 静态与健康对照（全部正常）

```text
tada-statics1.xqv9m8.icu/fg4/           → 302 → /fg4/index.html 200（34182B）
tada-games.tada-cdn-2026.icu/health     → 200
```

## 三、后端真实报错（TADA 容器日志，可直接定位）

```text
Traceback (most recent call last):
  File "share_libs/miniapp.py", line 692, in async_inner
  File "/app/tada/tada.py", line 3132, in common_req
    else await getReq(
  File "/app/tada/tada.py", line 856, in getReq
    raise RuntimeError(f"❌ 解析 Request 失败: {e}")
RuntimeError: ❌ 解析 Request 失败: Error parsing message with type 'serverProto.Request'
```

关键点：

```text
· 出错位置：tada/tada.py 第 856 行 getReq()
· 上层调用：tada/tada.py:3132 common_req → share_libs/miniapp.py:692 async_inner
· 异常类型：protobuf 解析失败（Error parsing message with type 'serverProto.Request'）
· 容器：dbqp-tada-release-01（后端 01，单机模式）；近 5 分钟同类错误 37 条
```

## 四、判断：客户端 protobuf 与后端定义不匹配

`serverProto.Request` 是后端按 `serverProto` 编译出的 protobuf 消息，报 “Error parsing message” 通常意味着：

```text
1) 游戏前端换了新版本协议（字段/序号/消息体变化），后端 serverProto 仍是旧定义
   → 需要用厂商最新 .proto 重新生成后端解析代码
2) 或请求体被截断 / 编码方式变化（Content-Type、压缩、长度）导致反序列化失败
3) 也可能是该游戏（540/fg4）走了一条后端还没支持的子协议
```

## 五、请开发这样处理（建议顺序）

```text
1) 用厂商最新 serverProto（.proto）重新生成后端解析代码，替换 tada 容器内相关模块，
   重启 dbqp-tada-release-01 后复测 fg4
2) 若确认协议没变，则抓一条「真实失败请求原文」对照：
   浏览器 F12 → Network → 找到 POST /fg4/req 的失败请求 → Copy as cURL（含请求体）发运维
3) 如需服务端抓原始请求体（十六进制）做对照，告知运维即可
```

## 六、已排除的方向（避免重复排查）

```text
· 静态资源：fg4 的 index.html 与目录 URL 均 200（单桶化切换后已逐个验证）
· CDN/Worker：同域其它游戏（c7d/lm）同样能命中后端（405），路由与回源正常
· 网络/国家白名单：动态域不受静态 Worker 的国家白名单影响，health 200
· 后端进程：TADA 容器运行中，其它 gameid 仍在正常结算
```

## 七、本地提交

```text
（提交号文末回写）
```
