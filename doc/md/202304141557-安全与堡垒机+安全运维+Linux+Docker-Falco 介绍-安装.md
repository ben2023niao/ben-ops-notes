---
id: "doc-007726e36ca1"
title: "Falco 介绍/安装"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全与堡垒机", "安全运维", "Linux", "Docker", "监控告警", "日志分析", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/04-安全运维/birdben/68655506.html"
---

# Falco 介绍/安装

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%AE%89%E5%85%A8%E4%B8%8E%E5%A0%A1%E5%9E%92%E6%9C%BA%2B%E5%AE%89%E5%85%A8%E8%BF%90%E7%BB%B4%2BLinux%2BDocker-Falco%20%E4%BB%8B%E7%BB%8D-%E5%AE%89%E8%A3%85.md)

Falco 可以监测调用 [Linux 系统调用](http://man7.org/linux/man-pages/man2/syscalls.2.html)的行为，并根据其不同的调用、参数及调用进程的属性发出警告。例如，Falco 可轻松检测：

- 容器内运行的 Shell
- 服务器进程产生意外类型的子进程
- 敏感文件读取（如 `/etc/shadow`）
- 非设备文件写入至 `/dev`
- 系统的标准二进制文件（如 `ls`）产生出站流量

## 与其他工具的对比

我们常常会被问到 Falco 与 [SELinux](https://en.wikipedia.org/wiki/Security-Enhanced_Linux)、[AppArmor](https://wiki.ubuntu.com/AppArmor)、[Auditd](https://linux.die.net/man/8/auditd) 或其他 Linux 安全策略工具有何不同。为此，我们在 [Sysdig 博客](https://sysdig.com/blog)上撰写了[一篇博文](https://sysdig.com/blog/selinux-seccomp-falco-technical-discussion/)，并详细对比了多款工具。

## 如何使用 Falco

Falco 应作为守护程序部署。您可将其作为一款 [deb](https://falco.org/docs/getting-started/installation#debian)/[rpm](https://falco.org/docs/getting-started/installation#centos-rhel) 软件包安装在主机或容器宿主上，亦或可以作为[容器](https://falco.org/docs/getting-started/running#docker)部署。当然，您也可以下载[源代码](https://falco.org/docs/getting-started/source)并自己动手编译安装。

您可通过[规则文件](https://falco.org/docs/rules)或[通用配置文件](https://falco.org/docs/configuration)定义 Falco 应监视的行为及事件。我们提供了一份示例规则文件 [`./rules/falco_rules.yaml`](https://github.com/falcosecurity/falco/blob/master/rules/falco_rules.yaml)，您可随意修改规则来适配您的工作环境。

当您撰写规则时，Falco 可读取由 Sysdig 产生的回溯文件。这一特性可让您在调整规则时“录制”有害行为，并无限次数地回放。

部署后，Falco 将利用 Sysdig 内核模块及用户空间函数库来监控规则文件定义中的任意事件。若异常事件发生，Falco 会将通知信息写入您所配置的输出中。

## Falco 行为报警

当 Falco 检测到可疑行为时，[报警信息](https://falco.org/docs/alerts)可通过下列渠道输出：

- 写入标准错误
- 写入文件
- 写入系统日志
- 管道至特定程序（如发送电子邮件）

## Falco安装  <https://falco.org/zh/docs/installation/>

```bash
#脚本化安装要在Linux上安装Falco
curl -o install_falco -s https://falco.org/script/install
#然后使用sha256sum工具(或类似的工具)验证脚本的SHA256校验和。
sha256sum install_falco 它应该是59201c1339cc53e86edcd7d2e7273e52f784b3cf7d4a3142059112b3b9062f6d。
sudo bash install_falco
#Debian/Ubuntu包管理器安装curl -s https://falco.org/repo/falcosecurity-3672BA8F.asc | apt-key add -
echo "deb https://download.falco.org/packages/deb stable main" | tee -a /etc/apt/sources.list.d/falcosecurity.list

apt-get update -y
apt-get -y install linux-headers-$(uname -r)
apt-get install -y falco

#CentOS/RHEL/Amazon Linux包管理器安装

rpm --import https://falco.org/repo/falcosecurity-3672BA8F.asc
curl -s -o /etc/yum.repos.d/falcosecurity.repo https://falco.org/repo/falcosecurity-rpm.repo
yum -y install kernel-devel-$(uname -r)
yum -y install falco

#docker安装
docker pull falcosecurity/falco
docker run -i -t \
 --name falco \
 --privileged \
 -v /var/run/docker.sock:/host/var/run/docker.sock \
 -v /dev:/host/dev \
 -v /proc:/host/proc:ro \
 -v /boot:/host/boot:ro \
 -v /lib/modules:/host/lib/modules:ro \
 -v /usr:/host/usr:ro \
 falcosecurity/falco
```
