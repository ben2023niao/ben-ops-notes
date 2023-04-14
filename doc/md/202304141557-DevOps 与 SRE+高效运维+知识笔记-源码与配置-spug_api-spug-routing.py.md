---
id: "doc-ecf1f9cefe8d"
title: "spug_api/spug/routing.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650263.html"
---

# spug_api/spug/routing.py

```python
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
from channels.routing import ProtocolTypeRouter
from consumer import routingapplication = ProtocolTypeRouter({
'websocket': routing.ws_router
})
```
