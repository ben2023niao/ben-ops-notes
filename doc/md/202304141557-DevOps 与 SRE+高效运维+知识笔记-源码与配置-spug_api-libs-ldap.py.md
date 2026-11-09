---
id: "doc-45d7fd3f108f"
title: "spug_api/libs/ldap.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650234.html"
---

# spug_api/libs/ldap.py

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-spug_api-libs-ldap.py.md)

```python
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
import ldap
class LDAP:
def __init__(self, server, port, rules, admin_dn, password, base_dn):
self.server = server
self.port = port
self.rules = rules
self.admin_dn = admin_dn
self.password = [已脱敏]
self.base_dn = base_dn
def valid_user(self, username, password):
try:
conn = ldap.initialize("ldap://{0}:{1}".format(self.server, self.port), bytes_mode=False)
conn.simple_bind_s(self.admin_dn, self.password)
search_filter = f'({self.rules}={username})'
ldap_result_id = conn.search(self.base_dn, ldap.SCOPE_SUBTREE, search_filter, None)
result_type, result_data = conn.result(ldap_result_id, 0)
if result_type == ldap.RES_SEARCH_ENTRY:
conn.simple_bind_s(result_data[0][0], password)
return True, None
else:
return False, None
except Exception as error:
args = error.args
return False, args[0].get('desc', '未知错误') if args else '%s' % error
```
