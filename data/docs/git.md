# Git 面试知识点速记（Python 后端 + AI 方向）

## 1. Git 是什么

### 1.1 一句话理解
Git 是一个**分布式版本控制系统**，用来追踪文件变更、支持多人协作开发，几乎是现代软件开发的标配工具。

### 1.2 它解决什么问题
**没有版本控制时的痛点：**
- 文件命名混乱：`v1.py`, `v2_final.py`, `v2_final_真的final.py`
- 多人协作容易互相覆盖代码
- 无法追溯"谁在什么时候改了什么"
- 回滚困难，出了 bug 不知道哪个版本引入的

**Git 的核心价值：**
- 完整的变更历史记录
- 支持分支开发，互不干扰
- 分布式架构，每个人都有完整仓库副本
- 合并冲突有明确的解决机制

---

## 2. Git 和 SVN 的区别

### 2.1 SVN（集中式）
- 只有一个中央服务器存储完整历史
- 每次提交都需要联网
- 服务器挂了，历史就丢了

### 2.2 Git（分布式）
- 每个开发者本地都有完整的仓库和历史
- 可以离线提交、查看日志、创建分支
- 任何一个副本都可以恢复整个项目

### 2.3 面试答法
> **面试回答模板：**
> Git 是分布式版本控制，每个开发者本地都有完整仓库；SVN 是集中式的，依赖中央服务器。Git 支持离线操作、分支更轻量、合并更强大，是目前业界主流选择。

---

## 3. Git 核心概念

### 3.1 三个区域
Git 管理文件有三个核心区域：

| 区域 | 说明 |
|------|------|
| **工作区（Working Directory）** | 你实际编辑文件的地方 |
| **暂存区（Staging Area / Index）** | `git add` 后文件进入这里，准备提交 |
| **本地仓库（Repository）** | `git commit` 后文件进入这里，形成一个版本快照 |

> **面试常问：git add 和 git commit 的区别？**
> **回答：** `git add` 把修改放入暂存区，`git commit` 把暂存区的内容提交到本地仓库形成一个版本。这种两步设计让你可以选择性地提交部分修改。

### 3.2 文件的四种状态
```
Untracked → Staged → Committed → Modified
   ↑                                  |
   └──────────────────────────────────┘
```
- **Untracked**：新文件，Git 还不知道它的存在
- **Staged**：已 `git add`，等待提交
- **Committed**：已提交到本地仓库
- **Modified**：已提交过的文件被修改了

### 3.3 HEAD 指针
- HEAD 指向当前所在的分支的最新提交
- `HEAD~1` 表示上一个提交，`HEAD~2` 表示上上个
- `detached HEAD` 状态：HEAD 直接指向某个 commit 而不是分支

---

## 4. 常用命令速记

### 4.1 基础操作
```bash
git init                    # 初始化仓库
git clone <url>             # 克隆远程仓库
git status                  # 查看当前状态
git add <file>              # 添加到暂存区
git add .                   # 添加所有修改
git commit -m "message"     # 提交
git log                     # 查看提交历史
git log --oneline --graph   # 简洁图形化日志
```

### 4.2 分支操作
```bash
git branch                  # 查看本地分支
git branch <name>           # 创建分支
git checkout <name>         # 切换分支
git checkout -b <name>      # 创建并切换
git switch <name>           # 切换分支（新语法）
git switch -c <name>        # 创建并切换（新语法）
git branch -d <name>        # 删除已合并的分支
git branch -D <name>        # 强制删除分支
```

### 4.3 远程操作
```bash
git remote -v               # 查看远程仓库
git fetch                   # 拉取远程更新（不合并）
git pull                    # 拉取并合并（= fetch + merge）
git push                    # 推送到远程
git push -u origin <branch> # 首次推送并关联远程分支
```

### 4.4 撤销操作
```bash
git checkout -- <file>      # 丢弃工作区修改
git restore <file>          # 丢弃工作区修改（新语法）
git reset HEAD <file>       # 取消暂存
git restore --staged <file> # 取消暂存（新语法）
git reset --soft HEAD~1     # 撤销提交，保留修改在暂存区
git reset --mixed HEAD~1    # 撤销提交，保留修改在工作区（默认）
git reset --hard HEAD~1     # 撤销提交，丢弃所有修改（危险！）
git revert <commit>         # 创建一个新提交来撤销指定提交（安全）
```

> **面试常问：reset 和 revert 的区别？**
> **回答：** `reset` 是回退，直接修改历史，适合本地还没 push 的提交；`revert` 是反做，生成一个新的提交来抵消之前的修改，不改变历史，适合已经 push 到远程的提交。

---

## 5. 分支管理与合并

### 5.1 merge vs rebase

**merge（合并）：**
```bash
git checkout main
git merge feature
```
- 保留完整的分支历史
- 会产生一个合并提交（merge commit）
- 历史是非线性的

**rebase（变基）：**
```bash
git checkout feature
git rebase main
```
- 把 feature 分支的提交"搬到" main 分支最新提交之后
- 历史变成线性的，更干净
- **不要对已经 push 到远程的公共分支做 rebase**

### 5.2 面试答法
> **面试回答模板：**
> merge 保留真实的分支历史，会产生合并提交；rebase 让历史变成线性，更整洁。一般建议：个人分支用 rebase 保持干净，合入主分支用 merge 保留记录。核心原则是**不要对公共分支做 rebase**。

### 5.3 解决冲突
```bash
# 合并时出现冲突
git merge feature
# 手动编辑冲突文件，冲突标记如下：
<<<<<<< HEAD
当前分支的内容
=======
要合并进来的内容
>>>>>>> feature

# 解决后
git add <resolved-file>
git commit
```

---

## 6. Git 工作流

### 6.1 Git Flow
```
main ──────────────────────────────────→
  └── develop ──────────────────────→
        ├── feature/login ──→ merge back
        ├── feature/pay ────→ merge back
        └── release/1.0 ───→ merge to main + develop
```
- `main`：生产环境代码
- `develop`：开发主线
- `feature/*`：功能分支
- `release/*`：发布准备
- `hotfix/*`：紧急修复

### 6.2 GitHub Flow（更简单）
- 只有 `main` 分支是长期分支
- 开发新功能：从 main 拉分支 → 开发 → 提 PR → Code Review → 合并
- 适合持续部署的项目

### 6.3 面试答法
> **面试回答模板：**
> 我们团队用的是类似 GitHub Flow 的工作流：main 分支保持可部署状态，开发新功能从 main 拉 feature 分支，完成后提 PR 经过 Code Review 再合并。如果是大型项目会用 Git Flow，多一个 develop 分支做开发主线。

---

## 7. 高频面试题

### 7.1 git fetch 和 git pull 的区别
> `fetch` 只是把远程的更新下载到本地，不会自动合并；`pull` = `fetch` + `merge`，会自动合并到当前分支。建议先 fetch 看看有什么变化，再决定怎么合并。

### 7.2 git stash 的使用场景
```bash
git stash           # 暂存当前修改
git stash list      # 查看暂存列表
git stash pop       # 恢复最近一次暂存并删除记录
git stash apply     # 恢复但不删除记录
git stash drop      # 删除某条暂存
```
> **场景：** 正在 feature 分支开发到一半，突然要切到 main 修 bug，但当前改动还不想提交，就用 `git stash` 先存起来。

### 7.3 如何回退已经 push 的提交
> 用 `git revert <commit-hash>`，它会生成一个新提交来撤销目标提交的改动，不会破坏历史。**千万不要用 `git reset --hard` + `git push --force`**，除非你非常清楚后果且团队同意。

### 7.4 cherry-pick 是什么
```bash
git cherry-pick <commit-hash>
```
> 把某个特定的提交"摘"到当前分支。场景：hotfix 分支修了一个 bug，想把这个修复也应用到 develop 分支，就可以 cherry-pick。

### 7.5 git reflog 的作用
```bash
git reflog
```
> reflog 记录了 HEAD 的所有移动历史，即使 `reset --hard` 丢失了提交，也能通过 reflog 找回。它是 Git 的"后悔药"。

### 7.6 .gitignore 的作用
```gitignore
# Python
__pycache__/
*.pyc
.env
venv/

# IDE
.idea/
.vscode/

# OS
.DS_Store
Thumbs.db
```
> 告诉 Git 哪些文件不需要追踪。常见的有编译产物、环境配置、IDE 配置、系统文件等。已经被 Git 追踪的文件加入 .gitignore 不会生效，需要先 `git rm --cached <file>`。

### 7.7 如何合并多个提交（squash）
```bash
# 交互式 rebase，合并最近 3 个提交
git rebase -i HEAD~3
# 在编辑器中把要合并的提交前面的 pick 改为 squash（或 s）
```
> **场景：** feature 分支开发过程中有很多零碎提交（"fix typo"、"wip"），合入主分支前用 squash 整理成一个有意义的提交。

---

## 8. 实用技巧

### 8.1 设置别名
```bash
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.lg "log --oneline --graph --all"
```

### 8.2 查看某行代码是谁写的
```bash
git blame <file>
```

### 8.3 查看两个分支的差异
```bash
git diff main..feature       # 查看差异
git log main..feature        # 查看 feature 有而 main 没有的提交
```

### 8.4 修改最近一次提交信息
```bash
git commit --amend -m "新的提交信息"
```
> 注意：如果已经 push 了，amend 后需要 force push，谨慎使用。

---

## 9. 面试加分项

### 9.1 Git 的存储原理（简要）
- Git 底层是一个**内容寻址的文件系统**
- 每个文件内容通过 SHA-1 哈希生成唯一标识
- 核心对象：**blob**（文件内容）、**tree**（目录结构）、**commit**（提交信息 + 指向 tree 的指针）
- 分支本质上就是一个指向 commit 的指针

### 9.2 大文件管理
```bash
# Git LFS（Large File Storage）
git lfs install
git lfs track "*.pth"    # 追踪 PyTorch 模型文件
git lfs track "*.h5"     # 追踪 Keras 模型文件
```
> **AI 方向加分：** 模型文件通常很大，不适合直接放 Git 仓库，应该用 Git LFS 或者专门的模型管理工具（MLflow、DVC）。

### 9.3 CI/CD 中的 Git
- Push 触发 CI 流水线（GitHub Actions / GitLab CI）
- PR 合并前自动跑测试、lint 检查
- 基于 tag 触发自动部署

> **面试回答模板：**
> 我们项目用 GitHub Actions 做 CI/CD，push 到 feature 分支会自动跑单元测试和代码检查，PR 合并到 main 后自动构建 Docker 镜像并部署到测试环境，打 tag 后触发生产环境部署。
