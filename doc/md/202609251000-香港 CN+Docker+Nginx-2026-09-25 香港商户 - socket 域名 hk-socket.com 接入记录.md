---
id: "doc-70fa1db5488e"
title: "2026-09-25 香港商户 / socket 域名 hk-socket.com 接入记录"
date: "2026-09-25T10:00:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "香港 CN"]
tags: ["香港 CN", "Docker", "Nginx", "CDN", "DNS", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/cn/docker/doc/2026-09-25-1000-%E3%80%90%E6%9E%B6%E6%9E%84%E6%94%B9%E9%80%A0%E3%80%91%E9%A6%99%E6%B8%AF%E5%95%86%E6%88%B7socket%E5%9F%9F%E5%90%8Dhk-socket.com%E6%8E%A5%E5%85%A5%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/cn/docker/doc/2026-09-25-1000-【架构改造】香港商户socket域名hk-socket.com接入记录.md"
sourceSha256: "975c1293c5c818021bad8fa658f6f654c4b6d1f4d51e92765476712f002507be"
sourceSystem: "project-doc"
---

# 2026-09-25 香港商户 / socket 域名 hk-socket.com 接入记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源文件：`~/Projects/ops/private-notes/cn/docker/doc/2026-09-25-1000-【架构改造】香港商户socket域名hk-socket.com接入记录.md`

> 整理日期：2026-09-25 10:00｜日期依据：文件名日期

## 一、任务

```text
Ben(C++) 需求：登录服务器（socket）需要一个独立域名转发到 platform-api（9090），
  且要与游戏域名分开，作为「商户域名」。Ben 运维已注册 hk-socket.com 并接入 Cloudflare。
要求：参考巴西项目配置，本轮不发送飞机群通知。
```

## 二、巴西参考做法

```text
巴西用 socket.<root> 二级域名做商户/API 入口（master：
  docker/doc/2026-08-20-1735-【架构改造】socket商户域名批量扩容记录.md）：
  - nginx 站点 socket.xtmpz.com.conf（已废弃）→ 扩为 22 个 socket.<root>
  - upstream socket_backend → 后端 192.0.2.1/0.4:9090（platform-api），
    带 keepalive 32 / keepalive_timeout 10s / keepalive_requests 1000
  - DNS 写法：socket.shanghu01.cc  A  192.0.2.13  proxied=True（橙云 -> 备用入口）
  - 根路径业务形态：https://socket.xtmpz.com/ -> 404（与内网 9090=404 一致）
```

## 三、香港配置

### 3.1 DNS（Cloudflare，zone hk-socket.com）

```text
zone：hk-socket.com（id 769370b71fa7b2c0de2ec0280e11a0c2，2026-09-25 01:50 创建、01:51 active，
      NS alexa/newt.ns.cloudflare.com；接入前为空 zone）
新增两条记录（均橙云，与巴西 socket.<root> 一致）：
  A  socket.hk-socket.com -> 192.0.2.37  proxied=True（主用：商户/socket 入口）
  A  hk-socket.com        -> 192.0.2.37  proxied=True（根域，便于测试/备用）
```

### 3.2 nginx（香港 standby 入口 192.0.2.37）

配置落仓库并在 standby 生效（老入口机 192.0.2.14 与本轮无关、未改动）：
`docker/deploy/hongkong/nginx-standby.conf` 新增 server 块：

```nginx
server {
    include snippets/bizops-hk-standby-tls.conf;      # 80 + 443（自签证书，仅供 CF 回源）
    server_name hk-socket.com socket.hk-socket.com;
    location = /healthz { default_type text/plain; return 200 "ok\n"; }
    location / {
        include snippets/bizops-hk-standby-proxy.conf;
        proxy_pass http://bizops_hk_standby_platform_api;   # 192.0.2.1/0.4:9090 + 外部双后端 failover
    }
}
```

自签证书重新生成，SAN 扩展为：

```text
hkcloudplay06.com, *.hkcloudplay06.com, hkcloudplay07.com, *.hkcloudplay07.com,
hk-socket.com, *.hk-socket.com, IP:192.0.2.1
```

操作过程：备份原站点配置（`bizops-hk-standby.conf.bak-20260925-*`）→ 覆盖 → `nginx -t` 通过 → reload。

## 四、验证

| 验证项 | 结果 |
| --- | --- |
| DNS（权威 / 192.0.2.30） | `socket.hk-socket.com`、`hk-socket.com` 均解析到 Cloudflare IP（104.21/172.67 段） |
| `https://socket.hk-socket.com/` | **404**，响应头含 `access-control-allow-headers: ..., x-token, ..., gdid`（platform-api 形态），与巴西 `socket.xtmpz.com/ -> 404` 一致 |
| `https://hk-socket.com/` | 404（同上口径） |
| `https://socket.hk-socket.com/healthz` | `ok`（standby 本机健康检查） |
| 回归：`pg-static.hkcloudplay06/07.com` | 200（证书 SAN 变更无影响） |
| 回归：`pg-static.hkcloudplay05.com`（老域名） | 200（未受影响） |

上游现状（standby 实测）：

```text
192.0.2.1:9090  未监听（prod-01 的 platform-api 容器未部署）
192.0.2.1:9090  可达（prod-02 上已在运行 platform-api）
192.0.2.18 / 192.0.2.19:9090  从 standby 不可达（外部后端有源 IP 白名单）
=> nginx 自动 failover 到 192.0.2.1，因此 socket 域名当前可用；
   自建后端容器正式部署后，192.0.2.1 会自动成为首选，无需改配置。
```

## 五、待办

```text
1. 自建后端容器正式部署（prod-01/prod-02 的 game-service-api 等），socket 域名即走本地双活；
2. 如需更多商户域名（参考巴西 22 个 socket.<root>），可在同 zone 加 socket.<新域> 并
   在 standby 的 server_name 追加；
3. 老入口机 192.0.2.14 上的 socket.hkplaycore.com 仍是 410 拒绝（cn 不启用），本轮未改动。
```

## 六、关联

```text
docker/deploy/hongkong/nginx-standby.conf                           standby 站点配置（含本轮 socket 块）
docker/doc/2026-09-24-1400-【架构改造】香港standby入口与新域名hkcloudplay0607接入记录.md
docker/doc/2026-09-24-1730-【架构改造】香港后端接入巴西容器仓库与容器启动测试记录.md
master/docker/doc/2026-08-20-1735-【架构改造】socket商户域名批量扩容记录.md   （巴西参考）
```
