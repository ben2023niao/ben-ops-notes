---
id: "doc-3d79657be12d"
title: "gitlab-docker-compose.yml"
date: "2022-06-11T16:36:02.884000+08:00"
dateSource: "GitBook 页面更新时间"
categories: ["容器与云原生", "Docker"]
tags: ["Docker", "Shell", "源码与配置"]
source: "https://xn--6o0a585a.gitbook.io/devops/docker/docker-compose/gitlab-docker-compose.yml.html"
sourceFormat: "GitBook rendered HTML"
sourceHtmlSha256: "f01778cbff41c55843dc5afe749357e7064a40728d6c489eae31ce0891159173"
---

# gitlab-docker-compose.yml

> 原文：[gitlab-docker-compose.yml](https://xn--6o0a585a.gitbook.io/devops/docker/docker-compose/gitlab-docker-compose.yml.html)

> 来源：GitBook 网页 HTML｜页面时间：2022-06-11 16:36｜日期依据：GitBook 页面更新时间

```
web:
  image: gitlab/gitlab-ce:11.4.5-ce.0
  container_name: gitlab
  restart: always
  hostname: gitlab
  environment:
    GITLAB_OMNIBUS_CONFIG: |
      external_url 'http://203.0.113.1'
      gitlab_rails['gitlab_shell_ssh_port'] = 80
      gitlab_rails['smtp_enable'] = true
      gitlab_rails['smtp_address'] = "smtp.163.com"
      gitlab_rails['smtp_port'] = 25
      gitlab_rails['smtp_user_name'] = "[邮箱已脱敏]"
      gitlab_rails['smtp_password'] = "邮箱密码"
      gitlab_rails['smtp_domain'] = "163.com"
      gitlab_rails['smtp_authentication'] = :login
      gitlab_rails['smtp_enable_starttls_auto'] = true
      gitlab_rails['gitlab_email_from'] = "[邮箱已脱敏]"
      user["git_user_email"] = "[邮箱已脱敏]"
  ports:
    - '443:443'
    - '2020:22'
    - '80:80'
  volumes:
    - '/data/docker/volume/gitlab/config:/etc/gitlab'
    - '/data/docker/volume/gitlab/logs:/var/log/gitlab'
    - '/data/docker/volume/gitlab/data:/var/opt/gitlab'

    #访问地址 localhost
    #默认账号 root
```
