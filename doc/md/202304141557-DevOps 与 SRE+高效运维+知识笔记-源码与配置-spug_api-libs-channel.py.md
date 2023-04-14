---
id: "doc-f93b91e1f852"
title: "spug_api/libs/channel.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650226.html"
---

# spug_api/libs/channel.py

```python
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import uuidlayer = get_channel_layer()
class Channel:
@staticmethod
def get_token():
return uuid.uuid4().hex@staticmethod
def send_notify(title, content):
message = {
'type': 'notify.message',
'title': title,
'content': content
}
async_to_sync(layer.group_send)('notify', message)
```
