---
id: "doc-cf45558843e2"
title: "glances监控部署"
date: "2021-12-21T15:32:00.464000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["可观测性", "监控"]
tags: ["监控", "Linux", "Shell", "Python", "Docker", "监控告警", "Telegram", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/jian-kong/glances-jian-kong-bu-shu.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "8a6a7c7334702cac6aa6b497f050eab0b8d155215e20ecda6ef319ffb62d8687"
---

# glances监控部署

> 原文：[glances监控部署](https://xn--6o0a585a.gitbook.io/devops/jian-kong/glances-jian-kong-bu-shu.html)

> 来源：GitBook 网页 HTML｜页面时间：2021-12-21 15:32｜日期依据：GitBook 页面更新时间

Linux

1 宝塔面板安装 docker 管理面板

2 宝塔面板开启61208端口(可不开)

3 运行docker命令

```bash
docker run -d --restart="always" --name glances -p 61208-61209:61208-61209 -e GLANCES_OPT="-w" -v /var/run/docker.sock:/var/run/docker.sock:ro --pid host docker.io/nicolargo/glances
```

Windows

1 安装 Python 2.7.9+ or 3.4+ ship with pip 环境

2 管理员方式启动powershell安装 glances

```
pip install glances bottle
```

3 然后开出站端口61208

4 powshell后台网页启动 glances

```
start-job{glances -w}
```

#### Android

1 安装Termux APK <https://play.google.com/store/apps/details?id=com.termux>

2 打开Termux 安装glances

```
apt update
apt upgrade
apt install clang python
pip install glances bottle
```

3 网页启动glances

macOS

**MacPorts**

FreeBSD

To install the binary package:

To install Glances from ports:

#### Glances 自动安装脚本：简单的方法

要安装依赖项和最新的 Glances 生产就绪版本（又名*master*分支），只需输入以下命令行：

或者

*注意*：这仅在某些 GNU/Linux 发行版和 Mac OS X 上受支持。

#### Docker：有趣的方式

Glances 容器是可用的。您可以使用它来监控您的服务器和所有其他容器！

获取 Glances 容器：

Docker Hub 存储库上的可用版本：

- *nicolargo/glances：最新*的基本 Debian Glances 映像版本，具有最少的依赖关系
- *nicolargo/glances:alpine-latest*用于具有最小依赖性的基本 Alpine Glances 映像版本
- *nicolargo/glances:latest-full*用于包含所有依赖项的完整 Debian Glances 映像版本
- *nicolargo/glances:alpine-latest-full*用于包含所有依赖项的完整 Alpine Glances 映像版本

您还可以通过将 latest 替换为 3.2.3（例如）来指定版本。

在*控制台模式下*运行最新版本的 Glances 容器：

此外，如果您想使用自己的 Glances.conf 文件，您可以创建自己的 Dockerfile：

或者，您可以使用 docker run 选项指定相同的内容：

其中`pwd`/glances.conf 是包含glances.conf 文件的本地目录。

以*Web服务器模式*运行容器（注意glances启动命令的GLANCES_OPT环境变量设置参数）：

### 官方文档api <https://glances.readthedocs.io/en/latest/index.html>
