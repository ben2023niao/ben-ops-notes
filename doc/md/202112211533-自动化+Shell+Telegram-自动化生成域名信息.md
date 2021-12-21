---
id: "doc-61e15bc86b57"
title: "自动化生成域名信息"
date: "2021-12-21T15:33:46.082000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["基础设施与自动化", "自动化"]
tags: ["自动化", "Shell", "Telegram", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/zi-dong-hua/zi-dong-hua-yun-wei/zi-dong-hua-sheng-cheng-yu-ming-xin-xi.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "341d27782ba07eddfe174ba60bd20784dc4e3c106a23ac9b4c7e8f27d2facbe3"
---

# 自动化生成域名信息

> 原文：[自动化生成域名信息](https://xn--6o0a585a.gitbook.io/devops/zi-dong-hua/zi-dong-hua-yun-wei/zi-dong-hua-sheng-cheng-yu-ming-xin-xi.html)

> 来源：GitBook 网页 HTML｜页面时间：2021-12-21 15:33｜日期依据：GitBook 页面更新时间

```bash
#!/bin/bash
cat > 域名信息聚合表.html << EOF
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
<HEAD>
  <META http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <TITLE>域名信息聚合表</TITLE>
  <META name="description" content="Free CT Log Certificate Search Tool from Sectigo (formerly Comodo CA)">
  <META name="keywords" content="crt.sh, CT, Certificate Transparency, Certificate Search, SSL Certificate, Sectigo, Comodo CA">
  <LINK href="//fonts.googleapis.com/css?family=Roboto+Mono|Roboto:400,400i,700,700i" rel="stylesheet">
  <STYLE type="text/css">
    a {
      white-space: nowrap;
    }
    body {
      color: #888888;
      font: 12pt Roboto, sans-serif;
      padding-top: 10px;
      text-align: center
    }
    form {
      margin: 0px
    }
    span {
      border-radius: 10px
    }
    span.heading {
      color: #888888;
      font: 12pt Roboto, sans-serif
    }
    span.title {
      background-color: #00B373;
      color: #FFFFFF;
      font: bold 18pt Roboto, sans-serif;
      padding: 0px 5px
    }
    span.text {
      color: #888888;
      font: 10pt Roboto, sans-serif
    }
    span.whiteongrey {
      background-color: #D9D9D6;
      color: #FFFFFF;
      font: bold 18pt Roboto, sans-serif;
      padding: 0px 5px
    }
    table {
      border-collapse: collapse;
      color: #222222;
      font: 10pt Roboto, sans-serif;
      margin-left: auto;
      margin-right: auto
    }
    table.options {
      border: none;
      margin-left: 10px
    }
    td, th {
      border: 1px solid #CCCCCC;
      padding: 0px 2px;
      text-align: left;
      vertical-align: top
    }
    td.outer, th.outer {
      border: 1px solid #CCCCCC;
      padding: 2px 20px;
      text-align: left
    }
    th.heading {
      color: #888888;
      font: bold italic 12pt Roboto, sans-serif;
      padding: 20px 0px 0px;
      text-align: center
    }
    th.options, td.options {
      border: none;
      vertical-align: middle
    }
    td.text {
      font: 10pt "Roboto Mono", sans-serif;
      padding: 2px 20px
    }
    td.heading {
      border: none;
      color: #888888;
      font: 12pt Roboto, sans-serif;
      padding-top: 20px;
      text-align: center
    }
    table.lint td, th {
      text-align: center
    }
    .button {
      background-color: #00B373;
      border-radius: 10px;
      color: #FFFFFF;
      font: bold 13pt Roboto, sans-serif
    }
    .copyright {
      font: 8pt Roboto, sans-serif;
      color: #00B373
    }
    .input {
      border: 1px solid #888888;
      font-weight: bold;
      text-align: center
    }
    .small {
      font: 8pt Roboto, sans-serif;
      color: #888888
    }
    .error {
      background-color: #FFDFDF;
      color: #CC0000;
      font-weight: bold
    }
    .fatal {
      background-color: #0000AA;
      color: #FFFFFF;
      font-weight: bold
    }
    .notice {
      background-color: #FFFFDF;
      color: #606000
    }
    .warning {
      background-color: #FFEFDF;
      color: #DF6000
    }
    *:focus {
      outline: 0px transparent !important
    }
  </STYLE>
</HEAD>
<BODY>
<TABLE>
EOF

for url in 55cha.com huoche2.com studyems.com 52lishi.com 2exam.com pcgta.cc ;do
        curl -s https://crt.sh/?q=$url | sed '1,151d'| sed "s/<\/BODY>//g" |sed "s/<\/HTML>//g" >> 域名信息聚合表.html
        sed -i "s/Logged At/记录日期/g" 域名信息聚合表.html
        sed -i "s/Not Before/域名SSL注册时间/g" 域名信息聚合表.html
        sed -i "s/Not After/域名SSL到期时间/g" 域名信息聚合表.html
        sed -i "s/Common Name/主域名/g" 域名信息聚合表.html
        sed -i "s/Matching Identities/子域名/g" 域名信息聚合表.html
        sed -i "s/Issuer Name/SSL证书发行机构/g" 域名信息聚合表.html

        for i in {1..13} ;do
                sed -i '$d' 域名信息聚合表.html
        done
done

echo '</TABLE>' >> 域名信息聚合表.html
echo '</BODY>' >> 域名信息聚合表.html
echo '</HTML>' >> 域名信息聚合表.html
```
