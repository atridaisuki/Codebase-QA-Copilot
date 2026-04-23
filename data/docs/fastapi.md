# FastAPI 面试知识回顾

## 1. FastAPI 是什么

- 基于 Python 3.7+ 的现代高性能 Web 框架
- 底层基于 Starlette（Web 部分）和 Pydantic（数据校验部分）
- 原生支持 async/await 异步编程
- 自动生成 OpenAPI (Swagger) 和 ReDoc 交互式文档

## 2. 核心特性

| 特性 | 说明 |
|------|------|
| 类型提示驱动 | 利用 Python type hints 自动完成参数校验、序列化、文档生成 |
| 高性能 | 性能与 Node.js / Go 同级，得益于 Starlette + uvicorn (ASGI) |
| 自动文档 | 访问 `/docs`（Swagger UI）和 `/redoc` 即可查看 API 文档 |
| 依赖注入 | 内置强大的 Depends 依赖注入系统 |
| 数据校验 | 基于 Pydantic，请求/响应自动校验并给出清晰错误信息 |

## 3. 基础用法

### 3.1 最小应用

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

启动：`uvicorn main:app --reload`

### 3.2 路径参数与查询参数

```python
# 路径参数 — 自动校验类型
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

- 路径参数：URL 路径中的 `{item_id}`，必填
- 查询参数：有默认值的函数参数，如 `q`，选填

### 3.3 请求体 (Pydantic Model)

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    description: str | None = None

@app.post("/items/")
async def create_item(item: Item):
    return item
```

## 4. 依赖注入 (Depends)

FastAPI 最强大的设计之一，用于复用逻辑、权限校验、数据库会话管理等。

```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db          # yield 之前是"请求前"，之后是"请求后"清理
    finally:
        db.close()

@app.get("/users/")
async def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

- `Depends` 支持嵌套：依赖可以依赖其他依赖
- 可用于全局（`app = FastAPI(dependencies=[Depends(verify_token)])`）

## 5. 中间件 (Middleware)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    import time
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start)
    return response
```

## 6. 异步与同步

```python
# 异步路由 — 适合 I/O 密集型（数据库、HTTP 请求）
@app.get("/async")
async def async_endpoint():
    data = await some_async_io()
    return data

# 同步路由 — FastAPI 会自动放到线程池执行，不会阻塞事件循环
@app.get("/sync")
def sync_endpoint():
    data = some_blocking_io()
    return data
```

关键点：
- 如果函数内没有 await 操作，用 `def` 即可，FastAPI 自动处理
- 如果用了 `async def` 但内部调用了阻塞操作，会阻塞整个事件循环

## 7. 响应模型与状态码

```python
from fastapi import status

class ItemOut(BaseModel):
    name: str
    price: float
    # 不暴露内部字段如 internal_code

@app.post("/items/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    return item  # 自动过滤掉 response_model 中没有的字段
```

## 8. 异常处理

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]

# 自定义全局异常处理
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})
```

## 9. 后台任务 (BackgroundTasks)

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # 耗时操作
    ...

@app.post("/notify/")
async def notify(bg: BackgroundTasks):
    bg.add_task(send_email, "user@example.com", "Hello")
    return {"message": "通知已发送"}  # 立即返回，邮件在后台发
```

## 10. 生命周期事件 (Lifespan)

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    db_pool = await create_pool()
    yield {"db": db_pool}
    # 关闭时执行
    await db_pool.close()

app = FastAPI(lifespan=lifespan)
```

## 11. 常见面试问题

**Q: FastAPI 和 Flask 的区别？**
- FastAPI 原生异步，Flask 默认同步
- FastAPI 自动数据校验和文档生成，Flask 需要额外扩展
- FastAPI 性能更高（ASGI vs WSGI）
- Flask 生态更成熟，社区更大

**Q: ASGI 和 WSGI 的区别？**
- WSGI：同步协议，一个请求占一个线程
- ASGI：异步协议，支持 WebSocket、HTTP/2、长连接，单线程可处理大量并发

**Q: Pydantic v1 vs v2？**
- v2 用 Rust 重写核心，性能提升 5-50 倍
- `from_orm` → `model_validate`，`dict()` → `model_dump()`
- FastAPI 0.100+ 支持 Pydantic v2

**Q: 如何部署 FastAPI？**
- 开发：`uvicorn main:app --reload`
- 生产：`gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
- 容器化：Dockerfile + uvicorn，配合 Nginx 反向代理
