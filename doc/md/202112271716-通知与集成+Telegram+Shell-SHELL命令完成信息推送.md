---
id: "doc-a84c1617585c"
title: "SHELL命令完成信息推送"
date: "2021-12-27T17:16:13.879000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["通知与集成", "Telegram"]
tags: ["Telegram", "Shell"]
source: "https://xn--6o0a585a.gitbook.io/devops/telegram-ji-qi-ren/shell-ming-ling-wan-cheng-xin-xi-tui-song.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "10033895bd36b84fd534abe6a8e82b424ada08b192acc499a1d14b0f248efc52"
---

# SHELL命令完成信息推送

> 原文：[SHELL命令完成信息推送](https://xn--6o0a585a.gitbook.io/devops/telegram-ji-qi-ren/shell-ming-ling-wan-cheng-xin-xi-tui-song.html)

> 来源：GitBook 网页 HTML｜页面时间：2021-12-27 17:16｜日期依据：GitBook 页面更新时间

### 1.推送文本信息

```
TOKEN=[已脱敏]	#TG机器人token
chat_ID=XXXXX		#用户ID或频道、群ID
message_text="xxxxx"		#要发送的信息
MODE='HTML'		#解析模式，可选HTML或Markdown
URL="https://api.telegram.org/bot${TOKEN}/sendMessage"		#api接口
#测试1：终端有日志
curl -s -X POST $URL -d chat_id=${chat_ID}  -d parse_mode=${MODE} -d text="${message_text}"
#测试2：终端无日志
curl -s -o /dev/null -X POST $URL -d chat_id=${chat_ID} -d text="${message_text}"
```

### 2.推送贴图

```
curl -s \
-X POST https://api.telegram.org/bot$BOT_API_KEY/sendSticker \
-d sticker="CAADAgAD3QADMNSdEY1VJRWnGm6vFgQ" \
-d chat_id=$CHAT_ID
```

效果截图：

![文档配图 1](../media/b0df8a5d90bf24b9ad.jpg)

Telegram机器人（二）：使用SHELL命令完成信息推送

### 3.推送任意文件

### 4.推送照片

### 5.其他推送

### 6.其他API

请参考：<https://core.telegram.org/bots>
