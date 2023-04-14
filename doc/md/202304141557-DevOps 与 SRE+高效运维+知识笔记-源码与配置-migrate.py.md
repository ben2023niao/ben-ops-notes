---
id: "doc-b025636d46f6"
title: "migrate.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/migrate.py_68650274.html"
---

# migrate.py

```python
import django
import sys
import osBASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spug.settings")
django.setup()from django.conf import settings
import subprocess
import shutil
import sys
import os
import re
class Version:
def __init__(self, version):
self.version = re.sub('[^0-9.]', '', version).split('.')
def __gt__(self, other):
if not isinstance(other, Version):
raise TypeError('required type Version')
for v1, v2 in zip(self.version, other.version):
if int(v1) == int(v2):
continue
elif int(v1) > int(v2):
return True
else:
return False
return False
if __name__ == '__main__':
old_version = Version(sys.argv[1])
now_version = Version(settings.SPUG_VERSION)
if old_version < Version('v3.0.2'):
old_path = os.path.join(settings.BASE_DIR, 'repos')
new_path = os.path.join(settings.REPOS_DIR)
if not os.path.exists(new_path):
print('执行 v3.0.1-beta.8 repos目录迁移')
shutil.move(old_path, new_path)
task = subprocess.Popen(f'cd {settings.BASE_DIR} && git checkout -- repos', shell=True)
if task.wait() != 0:
print('repos目录迁移失败，请联系官方人员')
```
