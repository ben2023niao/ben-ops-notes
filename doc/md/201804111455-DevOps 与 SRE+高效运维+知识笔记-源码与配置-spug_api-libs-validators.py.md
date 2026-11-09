---
id: "doc-8b6d1e88c0e5"
title: "spug_api/libs/validators.py"
date: "2018-04-11T14:55:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650251.html"
---

# spug_api/libs/validators.py

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/201804111455-DevOps%20%E4%B8%8E%20SRE%2B%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-spug_api-libs-validators.py.md)

```python
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
import ipaddress
from datetime import datetime
# 判断是否是ip地址
def ip_validator(value):
try:
ipaddress.ip_address(value)
return True
except ValueError:
return False
# 判断是否是日期字符串，支持 2018-04-11 或 2018-04-11 14:55:30
def date_validator(value: str) -> bool:
value = value.strip()
try:
if len(value) == 10:
datetime.strptime(value, '%Y-%m-%d')
return True
elif len(value) == 19:
datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
return True
except ValueError:
pass
return False
```
