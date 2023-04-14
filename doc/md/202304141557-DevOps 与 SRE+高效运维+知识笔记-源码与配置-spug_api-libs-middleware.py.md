---
id: "doc-d83472d9a943"
title: "spug_api/libs/middleware.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650238.html"
---

# spug_api/libs/middleware.py

```python
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .utils import json_response, get_request_real_ip
from apps.account.models import User
from apps.setting.utils import AppSetting
import traceback
import time
class HandleExceptionMiddleware(MiddlewareMixin):
"""
处理试图函数异常
"""
def process_exception(self, request, exception):
traceback.print_exc()
return json_response(error='Exception: %s' % exception)
class AuthenticationMiddleware(MiddlewareMixin):
"""
登录验证
"""
def process_request(self, request):
if request.path in settings.AUTHENTICATION_EXCLUDES:
return None
if any(x.match(request.path) for x in settings.AUTHENTICATION_EXCLUDES if hasattr(x, 'match')):
return None
access_token = request.headers.get('x-token') or request.GET.get('x-token')
if access_token and len(access_token) == 32:
x_real_ip = get_request_real_ip(request.headers)
user = User.objects.filter(access_token=access_token).first()
if user and user.token_expired >= time.time() and user.is_active:
if x_real_ip == user.last_ip or AppSetting.get_default('bind_ip') is False:
request.user = user
user.token_expired = time.time() + 8 * 60 * 60
user.save()
return None
response = json_response(error="验证失败，请重新登录")
response.status_code = 401
return response
```
