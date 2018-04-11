---
id: "doc-8b6d1e88c0e5"
title: "spug_api/libs/validators.py"
date: "2018-04-11T14:55:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650251.html"
---

# spug_api/libs/validators.py

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
