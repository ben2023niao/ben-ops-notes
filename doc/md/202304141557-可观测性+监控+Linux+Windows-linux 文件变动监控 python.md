---
id: "doc-7578d548246e"
title: "linux 文件变动监控 python"
date: "2023-04-14T15:57:00"
categories: ["可观测性", "监控"]
tags: ["可观测性", "监控", "Linux", "Windows", "监控告警", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/07-监控技巧/birdben/72066891.html"
---

# linux 文件变动监控 python

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-%E5%8F%AF%E8%A7%82%E6%B5%8B%E6%80%A7%2B%E7%9B%91%E6%8E%A7%2BLinux%2BWindows-linux%20%E6%96%87%E4%BB%B6%E5%8F%98%E5%8A%A8%E7%9B%91%E6%8E%A7%20python.md)

在linux中可以使用命令 find 来查看文件短时间内的文件修改情况，Windows中也提供了相应的api可以对相应的文件和目录进行监控。

在python中，这里介绍一个库，可作为文件监控的工具。

项目的地址在：<https://github.com/gorakhargosh/watchdog>
安装命令：

```
pip install watchdog
```

下面使用一段代码对当前文件进行监控，如下：

```python
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
if __name__ == "__main__":
logging.basicConfig(level=logging.INFO,
format='%(asctime)s - %(message)s',
datefmt='%Y-%m-%d %H:%M:%S')
path = sys.argv[1] if len(sys.argv) > 1 else '.'
event_handler = LoggingEventHandler()
observer = Observer()
observer.schedule(event_handler, path, recursive=True)
observer.start()
try:
while True:
time.sleep(1)
except KeyboardInterrupt:
observer.stop()
observer.join()
```

```
#如果出现了如下的错误：
raise OSError("inotify watch limit reached")
#可以这样处理：
echo 8192000 > /proc/sys/fs/inotify/max_user_watches
#运行此脚本：
python3 m.py /root/
#为了测试，我们在/root/目录下删除master.zip 和master.zip.1，结果如下提示：
2018-08-31 13:53:20 - Deleted file: /root/master.zip
2018-08-31 13:53:20 - Modified directory: /root
2018-08-31 13:53:37 - Deleted file: /root/master.zip.1
2018-08-31 13:53:37 - Modified directory: /root
#如果不使用python进行编程， 也可以直接使用脚本命令
watchmedo log --patterns="*.py;*.txt" --ignore-directories --recursive .
#可监控某一目录。
```
