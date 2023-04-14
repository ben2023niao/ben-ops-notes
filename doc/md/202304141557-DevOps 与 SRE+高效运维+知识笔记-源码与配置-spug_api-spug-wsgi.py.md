---
id: "doc-23514634a038"
title: "spug_api/spug/wsgi.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650270.html"
---

# spug_api/spug/wsgi.py

```
"""
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
WSGI config for spug project.It exposes the WSGI callable as a module-level variable named ``application``.For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""import osfrom django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spug.settings')application = get_wsgi_application()
```
