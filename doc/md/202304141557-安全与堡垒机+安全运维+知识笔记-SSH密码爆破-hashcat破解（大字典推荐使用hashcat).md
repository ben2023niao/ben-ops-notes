---
id: "doc-cb7dfb341e3a"
title: "SSH密码爆破-hashcat破解（大字典推荐使用hashcat)"
date: "2023-04-14T15:57:00"
categories: ["安全与堡垒机", "安全运维"]
tags: ["安全与堡垒机", "安全运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/04-安全运维/birdben/68652627.html"
---

# SSH密码爆破-hashcat破解（大字典推荐使用hashcat)

> hashcat的使用可以看这篇文章<https://xz.aliyun.com/t/4008>

将/etc/shadow文件，提取密码字段保存hash.txt

```
$6$qvhlqI7I$//0whlOY9i55tzFatxkzafR7n7KA2P2nRh7kMSo82KrGV89ujtSTPEJOQjXsRGpSEFuFKnCT0a0.g92kCstOP1
```

```
hashcat -m 1800 -a 0 -o result.txt hash.txt pass.txt --force

-m 是指定那种加密类型，1800是SHA-512(Unix)的代号，具体–help来查看；
-a  是指定攻击模式,0代表Straight模式,使用字典进行破解尝试;
-o 是破解出来的信息输出结果文件,输出到found.txt文件中;
hash.txt 是我们上面保存的加密密码文件；
pass.txt 是我们的爆破密码，越大越精越好；
--force 忽略破解过程中的警告信息,跑单条hash可能需要加上此选项
```

![文档配图](../media/743c260ec6114d2b19.png)
也可以使用**hashcat hash --show**来显示结果

![文档配图](../media/a38e40fc1f024334a0.png)
