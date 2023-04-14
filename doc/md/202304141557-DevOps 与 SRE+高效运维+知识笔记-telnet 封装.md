---
id: "doc-62388b30c199"
title: "telnet 封装"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/72057026.html"
---

# telnet 封装

```bash
#!/bin/bash
ip=$1
port=$2
echo > tmp.txt
cat > scan.sh <<"EOF"
/usr/bin/telnet $1 $2 << ! > tmp.txt
quit
!
EOF
 sh scan.sh $ip $port > /dev/null 2>&1 &
 sleep 0.5
 cat tmp.txt

rm -f ./scan.sh
rm -f ./tmp.txt
```
