# Python 面向对象基础

## 1. 一切皆对象

Python 中**所有东西都是对象**——int、str、list、函数、类本身、模块，全部都是对象。这是理解 Python 的起点。

```python
# 函数是对象，可以赋值给变量、传参、放进列表
def greet(name):
    return f"hello {name}"

fn = greet          # 函数赋值给变量
fn("world")         # "hello world"

funcs = [greet, len, print]  # 函数放进列表
funcs[0]("test")             # "hello test"

# 类也是对象
class Dog:
    pass

cls = Dog           # 类赋值给变量
obj = cls()         # 等价于 Dog()
```

这就是你说的"什么都能当右值"——因为一切都是对象，自然可以赋值、传参、返回。

## 2. 类与实例

```python
class AgentService:                    # 定义类
    max_retries = 3                    # 类属性：所有实例共享

    def __init__(self):                # 初始化方法（不是构造函数）
        self.client = None             # 实例属性：每个实例独立
        self.settings = get_settings()

    def chat(self, message):           # 实例方法
        ...

service = AgentService()   # 创建实例，自动调用 __init__
service.chat("hello")      # 调用实例方法，Python 自动把 service 传给 self
```

### self 是什么

`self` 不是关键字，只是约定俗成的名字。它就是实例本身。

```python
service.chat("hello")
# 等价于
AgentService.chat(service, "hello")
```

Python 在调用实例方法时，自动把实例作为第一个参数传进去。所以 `self.client` 就是"这个实例的 client 属性"。

### 类属性 vs 实例属性

```python
class Config:
    default_timeout = 30       # 类属性，定义在类体里

    def __init__(self, timeout=None):
        self.timeout = timeout or self.default_timeout  # 实例属性，定义在 __init__ 里

a = Config()
b = Config(60)
a.timeout          # 30（用了类属性的默认值）
b.timeout          # 60
Config.default_timeout  # 30（通过类访问）
```

关键区别：
- 类属性：所有实例共享同一份，通过 `类名.属性` 或 `self.属性` 访问
- 实例属性：每个实例独立一份，只能通过 `self.属性` 访问
- 如果实例属性和类属性同名，实例属性会**遮蔽**类属性

### `__init__` 不是构造函数

严格来说，`__new__` 才是构造函数（创建实例），`__init__` 是初始化函数（给实例设置属性）。99% 的情况你只需要写 `__init__`。

```python
obj = MyClass()
# 实际执行顺序：
# 1. MyClass.__new__(MyClass)  → 创建空实例
# 2. MyClass.__init__(obj)     → 初始化实例属性
```

## 3. 继承

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError

class Dog(Animal):                  # Dog 继承 Animal
    def speak(self):                # 重写父类方法
        return f"{self.name}: 汪汪"

class Cat(Animal):
    def speak(self):
        return f"{self.name}: 喵喵"

dog = Dog("旺财")
dog.speak()    # "旺财: 汪汪"
dog.name       # "旺财"  ← 继承了 Animal 的 __init__
```

### super() — 调用父类方法

```python
class Puppy(Dog):
    def __init__(self, name, toy):
        super().__init__(name)      # 调用 Dog（实际是 Animal）的 __init__
        self.toy = toy

    def speak(self):
        base = super().speak()      # 调用 Dog 的 speak
        return f"{base}（叼着{self.toy}）"
```

### 多重继承与 MRO

```python
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return "B"

class C(A):
    def method(self):
        return "C"

class D(B, C):      # 多重继承
    pass

D().method()        # "B"
D.__mro__           # (D, B, C, A, object) — 方法解析顺序
```

Python 用 C3 线性化算法确定 MRO，`super()` 按 MRO 顺序查找，不是简单地"调父类"。

## 4. 魔术方法（Dunder Methods）

双下划线方法让你的类能融入 Python 的语法体系。

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):             # repr(obj) 或在终端直接打印
        return f"Vector({self.x}, {self.y})"

    def __str__(self):              # str(obj) 或 print(obj)
        return f"({self.x}, {self.y})"

    def __add__(self, other):       # v1 + v2
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other):        # v1 == v2
        return self.x == other.x and self.y == other.y

    def __len__(self):              # len(obj)
        return 2

    def __getitem__(self, index):   # obj[0], obj[1]
        return (self.x, self.y)[index]

    def __iter__(self):             # for i in obj
        yield self.x
        yield self.y

    def __bool__(self):             # if obj:
        return self.x != 0 or self.y != 0
```

常用魔术方法速查：

| 方法 | 触发方式 | 用途 |
|------|---------|------|
| `__init__` | `MyClass()` | 初始化 |
| `__repr__` | `repr(obj)` | 开发者友好的字符串表示 |
| `__str__` | `str(obj)`, `print(obj)` | 用户友好的字符串表示 |
| `__len__` | `len(obj)` | 长度 |
| `__getitem__` | `obj[key]` | 下标访问 |
| `__setitem__` | `obj[key] = val` | 下标赋值 |
| `__contains__` | `x in obj` | 成员检测 |
| `__call__` | `obj()` | 让实例可调用 |
| `__enter__/__exit__` | `with obj:` | 上下文管理器 |
| `__iter__/__next__` | `for x in obj:` | 迭代器协议 |

### `__call__` — 让实例像函数一样调用

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, x):
        return x * self.factor

double = Multiplier(2)
double(5)       # 10  ← 实例当函数用
double(100)     # 200
```

## 5. 装饰器相关

### @property — 把方法伪装成属性

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius       # 约定：下划线前缀表示"内部使用"

    @property
    def radius(self):               # 读取：circle.radius
        return self._radius

    @radius.setter
    def radius(self, value):        # 赋值：circle.radius = 5
        if value < 0:
            raise ValueError("半径不能为负")
        self._radius = value

    @property
    def area(self):                 # 只读属性（没有 setter）
        return 3.14159 * self._radius ** 2

c = Circle(3)
c.radius        # 3（调用 getter）
c.radius = 5    # （调用 setter）
c.area          # 78.5（计算属性，不能赋值）
```

### @staticmethod 和 @classmethod

```python
class MathUtils:
    pi = 3.14159

    @staticmethod
    def add(a, b):              # 不需要 self 或 cls，就是个普通函数挂在类上
        return a + b

    @classmethod
    def circle_area(cls, r):    # 第一个参数是类本身，不是实例
        return cls.pi * r ** 2  # 通过 cls 访问类属性

MathUtils.add(1, 2)            # 3
MathUtils.circle_area(5)       # 78.5
```

项目中的实际例子（agent_service.py）：

```python
class AgentService:
    @staticmethod
    def _extract_text(content: list[Any]) -> str:
        # 不需要访问 self 的任何属性，所以用 staticmethod
        texts = [block.text for block in content if block.type == "text"]
        return "\n".join(texts).strip()

    @staticmethod
    def _dedupe_sources(source_dicts: list[dict]) -> list[SourceItem]:
        # 同理，纯工具函数，不依赖实例状态
        seen = set()
        ...
```

什么时候用哪个：
- `def method(self)` — 需要访问实例属性
- `@classmethod` — 需要访问类属性，或作为替代构造函数
- `@staticmethod` — 不需要访问实例或类，只是逻辑上属于这个类

## 6. 鸭子类型与协议

Python 不关心对象的类型，只关心它有没有需要的方法/属性。

```python
# 这三个完全不同的类，都能被 for 循环遍历，因为都实现了 __iter__
class MyList:
    def __iter__(self):
        yield 1; yield 2; yield 3

class MyRange:
    def __iter__(self):
        return iter(range(5))

class MyFile:
    def __iter__(self):
        yield "line1"; yield "line2"

for x in MyList(): print(x)    # 都能用
for x in MyRange(): print(x)
for x in MyFile(): print(x)
```

这就是"鸭子类型"——如果它走起来像鸭子、叫起来像鸭子，那它就是鸭子。不需要继承同一个基类，只要有对应的方法就行。

项目中的例子：`chat_stream()` 返回的是 `Generator`，FastAPI 的 `EventSourceResponse` 只要求传入一个可迭代对象——它不关心你传的是 generator、list 还是自定义类，只要能 `for event in xxx` 就行。

## 7. 上下文管理器（with 语句）

```python
# 最常见的用法
with open("file.txt") as f:
    content = f.read()
# 离开 with 块时自动调用 f.close()，即使发生异常

# 原理：实现 __enter__ 和 __exit__
class DatabaseConnection:
    def __enter__(self):
        self.conn = create_connection()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()           # 无论是否异常都会执行
        return False                # False = 不吞掉异常

with DatabaseConnection() as conn:
    conn.execute("SELECT ...")
# 自动关闭连接
```

更简洁的写法用 `contextmanager` 装饰器：

```python
from contextlib import contextmanager

@contextmanager
def timer(label):
    start = time.time()
    yield                           # yield 之前 = __enter__，之后 = __exit__
    print(f"{label}: {time.time() - start:.2f}s")

with timer("检索"):
    results = retrieval_service.retrieve(query)
```

## 8. 可变与不可变

```python
# 不可变：int, float, str, tuple, frozenset, bytes
a = "hello"
a[0] = "H"     # TypeError! 字符串不可变

# 可变：list, dict, set, 自定义对象
lst = [1, 2, 3]
lst[0] = 99    # OK

# 经典坑：可变默认参数
def bad(items=[]):          # 所有调用共享同一个 list 对象！
    items.append(1)
    return items

bad()   # [1]
bad()   # [1, 1]  ← 不是 [1]！

def good(items=None):       # 正确写法
    if items is None:
        items = []
    items.append(1)
    return items
```

### 赋值、浅拷贝、深拷贝

```python
import copy

original = [[1, 2], [3, 4]]

ref = original              # 赋值：同一个对象，改一个另一个也变
shallow = list(original)    # 浅拷贝：外层新对象，内层还是同一个引用
deep = copy.deepcopy(original)  # 深拷贝：完全独立的新对象

original[0][0] = 99
ref[0][0]       # 99（同一个对象）
shallow[0][0]   # 99（内层是同一个引用！）
deep[0][0]      # 1 （完全独立）
```

项目中的例子：

```python
# agent_service.py 第 54 行
messages = list(history)    # 浅拷贝！避免直接修改 store 里的列表
messages.append(...)        # 只影响 messages，不影响 history
```

## 9. 迭代器与生成器

### 迭代器协议

```python
class Countdown:
    def __init__(self, n):
        self.n = n

    def __iter__(self):         # 返回迭代器（这里返回自身）
        return self

    def __next__(self):         # 每次调用返回下一个值
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1

for i in Countdown(3):
    print(i)    # 3, 2, 1
```

### 生成器 — 迭代器的语法糖

```python
def countdown(n):
    while n > 0:
        yield n         # 暂停，返回值；下次调用从这里继续
        n -= 1

for i in countdown(3):
    print(i)    # 3, 2, 1

# 生成器表达式
squares = (x**2 for x in range(10))   # 注意是圆括号，不是方括号
```

`yield` 的关键特性：**惰性求值**。不会一次性生成所有值，而是每次要一个才算一个，省内存。

项目中的例子：

```python
# agent_service.py chat_stream() 就是一个生成器
def chat_stream(self, message, conversation_id) -> Generator:
    ...
    yield {"event": "text", "data": text}          # 暂停，推一个事件
    yield {"event": "tool_call", "data": ...}       # 暂停，推一个事件
    yield {"event": "done", "data": ...}            # 暂停，推一个事件
# FastAPI 拿到这个生成器后，每次 next() 取一个事件推给客户端
```

## 10. 类型注解

Python 的类型注解**不影响运行**，只是给人和工具（IDE、mypy）看的。

```python
# 基础类型
name: str = "hello"
count: int = 0
ratio: float = 0.5
flag: bool = True

# 容器类型
names: list[str] = ["a", "b"]
config: dict[str, Any] = {"key": "value"}
unique: set[int] = {1, 2, 3}
pair: tuple[str, int] = ("age", 25)

# 可选类型
client: str | None = None              # Python 3.10+
client: Optional[str] = None           # 等价写法（旧版）

# 函数签名
def chat(self, message: str, top_k: int = 3) -> AgentResponse:
    ...

# 复杂类型
from collections.abc import Generator
from typing import Any

def chat_stream(self, ...) -> Generator[dict[str, Any], None, None]:
    # Generator[YieldType, SendType, ReturnType]
    yield {"event": "text", "data": "..."}
```

项目中的实际例子：

```python
# agent_service.py
self.client: anthropic.Anthropic | None = None
# 意思：client 要么是 Anthropic 实例，要么是 None

def _process_tool_calls(
    self,
    content: list[Any],                    # Any 表示任意类型
    all_sources: list[dict[str, Any]],     # dict 的 key 是 str，value 是任意类型
    tool_steps: list[ToolStep],            # ToolStep 是 Pydantic model
) -> list[dict[str, Any]]:                 # 返回值类型
    ...
```

## 11. 常见面试问题

**Q: `__repr__` 和 `__str__` 的区别？**
- `__repr__` 面向开发者，应该尽量无歧义，理想情况下 `eval(repr(obj))` 能重建对象
- `__str__` 面向用户，可读性优先
- `print()` 优先调 `__str__`，没有则 fallback 到 `__repr__`

**Q: Python 的多态怎么实现？**
- 不需要接口或抽象类，靠鸭子类型天然支持
- 只要对象有对应的方法，就能用，不关心类型
- 也可以用 `abc.ABC` + `@abstractmethod` 强制子类实现

**Q: `is` 和 `==` 的区别？**
- `is` 比较的是内存地址（是不是同一个对象）
- `==` 比较的是值（调用 `__eq__`）
- `None` 的判断永远用 `is None`，不用 `== None`

**Q: 为什么 Python 没有真正的私有属性？**
- 单下划线 `_name`：约定私有，外部可以访问但不应该
- 双下划线 `__name`：名称改写（name mangling），变成 `_ClassName__name`，防止子类意外覆盖
- Python 哲学："我们都是成年人"，靠约定而非强制

**Q: `classmethod` 的典型用途？**
- 替代构造函数（工厂方法）：

```python
class Date:
    def __init__(self, year, month, day):
        self.year, self.month, self.day = year, month, day

    @classmethod
    def from_string(cls, date_str):     # 替代构造函数
        y, m, d = map(int, date_str.split("-"))
        return cls(y, m, d)             # cls 而不是 Date，支持子类继承

Date.from_string("2024-01-15")
```

**Q: 什么是描述符（Descriptor）？**
- 实现了 `__get__`、`__set__`、`__delete__` 中任意一个的对象
- `@property`、`@classmethod`、`@staticmethod` 底层都是描述符
- 是 Python 属性访问机制的核心，但日常开发很少需要自己写
