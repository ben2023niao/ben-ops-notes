---
id: "doc-3722dc3617d0"
title: "VirtualBox 安卓自动化构建发布"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68649827.html"
---

# VirtualBox 安卓自动化构建发布

安卓打包
1 电脑安装 virtualbox 注意电脑主板 boot 要开启 CPU 虚拟化
<https://www.virtualbox.org/wiki/Downloads>
2 下载镜像 安卓打包服务器带飞机完整版.ova 镜像 账号 android 密码 android
3 导入镜像开箱就可打包

![文档配图](../media/1c5949cb1d9dbc4c6b.png)
选择 为所有网卡重新生成 MAC 地址
![文档配图](../media/dedb58831023c44c53.png)
虚拟机内进入桌面的安卓各个分支源代码 git pull 就可拉最新代码 点击 android studio 点击 左上角 File -> Open -> 选择在桌面的 安卓各个分支源代码
![文档配图](../media/159fb4b57c69e5d266.png)
![文档配图](../media/845af91f394f31fd67.png)
点击 左上角 Build -> Generate Sigened Bundle... 选择 APK key store password key alias key pasword 这3个都填写 证书文件名(具体填写问安卓开发)
![文档配图](../media/b7f1f9c3d558a0066e.png)
选择 release 点击 左下角 Build BUILD SUCCESSFUL in 1s 就打包成功咯

![文档配图](../media/f8d0d5c62344dfe8d5.png)
后期 渠道包数量起来了 再整理 使用 grable 命令行快速批量打 几百个 包的笔记
