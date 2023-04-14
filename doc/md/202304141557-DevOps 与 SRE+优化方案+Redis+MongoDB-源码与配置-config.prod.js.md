---
id: "doc-a06ded3c354e"
title: "config.prod.js"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "优化方案"]
tags: ["DevOps 与 SRE", "优化方案", "Redis", "MongoDB", "CSRF", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/03-优化方案/birdben/config.prod.js_84415176.html"
---

# config.prod.js

```
'use strict';
module.exports = () => {
 const config = exports = {};
 config.debug = false;
 // 用于安全校验和回调域名根路径 开发路径域名（必填）
 // 线上环境此处替换为项目根域名 例如:https://blog.seosiwei.com (这里需要填写http|https和斜杠等字符)
 config.origin = [ 'https://img.18x18b.com','http://203.0.113.1:7001' ];
 // 百度地图api key
 config.BAIDUAK = 'WjR3GaQlZp4sxIiLt6RX86civGiT0qYR';
 // github login
 config.github = {
 client_id: 'xxxxxx',
 client_secret: 'xxxxxx',
 scope: [ 'user' ],
 };
 // ldap
 config.ldap = {
 server: 'ldap://xxx', // ldap服务器地址
 ou: 'xx', // ou
 dc: 'xx', // dc, 非com的另外一层的dc，例如 dc=foobar,dc=com, 这里填 foobar
 isLdap: false, // 是否采用ldap;
 };
 // 新浪微博 login
 config.weibo = {
 client_id: 'xxxxxx', // 微博的App Key
 client_secret: 'xxxxxx', // 微博的App Secret
 scope: [ 'all' ],
 };
 // wechat login
 config.wechat = {
 client_id: 'xxxxxx', // 微信的AppId
 client_secret: 'xxxxxx', // 微信的App Secret
 };
 // redis配置
 config.redis = {
 client: {
 port: 6379, // Redis port
 host: '203.0.113.1', // Redis host
 password: '',
 db: 0,
 },
 };
 // mongodb 服务
 const dbclients = {
 db3: {
 // 单机部署
 //url: 'mongodb://203.0.113.1:27017/performance',
 // 副本集 读写分离
 //url: 'mongodb://203.0.113.1:27014,203.0.113.1:27015/performance?replicaSet=rs2,203.0.113.1:27016,203.0.113.1:27017/performance?replicaSet=rs1',
 //单路由方式
 url: 'mongodb://203.0.113.1:27011/performance',
 // url: 'mongodb://203.0.113.1:28100,203.0.113.1:28101,203.0.113.1:28102/performance?replicaSet=rs1',
 // 集群分片
 // url: 'mongodb://203.0.113.1:30000/performance',
 options: {
 poolSize: 100,
 keepAlive: 10000,
 connectTimeoutMS: 10000,
 autoReconnect: true,
 reconnectTries: 100,
 reconnectInterval: 1000,
 useUnifiedTopology: true,
 },
 },
 };
 if (config.report_data_type === 'mongodb') {
 dbclients.db1 = {
 // url: 'mongodb://203.0.113.1:27017,203.0.113.1:27018/performance?replicaSet=performance',
 url: 'mongodb://203.0.113.1:27011/performance',
 options: {
 poolSize: 100,
 keepAlive: 10000,
 connectTimeoutMS: 10000,
 autoReconnect: true,
 reconnectTries: 100,
 reconnectInterval: 1000,
 useUnifiedTopology: true,
 },
 };
 }
 // mongoose配置
 config.mongoose = {
 clients: dbclients,
 };
 config.security = {
 domainWhiteList: [ 'https://img.18x18b.com','http://203.0.113.1:7001' ],
 csrf: {
 enable: false,
 ignore: '/api/v1/report/**',
 },
 };
 return config;
};
```
