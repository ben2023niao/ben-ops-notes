---
id: "doc-298a03782aee"
title: "项目自动化构建发布"
date: "2021-12-28T19:23:08.010000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["基础设施与自动化", "自动化"]
tags: ["自动化", "Shell", "Telegram", "数据库恢复", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/zi-dong-hua/xiang-mu-zi-dong-hua-gou-jian-fa-bu.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "513260f917a03c4f8bc5cd675b446052c5162f6ff5e33dab9c07e4074674a2a8"
---

# 项目自动化构建发布

> 原文：[项目自动化构建发布](https://xn--6o0a585a.gitbook.io/devops/zi-dong-hua/xiang-mu-zi-dong-hua-gou-jian-fa-bu.html)

> 来源：GitBook 网页 HTML｜页面时间：2021-12-28 19:23｜日期依据：GitBook 页面更新时间

测试环境前端h5代码自动化发布

```bash
#!/bin/bash
#/data/tg-test/dev_capital_test.sh
API="https://api.telegram.org/bot5035739927:AAEoN_prxkaWf7aapWH0Lgi5T8deAt4Ailk" #飞机机器人API
GID="chat_id=-747209743"                                                         #飞机机器人群ID
MSG="${API}/sendMessage?${GID}&text="                                            #发送文本方法
SF="$API/sendDocument?$GID -F document=@"                                        #发送文件方法

cd /data/tg-test/capital
gitinfo=`git log -1 | grep commit | awk '{print $2}'`
zip -q -r $gitinfo.capital.dev.zip /data/tg-test/capital/
mv $gitinfo.capital.dev.zip ../
cd /data/tg-test/
rm -rf /data/tg-test/capital                                                     ;curl $MSG"代码备份成功capital测试环境"

git clone -b test-stock https://example.invalid/repository    ;curl $MSG"代码拉取中capital测试环境"
cd /data/tg-test/capital
git pull                                                                         ;curl $MSG"代码拉取成功capital测试环境"
#echo "前端h5不需要构建"                                                         ;curl $MSG"代码构建成功capital测试环境"

echo ok                                                                          ;curl $MSG"代码发布成功capital测试环境"

echo "显示本次git版本信息"
curl -s -o /dev/null -X POST "https://api.telegram.org/bot5035739927:AAEoN_prxkaWf7aapWH0Lgi5T8deAt4Ailk/sendMessage" -d chat_id="-747209743" -d text="`git log -1`"
```

测试环境后端php代码自动化发布
