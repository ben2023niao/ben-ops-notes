---
id: "doc-4bb40f4b2a07"
title: "Beszel监控安装配置-对外版"
date: "2026-10-15T00:00:00+08:00"
dateSource: "正文日期"
categories: ["基础设施与自动化", "BKL UAT"]
tags: ["BKL UAT", "Docker", "Kubernetes", "监控告警", "自动化", "数据库恢复", "源码与配置"]
source: "project-file:///Projects/work/ops/devops/devops-bkl/doc/2026%E5%B9%B410%E6%9C%8815%E6%97%A5-%E5%A0%A1%E5%9E%92%E6%9C%BA%E4%B8%8E%E7%9B%91%E6%8E%A7%E9%83%A8%E7%BD%B2/Beszel%E7%9B%91%E6%8E%A7%E5%AE%89%E8%A3%85%E9%85%8D%E7%BD%AE-%E5%AF%B9%E5%A4%96%E7%89%88.txt"
sourcePath: "~/Projects/work/ops/devops/devops-bkl/doc/2026年10月15日-堡垒机与监控部署/Beszel监控安装配置-对外版.txt"
sourceSha256: "c6a747d2bb6572be21468bcca5fb91bc05c9fdad7eaa63945f39c613775f44f0"
sourceSystem: "project-doc"
---

# Beszel监控安装配置-对外版

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202610150000-%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%E4%B8%8E%E8%87%AA%E5%8A%A8%E5%8C%96%2BBKL%20UAT%2BDocker-Beszel%E7%9B%91%E6%8E%A7%E5%AE%89%E8%A3%85%E9%85%8D%E7%BD%AE-%E5%AF%B9%E5%A4%96%E7%89%88.md)

> 整理日期：2026-10-15 00:00｜日期依据：正文日期

Beszel 监控 - 安装配置

更新时间：2026-10-15

一、监控中心（Hub）部署

在被当作监控中心的服务器上执行一行即可：

docker run -d --name beszel --restart unless-stopped -p 8090:8090 -v /opt/beszel/beszel_data:/beszel_data henrygd/beszel

浏览器打开 http://xxxx:8090 注册第一个账号，第一个注册的用户自动是管理员。

二、被监控机器加入监控

在每台被监控机器上执行（要先装好 Docker）：

docker run -d --name beszel-agent --restart unless-stopped --network host -v /opt/beszel-agent:/var/lib/beszel-agent -v /var/run/docker.sock:/var/run/docker.sock:ro -e KEY="xxxx" -e 敏感凭据：[已脱敏] -e HUB_URL="http://xxxx:8090" henrygd/beszel-agent

说明：
KEY    是 Hub 的公钥，在 Hub 界面 设置 -> Tokens/Fingerprints 里可以复制
TOKEN  是通用 token（设置里生成），所有机器填同一个，agent 启动后会自动出现在 Hub 列表里
HUB_URL 填监控中心地址，agent 主动连 Hub，被监控机器不用开端口
/opt/beszel-agent 用来保存 agent 身份，重建容器时不会在 Hub 里多出一台重复机器，建议保留

如果不想用通用 token，也可以在 Hub 里手动"添加系统"，保存后会给出该机器专属的 KEY 和 TOKEN，填到上面同一条命令里即可。

三、部署完成后能看到什么

主机 CPU、内存、磁盘、网络、负载 的实时数据与历史曲线
每台机器上所有容器的 CPU、内存、网络占用，以及容器列表和实时日志
磁盘 SMART 健康、温度、网卡等硬件指标

四、报警配置

1. 设置 -> 通知，在 Webhook / Push 里填通知地址，Telegram 格式：

   telegram://<机器人token>@telegram?chats=<群ID>

2. 填完点"测试"，能收到消息说明通道正常。

3. 每台系统默认开启四条告警（在系统页面里可开关）：

   离线 / 宕机
   CPU 使用率超过 80% 持续 10 分钟
   内存使用率超过 80% 持续 10 分钟
   磁盘使用率超过 80% 持续 10 分钟

4. 阈值和持续时间都可以在告警规则里按需调整，也可以按系统复制规则到其他机器。

五、常用运维命令

看日志：      docker logs beszel         docker logs beszel-agent
重启：        docker restart beszel      docker restart beszel-agent
升级 Hub：    docker pull henrygd/beszel && docker rm -f beszel 后重新执行第一节命令
升级 Agent：  docker pull henrygd/beszel-agent && docker rm -f beszel-agent 后重新执行第二节命令
数据备份：    /opt/beszel/beszel_data 目录（数据库和配置都在里面），定期打包备份即可

六、注意事项

1. 用域名访问的时候，Hub 的站点地址要填对外域名，否则页面里的链接会指错。
2. Agent 需要能访问到 Hub 的地址（内网直连即可），方向是 agent 主动外连。
3. 监控中心建议只在内网开放，或者加访问控制，不要直接暴露在公网。
4. 被监控机器上会创建一个 agent 容器，占内存很小，可忽略不计。
5. 如果机器上跑的是 k8s 或多网卡，建议在启动参数里指定要采集的磁盘和网卡。
