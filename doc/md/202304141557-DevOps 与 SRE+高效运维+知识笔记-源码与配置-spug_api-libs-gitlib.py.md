---
id: "doc-35902a43f897"
title: "spug_api/libs/gitlib.py"
date: "2023-04-14T15:57:00"
categories: ["DevOps 与 SRE", "高效运维"]
tags: ["DevOps 与 SRE", "高效运维", "知识笔记"]
source: "03-安全运营与应急/07-工作运维离线知识库/11-高效运维/birdben/68650230.html"
---

# spug_api/libs/gitlib.py

> GitHub 仓库源文件：[点击打开网页渲染版](https://github.com/ben2023niao/ben-ops-notes/blob/main/doc/md/202304141557-DevOps%20%E4%B8%8E%20SRE%2B%E9%AB%98%E6%95%88%E8%BF%90%E7%BB%B4%2B%E7%9F%A5%E8%AF%86%E7%AC%94%E8%AE%B0-%E6%BA%90%E7%A0%81%E4%B8%8E%E9%85%8D%E7%BD%AE-spug_api-libs-gitlib.py.md)

```python
# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <[邮箱已脱敏]>
# Released under the AGPL-3.0 License.
from git import Repo, RemoteReference, TagReference, InvalidGitRepositoryError, GitCommandError
from tempfile import NamedTemporaryFile
from datetime import datetime
import shutil
import os
class Git:
def __init__(self, git_repo, repo_dir, pkey=None):
self.git_repo = git_repo
self.repo_dir = repo_dir
self.repo = None
self.pkey = pkey
self.fd = None
self.env = {}
def archive(self, filepath, commit):
with open(filepath, 'wb') as f:
self.repo.archive(f, commit)
def fetch_branches_tags(self):
self.fetch()
branches, tags = {}, {}
for ref in self.repo.references:
if isinstance(ref, RemoteReference):
if ref.remote_head != 'HEAD':
branches[ref.remote_head] = self._get_commits(f'origin/{ref.remote_head}', 30)
elif isinstance(ref, TagReference):
tags[ref.name] = {
'id': ref.tag.hexsha,
'author': ref.tag.tagger.name,
'date': self._format_date(ref.tag.tagged_date),
'message': ref.tag.message.strip()
} if ref.tag else {
'id': ref.commit.binsha.hex(),
'author': ref.commit.author.name,
'date': self._format_date(ref.commit.authored_date),
'message': ref.commit.message.strip()
}
tags = sorted(tags.items(), key=lambda x: x[1]['date'], reverse=True)
return branches, dict(tags)
def fetch(self):
try:
self.repo.remotes.origin.fetch(f=True, p=True, P=True)
except GitCommandError as e:
if self.env:
self.repo.remotes.origin.fetch(env=self.env, f=True, p=True, P=True)
else:
raise e
def _get_repo(self):
if os.path.exists(self.repo_dir):
try:
return Repo(self.repo_dir)
except InvalidGitRepositoryError:
if os.path.isdir(self.repo_dir):
shutil.rmtree(self.repo_dir)
else:
os.remove(self.repo_dir)
try:
repo = Repo.clone_from(self.git_repo, self.repo_dir)
except GitCommandError as e:
if self.env:
repo = Repo.clone_from(self.git_repo, self.repo_dir, env=self.env)
else:
raise e
return repo
def _get_commits(self, branch, count=10):
commits = []
for commit in self.repo.iter_commits(branch):
if len(commits) == count:
break
commits.append({
'id': commit.hexsha,
'author': commit.author.name,
'date': self._format_date(commit.committed_date),
'message': commit.message.strip()
})
return commits
def _format_date(self, timestamp):
if isinstance(timestamp, int):
date = datetime.fromtimestamp(timestamp)
return date.strftime('%Y-%m-%d %H:%M')
return timestamp
def __enter__(self):
if self.pkey:
self.fd = NamedTemporaryFile()
self.fd.write(self.pkey.encode())
self.fd.flush()
self.env = {'GIT_SSH_COMMAND': f'ssh -i {self.fd.name}'}
self.repo = self._get_repo()
return self
def __exit__(self, exc_type, exc_val, exc_tb):
if self.fd:
self.fd.close()
```
