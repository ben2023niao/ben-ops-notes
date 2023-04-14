---
id: "doc-7e69ed62d7cd"
title: "routing.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/routing.py_68650220.html"
---

# routing.py

```python
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
from django.urls import path
from channels.routing import URLRouter
from consumer.consumers import *ws_router = URLRouter([
path('ws/ssh/<int:id>/', SSHConsumer),
path('ws/subscribe/<str:token>/', PubSubConsumer),
path('ws/<str:module>/<str:token>/', ComConsumer),
path('ws/notify/', NotifyConsumer),
])
```
