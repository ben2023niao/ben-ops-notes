---
id: "doc-340327e8dc4d"
title: "域名检测告警功能方案-selenium"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Linux", "Java", "监控告警", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/66979508.html"
---

# 域名检测告警功能方案-selenium

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E4%BC%98%E5%8C%96%E6%96%B9%E6%A1%88%2BLinux%2BJava-%E5%9F%9F%E5%90%8D%E6%A3%80%E6%B5%8B%E5%91%8A%E8%AD%A6%E5%8A%9F%E8%83%BD%E6%96%B9%E6%A1%88-selenium.md)

方案一
思路 linux 服务器上 使用 selenium 驱动浏览器 来巡检域名

难点
监控信息发送飞机群
解决办法
shell封装一下 telegram 接口

难点
并发多个python脚本同时执行问题
解决办法
shell内使用 parallel 并发调度执行多个域名巡检脚本

难点
域名国内访问质量统计
解决办法
selenium内page_source.encode 函数来保存每次巡检后完整的html内容
然后shell 脚本判断统计 html 内 前端stroke-width 标签内 红色超时(#e61610) 字符串就获得 超时地区 了 其它颜色块代表不同网络质量

缺点
这种 bash+python 方案不适合小白用户，只面向专业运维
需要配置python环境和 浏览器驱动
并发检查效率被CPU核心数量限制，需要高配电脑
依赖第3方域名检查网站

效果图
![文档配图](../media/73c29ae1122d627be6.png)

源代码

```
#sudo apt-get install -y tidy parallel
IP=$(curl -s ip.me)
API="https://api.telegram.org/bot2133309226:AAECwiIYa-WuTtpW3S9_7U6ZwZ_z0GcBEwQ" #飞机机器人API
GID="chat_id=-771262501" #飞机机器人群ID
MSG="${API}/sendMessage?${GID}&text=" #发送文本方法
SF="$API/sendDocument?$GID -F document=@" #发送文件方法
PH="$API/sendPhoto?$GID -F photo=@" #发送图片方法
cat > www.ben << EOF
baidu.com
google.com
xxx.com
av.com
EOF
```

```
for URL in `cat www.ben | grep -v 域名` ;do
echo "谷歌浏览器打开 http://ping.chinaz.com/$URL"
echo '# -*- coding: UTF-8 -*-' > $URL.py
echo 'from selenium import webdriver' >> $URL.py
echo 'import time' >> $URL.py
echo 'ben = webdriver.Chrome()' >> $URL.py
echo "get_html = \"$URL.html\"" >> $URL.py
echo "f = open(get_html, 'wb')" >> $URL.py
echo "url = \"http://ping.chinaz.com/$URL\"" >> $URL.py
#echo 'ben.maximize_window()' >> $URL.py
echo 'ben.get(url)' >> $URL.py
echo 'ben.title' >> $URL.py
echo 'time.sleep(120)' >> $URL.py
echo 'f.write(ben.page_source.encode("UTF-8", "ignore")) #忽略非法字符' >> $URL.py
echo 'f.close()' >> $URL.py
echo "ben.get_screenshot_as_file(\"$URL.png\")" >> $URL.py
echo 'ben.quit()' >> $URL.py
done
```

## parallel命令是非常强大的并行计算命令，使用-j参数控制其并发数量, 每个CPU核心 -j+0 运行一个作业

#ls | grep py | parallel -j 50 python3 {}
ls | grep py | parallel -j+0 python3 {}

```
for i in `ls | grep html | sed "s/\.html//g"`
do
tidy $i.html > index.html 2>&1
cat index.html > $i.html
rm -f index.html

IPLIST=$(cat $i.html | \
grep '"javascript:">' | \
grep -E -o \
'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
```

```bash
function zp_check() {
curl $1 \
-H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
-H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,fil;q=0.7' \
-H 'Cache-Control: no-cache' \
-H 'Connection: keep-alive' \
-H 'Pragma: no-cache' \
-H 'Upgrade-Insecure-Requests: 1' \
-H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36' \
--compressed \
--insecure \
--connect-timeout 2 \
-s | grep '诈骗' | md5sum | awk '{print $1}'
}
```

#MD5=$(zp_check $1)

```bash
for ip in $IPLIST ; do
if [ "`zp_check $ip`" != "d41d8cd98f00b204e9800998ecf8427e" ];then
curl -s $MSG"$i 的节点ip $ip 跳诈 @ben_niao" > /dev/null
echo "$i 的节点ip $ip 跳诈"
touch $i跳炸ip_$ip.txt
else
if [ "$ip" = '203.0.113.1' ];then
curl -s $MSG"$i 的节点ip $ip 部分地区有运营商屏蔽 @ben_niao" > /dev/null
echo "$i 的节点ip $ip 部分地区有运营商屏蔽"
touch $i运营商屏蔽ip_$ip.txt
fi
if [ "$ip" = '203.0.113.1' ];then
curl -s $MSG"$i 的节点ip $ip 部分地区有运营商屏蔽 @ben_niao" > /dev/null
echo "$i 的节点ip $ip 部分地区有运营商屏蔽"
touch $i运营商屏蔽ip_$ip.txt
fi
echo "$i 的节点ip $ip 正常"
touch $i域名解析ip_$ip.txt
fi
done
```

```
#判断颜色来识别网络质量
AA=$(cat $i.html | grep '#24aa1d' | grep -v 'stroke-width' | wc -l)
AB=$(cat $i.html | grep '#42dd3f' | grep -v 'stroke-width' | wc -l)
AC=$(cat $i.html | grep '#bef663' | grep -v 'stroke-width' | wc -l)
AD=$(cat $i.html | grep '#f6ed44' | grep -v 'stroke-width' | wc -l)
AE=$(cat $i.html | grep '#f69833' | grep -v 'stroke-width' | wc -l)
AF=$(cat $i.html | grep '#e61610' | grep -v 'stroke-width' | wc -l)
```

```
#if [ "$AA" != "0" ];then curl $MSG"$i $AA 个地区延迟 <=400ms " ; curl $PH"$i.png" ;fi
#if [ "$AB" != "0" ];then curl $MSG"$i $AA 个地区延迟 400~800ms " ; curl $PH"$i.png" ;fi
#if [ "$AC" != "0" ];then curl $MSG"$i $AA 个地区延迟 800~1200ms " ; curl $PH"$i.png" ;fi
#if [ "$AD" != "0" ];then curl $MSG"$i $AA 个地区延迟 1200~1600ms @ben_niao" ; curl $PH"$i.png" ;fi
#if [ "$AE" != "0" ];then curl $MSG"$i $AA 个地区延迟 <1600ms @ben_niao" ; curl $PH"$i.png" ;fi
if [ "$AF" != "0" ];then curl $MSG"$i $AA 个地区延迟 超时 @ben_niao" ; curl $PH"$i.png" ;fi
done
ls | grep txt | grep -v 解析
```
