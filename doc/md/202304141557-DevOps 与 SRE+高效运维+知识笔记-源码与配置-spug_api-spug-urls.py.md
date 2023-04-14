---
id: "doc-7d231e2a42cd"
title: "spug_api/spug/urls.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650267.html"
---

# spug_api/spug/urls.py

```python
"""spug URL Configuration
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.The `urlpatterns` list routes URLs to views. For more information please see:
https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
1. Add an import: from my_app import views
2. Add a URL to urlpatterns: path('', views.home, name='home')
Class-based views
1. Add an import: from other_app.views import Home
2. Add a URL to urlpatterns: path('', Home.as_view(), name='home')
Including another URLconf
1. Import the include() function: from django.urls import include, path
2. Add a URL to urlpatterns: path('blog/', include('blog.urls'))
"""
from django.urls import path, includeurlpatterns = [
path('account/', include('apps.account.urls')),
path('host/', include('apps.host.urls')),
path('exec/', include('apps.exec.urls')),
path('schedule/', include('apps.schedule.urls')),
path('monitor/', include('apps.monitor.urls')),
path('alarm/', include('apps.alarm.urls')),
path('setting/', include('apps.setting.urls')),
path('config/', include('apps.config.urls')),
path('app/', include('apps.app.urls')),
path('deploy/', include('apps.deploy.urls')),
path('repository/', include('apps.repository.urls')),
path('home/', include('apps.home.urls')),
path('notify/', include('apps.notify.urls')),
path('file/', include('apps.file.urls')),
path('apis/', include('apps.apis.urls')),
]
```
