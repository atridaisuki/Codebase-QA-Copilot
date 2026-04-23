这里为你整理并排版好了这份《Docker 面试知识点速记》，使用了 Markdown 的层级标题、代码块、引用和加粗等语法，阅读体验非常棒，非常适合直接导出为 PDF 或导入到 Notion/Typora 中背诵复习：

---

# Docker 面试知识点速记（Python 后端 + AI 方向）

## 1. Docker 是什么

### 1.1 一句话理解
Docker 是一种容器化技术，可以把应用及其运行环境一起打包，保证**“开发环境能跑，测试环境也能跑，线上也能跑”**。

### 1.2 它解决什么问题
**传统开发常见问题：**
- 我电脑能跑，你电脑跑不了
- Python 版本不一致
- 依赖包冲突
- 部署机器环境不一致
- 服务太多，手工启动麻烦

**Docker 的核心价值：**
- 环境一致性
- 交付标准化
- 部署方便
- 隔离性更好
- 资源利用率高于虚拟机

---

## 2. Docker 和虚拟机的区别

### 2.1 虚拟机
- 在宿主机上虚拟出完整操作系统
- 每个虚拟机都有自己的 OS、内核的一套抽象层
- 比较重，启动慢，占资源多

### 2.2 容器
- 共享宿主机内核
- 只隔离进程、网络、文件系统等运行环境
- 更轻量，启动更快

### 2.3 面试答法
> **面试回答模板：**
> Docker 容器不是完整虚拟机，它本质上是宿主机上的一个被隔离的进程组。相比 VM，它更轻量、启动更快、资源占用更少，但隔离强度通常弱于完整虚拟机。

---

## 3. Docker 核心概念

### 3.1 镜像（Image）
镜像可以理解为：
- 容器的“模板”
- 一个只读的文件层集合
- 包含应用运行所需的代码、依赖、环境

**例如：** `python:3.11-slim`, `nginx:latest`, `postgres:16`

> **面试常问：镜像和容器的关系是什么？**
> **回答：** 镜像是静态模板，容器是镜像启动后的运行实例。类比于面向对象编程，镜像像“类”，容器像“对象”。

### 3.2 容器（Container）
容器是：
- 镜像运行起来后的实例
- 有自己的进程、网络空间、文件系统视图
- 但共享宿主机内核

**特点：** 可以启动、停止、删除；默认是临时的，容器内部改动如果不做持久化，删除后会丢失。

### 3.3 仓库（Registry）
存放镜像的地方。
**常见：** Docker Hub, 阿里云镜像仓库, Harbor, AWS ECR, GCP Artifact Registry。
**常见命令：**
```bash
docker pull python:3.11-slim
docker push yourname/yourimage:1.0
```

### 3.4 Dockerfile
构建镜像的脚本。你不会自己写 Docker，通常就是指不会写 Dockerfile。
它定义：基础镜像、工作目录、复制文件、安装依赖、暴露端口、启动命令。

### 3.5 Volume（卷）
卷用于**持久化数据**。因为容器删除后，内部数据可能丢失，所以数据库、上传文件、缓存目录等通常需要挂载卷。
**典型用途：** MySQL/PostgreSQL 数据目录、Redis 持久化文件、模型文件目录、日志目录。

### 3.6 Network（网络）
容器之间通信依赖 Docker 网络。
**例如：** web 容器访问 db 容器，可以直接通过服务名访问：`db:5432`。Compose 启动的服务默认就在同一个网络里。

---

## 4. Docker 常用命令

### 4.1 查看信息
```bash
docker --version
docker info
docker images
docker ps
docker ps -a
```

### 4.2 拉取和构建镜像
```bash
docker pull python:3.11-slim
docker build -t myapp:1.0 .
```

### 4.3 运行容器
```bash
docker run -d -p 8000:8000 --name myapp myapp:1.0
```
**常见参数：**
- `-d`：后台运行
- `-p`：主机端口:容器端口
- `--name`：容器名
- `-e`：环境变量
- `-v`：挂载卷
- `--rm`：退出后自动删除

### 4.4 查看日志
```bash
docker logs container_name
docker logs -f container_name  # 持续跟踪日志
```

### 4.5 进入容器
```bash
docker exec -it container_name /bin/bash
# 如果没有 bash，可以用 sh：
docker exec -it container_name /bin/sh
```

### 4.6 停止/删除
```bash
docker stop container_name
docker rm container_name
docker rmi image_name
```

---

## 5. Dockerfile 核心语法 (最重要的部分)

### 5.1 FROM
指定基础镜像。
```dockerfile
FROM python:3.11-slim
```
> **面试点：为什么常用 slim？不总是用 alpine？**
> **回答：** `slim` 体积更小、拉取更快且安全面更小。不总是用 `alpine` 是因为 `alpine` 虽小，但在安装某些 Python 包、C 扩展、AI 依赖时容易出问题，编译极其麻烦。

### 5.2 WORKDIR
设置工作目录。之后的命令默认在 `/app` 下执行。
```dockerfile
WORKDIR /app
```

### 5.3 COPY
复制文件到镜像中。
```dockerfile
COPY requirements.txt .
COPY . .
```
*注意：`COPY . .` 会把当前目录全部复制进去，如果没有 `.dockerignore`，会把很多不该复制的东西带进去。*

### 5.4 RUN
构建镜像时执行命令。
```dockerfile
RUN pip install -r requirements.txt
```

### 5.5 CMD
指定容器启动时**默认执行**的命令。
```dockerfile
CMD ["python", "app.py"]
```
*注意：一个 Dockerfile 通常只有一个最终生效的 CMD，且可被 `docker run` 的参数覆盖。*

### 5.6 ENTRYPOINT
定义容器主入口。
```dockerfile
ENTRYPOINT ["python"]
CMD ["app.py"]
```
> **面试常问：CMD 和 ENTRYPOINT 区别？**
> **回答：** `CMD` 是默认命令/参数，容易被运行时覆盖；`ENTRYPOINT` 是固定入口，通常不轻易被替换。两者经常组合使用。

### 5.7 EXPOSE
声明容器监听的端口（只是文档性声明，真正的端口映射还是靠 `-p`）。
```dockerfile
EXPOSE 8000
```

### 5.8 ENV
设置环境变量。
```dockerfile
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
```
*Python 常见设置：`PYTHONUNBUFFERED=1` (日志实时输出)；`PYTHONDONTWRITEBYTECODE=1` (不生成 `.pyc` 文件)*

---

## 6. Python 后端项目的标准 Dockerfile (以 FastAPI 为例)

```dockerfile
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 面试高频点：为什么要先 copy requirements.txt，再 copy 全部代码？
**这是 Docker 构建优化的经典点！**
如果写成：
```dockerfile
COPY . .
RUN pip install -r requirements.txt
```
每次哪怕只改了一行业务代码，都会导致依赖层缓存失效，重新下载安装所有依赖，构建极慢。
**优化写法：** 先 COPY `requirements.txt` 并安装依赖。这样只有依赖变更时，才会重新安装依赖，极大利用了 Docker 的**分层缓存机制**。

---

## 7. .dockerignore 是什么

类似 `.gitignore`，告诉 Docker 构建镜像时**不要复制**哪些文件。
**示例：**
```text
__pycache__/
*.pyc
.git/
.venv/
logs/
data/
*.ipynb_checkpoints
```
> **面试答法：** `.dockerignore` 的作用是减少构建上下文体积、提升构建效率，并避免把本地虚拟环境、无关或敏感文件（如日志、大模型权重）复制进镜像。

---

## 8. Docker 镜像分层和缓存机制

- **分层：** Dockerfile 中的指令（如 COPY, RUN）一般都会形成独立的文件层。
- **缓存：** 构建时会复用没变化的层。顺序很重要：**不常变化的步骤放前面，经常变化的步骤放后面**。

---

## 9. 容器端口映射

### EXPOSE 和 -p 的区别
- `EXPOSE 8000`：只是声明容器内部服务使用 8000 端口。
- `docker run -p 8080:8000`：真正把**宿主机**的 `8080` 端口映射/转发到**容器**的 `8000` 端口。

---

## 10. 数据持久化：Volume 和 Bind Mount

### 10.1 Bind Mount (绑定挂载)
把宿主机绝对路径直接挂载到容器。如：`-v ./app:/app`
**适合：** 本地开发热更新、挂载代码目录、快速调试。

### 10.2 Volume (数据卷)
由 Docker 统一管理的数据卷。如：`-v postgres_data:/var/lib/postgresql/data`
**适合：** 数据库存储、正式环境持久化。

> **面试回答：** Bind mount 强依赖宿主机目录结构，更适合开发时映射本地代码目录；Volume 由 Docker 托管，可移植性更好，适合数据库等需要稳定持久化的数据。

---

## 11. Docker 网络基础 (高频避坑点)

在 `docker-compose.yml` 中启动的服务，Docker 默认会创建同一个网络。同一网络下，服务之间可以直接通过**服务名**访问。

> **🔥 面试/实战巨坑：为什么容器里不能用 localhost 连另一个容器？**
> **原因：** `localhost` 指的是**当前容器自己**，不是宿主机，也不是别的容器！
> **例如：** 在 web 容器里写 `localhost:5432` 指的是 web 容器自己的 5432 端口。要访问数据库容器，必须写 `db:5432`（假设数据库服务名叫 db）。

---

## 12. Docker Compose 是什么

Docker Compose 用于**定义和运行多个关联容器（多容器编排）**。
**典型场景：** 一个 Python Web 服务 + 一个 PostgreSQL + 一个 Redis + 一个 Celery Worker，全在一个 `compose.yml` 里定义并一键启动。

---

## 13. docker-compose.yml 核心结构示例

```yaml
version: "3.9"

services:
  web:
    build: .
    container_name: fastapi_app
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/mydb
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    container_name: postgres_db
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7

volumes:
  postgres_data:
```

### Compose 关键字段理解：
- `services`: 定义所有服务（容器）。
- `build`: 根据当前目录 Dockerfile 构建镜像。
- `image`: 直接使用已有镜像。
- `ports`: 端口映射。
- `volumes`: 挂载卷。
- `environment`: 注入环境变量。
- `depends_on`: 声明启动顺序依赖。（**注意：只保证启动顺序，不保证服务已经完全 ready 可用！**）

### Compose 常用命令 (新版推荐使用 `docker compose`)
```bash
docker compose up -d    # 后台启动所有服务
docker compose down     # 停止并删除容器和网络
docker compose build    # 重新构建镜像
docker compose logs -f web  # 跟踪 web 服务的日志
```

---

## 14. 开发环境和生产环境的区别

> **面试回答模板：**
> **开发环境**更强调调试效率，通常会使用 Bind Mount 挂载源码，并开启热更新（reload），日志级别更详细。
> **生产环境**更强调稳定性和可复制部署，通常直接运行构建好的、包含完整代码的镜像，不依赖本地文件挂载。通常会使用 gunicorn 等生产级 WSGI/ASGI 服务器，并配置健康检查、重启策略和资源限制。

---

## 15. Python 项目 Dockerfile 最佳实践

1. **选择合适基础镜像**：用 `slim`，指定具体版本（避开 `latest`）。
2. **利用缓存优化构建**：先 COPY 依赖文件，安装后再 COPY 业务代码。
3. **使用 `.dockerignore`**：避免拷贝 `.git`、大模型、虚拟环境。
4. **不要把密钥写进镜像**：通过环境变量或 Secret 管理系统注入。
5. **一个容器只做一件事**：别把 Web、DB、Redis 全塞进一个容器。
6. **尽量使用非 root 用户**：更安全（`USER appuser`）。

---

## 16. 多阶段构建（Multi-stage build）

**作用：** 减少最终镜像大小。前一个阶段编译/构建，后一个阶段只复制运行所需产物。

```dockerfile
# 阶段 1：Builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# 阶段 2：Runner
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
CMD ["python", "app.py"]
```
> **面试说法：** 多阶段构建可以把构建依赖（如 C 编译器）和运行环境分离，显著减少最终镜像体积，同时降低安全攻击面。

---

## 17. AI 项目中的 Docker 特殊点（AI 后端必看）

1. **镜像极大：** 包含 PyTorch, CUDA, Transformers 等。需特别注意依赖拆分和镜像层缓存。
2. **大模型文件处理：** 绝不建议把大模型权重（`.bin` / `.safetensors`）直接打进镜像。推荐：
   - 启动后下载
   - 挂载宿主机模型目录（`volumes: - ./models:/models`）
   - 单独做模型缓存卷
3. **GPU 容器：** Docker 本身不提供计算能力，需宿主机装 NVIDIA 驱动 + `NVIDIA Container Toolkit`，暴露 GPU 给容器。
4. **服务分层：** AI 系统常拆分为 API 服务、推理服务、MQ/Redis、向量数据库（Milvus）、Worker 异步任务池。

---

## 18. 容器启动失败怎么排查？（实战高频）

**第一步永远是：** `docker logs container_name`

**标准排查流程（面试答法）：**
1. `docker ps -a` 看容器状态（Exited 还是 Up）。
2. `docker logs` 看报错信息。
3. 如果容器没挂，用 `docker exec -it` 进入容器检查文件和环境。
4. 检查端口映射是否冲突（`Bind for 0.0.0.0:8000 failed`）。
5. 检查环境变量、挂载目录（是否把镜像内代码覆盖空了）。
6. 检查服务间网络（数据库主机名是否写错，是否连到了 `localhost`）。

---

## 19. 两个致命的常见 Bug 坑

### 坑 1：为什么容器启动了但服务访问不到？
如果你的代码写的是：`uvicorn main:app --host 127.0.0.1 --port 8000`
**错误原因：** 这样只能在容器内部访问。
**正确做法：** 必须改成 `--host 0.0.0.0`，才能通过端口映射暴露给宿主机！

### 坑 2：Compose 中 depends_on 的坑
很多人以为 `depends_on: - db` 意味着 web 服务一定能连上 db。
**错误原因：** 它只保证 db 容器先启动，**不保证数据库进程已经 ready 准备好接受连接**。
**解决思路：** 数据库通常加载较慢，需要配合 Docker 健康检查（Healthcheck）或应用代码层面的重试机制。

---

## 20. 典型面试题与标准回答速记

**Q1：Docker 镜像和容器的区别？**
> 答：镜像是静态模板，包含应用和运行环境；容器是镜像运行后的实例。一个镜像可以启动多个容器。

**Q2：Docker 和虚拟机有什么区别？**
> 答：虚拟机会虚拟出完整操作系统，资源更重；Docker 容器共享宿主机内核，更轻量、启动更快，但隔离粒度弱于 VM。

**Q3：为什么 Dockerfile 里先复制 requirements.txt？**
> 答：为了利用 Docker 缓存机制。这样只有依赖文件变化时才重新安装依赖，改动业务代码不会导致每次都重新 pip install。

**Q4：为什么容器里访问数据库不能写 localhost？**
> 答：因为容器内的 localhost 指的是当前容器自己，不是数据库容器。应该通过 Docker 网络中的服务名访问（如 db:5432）。

**Q5：为什么 FastAPI/Flask 在 Docker 里要监听 0.0.0.0？**
> 答：因为如果只监听 127.0.0.1，服务只能被容器内部访问；监听 0.0.0.0 才能绑定所有网卡，从而通过端口映射被外部宿主机访问。

**Q6：生产环境为什么不建议直接挂载源码（Bind Mount）？**
> 答：因为生产环境强调“镜像不可变性”和部署一致性，挂载本地源码会引入宿主机差异，导致部署状态不可控。

**Q7：AI 项目 Docker 化时有什么额外注意点？**
> 答：主要是镜像大、依赖复杂、模型权重巨大且通常需要 GPU。需要优化层缓存，避免把大模型权重打进镜像（应通过挂载注入），并配置 GPU Runtime 运行环境。

---

## 21. 记忆版超简短口诀

*   **Docker 核心四件套：** 镜像（模板）、容器（实例）、网络（服务互联）、卷（数据持久化）。
*   **Dockerfile 核心五步：** FROM -> WORKDIR -> COPY -> RUN -> CMD。
*   **Compose 核心五项：** services, build/image, ports, volumes, environment。
*   **高频避坑三件套：** 别写 localhost、后端监听 0.0.0.0、depends_on 不等于 ready。