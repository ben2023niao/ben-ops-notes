---
id: "doc-65486dfda776"
title: "spug_api/libs/decorators.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "权限管理", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650228.html"
---

# spug_api/libs/decorators.py

```python
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
from functools import wraps
from .utils import json_response
def auth(perm_list):
def decorate(view_func):
codes = perm_list.split('|')@wraps(view_func)
def wrapper(*args, **kwargs):
user = None
for item in args[:2]:
if hasattr(item, 'user'):
user = item.user
break
if user and user.has_perms(codes):
return view_func(*args, **kwargs)
return json_response(error='权限拒绝')return wrapperreturn decorate
```
