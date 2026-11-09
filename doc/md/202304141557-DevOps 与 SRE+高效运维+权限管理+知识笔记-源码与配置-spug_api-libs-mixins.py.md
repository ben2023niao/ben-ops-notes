---
id: "doc-6f81c8b97b75"
title: "spug_api/libs/mixins.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "权限管理", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650240.html"
---

# spug_api/libs/mixins.py

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%2B%E6%9D%83%E9%99%90%E7%AE%A1%E7%90%86%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-spug_api-libs-mixins.py.md)

```python
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
from django.views.generic import View
from .utils import json_response
# 混入类，提供Model实例to_dict方法
class ModelMixin(object):
__slots__ = ()
def to_dict(self, excludes: tuple = None, selects: tuple = None) -> dict:
if not hasattr(self, '_meta'):
raise TypeError('<%r> does not a django.db.models.Model object.' % self)
elif selects:
return {f: getattr(self, f) for f in selects}
elif excludes:
return {f.attname: getattr(self, f.attname) for f in self._meta.fields if f.attname not in excludes}
else:
return {f.attname: getattr(self, f.attname) for f in self._meta.fields}
def update_by_dict(self, data):
for key, value in data.items():
setattr(self, key, value)
self.save()
class AdminView(View):
def dispatch(self, request, *args, **kwargs):
if hasattr(request, 'user') and request.user.is_supper:
return super().dispatch(request, *args, **kwargs)
else:
return json_response(error='权限拒绝')
```
