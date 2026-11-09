---
id: "doc-a6a5e81a2a81"
title: "【发布】全厂家切单机 01 + nginx 调试模式（进客户前）"
date: "2026-09-04T03:10:00+08:00"
dateSource: "文件名日期"
categories: ["历史运维与项目交付", "巴西主站"]
tags: ["巴西主站", "Docker", "Nginx", "自动化", "CDN", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/ops/private-notes/master/docs/history/2026-09-04-0310-%E3%80%90%E5%8F%91%E5%B8%83%E3%80%91%E5%85%A8%E5%8E%82%E5%AE%B6%E5%88%87%E5%8D%95%E6%9C%BA01%E4%B8%8Enginx%E8%B0%83%E8%AF%95%E6%A8%A1%E5%BC%8F%E8%AE%B0%E5%BD%95.md"
sourcePath: "~/Projects/ops/private-notes/master/docs/history/2026-09-04-0310-【发布】全厂家切单机01与nginx调试模式记录.md"
sourceSha256: "6f37ddb3ccb7d49a865c4ae4885bc1adebe007cc3d5628e319e2c4fe0bd69580"
sourceSystem: "project-doc"
---

# 【发布】全厂家切单机 01 + nginx 调试模式（进客户前）

> 公开版脱敏说明：公司、平台、节点、账号、地址和业务对象均已替换为示例标识；替换后的名称仅用于公开复盘。

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202609040310-%E5%B7%B4%E8%A5%BF%E4%B8%BB%E7%AB%99%2BDocker%2BNginx-%E3%80%90%E5%8F%91%E5%B8%83%E3%80%91%E5%85%A8%E5%8E%82%E5%AE%B6%E5%88%87%E5%8D%95%E6%9C%BA%2001%20%2B%20nginx%20%E8%B0%83%E8%AF%95%E6%A8%A1%E5%BC%8F%EF%BC%88%E8%BF%9B%E5%AE%A2%E6%88%B7%E5%89%8D%EF%BC%89.md)

> 整理日期：2026-09-04 03:10｜日期依据：文件名日期

时间：2026-09-04 03:15（Asia/Manila）
项目：某业务公司 / PGServer master（nginx + 后端容器）
状态：✅ 已全部单机 01 运行并验证（02/03 停止、nginx 02/03 down）

## 一、背景

```text
早上 5 点商户上线前，需要“全部厂家游戏只跑到 01”，
nginx 参考 PG 模式，02/03 标 down，方便单机查看日志定位问题。
```

## 二、执行

```text
1) 02/03 停止容器（各 8 个）：
   bizops-pg/vendor_a/pp/popok/vendor_c/vendor_d/g759/platform-api-release-02/03
   （pg 此前已停；本次补齐其余 + platform-api）
2) nginx（备用机 192.0.2.13）：
   /etc/nginx/conf.d/00.vendor-upstreams.conf
   vendor_a(9096)/vendor_a_ws2(8765)/socket(9090=platform-api)/pp(9101)/
   ppk(9103)/vendor_c(9104)/vendor_d(9102)/g759(9019) 的 192.0.2.1/.11
   全部追加 down（共 18 条 down，含 pg 2 条）
   备份：00.vendor-upstreams.conf.bak-20260904-single01
3) 01 容器：8 个厂家+platform-api 全部 Up（pg 为新版 V20260904）
```

## 三、验证

```text
公网 /health 9/9 rcode=0（仅 01 承担）：
api / vendor_a-games / pp-games / ppk-games / vendor_c-games /
vendor_d-games / g759-games（xqv9m8）+ g759/vendor_a-games（cdn-tokyo-bizops）
```

## 四、恢复步骤

```text
1) nginx：还原 00.vendor-upstreams.conf.bak-20260904-single01 并 reload
   （或移除各 upstream 中 02/03 的 down;）；
2) 02/03：按需 update_pgserver.py/start 各容器后 docker start。
```

## 五、飞机群通知 message_id

```text
5122 开始（全厂家切单机计划）
（汇总/文档/提交结果见文末回写）
```

## 六、本地提交

```text
（提交号文末回写；master 领先 origin/master，未 Push）
```
