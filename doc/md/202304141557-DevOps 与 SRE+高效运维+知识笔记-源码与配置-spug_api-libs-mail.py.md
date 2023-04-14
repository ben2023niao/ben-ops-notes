---
id: "doc-7339ba18a431"
title: "spug_api/libs/mail.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650236.html"
---

# spug_api/libs/mail.py

```python
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib
class Mail:
def __init__(self, server, port, username, password, nickname=None):
self.host = server
self.port = int(port)
self.user = username
self.password = [已脱敏]
self.nickname = nickname
def get_server(self):
if self.port == 465:
server = smtplib.SMTP_SSL(self.host, self.port)
elif self.port == 587:
server = smtplib.SMTP(self.host, self.port)
server.ehlo()
server.starttls()
else:
server = smtplib.SMTP(self.host, self.port)
server.login(self.user, self.password)
return server
def send_text_mail(self, receivers, subject, body):
server = self.get_server()
msg = MIMEText(body, 'plain', 'utf-8')
msg['Subject'] = Header(subject, 'utf-8')
msg['From'] = formataddr((self.nickname, self.user)) if self.nickname else self.user
server.sendmail(self.user, receivers, msg.as_string())
server.quit()
```
