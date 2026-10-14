---
id: "doc-18c160aa9b6b"
title: "【问题排查】发布健康检查 WARNING 假警：.env 值以 = 结尾导致 PHP 解析失败"
date: "2026-10-15T00:00:00+08:00"
dateSource: "文件名日期"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Python", "Docker", "Redis", "自动化", "安全运维", "故障排查"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-15-%E3%80%90%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E3%80%91%E5%8F%91%E5%B8%83%E5%81%A5%E5%BA%B7%E6%A3%80%E6%9F%A5WARNING%E5%81%87%E8%AD%A6-%E7%8E%AF%E5%A2%83%E6%96%87%E4%BB%B6%E7%AD%89%E5%8F%B7%E7%BB%93%E5%B0%BE%E5%80%BC%E5%AF%BC%E8%87%B4PHP%E8%A7%A3%E6%9E%90%E5%A4%B1%E8%B4%A5.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-15-【问题排查】发布健康检查WARNING假警-环境文件等号结尾值导致PHP解析失败.md"
sourceSha256: "9a48523622f59f8c8b08ae65425f942b6939b8dd70bb80b61d46a7a9066cadf6"
sourceSystem: "project-doc"
---

# 【问题排查】发布健康检查 WARNING 假警：.env 值以 = 结尾导致 PHP 解析失败

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/docs/2026-10-15-【问题排查】发布健康检查WARNING假警-环境文件等号结尾值导致PHP解析失败.md`

> 整理日期：2026-10-15 00:00｜日期依据：文件名日期

- 日期：2026-10-15
- 环境：**线上环境**（16.209.16.108，发布 `main / 6e46c0cc3f77`）
- 触发：发布成功但健康检查结论为 **WARNING**：
  `Redis：203.0.113.1:6379 closed errno=111`、`MongoDB：203.0.113.1:27017 closed errno=111`
- 结论：**业务完全正常，是健康检查的假警**——`parse_ini_file()` 读不了业务 `.env`，于是回落到 `203.0.113.1` 去探测

---

## 一、现象

```text
【游点涩-后端-main-6e46c0cc3f77】发布警告
检查：HTTP 200｜Session writable
Hosts：ok
Redis：203.0.113.1:6379 closed errno=111 err=Connection refused time=0ms
MongoDB：203.0.113.1:27017 closed errno=111 err=Connection refused time=0ms
队列：ok
结论：WARNING
```

注意：**探测地址是 `203.0.113.1`**，而线上后端并不在本机跑 Redis/Mongo —— 这是"回落默认值"的特征。

---

## 二、根因（已定位到具体行）

### 2.1 直接原因：`.env` 里有一个值以 `=` 结尾

```text
$ docker exec youdianse-main-php-web php -r 'var_dump(parse_ini_file("/var/www/html/youdianse-php/.env", true) === false);'
Warning: syntax error, unexpected '=' in /var/www/html/youdianse-php/.env on line 100
bool(true)          ← parse_ini_file 解析失败，返回 false
```

第 100 行：

```ini
AWS_DOMAIN_ENCRYPT_KEY=Asgdwt+27jdwrc8=
```

PHP 的 `parse_ini_file()` 对**未加引号、且含保留字符**的值很严格，这里的 base64 结尾 `=` 会让它直接
报 `syntax error, unexpected '='` 并**整体返回 false**（不是只丢这一个键）。

### 2.2 放大原因：健康检查把解析失败"静默降级"成了 203.0.113.1

```python
# 修复前：检查脚本里这段是用 PHP 解析的
'$env=parse_ini_file("/var/www/html/youdianse-php/.env", true);'
'$targets=[["Redis",$env["redis"]["host"] ?? "203.0.113.1", ...],'
'          ["Mongo",$env["database.mongodb.default"]["host"] ?? "203.0.113.1", ...]];'
```

`parse_ini_file` 返回 false → `$env["redis"]["host"]` 取不到 → 走 `?? "203.0.113.1"` 兜底 →
去连本机 6379/27017 → 必然 `Connection refused` → 结论 WARNING。

### 2.3 为什么业务没事

```text
· [redis]                       host = 203.0.113.1   port = 6379
· [database.mongodb.default]    host = server.db1.com port = 27017（容器 hosts 指向 203.0.113.1）
· 应用自身读 .env 正常 → HTTP 200、Session writable、队列 ok，站点与业务日志都正常
```

也就是说：**只有"巡检用的解析方式"坏了，业务链路没坏。**

---

## 三、修复（`cicd-web/core.py`）

不再让健康检查依赖 PHP 的严格解析，改为**在 Python 侧宽容解析 `.env`**，再把地址交给容器内 PHP 探测：

```python
def read_backend_env(target_container: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    """宽容读取容器内业务 .env，返回 {段名: {键: 值}}。
    （注释里记录：.env 里 `KEY=xxx=` 这种以 = 结尾的值会让 PHP parse_ini_file 直接失败）"""

def resolve_dep_targets(env) -> List[Tuple[str, str, int]]:
    """从 .env 解析出 Redis / MongoDB 的 host:port（缺失才回落 203.0.113.1/默认端口）"""
```

探测命令改为**通过 argv 传 host/port**（不再把 PHP 解析逻辑塞进探测脚本）：

```python
dep_php = '$targets=[["Redis",$argv[1],(int)$argv[2]],["Mongo",$argv[3],(int)$argv[4]]]; ...'
dep_cmd = ["docker","exec","<web>","php","-r",dep_php,
           redis_host, str(redis_port), mongo_host, str(mongo_port)]
```

另外在健康检查里新增一行日志：`依赖目标：Redis 203.0.113.1:6379；Mongo server.db1.com:27017`，
以后一眼就能看出探测的是不是真实地址。

---

## 四、验证（生产 16.209.16.108）

```text
① 解析结果：read_backend_env()/resolve_dep_targets() → [('Redis','203.0.113.1',6379), ('Mongo','server.db1.com',27017)]
② 端口探测：Redis 203.0.113.1:6379 open time=1ms ｜ Mongo server.db1.com:27017 open time=0ms
③ 完整健康检查（直接调用 check_services）：
     HTTP：200 ｜ Session：writable
     Redis：203.0.113.1:6379 open ｜ MongoDB：server.db1.com:27017 open
     Hosts：ok ｜ 队列：ok
     HealthResult.ok = True        ← 发布结论会是 SUCCESS，不再是 WARNING
④ 服务：cicd-web active，18090 → 200
```

> 本次未重跑发布（线上发布动作由运维执行）。**下一次发布（或手工触发健康检查）就会看到正确结论**；
> 刚发布的 `6e46c0cc3f77` 本身是成功的（HTTP 200 / Session writable / 队列 ok / 站点正常）。

---

## 五、后续建议

1. **`.env` 侧**（可选，根治）：把 `AWS_DOMAIN_ENCRYPT_KEY` 的值加引号 —— `AWS_DOMAIN_ENCRYPT_KEY="Asgdwt+27jdwrc8="`。
   该值来自配置仓库（`docker-youdianse-php-config-main`），改动前请确认业务侧取值方式不会把引号当内容。
   **注意**：本次修复后健康检查已不依赖 `parse_ini_file`，所以这步不是必须的。
2. 任何"用 `parse_ini_file()` 读业务 `.env`"的新脚本都要小心：它**一处语法错误会导致整份文件解析失败**，
   且失败往往被 `??` 默认值掩盖。建议统一走宽容解析（或使用业务框架自己的配置读取器）。
3. 巡检类脚本遇到"回落默认值"时应在日志里**显式标注**（本次已加"依赖目标"一行），避免把假警当故障。

---

## 六、回滚

```bash
# 生产（16.209.16.108）
cd /opt/docker-youdianse-php
sudo cp -a cicd-web/core.py.bak.depfix-20261015-140517 cicd-web/core.py
sudo systemctl restart cicd-web && systemctl is-active cicd-web
```
