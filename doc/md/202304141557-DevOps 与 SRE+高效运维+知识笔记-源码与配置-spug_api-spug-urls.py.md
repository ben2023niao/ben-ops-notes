---
id: "doc-7d231e2a42cd"
title: "spug_api/spug/urls.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650267.html"
---

# spug_api/spug/urls.py

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-spug_api-spug-urls.py.md)

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
