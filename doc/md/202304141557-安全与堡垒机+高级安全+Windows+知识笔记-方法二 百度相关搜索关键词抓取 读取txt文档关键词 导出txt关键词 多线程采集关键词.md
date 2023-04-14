---
id: "doc-4a29bc87b5ea"
title: "方法二 百度相关搜索关键词抓取 读取txt文档关键词 导出txt关键词 多线程采集关键词"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "高级安全"]
tags: ["安全与堡垒机", "高级安全", "Windows", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/05-拓展/birdben/68655782.html"
---

# 方法二 百度相关搜索关键词抓取 读取txt文档关键词 导出txt关键词 多线程采集关键词

```python
#百度相关搜索关键词抓取，读取txt关键词，导出txt关键词
# -*- coding=utf-8 -*-
import requests
import re
import time
from multiprocessing.dummy import Pool as ThreadPool
#百度相关关键词查询
def xgss(url):
headers = {
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
}
html=requests.get(url,headers=headers).text
#print(html)
ze=r'<div id="rs"><div class="tt">相关搜索</div><table cellpadding="0">(.+?)</table></div>'
xgss=re.findall(ze,html,re.S)
#print(xgss)
xgze=r'<th><a href="(.+?)">(.+?)</a></th>'
sj=re.findall(xgze,str(xgss),re.S)
#print(sj)
gjc=''
for x in sj:
print(x[1])
gjc=gjc+x[1]+'\n'
# 导出关键词为txt文本
with open(".\gjcsj.txt", 'a', encoding='utf-8') as f:
f.write(gjc)
print("-----------------------------------")
return gjc
print("程序运行，正在导入关键词列表！！！")
print("-----------------------------------")
# 导入要搜索的关键词txt列表
urls = []
data = []
for line in open('.\gjc.txt', "r", encoding='utf-8'):
data.append(line)
print("导入关键词列表成功！")
print("-----------------------------------")
#转换关键词为搜索链接
for keyword in data:
url = 'https://www.baidu.com/s?wd=' + keyword
urls.append(url)
print("采集百度相关搜索关键词开启！")
print("...................")
#多线程获取相关关键词
try:
# 开4个 worker，没有参数时默认是 cpu 的核心数
pool = ThreadPool()
results = pool.map(xgss, urls)
pool.close()
pool.join()
print("采集百度相关搜索关键词完成，已保存于gjcsj.txt！")
except:
print("Error: unable to start thread")
print("8s后程序自动关闭！！！")
time.sleep(8)
```
