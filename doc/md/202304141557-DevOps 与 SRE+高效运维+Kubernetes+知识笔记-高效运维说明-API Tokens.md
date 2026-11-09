---
id: "doc-17e01ffc5d2c"
title: "API Tokens"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "Kubernetes", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/API-Tokens_68655157.html"
---

# API Tokens

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%2BKubernetes%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%E8%AF%B4%E6%98%8E-API%20Tokens.md)

我们建议您在创建 API KEY 时，给它设置一个有效时间。有些 API Tokens 是永久有效(`ttl=0`)，除非删除它们，否则永不失效，并且 API Tokens 不会因更改用户密码而失效。

您可以通过删除 API Tokens 或禁用用户来禁用它们。

## 删除 API Token

删除 API Tokens 的操作步骤如下：

1. 访问 Rancher API 视图中的所有 Tokens 列表：`https://<Rancher-Server-IP>/v3/tokens`。
2. 通过要删除的 Tokens ID 访问，例如：`https://<Rancher-Server-IP>/v3/tokens/kubectl-shell-user-vqkqt`。
3. 单击**删除**。

以下是用`ttl=0`生成的 Tokens 完整列表：

| Token | 描述 |

| --- | --- |

| `kubeconfig-*` | Kubeconfig Token |

| `kubectl-shell-*` | UI 中执行 `kubectl` 命令的 Token |

| `agent-*` | Agent 使用的 Token |

| `compose-token-*` | compose 使用的 Token |

| `helm-token-*` | Helm chart 使用的 Token |

| `*-pipeline*` | 项目流水线使用的 Token |

| `telemetry-*` | Telemetry Token |

| `drain-node-*` | Token for drain (我们使用 `kubectl` 来执行驱逐操作，因为没有原生 Kubernetes API 支持这个操作) |

### 在 Kubeconfig Tokens 上设置 TTL

*v2.4.6+ 可用*

从 Rancher v2.4.6 开始，管理员可以对 Kubeconfig 令牌设置全局 TTL。一旦令牌过期，kubectl 命令将要求用户对 Rancher 进行验证。

#### 说明

现有的 kubeconfig 标记不会随着新的 TTL 而更新。管理员可以删除旧的 kubeconfig 标记。

1. 在 Rancher API 视图`https://<Rancher-Server-IP/v3/settings/kubeconfig-generate-token>中禁用 kubeconfig-generate-token 设置。该设置指示 Rancher 不再在用户单击下载 kubeconfig 文件时自动生成令牌。kubeconfig 文件现在将提供登录 Rancher 的命令。
2. 编辑该设置，并将该值设置为 `false`。
3. 在 Rancher API 视图中进入设置 kubeconfig-token-ttl-minutes，网址为`https://<Rancher-Server-IP/v3/settings/kubeconfig-token-ttl-minutes`。默认情况下，kubeconfig-token-ttl-minutes 为 960 分钟（16 小时）。
4. 编辑设置并将其设置为所需的持续时间，单位为分钟。 ***注意：***这个值不能超过 API 令牌的最大长度。(`https://<Rancher-Server-IP/v3/settings/auth-token-max-ttl-minutes`)。在 Rancher v2.4.6 中，auth-token-max-ttl-minutes 默认设置为 1440（24 小时）。从 Rancher v2.4.7 开始，auth-token-max-ttl-minutes 将默认为 0，允许令牌永不过期，与 v2.4.5 类似。
