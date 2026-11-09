---
id: "doc-aac8b4073480"
title: "【架构+优化】bizops-ops-console 实时执行审计与结果集权限自愈部署记录"
date: "2026-11-02T16:40:00"
categories: ["安全与堡垒机", "访问控制"]
tags: ["安全与堡垒机", "访问控制", "Docker", "Nginx", "SQL注入", "权限管理", "备份恢复", "知识笔记"]
source: "03-安全运营与应急/03-安全配置与访问控制/某业务公司-权限与审计/2026-11-02-1640-【架构+优化】bizops-ops-console实时执行审计与结果集权限自愈部署记录.md"
---

# 【架构+优化】bizops-ops-console 实时执行审计与结果集权限自愈部署记录

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> 来源：本地项目文档 `game/pgserver/master/docs/history/2026-11-02-1640-【架构+优化】bizops-ops-console实时执行审计与结果集权限自愈部署记录.md`
> 整理：2026-11-09。仅复制到知识库，未改动原项目文件；敏感凭据已脱敏。

更新时间：2026-11-02 16:40（Asia/Manila）

执行范围：本地 master、巴西宝塔控制台、巴西 01/02/04/05、香港 01/02。

## 一、结论

`bizops-ops-console` 已从静态 HTML 方案升级为可执行的 FastAPI 控制台，
部署于巴西宝塔，通过 SSH 调用白名单入口对应的发布命令；浏览器可实时查看
stdout/stderr、退出码和状态，并把操作与完整输出写入 SQLite 审计库。

本次同时把结果集权限处理纳入每次后端发布：

1. `rsync` 拉取运行时统一加 `--chown=1000:1000`；
2. 同步完成后立即静默执行 `fix_result_perms.sh`；
3. 启动容器前校验 `bizops-result-perms.timer` 为 enabled + active；
4. 再次扫描 `game_result_datas`，仍有错误属主或 owner 不可读写时立即中止；
5. 六台后端的运行期 timer 均保持 enabled + active，作为最后兜底。

## 二、开始前基线

```text
本地分支：master
本地 HEAD：a72f41fb4f7052d4657d0004cbdb26f5a6493c97
origin/master：a72f41fb4f7052d4657d0004cbdb26f5a6493c97
origin/ben：9748ad3224c60099fd7b6c0756b628ad10e59fc7
开始状态：工作区干净；本地/远端 master 一致
```

## 三、告警证据与根因

2026-11-02 16:24～16:31（北京）结果集权限 timer 在巴西 01、02、04、05
检测到同一类异常：

```text
命令来源：发版 rsync -a
异常条目：821 个左右
典型属主：root:root
典型权限：777
目标属主：1000:1000（宿主机显示 ubuntu:ubuntu）
修复结果：剩余 0
```

`rsync -a` 会保留源端 owner/group，打包机源目录中的 root 属主因此覆盖后端
运行目录。timer 已经能自愈并告警，但发布时间仍可能出现短窗口；本次把这层
自愈移动到同步与启动之间，并从同步源头强制目标属主。

## 四、控制台实现

### 4.1 部署拓扑

```text
浏览器
  -> 192.0.2.1:8787（宝塔 Nginx）
  -> 192.0.2.1:8788
  -> bizops-ops-console 容器
  -> 私网 SSH
  -> 03 / 巴西后端 / 香港后端
```

容器名：`bizops-ops-console`

容器不挂载宿主机 Docker Socket；发布命令通过私网 SSH 到达目标机。宝塔
Nginx 负责公网端口反代，容器端口只绑定本机回环。

### 4.2 鉴权与审计

- 单密码登录，无用户名；
- HttpOnly + SameSite=Strict Cookie；
- 默认会话 12 小时；
- 同 IP 5 分钟内失败 5 次限速；
- SQLite 保存登录、页面点击/输入、执行命令、输出、退出码和通知结果；
- `sshpass` 密码、URL 内嵌凭据、Bot Token 在落库前脱敏；
- 密码、SSH 密码、GitLab URL、Telegram Token/Chat ID 只从只读 Secret 文件读取。

### 4.3 实时输出与状态

- 执行接口创建 Job 后返回 `events_url`；
- 前端使用 SSE 接收 `stage/stdout/vendor/complete/error/cancelled`；
- 输出显示在被点击命令的下方；
- 执行中同步更新巴西 01/02/04/05、香港 01/02、打包机 03 状态；
- 8 个镜像厂家分别更新“待打包/已打包”；
- 页面刷新后从 `/api/jobs` 恢复服务器和镜像状态；
- 断线后 EventSource 重连并从事件序号继续读取。

### 4.4 页面操作

- 命令默认折叠，但折叠标题右侧也能点击“执行”；
- 一键准备：通知、拉代码、构建、检查；
- 一键巴西：01 金丝雀后按 02 → 04 → 05；
- 一键香港：01 后按配置批量；
- 移动端一键按钮竖向排列，服务器状态为两列，审计抽屉不超出视口；
- Cloudflare 缓存区明确提示必须登录固定页面，不能在控制台内直接清除。

## 五、结果集权限闭环

每个后端发布命令的固定阶段变为：

```text
pull images
→ stop containers
→ rsync
→ NOTIFY=0 /opt/bizops-scripts/fix_result_perms.sh
→ check bizops-result-perms.timer enabled + active
→ scan game_result_datas
→ start containers
→ verify Image ID
→ print container status
```

同步参数：

```text
rsync -a ... --chown=1000:1000 ...
```

启动前门禁：

```text
RESULT_PERMS_TIMER=OK
RESULT_PERMS_NOW=OK
```

任一检查失败，命令以非零退出码结束，后续启动和批量节点不再执行。

## 六、六台后端验证

2026-11-02 16:38（Asia/Manila）实测：

| 区域 | 机器 | 结果集根目录 | timer |

| --- | --- | --- | --- |

| 巴西 | prod-01 | `ubuntu:ubuntu 777` | enabled + active，service success |

| 巴西 | prod-02 | `ubuntu:ubuntu 777` | enabled + active，service success |

| 巴西 | prod-04 | `ubuntu:ubuntu 777` | enabled + active，service success |

| 巴西 | prod-05 | `ubuntu:ubuntu 777` | enabled + active，service success |

| 香港 | prod-01 | `ubuntu:ubuntu 777` | enabled + active，service success |

| 香港 | prod-02 | `ubuntu:ubuntu 777` | enabled + active，service success |

宿主机显示名 `ubuntu` 对应容器运行 UID/GID `1000`。

## 七、控制台验证

### 7.1 本地容器

```text
未登录访问 /：303
错误密码：401
正确密码：303
登录后页面：200
非法 command_id：400
非法 SSH 目标：400
SSE：stage / stdout / complete 正常
错误 SSH 密码：退出码 255，Job 保存为 failed
```

使用错误 SSH 密码的 UI 测试在远端认证前失败，没有执行停容器、同步或启动。

### 7.2 宝塔线上

```text
公网健康检查：200
未登录页面：303
错误密码：401
正确密码：303
页面：200
无害只读命令：03 hostname
退出码：0
Job 状态：passed
```

最终部署：

```text
容器：bizops-ops-console
镜像：bizops-ops-console:20261102
镜像 ID：sha256:d9b6c51b42a2a15196e81fa5a5ce68a0ed52da7d28fe3362c799e0e219a5e1d8
容器：Up (healthy)
入口：http://192.0.2.1:8787
```

## 八、交付物

```text
deliverables/bizops-ops-console/
deliverables/bizops-ops-console-20261102.zip
ZIP SHA256：cbbf7eb9a0d3eb397f18ba77d87648051893480013d6cf1ab0489a96a08e10d0
```

ZIP 不包含：

- 生产 `data/`；
- `/run/secrets`；
- SSH 密码；
- GitLab 内嵌凭据；
- Telegram Token/Chat ID。

## 九、备份与回滚

部署前宝塔备份：

```text
/opt/bizops-ops-console/backups/code-before-20261102-163909.tar.gz
```

回滚代码：

```bash
cd /opt/bizops-ops-console
tar -xzf backups/code-before-20261102-163909.tar.gz -C .
docker compose -f deploy/docker-compose.yml up -d --build
curl -fsS http://192.0.2.1:8788/api/health
```

回滚不会删除 `data/`、`secrets/` 或业务服务器上的运行目录。

## 十、安全边界

- 后端服务器不新增公网 8787 规则；
- 容器不挂 Docker Socket；
- 控制台只绑定 `192.0.2.1:8788`；
- GCP 防火墙只开放宝塔入口 `8787`；
- Cloudflare Access 或 HTTPS 域名仍建议作为下一阶段；
- 真实密码、Token、GitLab URL 不进入 Git、交付 ZIP 或群消息。

## 十一、通知与 Git

```text
汇总消息：721
文档消息：722
提交结果：
```
