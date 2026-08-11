---
id: "doc-76241f97a8b3"
title: "18gamephp"
date: "2026-08-11T15:09:59+08:00"
dateSource: "文件创建/修改时间"
categories: ["业务系统运维", "游点涩"]
tags: ["游点涩", "Shell", "Docker", "故障排查", "源码与配置"]
source: "project-file:///Projects/work/game/youdianse-docker/main/docker-youdianse-php/src/youdianse-php/doc/developer_rules.md"
sourcePath: "~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/src/youdianse-php/doc/developer_rules.md"
sourceSha256: "c2f027b76dad66cab3444218621357e2642ff4c849d14476e9540b528bf2d054"
sourceSystem: "project-doc"
---

# 18gamephp

> 来源文件：`~/Projects/work/game/youdianse-docker/main/docker-youdianse-php/src/youdianse-php/doc/developer_rules.md`

> 整理日期：2026-08-11 15:09｜日期依据：文件创建/修改时间

### 数据库表模型生成
* 1-app\Resource\tables\ 下面创建对应的数据json文件来生产数据表和models
* 2-创建完毕后运行  php bin/shell.php tools model xxxx 命令来执行生成model和数据表以及其索引(注意:必须执行这个命令否则不生成索引)
* 3-一些大型log表,在入库的时候insert的时候,使用false不生成自增数字id,防止冲突,使用默认的objectid

### 请求限流器!CommonService::checkActionLimit(key)
* 1-后台key规范是do_行为_backend_控制器_方法_
* 2-接口key规范是do_行为_api_控制器_方法_

### git 流程
* 1-每个需求都必须从main分支创建一个开发分支进行开发(分支案例: feature/cike20260123-xxxx需求),
* 2-本地开发完毕后把开发分支合并到test分支(dev),
* 3-测试人员测试无误后,允许上线,再把开发分支合并到pre分支(预发分支进行验证)
* 4-验证完毕后合并main生产发你只

### 开发规范 必须严格遵循
* 接口全部用POST , 返回的字段全部用string, 降低对接成本
* 一般在Repository层做数据格式转换,不要偷懒封装方法批量转换
* 变量用小驼峰,如userRow、userInfo
* 数据库查出来的数据 用 xxRow 比如用户 userRow
* 缓存查出来的数据 用 xxInfo 比如用户userInfo
* MediaTask 禁止修改
* 禁止对整个文件进行格式化操作（避免git冲突可能性）

### 定时任务（cron）
```shell
 */1 * * * *     /bin/sh /var/www/html/18game/18game_php/bin/start.sh >/dev/null&
```

### 控制台命令的使用方式
php bin/shell.php {task} {action}
如
```shell
php bin/shell.php tools model
```

### Git Commit Message 规范

#### commit message格式
```
<type>(<scope>): <subject>
```

#### type
* feat：新功能（feature）
* fix：修补 bug
* docs：文档（documentation）
* style：格式（不影响代码运行的变动）
* refactor：重构（即不是新增功能，也不是修改 bug 的代码变动）
* test：增加测试
* chore：构建过程或辅助工具的变动

#### scope
scope 用于说明 commit 影响的范围，比如数据层、控制层、视图层等等，视仓库不同而不同。

#### subject
subject 是 commit 目的的简短描述，不超过 50 个字符。

#### Git Commit Message范例
* fix(global):修复checkbox不能复选的问题
* fix(common): 修复字体过小的BUG，将通用管理下所有页面的默认字体大小修改为 14px
* fix: value.length -> values.length
* feat: 添加网站主页静态页面
* chore: 将表格中的查看详情改为详情

### Email
* composer require phpmailer/phpmailer:^6.9.3
* composer require async-aws/ses:^1.12
* composer require aws/aws-sdk-php:3.273.0
