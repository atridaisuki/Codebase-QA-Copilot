# Linux 指令入门

这份笔记是给**零基础**准备的。

目标不是把 Linux 学全，而是先掌握：

1. 能看懂别人说的命令
2. 能自己在终端里完成基本操作
3. 能应对 Python 后端 + AI 岗常见面试问题
4. 能在服务器 / Docker / 项目环境里做基础排查

---

# 1. 先理解：什么是终端命令？

你平时在图形界面里点文件夹、点文件、点运行按钮。

而在 Linux 里，很多操作是通过**终端**完成的。你输入一行命令，系统就按你的要求执行。

比如：

```bash
pwd
```

这条命令的意思是：

- `pwd` = print working directory
- 查看“我当前所在的目录”

终端返回的可能是：

```bash
/home/user/project
```

意思就是：你现在正站在 `project` 这个目录里。

可以把终端理解成：

- 你在和操作系统“打字对话”
- 每条命令都是一个动作
- 目录就像文件夹
- 文件和 Windows / Mac 的文件本质差不多

---

# 2. 先学最基础的：目录和文件

这是最最常用的一组。

## 2.1 `pwd`：查看当前目录

```bash
pwd
```

作用：查看你当前所在的位置。

示例输出：

```bash
/home/admin/project
```

什么时候用：

- 不知道自己现在在哪
- 进入了很多层目录后想确认位置
- 面试里常作为入门问题

面试可能会问：

- `pwd` 是做什么的？

可以这样答：

> `pwd` 用来查看当前工作目录，也就是当前终端所在路径。

---

## 2.2 `ls`：查看当前目录下有什么

```bash
ls
```

作用：列出当前目录里的文件和文件夹。

例如：

```bash
app  tests  requirements.txt  Dockerfile
```

说明当前目录下有：

- `app` 文件夹
- `tests` 文件夹
- `requirements.txt` 文件
- `Dockerfile` 文件

### 常用变体

#### `ls -l`

```bash
ls -l
```

显示详细信息，比如：

- 文件权限
- 文件拥有者
- 文件大小
- 修改时间

#### `ls -a`

```bash
ls -a
```

显示隐藏文件。

Linux 中以 `.` 开头的文件通常是隐藏文件，比如：

- `.env`
- `.gitignore`
- `.venv`

#### `ls -la`

```bash
ls -la
```

这是最常用的写法之一：

- `-l`：详细信息
- `-a`：包含隐藏文件

面试常问：

- `ls` 是什么？
- `ls -l` 和 `ls -a` 的区别？

回答思路：

> `ls` 用来列出目录内容；`ls -l` 看详细信息，`ls -a` 显示隐藏文件，`ls -la` 是两者结合。

---

## 2.3 `cd`：切换目录

```bash
cd app
```

作用：进入 `app` 目录。

### 常见写法

#### 进入子目录

```bash
cd app
```

#### 回到上一级目录

```bash
cd ..
```

`..` 的意思是“上一级目录”。

#### 回到用户主目录

```bash
cd ~
```

`~` 表示当前用户的家目录。

#### 切到绝对路径

```bash
cd /home/admin/project
```

---

面试常问：

- `cd ..` 是什么意思？
- `cd ~` 是什么意思？

回答：

> `cd` 用来切换目录，`cd ..` 回到上一级，`cd ~` 回到当前用户主目录。

---

## 2.4 `mkdir`：创建目录

```bash
mkdir logs
```

作用：创建一个名为 `logs` 的目录。

### 常见写法

#### 创建多级目录

```bash
mkdir -p data/raw
```

`-p` 的作用是：

- 如果上层目录不存在，就一起创建
- 已存在也不会报错

---

## 2.5 `touch`：创建空文件

```bash
touch app.log
```

作用：创建一个空文件。

常用于：

- 临时建文件
- 模拟日志文件
- 测试脚本

---

## 2.6 `cp`：复制文件或目录

### 复制文件

```bash
cp a.txt b.txt
```

意思：把 `a.txt` 复制一份，命名为 `b.txt`。

### 复制目录

```bash
cp -r app backup_app
```

`-r` 表示递归复制目录。

---

## 2.7 `mv`：移动或重命名

### 重命名文件

```bash
mv old.txt new.txt
```

### 移动文件到目录

```bash
mv app.log logs/
```

作用：

- 可以移动文件
- 也可以重命名

---

## 2.8 `rm`：删除文件

```bash
rm app.log
```

作用：删除文件。

### 删除目录

```bash
rm -r logs
```

- `-r`：递归删除目录

### 强制删除

```bash
rm -rf logs
```

- `-f`：强制，不提示

注意：

`rm` 删除后一般**不能轻易恢复**。

所以你要先建立习惯：

- 先 `ls` 看清楚
- 再删除
- 不要乱用 `rm -rf`

面试里如果问到，可以体现安全意识：

> `rm -rf` 很危险，实际使用前我会先确认路径和内容，避免误删。

---

# 3. 看文件内容

开发时非常高频，尤其是看配置、看代码、看日志。

## 3.1 `cat`：直接输出整个文件

```bash
cat requirements.txt
```

作用：把文件内容全部打印出来。

适合：

- 小文件
- 配置文件
- 快速查看内容

不适合：

- 很大的日志文件
- 很长的代码文件

因为会一口气刷满终端。

---

## 3.2 `less`：分页查看文件

```bash
less app.log
```

作用：分页查看文件，适合大文件。

在 `less` 里常用操作：

- `j`：往下
- `k`：往上
- `/error`：搜索 `error`
- `q`：退出

这个命令比 `cat` 更适合看大日志。

---

## 3.3 `head`：看前几行

```bash
head app.log
```

默认看前 10 行。

也可以指定行数：

```bash
head -n 20 app.log
```

作用：

- 看文件开头
- 看 CSV / 日志 / 配置文件前几行

---

## 3.4 `tail`：看后几行

```bash
tail app.log
```

默认看最后 10 行。

指定行数：

```bash
tail -n 50 app.log
```

---

## 3.5 `tail -f`：实时看日志

```bash
tail -f app.log
```

这个命令非常重要。

作用：

- 持续监控文件末尾的新内容
- 日志一更新，终端就跟着显示

适合：

- 看服务启动日志
- 看接口请求日志
- 看报错日志

面试非常常见：

- 如何实时查看日志？

标准回答：

> 可以用 `tail -f app.log` 实时跟踪日志输出。

---

# 4. 搜索命令：开发排查必会

## 4.1 `grep`：搜索文件内容

这是最常见的文本搜索命令之一。

### 搜索关键字

```bash
grep "error" app.log
```

作用：从 `app.log` 中找出包含 `error` 的行。

### 忽略大小写

```bash
grep -i "error" app.log
```

可以匹配：

- `error`
- `Error`
- `ERROR`

### 递归搜索目录

```bash
grep -r "TODO" .
```

意思：在当前目录及其子目录中，搜索包含 `TODO` 的内容。

### 显示行号

```bash
grep -n "port" config.py
```

输出时会带行号，方便定位。

---

面试常问：

- 怎么在文件里搜某个关键字？
- 怎么在整个项目里找某个字符串？

回答：

> 可以用 `grep` 搜索文件内容，比如 `grep "error" app.log`，如果要递归搜索整个项目可以用 `grep -r "xxx" .`。

---

## 4.2 `find`：查找文件

按文件名搜索非常常见。

### 找 Python 文件

```bash
find . -name "*.py"
```

意思：在当前目录及其子目录中，查找所有 `.py` 文件。

### 找某个特定文件

```bash
find . -name "requirements.txt"
```

作用：找出叫 `requirements.txt` 的文件。

---

面试常问：

- 怎么找一个文件？

回答：

> 我会用 `find`，比如 `find . -name "*.py"` 查 Python 文件，或者 `find . -name "xxx"` 找指定文件。

---

# 5. 进程相关：服务排查高频

如果你做 Python 后端或 AI 服务，这一组很重要。

## 5.1 `ps`：查看进程

```bash
ps aux
```

作用：查看当前系统中的进程。

在开发中常这样配合用：

```bash
ps aux | grep python
```

意思：

- 先列出所有进程
- 再过滤出包含 `python` 的进程

可以用来判断：

- Python 服务有没有启动
- 某个脚本是否仍在运行
- 模型服务是否还活着

---

## 5.2 `kill`：结束进程

```bash
kill 12345
```

这里 `12345` 是进程号（PID）。

如果普通结束不行，有时会用：

```bash
kill -9 12345
```

但不要养成动不动就 `-9` 的习惯。

更好的理解是：

- `kill PID`：尝试正常结束
- `kill -9 PID`：强制结束

面试可能问：

- 如何结束一个进程？

回答：

> 先通过 `ps aux | grep python` 找到 PID，再用 `kill PID` 结束。如果进程无响应，再考虑 `kill -9 PID`。

---

# 6. 端口相关：后端面试很常见

后端服务通常会监听某个端口，比如：

- FastAPI：8000
- Flask：5000
- Jupyter：8888
- 模型服务：各种自定义端口

## 6.1 `ss -tuln`：查看监听端口

```bash
ss -tuln
```

作用：查看当前系统正在监听的端口。

你会看到类似：

```bash
LISTEN 0 128 0.0.0.0:8000
```

意思：8000 端口正在被某个服务监听。

---

## 6.2 `lsof -i :8000`：查看是谁占用了端口

```bash
lsof -i :8000
```

作用：查看哪个进程占用了 8000 端口。

这在面试里很高频。

回答示例：

> 如果 8000 端口被占用，我会先用 `lsof -i :8000` 或 `ss -tuln` 查看，再找到对应进程并处理。

---

# 7. 网络相关：最常用的是 `curl`

## 7.1 `curl`：发 HTTP 请求

```bash
curl http://localhost:8000
```

作用：向一个 URL 发请求。

这对后端和 AI 应用都很常用，因为你经常要测试：

- 服务是否启动成功
- API 是否通
- 接口返回什么内容

### 请求接口示例

```bash
curl http://127.0.0.1:8000/health
```

如果接口健康，可能返回：

```json
{"status":"ok"}
```

### 发送 POST 请求

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"hello"}'
```

这是稍微进阶一点的用法。

面试里通常不一定让你手写完整参数，但要知道 `curl` 是干什么的。

---

# 8. 环境变量：Python / AI 很重要

很多项目不会把密钥直接写进代码，而是用环境变量。

## 8.1 `env`：查看环境变量

```bash
env
```

作用：列出当前环境变量。

---

## 8.2 `export`：设置环境变量

```bash
export API_KEY=abc123
```

作用：设置一个环境变量。

比如启动 Python 服务前：

```bash
export OPENAI_API_KEY=xxxxx
python app.py
```

或者：

```bash
export DATABASE_URL=postgresql://...
uvicorn app.main:app --reload
```

面试高频：

- 环境变量怎么设置？

回答：

> 在 shell 里可以用 `export 变量名=值` 设置环境变量，比如 `export API_KEY=xxx`。

---

# 9. 权限相关

## 9.1 `chmod`：修改权限

最常见的是给脚本加执行权限。

```bash
chmod +x run.sh
```

作用：让 `run.sh` 可以直接执行。

例如：

```bash
./run.sh
```

如果没有执行权限，可能跑不起来。

面试里一般不会深挖权限位，但至少知道：

- `chmod` 是改权限
- `+x` 是加执行权限

---

## 9.2 `sudo`：以管理员权限执行

```bash
sudo apt update
```

作用：用更高权限执行命令。

常见于：

- 安装软件
- 修改系统配置
- 某些目录权限不足时

面试只要知道它的概念即可，不需要展开很多。

---

# 10. 压缩和解压

## 10.1 `tar -xzf`：解压 `.tar.gz`

```bash
tar -xzf file.tar.gz
```

作用：解压压缩包。

## 10.2 `tar -czf`：打包压缩

```bash
tar -czf backup.tar.gz app/
```

作用：把 `app/` 压缩成 `backup.tar.gz`。

在部署、传文件、下载数据包时比较常见。

---

# 11. 后台运行：AI 训练 / 服务部署会用到

## 11.1 `nohup`

如果你关掉终端后，还希望程序继续跑，可以用：

```bash
nohup python app.py &
```

解释：

- `nohup`：终端关闭后程序继续运行
- `&`：放到后台运行

输出通常会写到 `nohup.out`。

适合：

- 长时间训练脚本
- 后台启动服务
- 临时在服务器上跑任务

面试里如果是 AI 岗，这个有可能会问到。

---

# 12. 日志、管道、重定向：终端思维的关键

这一部分不是“某一个命令”，但很重要。

## 12.1 管道 `|`

管道的意思是：

- 把左边命令的输出
- 交给右边命令继续处理

例如：

```bash
ps aux | grep python
```

意思：

- `ps aux` 输出所有进程
- `grep python` 从中筛出包含 python 的行

这是非常非常高频的用法。

---

## 12.2 重定向 `>`

```bash
python app.py > output.log
```

意思：

- 把原本打印到终端的内容
- 写入 `output.log`

注意：

- `>`：覆盖写入
- `>>`：追加写入

例如：

```bash
echo "new line" >> app.log
```

---

# 13. Python 后端 + AI 最常见组合场景

下面是最值得你记住的实战场景。

## 场景 1：看项目目录

```bash
pwd
ls -la
```

作用：

- 看自己在哪
- 看当前目录有什么

---

## 场景 2：进入项目并启动服务

```bash
cd project
python app.py
```

或者：

```bash
uvicorn app.main:app --reload
```

---

## 场景 3：查看配置文件

```bash
cat requirements.txt
less .env
```

---

## 场景 4：查看日志

```bash
tail -f app.log
```

---

## 场景 5：搜索错误信息

```bash
grep -i "error" app.log
```

---

## 场景 6：查 Python 服务是否在运行

```bash
ps aux | grep python
```

---

## 场景 7：查端口被谁占用

```bash
lsof -i :8000
```

---

## 场景 8：结束异常进程

```bash
kill PID
```

---

## 场景 9：测试接口

```bash
curl http://127.0.0.1:8000/health
```

---

## 场景 10：设置环境变量再启动服务

```bash
export API_KEY=xxxx
python app.py
```

---

# 14. 面试最常问的命令总结

下面这些是你最该掌握的。

## 第一梯队：一定要会

```bash
pwd
ls
ls -la
cd
cat
less
head
tail
tail -f
grep
find
ps aux
kill
curl
env
export
chmod +x
```

## 第二梯队：后端更常见

```bash
ss -tuln
lsof -i :8000
nohup python app.py &
tar -xzf file.tar.gz
```

## 第三梯队：知道即可

```bash
sudo
cp -r
mv
rm -r
mkdir -p
```

---

# 15. 面试回答不要只背定义，要带场景

比如面试官问：

## 问：你用过 `grep` 吗？

不推荐只答：

> 用过，是搜索字符串。

更好答法：

> 用过，我常用 `grep` 搜索日志里的错误关键字，比如 `grep -i "error" app.log`，也会用 `grep -r` 在项目里搜配置项或某段代码。

---

## 问：怎么实时看日志？

答：

> 我会用 `tail -f app.log` 持续跟踪日志输出，如果要定位错误，也会结合 `grep` 过滤关键字。

---

## 问：端口被占用了怎么办？

答：

> 我会先用 `lsof -i :8000` 或 `ss -tuln` 看哪个进程占用了端口，再决定是否结束旧进程或者换端口重新启动服务。

---

# 16. 给零基础的学习顺序

不要一口气全背，建议按顺序来。

## 第 1 步：先学目录和文件

先熟练这些：

```bash
pwd
ls
ls -la
cd
mkdir
touch
cp
mv
rm
```

目标：

- 能在终端里像用文件管理器一样操作文件

---

## 第 2 步：学会看文件

```bash
cat
less
head
tail
tail -f
```

目标：

- 能看配置文件
- 能看代码片段
- 能看日志

---

## 第 3 步：学搜索

```bash
grep
find
```

目标：

- 能找文件
- 能找报错
- 能搜项目里的关键词

---

## 第 4 步：学服务排查

```bash
ps aux
kill
ss -tuln
lsof -i :8000
curl
```

目标：

- 知道服务在不在
- 知道端口占用情况
- 知道接口通不通

---

## 第 5 步：学环境和后台运行

```bash
env
export
nohup python app.py &
chmod +x run.sh
```

目标：

- 会设置环境变量
- 会让程序后台运行
- 会处理基本脚本权限问题

---

# 17. 给你的面试准备建议

如果你现在基础弱，不要焦虑。

对 Python 后端 + AI 来说，你先把下面这些练熟，就已经比很多只会背八股的人更实用：

```bash
pwd
ls -la
cd
cat
less
tail -f
grep
find
ps aux | grep python
kill PID
lsof -i :8000
curl http://127.0.0.1:8000/health
export API_KEY=xxx
nohup python app.py &
chmod +x run.sh
```

建议练法：

1. 自己开一个测试目录
2. 用这些命令操作几次
3. 启一个简单的 FastAPI 或 Flask 项目
4. 自己看日志、查进程、查端口、用 curl 调接口

这样比单纯背命令有效得多。

---

# 18. 最后的小结

你不需要一开始就学很深。

对面试来说，先掌握下面这条主线：

- 会进目录：`cd`
- 会看文件：`cat` / `less`
- 会看日志：`tail -f`
- 会搜索：`grep` / `find`
- 会查服务：`ps` / `kill`
- 会查端口：`lsof` / `ss`
- 会测接口：`curl`
- 会配环境：`export`

这已经足够应对大部分 Python 后端 + AI 岗的 Linux 基础问题。

如果后面你继续学 Docker、部署、GPU、训练脚本，这些命令会自然串起来。
