---
id: "doc-39ea17b7e751"
title: "spug_api/libs/parser.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650242.html"
---

# spug_api/libs/parser.py

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-spug_api-libs-parser.py.md)

```python
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
import jsonfrom .utils import AttrDict
# 自定义的解析异常
class ParseError(BaseException):
def __init__(self, message):
self.message = message
# 需要校验的参数对象
class Argument(object):
"""
:param name: name of option
:param default: default value if the argument if absent
:param bool required: is required
"""
def __init__(self, name, default=None, handler=None, required=True, type=str, filter=None, help=None):
self.name = name
self.default = default
self.type = type
self.required = required
self.filter = filter
self.help = help
self.handler = handler
if not isinstance(self.name, str):
raise TypeError('Argument name must be string')
if filter and not callable(self.filter):
raise TypeError('Argument filter is not callable')
def parse(self, has_key, value):
if not has_key:
if self.required and self.default is None:
raise ParseError(
self.help or 'Required Error: %s is required' % self.name)
else:
return self.default
elif value in [u'', '', None]:
if self.default is not None:
return self.default
elif self.required:
raise ParseError(self.help or 'Value Error: %s must not be null' % self.name)
elif self.help:
raise ParseError(self.help)
else:
return value
try:
if self.type:
if self.type in (list, dict) and isinstance(value, str):
value = json.loads(value)
assert isinstance(value, self.type)
elif self.type == bool and isinstance(value, str):
assert value.lower() in ['true', 'false']
value = value.lower() == 'true'
elif not isinstance(value, self.type):
value = self.type(value)
except (TypeError, ValueError, AssertionError):
raise ParseError(self.help or 'Type Error: %s type must be %s' % (
self.name, self.type))if self.filter:
if not self.filter(value):
raise ParseError(
self.help or 'Value Error: %s filter check failed' % self.name)
if self.handler:
value = self.handler(value)
return value
# 解析器基类
class BaseParser(object):
def __init__(self, *args):
self.args = []
for e in args:
if isinstance(e, str):
e = Argument(e)
elif not isinstance(e, Argument):
raise TypeError('%r is not instance of Argument' % e)
self.args.append(e)
def _get(self, key):
raise NotImplementedError
def _init(self, data):
raise NotImplementedError
def add_argument(self, **kwargs):
self.args.append(Argument(**kwargs))
def parse(self, data=None, clear=False):
rst = AttrDict()
try:
self._init(data)
for e in self.args:
has_key, value = self._get(e.name)
if clear and has_key is False and e.required is False:
continue
rst[e.name] = e.parse(has_key, value)
except ParseError as err:
return None, err.message
return rst, None
# Json解析器
class JsonParser(BaseParser):
def __init__(self, *args):
self.__data = None
super(JsonParser, self).__init__(*args)
def _get(self, key):
return key in self.__data, self.__data.get(key)
def _init(self, data):
try:
if isinstance(data, (str, bytes)):
self.__data = json.loads(data) if data else {}
else:
assert hasattr(data, '__contains__')
assert hasattr(data, 'get')
assert callable(data.get)
self.__data = data
except (ValueError, AssertionError):
raise ParseError('Invalid data type for parse')
```
