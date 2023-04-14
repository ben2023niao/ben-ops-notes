---
id: "doc-33aae2cdaf7e"
title: "manage.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/manage.py_68650182.html"
---

# manage.py

```python
#!/usr/bin/env python
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
"""Django's command-line utility for administrative tasks."""
import os
import sys
def main():
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spug.settings')
try:
from django.core.management import execute_from_command_line
except ImportError as exc:
raise ImportError(
"Couldn't import Django. Are you sure it's installed and "
"available on your PYTHONPATH environment variable? Did you "
"forget to activate a virtual environment?"
) from exc
execute_from_command_line(sys.argv)
if __name__ == '__main__':
main()
```
