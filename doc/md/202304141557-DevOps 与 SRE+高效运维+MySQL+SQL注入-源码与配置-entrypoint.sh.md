---
id: "doc-1f32bd110706"
title: "entrypoint.sh"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "MySQL", "SQL注入", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/entrypoint.sh_68650140.html"
---

# entrypoint.sh

```bash
#!/bin/bash
#
set -eif [ -e /root/.bashrc ]; then
source /root/.bashrc
fiif [ ! -d /data/spug ]; then
tar xf /tmp/spug.tar.gz -C /data/
SECRET_KEY=$(< /dev/urandom tr -dc '!@#%^.a-zA-Z0-9' | head -c50)
cat > /data/spug/spug_api/spug//overrides.py << EOF
DEBUG = False
ALLOWED_HOSTS = ['203.0.113.1']
SECRET_KEY = '${SECRET_KEY}'DATABASES = {
'default': {
'ATOMIC_REQUESTS': True,
'ENGINE': 'django.db.backends.mysql',
'NAME': 'spug',
'USER': 'spug',
'PASSWORD': 'spug.dev',
'HOST': 'localhost',
'OPTIONS': {
'unix_socket': '/var/lib/mysql/mysql.sock',
'charset': 'utf8mb4',
'sql_mode': 'STRICT_TRANS_TABLES',
}
}
}
EOF
fiif [ ! -d /data/mysql ]; then
mkdir -p /data/mysql
mysql_install_db
chown -R mysql.mysql /data/mysqltfile=`mktemp`
cat >> $tfile << EOF
use mysql;
flush privileges;
create database spug character set utf8mb4 collate utf8mb4_unicode_ci;
grant all on spug.* to spug@'localhost' identified by 'spug.dev';
flush privileges;
EOF/usr/libexec/mysqld --user=mysql --bootstrap < $tfile
rm -f $tfile
fiexec supervisord -c /etc/supervisord.conf
```
