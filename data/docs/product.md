这里为你整理并排版好了这份Python面试题，已经去除了所有的水印杂质，并对代码块、层级标题、列表结构等进行了精美的 Markdown 格式化处理，非常适合直接阅读、复习或导出为 PDF：

***

# 精心整理170道Python面试题，建议收藏！

精心整理的基础篇 Python 相关的基础知识，用于面试，或者平时复习，都是很好的！废话不多说，直接开搞。

<details>
<summary><b>点击展开 / 折叠题目目录</b></summary>


1. 为什么学习 Python
2. 解释型和编译型语言的区别
3. 简述下 Python 中的字符串、列表、元组和字典
4. 简述上述数据类型的常用方法
5. 简述 Python 中的字符串编码
6. 一行代码实现数值交换
7. is 和 == 的区别
8. Python 函数中的参数类型
9. `*arg` 和 `**kwarg` 作用
10. 一行代码实现1-100之和
11. 获取当前时间
12. PEP8 规范
13. Python 的深浅拷贝
14. 查看下面代码的输出
15. 可变类型与不可变类型
16. 打印九九乘法表
17. filter、map、reduce 的作用
18. re 的 match 和 search 区别
19. 面向对象中`__new__` 和 `__init__` 区别
20. 三元运算规则
21. 生成随机数
22. zip 函数用法
23. range 和 xrange 的区别
24. with 方法打开文件的作用
25. 什么是正则的贪婪匹配
26. 为什么不建议函数的默认参数传入可变对象
27. 字符串转列表
28. 字符串转整数
29. 删除列表中的重复值
30. 字符串单词统计
31. 列表推导，求奇偶数
32. 一行代码展开列表
33. 实现二分法查找函数
34. 字典和 json 转换
35. 列表推导式、字典推导式和生成器
36. 简述 read、readline、readlines 的区别
37. 打乱一个列表
38. 反转字符串
39. 单下划线和双下划线的作用
40. 新式类和旧式类
41. Python 面向对象中的继承有什么特点
42. super 函数的作用
43. 类中的各种函数
44. 如何判断是函数还是方法
45. isinstance 的作用以及与 type()的区别
46. 单例模式与工厂模式
47. 查看目录下的所有文件
48. 计算1到5组成的互不重复的三位数
49. 去除字符串首尾空格
50. 去除字符串中间的空格
51. 字符串格式化方式
52. 将"hello world"转换为首字母大写"HelloWorld"(不使用 title 函数)
53. 一行代码转换列表中的整数为字符串
54. 合并两个元组到字典
55. 给出如下代码的输入，并简单解释
56. Python 中的反射
57. 实现一个简单的 API
58. metaclass 元类
59. sort 和 sorted 的区别
60. Python 中的 GIL
61. 产生8位随机密码
62. 输出原始字符
63. 列表内，字典按照 value 大小排序
64. 简述 any() 和 all() 方法
65. 反转整数
66. 函数式编程
67. 简述闭包
68. 简述装饰器
69. 协程的优点
70. 实现一个斐波那契数列
71. 正则切分字符串
72. yield 用法
73. 冒泡排序
74. 快速排序
75. requests 简介
76. 比较两个 json 数据是否相等
77. 读取键盘输入
78. enumerate
79. pass 语句
80. 正则匹配邮箱
81. 统计字符串中大写字母的数量
82. json 序列化时保留中文
83. 简述继承
84. 什么是猴子补丁
85. help() 函数和 dir() 函数
86. 解释 Python 中的`//`，`％`和`**`运算符
87. 主动抛出异常
88. tuple 和 list 转换
89. 简述断言
90. 什么是异步非阻塞
91. 什么是负索引
92. 退出 Python 后，内存是否全部释放
93. Flask 和 Django 的异同
94. 创建删除操作系统上的文件
95. 简述 logging 模块
96. 统计字符串中单词出现次数
97. 正则 re.complie 的作用
98. try except else finally 的意义
99. 反转列表
100. 字符串中数字替换
     **综合篇：网络编程**
101. 简述 OSI 七层协议
102. 三次握手、四次挥手的流程
103. 什么是 C/S 和 B/S 架构
104. TCP 和 UDP 的区别
105. 局域网和广域网
106. arp 协议
107. 什么是 socket？简述基于 TCP 协议的套接字通信流程
108. 简述 进程、线程、协程的区别以及应用场景
109. 如何使用线程池和进程池
110. 进程之间如何进行通信
111. 进程锁和线程锁
112. 什么是并发和并行
113. threading.local 的作用
114. 什么是域名解析
115. LVS 是什么及作用
116. Nginx 的作用
117. keepalived 及 HAProxy
118. 什么是 rpc
119. 从浏览器输入一个网址到展示网址页面的过程
120. 什么是cdn
     **综合篇：数据库和框架**
121. 列举常见的数据库
122. 数据库设计三大范式
123. 什么是数据库事务
124. MySQL 索引种类
125. 数据库设计中一对多和多对多的应用场景
126. 简述触发器、函数、视图、存储过程
127. 常用 SQL 语句
128. 主键和外键的区别
129. 如何开启 MySQL 慢日志查询
130. MySQL 数据库备份命令
131. char 和 varchar 的区别
132. 最左前缀原则
133. 无法命中索引的情况
134. 数据库读写分离
135. 数据库分库分表
136. redis 和 memcached 比较
137. redis 中数据库默认是多少个 db 及作用
138. redis 有哪几种持久化策略
139. redis 支持的过期策略
140. 如何保证 redis 中的数据都是热点数据
141. Python 操作 redis
142. 基于 redis 实现发布和订阅
143. 如何高效的找到 redis 中的某个 KEY
144. 基于 redis 实现先进先出、后进先出及优先级队列
145. redis 如何实现主从复制
146. 循环获取 redis 中某个非常大的列表数据
147. redis 中的 watch 的命令的作用
148. redis 分布式锁
149. http 协议
150. uwsgi，uWSGI 和 WSGI 的区别
151. HTTP 状态码
152. HTTP 常见请求方式
153. 响应式布局
154. 实现一个简单的 AJAX 请求
155. 同源策略
156. 什么是 CORS
157. 什么是 CSRF
158. 前端实现轮询、长轮询
159. 简述 MVC 和 MTV
160. 接口的幂等性
161. Flask 框架的优势
162. 什么是 ORM
163. PV、UV 的含义
164. supervisor 的作用
165. 使用 ORM 和原生 SQL 的优缺点
166. 列举一些 django 的内置组件
167. 列举 Django 中执行原生 sql 的方法
168. cookie 和 session 的区别
169. beautifulsoup 模块的作用
170. Selenium 模块简述
     </details>

---

## 基础篇

### 1. 为什么学习 Python

Python 语言简单易懂，上手容易，随着 AI 风潮，越来越火。

### 2. 解释型和编译型语言的区别

- **编译型语言**：把做好的源程序全部编译成二进制的可运行程序。然后，可直接运行这个程序。如：C，C++
- **解释型语言**：把做好的源程序翻译一句，然后执行一句，直至结束！如：Python。（Java 有些特殊，java程序也需要编译，但是没有直接编译称为机器语言，而是编译称为字节码，然后用解释方式执行字节码。）

### 3. 简述下 Python 中的字符串、列表、元组和字典

- **字符串（str）**：字符串是用引号括起来的任意文本，是编程语言中最常用的数据类型。
- **列表（list）**：列表是有序的集合，可以向其中添加或删除元素。
- **元组（tuple）**：元组也是有序集合，但是是无法修改的。即元组是不可变的。
- **字典（dict）**：字典是无序的集合，是由 key-value 组成的。
- **集合（set）**：是一组 key 的集合，每个元素都是唯一，不重复且无序的。

### 4. 简述上述数据类型的常用方法

**字符串：**

- **切片**

  ```python
  mystr = 'luobodazahui'
  mystr[1:3] 
  # output: 'uo'
  ```

- **format**

  ```python
  mystr2 = "welcome to luobodazahui, dear {name}"
  mystr2.format(name="baby")
  # output: 'welcome to luobodazahui, dear baby'
  ```

- **join**：可以用来连接字符串，将字符串、元组、列表中的元素以指定的字符(分隔符)连接生成一个新的字符串。

  ```python
  mylist = ['luo','bo','da','za','hui']
  mystr3 = '-'.join(mylist)
  print(mystr3)
  # output: 'luo-bo-da-za-hui'
  ```

- **replace**：`String.replace(old,new,count)` 将字符串中的 old 字符替换为 New 字符，count 为替换的个数。

  ```python
  mystr4 = 'luobodazahui-haha'
  print(mystr4.replace('haha', 'good'))
  # output: luobodazahui-good
  ```

- **split**：切割字符串,得到一个列表。

  ```python
  mystr5 = 'luobo,dazahui good'
  print(mystr5.split())       # 以空格分割 -> ['luobo,dazahui', 'good']
  print(mystr5.split('h'))    # 以h分割 -> ['luobo,daza', 'ui good']
  print(mystr5.split(','))    # 以逗号分割 -> ['luobo', 'dazahui good']
  ```

**列表：**

- **切片**：同字符串

- **append 和 extend**：向列表中添加元素

  ```python
  mylist1 = [1, 2]
  mylist2 = [3, 4]
  mylist3 = [1, 2]
  mylist1.append(mylist2)
  print(mylist1)  # output: [1, 2, [3, 4]]
  
  mylist3.extend(mylist2)
  print(mylist3)  # output: [1, 2, 3, 4]
  ```

- **删除元素**：del：根据下标进行删除；pop：删除最后一个元素；remove：根据元素的值进行删除。

  ```python
  mylist4 = ['a', 'b', 'c', 'd']
  del mylist4[0]
  print(mylist4)   # output: ['b', 'c', 'd']
  
  mylist4.pop()
  print(mylist4)   # output: ['b', 'c']
  
  mylist4.remove('c')
  print(mylist4)   # output: ['b']
  ```

- **元素排序**：`sort`是将list按特定顺序重新排列，默认为由小到大，参数 `reverse=True` 可改为倒序；`reverse`是将list逆置。

  ```python
  mylist5 = [1, 5, 2, 3, 4]
  mylist5.sort()
  print(mylist5)   # output: [1, 2, 3, 4, 5]
  
  mylist5.reverse()
  print(mylist5)   # output: [5, 4, 3, 2, 1]
  ```

**字典：**

- **清空字典**：`dict.clear()`

  ```python
  dict1 = {'key1':1, 'key2':2}
  dict1.clear()
  print(dict1)     # output: {}
  ```

- **指定删除**：使用 pop 方法来指定删除字典中的某一项。

  ```python
  dict1 = {'key1':1, 'key2':2}
  d1 = dict1.pop('key1')
  print(d1)        # output: 1
  print(dict1)     # output: {'key2': 2}
  ```

- **遍历字典**

  ```python
  dict2 = {'key1':1, 'key2':2}
  mykey = [key for key in dict2]
  print(mykey)     # output: ['key1', 'key2']
  
  myvalue = [value for value in dict2.values()]
  print(myvalue)   # output: [1, 2]
  
  key_value = [(k, v) for k, v in dict2.items() ]
  print(key_value) # output: [('key1', 1), ('key2', 2)]
  ```

- **fromkeys**：用于创建一个新字典，以序列中元素做字典的键，value 为字典所有键对应的初始值。

  ```python
  keys = ['zhangfei', 'guanyu', 'liubei', 'zhaoyun']
  dict.fromkeys(keys, 0)
  # output: {'zhangfei': 0, 'guanyu': 0, 'liubei': 0, 'zhaoyun': 0}
  ```

### 5. 简述 Python 中的字符串编码

计算机在最初的设计中，采用了8个比特（bit）作为一个字节（byte）的方式。一个字节能表示的最大的整数就是255。最早，计算机只有 ASCII 编码。后来发明了Unicode，把所有语言都统一到一套编码里。当需要保存到硬盘或者需要传输的时候，就转换为UTF-8编码。
在 Python 中，以 Unicode 方式编码的字符串，可以使用 `encode()` 方法来编码成指定的 bytes，也可以通过 `decode()` 方法来把 bytes 编码成字符串。

```python
"中文".encode('utf-8')
# output: b'\xe4\xb8\xad\xe6\x96\x87'

b'\xe4\xb8\xad\xe6\x96\x87'.decode('utf-8')
# output: '中文'
```

### 6. 一行代码实现数值交换

```python
a = 1
b = 2
a, b = b, a
print(a, b)
# output: 2 1
```

### 7. is 和 == 的区别

```python
c = d = [1,2]
e = [1,2]
print(c is d)  # True
print(c == d)  # True
print(c is e)  # False
print(c == e)  # True
```

`==` 是比较操作符，只是判断对象的值（value）是否一致；而 `is` 则判断的是对象之间的身份（内存地址）是否一致。对象的身份可以通过 `id()` 方法来查看：

```python
id(c) # 88748080
id(d) # 88748080
id(e) # 88558288
```

可以看出，只有id一致时，is比较才会返回True。

### 8. Python 函数中的参数类型

位置参数，默认参数，可变参数，关键字参数。

### 9. `*arg` 和 `**kwarg` 作用

允许我们在调用函数的时候传入多个实参。

```python
def test(*arg, **kwarg):
    if arg:
        print("arg:", arg)
    if kwarg:
        print("kwarg:", kwarg)

test('ni', 'hao', key='world')
```

**output:**

```text
arg: ('ni', 'hao')
kwarg: {'key': 'world'}
```

可以看出，`*arg` 会把位置参数转化为 tuple，`**kwarg` 会把关键字参数转化为 dict。

### 10. 一行代码实现1-100之和

```python
sum(range(1, 101))
```

### 11. 获取当前时间

```python
import time
import datetime

print(datetime.datetime.now())
print(time.strftime('%Y-%m-%d %H:%M:%S'))
```

**output:**

```text
2019-06-07 18:12:11.165330
2019-06-07 18:12:11
```

### 12. PEP8 规范

简单列举10条：

1. 尽量以免单独使用小写字母'l'，大写字母'O'，以及大写字母'I'等容易混淆的字母。
2. 函数命名使用全部小写的方式，可以使用下划线。
3. 常量命名使用全部大写的方式，可以使用下划线。
4. 使用 has 或 is 前缀命名布尔元素，如:`is_connect = True`。
5. 不要在行尾加分号, 也不要用分号将两条命令放在同一行。
6. 不要使用反斜杠连接行。
7. 顶级定义之间空2行, 方法定义之间空1行。
8. 如果一个类不继承自其它类, 就显式的从 object 继承。？
9. 内部使用的类、方法或变量前，需加前缀 `_` 表明此为内部使用的。*
10. 要用断言来实现静态类型检测。？

### 13. Python 的深浅拷贝

**浅拷贝**

```python
import copy
list1 = [1, 2, 3, [1, 2]]
list2 = copy.copy(list1)
list2.append('a')
list2[3].append('a')
print(list1, list2)
# output: 
# [1, 2, 3, [1, 2, 'a']] 
# [1, 2, 3, [1, 2, 'a'], 'a']
```

能够看出，浅拷贝只成功”独立“拷贝了列表的外层，而列表的内层列表，还是共享的。

**深拷贝**

```python
import copy
list1 = [1, 2, 3, [1, 2]]
list3 = copy.deepcopy(list1)
list3.append('a')
list3[3].append('a')
print(list1, list3)
# output: 
# [1, 2, 3, [1, 2]] 
# [1, 2, 3, [1, 2, 'a'], 'a']
```

深拷贝使得两个列表完全独立开来，每一个列表的操作，都不会影响到另一个。

### 14. 查看下面代码的输出

```python
def num():
    return [lambda x: i * x for i in range(4)]
print([m(1) for m in num()])
```

**output:** `[3, 3, 3, 3]`
通过运行结果，可以看出 i 的取值为3，很神奇。（闭包延迟绑定机制）

### 15. 可变类型与不可变类型

- **可变数据类型**：list、dict、set
- **不可变数据类型**：int/float、str、tuple

### 16. 打印九九乘法表

```python
for i in range(1, 10):
    for j in range(1, i+1):
        print("%s*%s=%s " % (i, j, i*j), end="")
    print()
```

print 函数默认是会换行的，其有一个默认参数 `end`。如果像例子中，我们把 end 参数显示的置为 `""`，那么 print 函数执行完后就不会换行了，这样就达到了九九乘法表的效果了。

### 17. filter、map、reduce 的作用

**filter 函数**：用于过滤序列，它接收一个函数和一个序列，把函数作用在序列的每个元素上，然后根据返回值决定保留还是丢弃该元素。

```python
mylist = [1, 2, 3, 4, 5, 6, 7, 8, 9]
list(filter(lambda x: x%2 == 1, mylist))
# output: [1, 3, 5, 7, 9] (保留奇数列表)
```

**map 函数**：传入一个函数和一个序列，并把函数作用到序列的每个元素上，返回一个可迭代对象。

```python
mylist = [1, 2, 3, 4, 5, 6, 7, 8, 9]
list(map(lambda x: x*2, mylist))
# output: [2, 4, 6, 8, 10, 12, 14, 16, 18]
```

**reduce 函数**：用于递归计算，同样需要传入一个函数和一个序列，并把函数和序列元素的计算结果与下一个元素进行计算。

```python
from functools import reduce
reduce(lambda x, y: x+y, range(101))
# output: 5050
```

### 18. re 的 match 和 search 区别

`match()` 函数只检测要匹配的字符是不是在 string 的开始位置匹配；`search()` 会扫描整个 string 查找匹配。

### 19. 面向对象中 `__new__` 和 `__init__` 区别

- `__new__` 是在实例创建之前被调用的，因为它的任务就是创建实例然后返回该实例对象，是个静态方法。
- `__init__` 是当实例对象创建完成后被调用的，然后设置对象属性的一些初始值，通常用在初始化一个类实例的时候，是一个实例方法。

1. `__new__` 至少要有一个参数 `cls`，代表当前类，此参数在实例化时由Python解释器自动识别。
2. `__new__` 必须要有返回值，返回实例化出来的实例。可以 return 父类（通过 `super(当前类名, cls).__new__`）出来的实例，或者直接是 `object` 的 `__new__` 出来的实例。
3. `__init__` 有一个参数 `self`，就是这个 `__new__` 返回的实例。`__init__` 不需要返回值。
4. 如果 `__new__` 创建的是当前类的实例，会自动调用 `__init__` 函数；如果是其他类的类名，那么实际创建返回的就是其他类的实例，就不会调用当前类的 `__init__` 函数。

### 20. 三元运算规则

```python
a, b = 1, 2
h = a - b if a > b else a + b
print(h)
# output: 3
```

### 21. 生成随机数

```python
import random
print(random.random())
print(random.randint(1, 100))
print(random.uniform(1, 5))
```

### 22. zip 函数用法

`zip()` 函数将可迭代的对象作为参数，将对象中对应的元素打包成一个个元组，然后返回由这些元组组成的列表。

```python
list1 = ['zhangfei', 'guanyu', 'liubei','zhaoyun']
list2 = [0, 3, 2, 4]
list(zip(list1, list2))
# output: [('zhangfei', 0), ('guanyu', 3), ('liubei', 2), ('zhaoyun', 4)]
```

### 23. range 和 xrange 的区别

- `range([start,] stop[, step])`，根据 start 与 stop 指定的范围以及 step 设定的步长，生成一个序列。
- `xrange` 生成一个生成器，可以很大的节约内存（Python3中已将xrange更名为range）。

### 24. with 方法打开文件的作用

文件在进行读写的时候可能会出现一些异常状况，按照常规的写法我们需要 `try`, `except`, `finally` 做异常判断，并且最终不管遇到什么情况，都要执行 `finally f.close()` 关闭文件。`with` 方法帮我们自动实现了 `finally` 中的 `f.close`。

### 25. 什么是正则的贪婪匹配

Python 中默认是贪婪匹配模式。

- **贪婪模式**：正则表达式一般趋向于最大长度匹配。
- **非贪婪模式**：在整个表达式匹配成功的前提下，尽可能少的匹配。

### 26. 为什么不建议函数的默认参数传入可变对象

例如：

```python
def test(L=[]):
    L.append('test')
    print(L)

test() # output: ['test']
test() # output: ['test', 'test']
```

默认参数是一个列表，是可变对象 `[]`。Python 在函数定义的时候，默认参数 `L` 的值就被计算出来了，每次调用函数如果 `L` 的值变了，那么下次调用时，默认参数的值就已经不再是 `[]` 了。

### 27. 字符串转列表

```python
mystr = '1,2,3'
mystr.split(',')
# output: ['1', '2', '3']
```

### 28. 字符串转整数

```python
mylist = ['1', '2', '3']
list(map(lambda x: int(x), mylist))
# output: [1, 2, 3]
```

### 29. 删除列表中的重复值

```python
mylist = [1, 2, 3, 4, 5, 5]
list(set(mylist))#会打乱顺序

mylist = list(dict.fromkeys(mylist))#用字典不会打乱顺序
```

### 30. 字符串单词统计

```python
from collections import Counter
mystr = 'sdfsfsfsdfsd,were,hrhrgege.sdfwe!sfsdfs'
Counter(mystr)
# output: Counter({'s': 9, 'd': 5, 'f': 7, ',': 2, 'w': 2, 'e': 5, 'r': 3, 'h': 2, 'g': 2, '.': 1, '!': 1})
```

### 31. 列表推导，求奇偶数

```python
[x for x in range(10) if x % 2 == 1]
# output: [1, 3, 5, 7, 9]
```

### 32. 一行代码展开列表

```python
list1 = [[1, 2], [3, 4], [5, 6]]
[j for i in list1 for j in i]
# output: [1, 2, 3, 4, 5, 6]
```

### 33. 实现二分法查找函数

二分查找算法也称折半查找，必须是有序序列才可以使用。
**递归算法**

```python
def binary_search(data, item):
    n = len(data)
    if n > 0:
        mid = n // 2
        if data[mid] == item:
            return True
        elif data[mid] > item:
            return binary_search(data[:mid], item)
        else:
            return binary_search(data[mid+1:], item)
    return False

list1 = [1, 4, 5, 66, 78, 99, 100, 101, 233, 250, 444, 890]
binary_search(list1, 999)
```

**非递归算法**

```python
def binary_search(data, item):
    n = len(data)
    first = 0
    last = n - 1
    while first <= last:
        mid = (first + last) // 2
        if data[mid] == item:
            return True
        elif data[mid] > item:
            last = mid - 1
        else:
            first = mid + 1
    return False

list1 = [1, 4, 5, 66, 78, 99, 100, 101, 233, 250, 444, 890]
binary_search(list1, 99)
```

### 34. 字典和 json 转换

```python
import json

# 字典转 json
dict1 = {'zhangfei':1, "liubei":2, "guanyu": 4, "zhaoyun":3}
myjson = json.dumps(dict1)
print(myjson)
# output: '{"zhangfei": 1, "liubei": 2, "guanyu": 4, "zhaoyun": 3}'

# json 转字典
mydict = json.loads(myjson)
print(mydict)
# output: {'zhangfei': 1, 'liubei': 2, 'guanyu': 4, 'zhaoyun': 3}
```

### 35. 列表推导式、字典推导式和生成器

```python
import random

td_list = [i for i in range(10)]
print("列表推导式", td_list, type(td_list))

ge_list = (i for i in range(10))
print("生成器", ge_list)

dic = {k: random.randint(4, 9) for k in ["a", "b", "c", "d"]}
print("字典推导式", dic, type(dic))
```

**output:**

```text
列表推导式 [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] <class 'list'>
生成器 <generator object <genexpr> at 0x0139F070>
字典推导式 {'a': 6, 'b': 5, 'c': 8, 'd': 9} <class 'dict'>
```

*

### 36. 简述 read、readline、readlines 的区别

- `read` 读取整个文件
- `readline` 读取下一行,使用生成器方法
- `readlines` 读取整个文件到一个迭代器以供我们遍历

### 37. 打乱一个列表

```python
import random
list2 = [1, 2, 3, 4, 5, 6]
random.shuffle(list2)
print(list2)
# output: [4, 6, 5, 1, 2, 3]
```

### 38. 反转字符串

```python
str1 = 'luobodazahui'
str1[::-1]
# output: 'iuhazadoboul'
```

### 39. 单下划线和双下划线的作用

- `__foo__`：一种约定，Python 内部的名字，用来区别其他用户自定义的命名，以防冲突，例如 `__init__()`, `__del__()` 等特殊方法。
- `_foo`：一种约定，用来指定变量私有。不能用 `from module import *` 导入，其他方面和公有变量一样访问。
- `__foo`：这个有真正的意义，解析器用 `_classname__foo` 来代替这个名字，以区别和其他类相同的命名，它无法直接像公有成员一样随便访问，通过 `对象名._类名__xxx` 这样的方式可以访问。

### 40. 新式类和旧式类

- 在 Python 里凡是继承了 object 的类，都是新式类
- Python3 里只有新式类
- Python2 里面继承 object 的是新式类，没有写父类的是经典类（旧式类）
- 经典类目前在 Python 里基本没有应用

### 41. Python 面向对象中的继承有什么特点

- 同时支持单继承与多继承，当只有一个父类时为单继承，当存在多个父类时为多继承。   （多个父类）
- 子类会继承父类所有的属性和方法，子类也可以覆盖父类同名的变量和方法。
- 在继承中基类的构造（`__init__()`）方法不会被自动调用，它需要在其派生类的构造中专门调用。（父类的init会被子类的init覆盖，父类的元素子类要重新传）
- 在调用基类的方法时，需要加上基类的类名前缀，且需要带上 `self` 参数变量。（父类.init() or super().init）

### 42. super 函数的作用

`super()` 函数是用于调用父类(超类)的一个方法。

```python
class A():
    def funcA(self):
        print("this is func A")

class B(A):
    def funcA_in_B(self):
        super(B, self).funcA()#python2写法 python3 super()就行了

    def funcC(self):
        print("this is func C")

ins = B()
ins.funcA_in_B()
ins.funcC()
```

**output:**

```text
this is func A
this is func C
```

### 43. 类中的各种函数

主要分为实例方法、类方法和静态方法：

- **实例方法** 普通方法，参数传self

  - 定义：第一个参数必须是实例对象，该参数名一般约定为“self”。
  - 调用：只能由实例对象调用。

- **类方法** 只能用类属性，传cls

  - 定义：使用装饰器 `@classmethod`。第一个参数必须是当前类对象，一般约定为“cls”。
  - 调用：实例对象和类对象都可以调用。

- **静态方法** 普通函数，随手放里面罢了

  - 定义：使用装饰器 `@staticmethod`。参数随意，没有“self”和“cls”参数。

  - 调用：实例对象和类对象都可以调用。

    

    **抽象方法** 里面是空的，规范子类的格式，统一接口用

### 44. 如何判断是函数还是方法

- 与类和实例无绑定关系的 function 都属于函数（function）
- 与类和实例有绑定关系的 function 都属于方法（method）

```python
def func1():
    pass
print(func1) # <function func1 at ...>

class People(object):
    def func2(self):
        pass

    @staticmethod
    def func3():
        pass

    @classmethod
    def func4(cls):
        pass

people = People()
print(people.func2) # <bound method People.func2 of ...>
print(people.func3) # <function People.func3 at ...>
print(people.func4) # <bound method People.func4 of <class '__main__.People'>>
```

### 45. isinstance 的作用以及与 type()的区别

`isinstance()` 函数来判断一个对象是否是一个已知的类型。
**区别：**

- `type()` 不会认为子类是一种父类类型，不考虑继承关系。
- `isinstance()` 会认为子类是一种父类类型，考虑继承关系。

```python
class A(object): pass
class B(A): pass

a = A()
b = B()
print(isinstance(a, A))   # True
print(isinstance(b, A))   # True
print(type(a) == A)       # True
print(type(b) == A)       # False
```

### 46. 单例模式与工厂模式 *

- **单例模式**：主要目的是确保某一个类只有一个实例存在。
- **工厂模式**：包涵一个超类，这个超类提供一个抽象化的接口来创建一个特定类型的对象，而不是决定哪个对象可以被创建。

### 47. 查看目录下的所有文件

```python
import os
print(os.listdir('.'))
```

### 49. 去除字符串首尾空格

```python
str1 = " hello nihao "
str1.strip()
# output: 'hello nihao'
```

### 50. 去除字符串中间的空格

```python
str2 = "hello you are good"
print(str2.replace(" ", ""))
"".join(str2.split(" "))
# output: 'helloyouaregood'
```

### 51. 字符串格式化方式

1. **使用 `%` 操作符**

   ```python
   print("This is for %s" % "Python")
   ```

2. **str.format** (Python3 引入)

   ```python
   print("This is my {}".format("chat"))
   print("This is {name}, hope you can {do}".format(name="zhouluob", do="like"))
   ```

3. **f-strings** (Python3.6+ 引入)

   ```python
   name = "luobodazahui"
   print(f"hello {name}")
   ```

### 52. 将"hello world"转换为首字母大写"HelloWorld"(不使用 title 函数)

```python
str1 = "hello world"
" ".join(list(map(lambda x: x.capitalize(), str1.split(" "))))
# output: 'Hello World'
```

### 53. 一行代码转换列表中的整数为字符串

```python
list1 = [1, 2, 3]
list(map(lambda x: str(x), list1))
# output: ['1', '2', '3']
```

### 54. 合并两个元组到字典

```python
a = ("zhangfei", "guanyu")
b = (66, 80)
dict(zip(a, b))
# output: {'zhangfei': 66, 'guanyu': 80}
```

### 55. 给出如下代码的输入，并简单解释

**例子1：**

```python
a = (1, 2, 3, [4, 5, 6, 7], 8)
a[3] = 2
```

**报错：**

```text
TypeError: 'tuple' object does not support item assignment
```

**例子2：**

```python
a = (1, 2, 3, [4, 5, 6, 7], 8)
a[3][2] = 2
print(a)
# output: (1, 2, 3, [4, 5, 2, 7], 8)
```

解释：tuple 是不可变类型，不能改变 tuple 里的元素（例子1）；而 list 是可变类型，改变其内部元素是允许的（例子2）。

### 56. Python 中的反射

反射就是通过字符串的形式，导入模块；通过字符串的形式，去模块寻找指定函数，并执行。利用字符串的形式去对象（模块）中操作成员，一种基于字符串的事件驱动！

```python
class NewClass(object):
    def __init__(self, name, male):
        self.name = name
        self.male = male

people = NewClass('luobo', 'boy')
print(hasattr(people, 'name'))      # True
print(getattr(people, 'name'))      # luobo
setattr(people, 'male', 'girl')
print(getattr(people, 'male'))      # girl
```

`getattr`, `hasattr`, `setattr`, `delattr` 对模块的修改都在内存中进行，并不会影响文件中真实内容。

### 57. 实现一个简单的 API

使用 flask 构造 web 服务器：

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def simple_api():
    result = request.get_json()
    return result

if __name__ == "__main__":
    app.run()
```

### 58. metaclass 元类

- 先定义类以后，就可以根据这个类创建出实例；
- 先定义元类，根据 metaclass 创建出类。

```python
class MyMetaclass(type):
    def __new__(cls, class_name, class_parents, class_attr):
        class_attr['print'] = "this is my metaclass's subclass %s" % class_name
        return type.__new__(cls, class_name, class_parents, class_attr)

class MyNewclass(object, metaclass=MyMetaclass):
    pass

myinstance = MyNewclass()
print(myinstance.print)
# output: "this is my metaclass's subclass MyNewclass"
```

### 59. sort 和 sorted 的区别

- `sort()` 是可变对象列表（list）的方法，无参数，无返回值，会改变可变对象。
- `sorted()` 是产生一个新的对象。返回一个排序后的结果，不改变原始对象，适用于任何可迭代容器。

### 60. Python 中的 GIL

GIL 是 Python 的全局解释器锁。同一进程中假如有多个线程运行，一个线程在运行 Python 程序的时候会占用 Python 解释器（加了一把锁即 GIL），使该进程内的其他线程无法运行。如果在多线程中遇到耗时IO操作，解释器锁会解开，使其他线程运行。

### 61. 产生8位随机密码

```python
import random
import string
"".join(random.choice(string.printable[:-7]) for i in range(8))
# output: 'd5^NdNJp'
```

### 62. 输出原始字符

```python
print('hello\nworld')   # 换行
print(b'hello\nworld')  # bytes
print(r'hello\nworld')  # 原始字符输出 hello\nworld
```

### 63. 列表内，字典按照 value 大小排序

```python
list1 = [{'name': 'guanyu', 'age':29}, 
         {'name': 'zhangfei', 'age': 28}, 
         {'name': 'liubei', 'age':31}]
sorted(list1, key=lambda x: x['age'])
```

### 64. 简述 any() 和 all() 方法

- `all()` 如果存在 `0`/`Null`/`False` 返回 False，否则返回 True。
- `any()` 如果都是 `0`/`None`/`False`/`Null` 时返回 False，只要有一个真则返回 True。

### 65. 反转整数

```python
def reverse_int(x):
    if not isinstance(x, int):
        return False
    if -10 < x < 10:
        return x
    tmp = str(x)
    if tmp[0] != '-':
        tmp = tmp[::-1]
        return int(tmp)
    else:
        tmp = tmp[1:][::-1]
        x = int(tmp)
        return -x

reverse_int(-23837)
# output: -73832
```

### 66. 函数式编程

函数作为返回值例子：

```python
def sum(*args):
    def inner_sum():
        tmp = 0
        for i in args:
            tmp += i
        return tmp
    return inner_sum

mysum = sum(2, 4, 6)
print(mysum())  # output: 12
```

### 67. 简述闭包

如果在一个内部函数里，对在外部作用域（但不是在全局作用域）的变量进行引用，那么内部函数就被认为是闭包 (closure)。
闭包特点：

1. 必须有一个内嵌函数。
2. 内嵌函数必须引用外部函数中的变量。
3. 外部函数的返回值必须是内嵌函数。

### 68. 简述装饰器

装饰器是一种特殊的闭包，就是在闭包的基础上传递了一个函数，然后覆盖原来函数的执行入口，以后调用这个函数的时候，就可以额外实现一些功能了。

```python
import time
def log(func):
    def inner_log(*args, **kw):
        print("Call: {}".format(func.__name__))
        return func(*args, **kw)
    return inner_log

@log
def timer():
    print(time.time())

timer()
```

### 69. 协程的优点

1. 子程序切换不是线程切换，而是由程序自身控制。
2. 没有线程切换的开销，和多线程比，线程数量越多，协程的性能优势就越明显。
3. 不需要多线程的锁机制，因为只有一个线程，不存在同时写变量冲突。

### 70. 实现一个斐波那契数列

**生成器法：**

```python
def fib(n):
    a, b = 0, 1
    while n:
        a, b = b, a+b
        n -= 1
        yield a

[i for i in fib(10)]
# output: [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
```

**递归法：**

```python
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

[fib(i) for i in range(1, 11)]
```

### 71. 正则切分字符串

```python
import re
str1 = 'hello world:luobo dazahui'
result = re.split(r":| ", str1)
print(result)
# output: ['hello', 'world', 'luobo', 'dazahui']
```

### 72. yield 用法

```python
def foryield():
    print("start test yield")
    while True:
        result = yield 5
        print("result:", result)

g = foryield()
print(next(g))
print("*" * 20)
print(next(g))
```

可以看出，第一个调用 `next()` 函数，程序只执行到了 `result = yield 5`，同时由于 yield 中断了程序，所以 result 也没有被赋值，所以第二次执行 `next()` 时，result 是 None。

### 73. 冒泡排序

```python
list1 = [2, 5, 8, 9, 3, 11]

def paixu(data, reverse=False):
    if not reverse:
        for i in range(len(data) - 1):
            for j in range(len(data) - 1 - i):
                if data[j] > data[j+1]:
                    data[j], data[j+1] = data[j+1], data[j]
        return data
    else:
        for i in range(len(data) - 1):
            for j in range(len(data) - 1 - i):
                if data[j] < data[j+1]:
                    data[j], data[j+1] = data[j+1], data[j]
        return data

print(paixu(list1, reverse=True))
# output: [11, 9, 8, 5, 3, 2]
```

### 74. 快速排序

```python
list1 = [8, 5, 1, 3, 2, 10, 11, 4, 12, 20]

def partition(arr, low, high):
    i = (low - 1)
    pivot = arr[high]
    for j in range(low, high):
        if arr[j] <= pivot:
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i+1], arr[high] = arr[high], arr[i+1]
    return (i + 1)

def quicksort(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)

quicksort(list1, 0, len(list1)-1)
print(list1)
# output: [1, 2, 3, 4, 5, 8, 10, 11, 12, 20]
```

### 75. requests 简介

该库是发起 HTTP 请求的强大类库，调用简单，功能强大。

```python
import requests
url = "http://www.luobodazahui.top"
response = requests.get(url) 
response.encoding = "utf-8" 
html = response.text 
```

### 76. 比较两个 json 数据是否相等

```python
dict1 = {"zhangfei": 12, "guanyu": 13, "liubei": 18}
dict2 = {"zhangfei": 12, "guanyu": 13, "liubei": 18}

def compare_dict(dict1, dict2):
    # 此处省略具体实现，可通过遍历 keys 并对比 values 解决
    pass
```

### 77. 读取键盘输入

```python
def forinput():
    input_text = input()
    print("your input text is: ", input_text)
```

### 78. enumerate

`enumerate()` 函数用于将一个可遍历的数据对象组合为一个索引序列，一般用在 for 循环当中。

```python
data1 = ['one', 'two', 'three', 'four']
for i, enu in enumerate(data1):
    print(i, enu)
```

### 79. pass 语句

pass 是空语句，是为了保持程序结构的完整性。pass 不做任何事情，一般用做占位语句。

### 80. 正则匹配邮箱

```python
import re
email_list = ["test01@163.com", "test02@163.123", ".test03g@qq.com", "test04@gmail.com"]
for email in email_list:
    ret = re.match(r"[\w]{4,20}@(.*)\.com$", email)
    if ret:
        print("%s 是符合规定的邮件地址" % email)
    else:
        print("%s 不符合要求" % email)
```

### 81. 统计字符串中大写字母的数量

```python
str2 = 'werrQWSDdiWuW'
counter = sum(1 for i in str2 if i.isupper())
print(counter)  # output: 6
```

### 82. json 序列化时保留中文

```python
import json
dict1 = {'name': '萝卜', 'age': 18}
dict1_new = json.dumps(dict1, ensure_ascii=False)
print(dict1_new)
# output: {"name": "萝卜", "age": 18}
```

### 83. 简述继承

Python 支持以下类型的继承：

- 单继承
- 多重继承
- 多级继承
- 分层继承
- 混合继承

### 84. 什么是猴子补丁

猴子补丁是指在运行时动态修改类和模块。
用处：在运行时替换方法、属性等；在不修改第三方代码的情况下增加原来不支持的功能。

### 85. help() 函数和 dir() 函数

- `help()` 函数返回帮助文档和参数说明。
- `dir()` 函数返回对象中的所有成员 (任何类型)。

### 86. 解释 Python 中的 `//`，`％` 和 `**` 运算符

- `//`：执行地板除法，返回结果的整数部分(向下取整)。
- `%`：取模符号，返回除法后的余数。
- `**`：表示取幂，a**b 返回 a 的 b 次方。

### 87. 主动抛出异常

使用 `raise` 关键字。

```python
def test_raise(n):
    if not isinstance(n, int):
        raise Exception('not a int type')
```

### 88. tuple 和 list 转换

```python
tuple1 = (1, 2, 3, 4)
list1 = list(tuple1)
tuple2 = tuple(list1)
```

### *89. 简述断言

Python的断言就是检测一个条件，如果条件为真，它什么都不做；反之它触发一个带可选错误信息的 `AssertionError`。

```python
assert n == 2, "n is not 2"
```

### *90. 什么是异步非阻塞

- **同步**：就是在发出一个功能调用时，在没有得到结果之前，该调用就不会返回。
- **异步**：调用在发出之后, 这个调用就直接返回了, 所以没有返回结果。当该异步功能完成后，被调用者可以通过状态、通知或回调来通知调用者。
- **阻塞**：调用结果返回之前，当前线程会被挂起。
- **非阻塞**：在不能立刻得到结果之前也会立刻返回，同时该函数不会阻塞当前线程。

### 91. 什么是负索引

正的数字使用'0'作为第一个索引。负数的索引从'-1'开始，表示序列中的最后一个索引，'-2'作为倒数第二个索引。

### 92. 退出 Python 后，内存是否全部释放

不是的，那些具有对象循环引用或者全局命名空间引用的变量，在 Python 退出时往往不会被释放。另外不会释放 C 库保留的部分内容。

### 93. Flask 和 Django 的异同

- **Flask** 是 “microframework”，主要用来编写小型应用程序，自由度高，扩展性强。
- **Django** 适用于大型应用程序。它提供了灵活性，以及完整的程序框架，内置了 ORM、Admin 等组件。

### 94. 创建删除操作系统上的文件

```python
import os
f = open('test.txt', 'w')
f.close()
os.remove('test.txt')
```

### 95. 简述 logging 模块

logging 模块是 Python 内置的标准模块，主要用于输出运行日志。相比 print，具备如下优点：可以设置不同的日志等级，决定将信息输出到什么地方。

### 96. 统计字符串中单词出现次数

```python
from collections import Counter
str1 = "nihsasehndciswemeotpxc"
print(Counter(str1))
```

### 97. 正则 re.compile 的作用

`re.compile` 是将正则表达式编译成一个对象，加快速度，并重复使用。

### 98. try except else finally 的意义

- `try ... except ... else` 没有捕获到异常，执行 else 语句。
- `try ... except ... finally` 不管是否捕获到异常，都执行 finally 语句。

### 99. 反转列表

使用切片 `mylist[::-1]` (创建新列表) 或 `mylist.reverse()` (更改原列表，速度更快)。

### 100. 字符串中数字替换

```python
import re
str1 = '我是周萝卜，今年18岁'
result = re.sub(r"\d+", "20", str1)
print(result)
# output: 我是周萝卜，今年20岁
```

---

## 综合篇：网络编程

### 101. 简述 OSI 七层协议

七层划分为：应用层、表示层、会话层、传输层、网络层、数据链路层、物理层。

- 物理层：网线，电缆等
- 数据链路层：Mac 地址
- 网络层：IP 地址
- 传输层：TCP，UDP 协议
- 应用层：FTP 协议，Email，WWW 等

### 102. 三次握手、四次挥手的流程

都发生在传输层。
**三次握手：**

1. 第一次握手：主机 A 发送 `syn＝1` 请求到服务器，进入 SYN_SEND 状态。
2. 第二次握手：主机 B 收到请求后，向 A 发送 `ack, syn=1` 的包，进入 SYN_RECV 状态。
3. 第三次握手：主机 A 收到后检查确认，再发送 `ack=1`，主机 B 收到后确认，连接建立成功。

**四次挥手：**

1. 服务器 A 发送一个 FIN，用来关闭 A 到 B 的数据传送。
2. 服务器 B 收到这个 FIN，发回一个 ACK，确认序号为收到的序号加1。
3. 服务器 B 关闭与服务器 A 的连接，发送一个 FIN 给服务器 A。
4. 服务器 A 发回 ACK 报文确认。

### 103. 什么是 C/S 和 B/S 架构

- **B/S**：浏览器/服务器模式。优点：零安装，维护简单。缺点：安全性较差。
- **C/S**：客户端/服务器模式。优点：安全性好，数据传输较快。缺点：对PC机操作系统有要求，维护成本高。

### 104. TCP 和 UDP 的区别

- **TCP**：提供可靠的通信传输，可以进行丢包重发控制和顺序控制。应用：FTP、短信。
- **UDP**：利用 IP 提供面向无连接的通信服务，不提供复杂的控制机制。应用：媒体流。

### 105. 局域网和广域网

- **广域网（WAN）**：跨接很大的物理范围，形成国际性的远程网络。
- **局域网（LAN）**：某一区域内由多台计算机互联成的计算机组，一般方圆几千米以内。

### 106. arp 协议

ARP 即地址解析协议，用于实现从 IP 地址到 MAC 地址的映射。

### 107. 什么是 socket？简述基于 TCP 协议的套接字通信流程

socket 是对 TCP/IP 协议的封装，它是一组调用接口（API 函数）。

**Server:**

```python
import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 9999))
s.listen(5)
```

**Client:**

```python
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 9999))
```

### 108. 简述 进程、线程、协程的区别以及应用场景

- **进程**：每个进程都有自己的独立内存空间。密集 CPU 任务（如计算）用多进程。
- **线程**：比进程更小的能独立运行的基本单位，共享进程资源。密集 I/O 任务（网络/磁盘）使用多线程。
- **协程**：用户态的轻量级线程，调度完全由用户控制。单线程上执行多个任务，无切换开销。

### 109. 如何使用线程池和进程池

使用 `multiprocessing.Pool` 或 `concurrent.futures` (如 `ThreadPoolExecutor` 和 `ProcessPoolExecutor`) 限制启动的并发任务数。

### 110. 进程之间如何进行通信

Python 的 `multiprocessing` 模块提供了 `Queue`、`Pipes`、`Manager` 等多种方式来交换数据。

### 111. 进程锁和线程锁

- **进程锁**：使用本地系统的信号量控制，保证关键代码段不被并发调用。
- **线程锁**：多线程几乎同时修改共享数据时，使用互斥锁保证每一次只有一个线程进入写入操作。

### 112. 什么是并发和并行

- **并行**：多个 CPU 核心，不同的程序分配给不同的 CPU 同时执行。
- **并发**：单个 CPU 核心，通过时间切片交替执行多个程序。

### 113. threading.local 的作用

ThreadLocal 在每一个变量中都会创建一个副本，每个线程都可以访问自己内部的副本变量，对其他线程不可见。

### 114. 什么是域名解析

将域名解析为 IP 地址的过程，通过 DNS 服务器查找。

### 115. LVS 是什么及作用

LVS (Linux Virtual Server) 是一个虚拟服务器集群系统，即负载均衡服务器。

### 116. Nginx 的作用

主要功能：反向代理、负载均衡、HTTP 服务器（动静分离）、正向代理。

### 117. keepalived 及 HAProxy

HAProxy 提供负载均衡及代理。keepalived 是保证集群高可用的服务软件，防止单点故障。

### 118. 什么是 rpc

RPC 是指远程过程调用，允许跨服务器通过网络调用函数/方法。

### 119. 从浏览器输入一个网址到展示网址页面的过程

1. 浏览器通过 DNS 查找 IP。
2. 给 IP 对应的 web 服务器发送 HTTP 请求。
3. 服务器返回响应。
4. 浏览器渲染页面。

### 120. 什么是 cdn

内容分发网络（CDN），依靠部署在各地的边缘服务器，使用户就近获取内容，提高访问速度。

---

## 综合篇：数据库和框架

### 121. 列举常见的数据库

- **关系型**：MySQL，Oracle，SQLServer，SQLite
- **非关系型**：MongoDB，Redis，HBase

### 122. 数据库设计三大范式

1. **第一范式**：属性不能再分解。
2. **第二范式**：非主属性都要依赖于每一个关键属性。
3. **第三范式**：数据不能存在传递关系（直接依赖主键）。

### 123. 什么是数据库事务

事务是一个操作序列，要么都执行，要么都不执行。
四个属性：原子性，一致性，隔离性和持久性 (ACID)。

### 124. MySQL 索引种类

普通索引、唯一索引、主键索引、组合索引、全文索引。

### 125. 数据库设计中一对多和多对多的应用场景

- **一对一**：学生对应身份证。
- **一对多**：班级包含多名学生。
- **多对多**：学生选择多门课。

### 126. 简述触发器、函数、视图、存储过程

- **触发器**：在 insert/update/delete 时自动执行的代码块。
- **函数**：自定义逻辑实现。
- **视图**：查询结果形成的虚拟表。
- **存储过程**：封装的代码段，预编译效率高。

### 127. 常用 SQL 语句

- **DML**：`SELECT`, `UPDATE`, `DELETE`, `INSERT INTO`
- **DDL**：`CREATE DATABASE/TABLE/INDEX`, `ALTER DATABASE/TABLE`, `DROP TABLE/INDEX`

### 128. 主键和外键的区别

- **主键**：唯一标识记录，不能重复，不为空。
- **外键**：关联另一张表的主键，保持数据一致性。

### 129. 如何开启 MySQL 慢日志查询

修改配置文件 `my.cnf` 增加：

```text
slow_query_log=ON 
long_query_time = 2 
```

### 130. MySQL 数据库备份命令

```bash
mysqldump -u 用户名 -p 数据库名 > 导出的文件名
```

### 131. char 和 varchar 的区别

- **char**：定长，索引效率极高。
- **varchar**：变长，节省空间，但效率略低。

### 132. 最左前缀原则

多列联合索引（如 `col1, col2, col3`），查询时必须按从左到右的顺序匹配才能命中索引。

### 133. 无法命中索引的情况

`or` 关键字、左前导模糊查询 (`like '%a'`)、组合索引不符合最左前缀、强制类型转换、负向查询 (`!=`, `NOT IN`)。

### 134. 数据库读写分离

主库用于写数据，多个从库完成读操作，主从库之间进行数据同步。

### 135. 数据库分库分表

水平切分，将同一个表的数据按规则分散到多个库或表中，减小单表数据量。

### 136. redis 和 memcached 比较

- redis 支持更丰富的数据结构（list, set, hash）。
- redis 支持持久化（aof/rdb）。
- memcached 宕机后数据全丢，redis 可恢复。

### 137. redis 中数据库默认是多少个 db 及作用

默认16个数据库，单机隔离数据使用，集群模式下无此概念。

### 138. redis 有哪几种持久化策略

- **RDB**：定时将内存数据 dump 到磁盘。
- **AOF**：将操作日志以追加方式写入文件。

### 139. redis 支持的过期策略

定期删除 + 惰性删除（获取时检查是否过期再删除）。

### 140. 如何保证 redis 中的数据都是热点数据

设置 Redis 最大占用内存，并配置淘汰策略（如 LRU），自动淘汰冷数据。

### 141. Python 操作 redis

```python
import redis
pool = redis.ConnectionPool(host='host', port=6379)
r = redis.Redis(connection_pool=pool)
```

### 142. 基于 redis 实现发布和订阅

利用 `r.pubsub()` 和 `r.publish()`。

### 143. 如何高效的找到 redis 中的某个 KEY

`con.keys(pattern='key*')` 或使用 `SCAN` 命令更为高效。

### 144. 基于 redis 实现先进先出、后进先出及优先级队列

- FIFO (队列)：`rpush` + `lpop`
- LIFO (栈)：`rpush` + `rpop`
- 优先级：使用 ZSET (`zadd`, `zrange`)

### 145. redis 如何实现主从复制

在从服务器中配置 `SLAVEOF 主服务器IP 端口`。

### 146. 循环获取 redis 中某个非常大的列表数据

利用 `lindex` 结合 python 生成器 (`yield`) 增量迭代。

### 147. redis 中的 watch 的命令的作用

用于事务操作前监视 key，若执行前 key 被改动，则取消事务执行（乐观锁）。

### 148. redis 分布式锁

设置一个带过期时间的 key，利用 setnx（Set if Not eXists）保证互斥。

### 149. http 协议

超文本传输协议，基于 TCP，默认 80 端口，客户端发起请求，服务端给与响应。

### 150. uwsgi，uWSGI 和 WSGI 的区别

- **WSGI**：Web Server Gateway Interface 规范。
- **uwsgi**：一种线路协议。
- **uWSGI**：实现了 WSGI 规范和 uwsgi 协议的 Web 服务器。

### 151. HTTP 状态码

1xx (信息)，2xx (成功)，3xx (重定向)，4xx (客户端错误)，5xx (服务端错误)。

### 152. HTTP 常见请求方式

GET，POST，PUT，DELETE，PATCH 等。

### 153. 响应式布局

一个网站能够自动适应和兼容多个终端及屏幕尺寸。

### 154. 实现一个简单的 AJAX 请求

```javascript
$.ajax({
    type: "GET",
    url: "test.json",
    data: {username: $("#username").val()},
    dataType: "json",
    success: function(data){ /* 渲染逻辑 */ }
});
```

### 155. 同源策略

限制同一个源加载的文档如何与另一个源的资源交互（协议、域名、端口一致才算同源）。

### 156. 什么是 CORS

跨域资源共享，是 AJAX 跨域请求资源的一种方式。

### 157. 什么是 CSRF

跨站请求伪造（Cross-site request forgery）。

### 158. 前端实现轮询、长轮询

- **轮询**：使用 `setInterval` 定时发送 ajax。
- **长轮询**：在 ajax 的 `onreadystatechange` 中递归调用 ajax 自己。

### 159. 简述 MVC 和 MTV

- **MVC**：Model（模型）、View（视图）、Controller（控制器）。
- **Django MTV**：Model（模型 ORM）、Template（模板展示）、View（视图逻辑，相当于控制器）。

### 160. 接口的幂等性

用户对于同一操作发起的一次或多次请求的结果是一致的，不会产生副作用。

### 161. Flask 框架的优势

简洁，轻巧，扩展性强，自由度高。

### 162. 什么是 ORM

对象关系映射 (Object Relational Mapping)，将数据库表的数据映射成 Python 对象。

### 163. PV、UV 的含义

- **PV**：页面浏览量或点击量。
- **UV**：独立访客数（以 cookie 为依据）。

### 164. supervisor 的作用

进程管理工具，能够方便地启动、停止、重启被管理的进程，并支持崩溃自动拉起。

### 165. 使用 ORM 和原生 SQL 的优缺点

- **ORM 优点**：面向对象清晰、防止 SQL 注入、方便动态构造和重构。
- **ORM 缺点**：不易处理复杂查询、性能不如原生 SQL。

### 166. 列举一些 django 的内置组件

Admin 组件，Model 组件，Form 组件，ModelForm 组件。

### 167. 列举 Django 中执行原生 sql 的方法

1. `connection.cursor().execute("SQL")`
2. `queryset.extra()`
3. `Model.objects.raw("SQL")`

### 168. cookie 和 session 的区别

- **cookie**：保存在浏览器端。
- **session**：保存在服务端，依赖客户端保存的 sessionId cookie 来识别。

### 169. beautifulsoup 模块的作用

解析、遍历、维护 HTML/XML 网页的“标签树”，用于爬虫解析。

### 170. Selenium 模块简述

模拟操作浏览器的库，支持自动化点击、动态页面加载渲染和截屏等。