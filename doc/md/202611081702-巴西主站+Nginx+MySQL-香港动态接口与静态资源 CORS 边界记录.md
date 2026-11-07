---
id: "doc-42b228c62a99"
title: "香港动态接口与静态资源 CORS 边界记录"
date: "2026-11-08T17:02:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Nginx", "MySQL", "CDN", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/pgserver/master/docs/history/2026-11-08-1702-%E3%80%90%E6%A0%B8%E5%AF%B9%E3%80%91%E9%A6%99%E6%B8%AF%E5%8A%A8%E6%80%81%E6%8E%A5%E5%8F%A3%E4%B8%8E%E9%9D%99%E6%80%81%E8%B5%84%E6%BA%90CORS%E8%BE%B9%E7%95%8C%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/work/game/pgserver/master/docs/history/2026-11-08-1702-【核对】香港动态接口与静态资源CORS边界记录.md"
sourceSha256: "9d863027009136cff03d42810e65f0cee2bae8cf1dccf6aa1a4b06c2467a9ce9"
sourceSystem: "project-doc"
---

# 香港动态接口与静态资源 CORS 边界记录

> 来源文件：`~/Projects/work/game/pgserver/master/docs/history/2026-11-08-1702-【核对】香港动态接口与静态资源CORS边界记录.md`

> 整理日期：2026-11-08 17:02｜日期依据：文件名日期

时间：2026-11-08 17:02 至 19:35（Asia/Manila）

执行范围：`m4q7z1.shop`、`p3w9n5.shop` 两个腾讯云 EdgeOne 站点，以及香港源站 Nginx。

## 一、结论

动态接口的 CORS 由业务代码负责。Nginx 只透传后端响应头，EdgeOne 只做动态转发和 NoCache，不补 CORS。

运维需要关注静态资源的跨域读取能力。当前抽查的静态域名已经返回允许任意来源的响应头，动态域名也不需要额外兜底。

本次处理期间曾临时添加动态 EdgeOne CORS 规则 `rule-3x65h1mmsj0a`。按上述架构复核后已撤回。腾讯云 API 回读两个站点的自定义规则数量均为 0。

## 二、源站直连验证

测试使用 `http://34.150.1.185` 加业务 Host，绕过 EdgeOne，直接检查香港 Nginx 和上游后端。

| 目标 | 请求 | 结果 |
|---|---|---|
| `api.m4q7z1.shop` | GET，Origin 为 `https://pg-games.m4q7z1.shop` | 400；返回 `ACAO=https://pg-games.m4q7z1.shop` 和 `Allow-Credentials=true` |
| `api.m4q7z1.shop` | OPTIONS，任意 Origin | 204；按请求 Origin 返回 `ACAO` |
| `socket.p3w9n5.shop` | GET，Origin 为 `https://probe.example` | 400；返回 `ACAO=https://probe.example` 和 `Allow-Credentials=true` |

返回的允许方法包含 GET、POST、PUT、DELETE、OPTIONS。允许头包含 Content-Type、Authorization、x-token、X-Token、x-app-trace-id、token 和 gdid。

这些头来自源站链路，不由 EdgeOne 规则新增。API 实际响应仍固定返回 `https://pg-games.m4q7z1.shop`；如果开发继续看到该来源的跨域失败，应检查业务代码分支和浏览器缓存，不再向 Nginx 或 EdgeOne 增加规则。

## 三、EdgeOne 验证

| Zone | Zone ID | 自定义规则数 | 处理结果 |
|---|---|---:|---|
| `m4q7z1.shop` | `zone-3vm5evyb78ic` | 0 | 临时动态 CORS 兜底已撤回 |
| `p3w9n5.shop` | `zone-3vm7chzbxkcb` | 0 | 无动态 CORS 规则 |

动态接口的 `eo-cache-status` 为 `MISS`，没有发现动态响应被边缘缓存。

## 四、静态域名抽检

| 域名 | ACAO | Allow-Methods | Allow-Headers | 结论 |
|---|---|---|---|---|
| `pg-static.m4q7z1.shop` | `*` | GET、HEAD、OPTIONS | `*` | 可跨域读取 |
| `jili-static.m4q7z1.shop` | `*` | GET、HEAD、OPTIONS | `*` | 可跨域读取 |
| `g759-static.m4q7z1.shop` | `*` | GET、HEAD、OPTIONS | `*` | 可跨域读取 |

`pg-games.m4q7z1.shop` 对任意 Origin 返回反射值与 `Allow-Credentials=true`，不影响静态资源域现有的任意来源策略。

## 五、最终操作

1. 撤回动态 EdgeOne CORS 兜底规则。
2. 保持动态 Nginx 配置为上游 CORS 头透传，不响应替代预检。
3. 保持动态域名 NoCache。
4. 静态域名沿用现有 `ACAO=*`、GET/HEAD/OPTIONS 策略。
5. 开发复测仍失败时，优先检查业务代码是否只允许固定 Origin，或浏览器是否命中了变更前的失败缓存。

## 六、浏览器下注复测与最终故障边界

使用百利账号进入 PG 麻将胡了后，游戏资源能够完整加载，认证、游戏信息、资源列表接口均返回
200。点击一次最小额下注后，浏览器控制台出现：

```text
Access to XMLHttpRequest at 'https://api.k8x2v9.shop/game-api/pg/v2/Spin' ...
has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

香港 Nginx 对同一个 trace ID 记录 `499`、`0` 字节，持续约 15 秒。PG 后端日志同时显示：

```text
接口执行超时 | 异步函数: do_game_spin | 耗时: 14.99s
```

后端在该请求内已经选出游戏结果并生成余额变化，但随后停在
`_save_bet_history_record` 投注流水保存步骤。浏览器报告的 CORS 是请求被取消后的次生现象，
不是动态域名响应头配置导致。

结果集复核结果：

```text
巴西 01：159 个基础结果库
香港 01：159 个基础结果库
香港 02：159 个基础结果库
文件名和字节大小：三端逐项无差异
pg_65.db SHA256：b81607cbff8175a4ce7b07cdb47c17362f76387e20a4cd47a74e129694195be0
quick_check：ok
目录和文件：appuser/appuser、uid=1000、可写
```

因此，历史记录中的“结果集只读或结果库内容不一致”问题不适用于本次 PG65。

重启核查进一步发现，香港 PG 容器新建 MySQL 连接时超时：

```text
Can't connect to MySQL server on '47.239.230.107' (timed out)
```

香港 01、02 和入口 Nginx 到该地址的 TCP 3306 均超时。PG01 已停止自动重启循环，
PG02 保持原连接运行，避免同时失去两台后端。待 DBA 放通香港后端公网/内网源 IP
后，再继续两台服务器的全部业务容器滚动重启。

本记录不包含腾讯云 SecretKey、Telegram Token 或后端认证信息。
