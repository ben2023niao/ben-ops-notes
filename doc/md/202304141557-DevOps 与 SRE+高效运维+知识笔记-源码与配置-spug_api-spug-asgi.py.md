---
id: "doc-db515675aeac"
title: "spug_api/spug/asgi.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650261.html"
---

# spug_api/spug/asgi.py

```python
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""
import os
import django
from channels.routing import get_default_applicationos.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spug.settings')
django.setup()
application = get_default_application()
```
