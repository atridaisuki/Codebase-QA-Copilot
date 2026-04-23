# Redis 面试知识点详解

## 一、Redis 基础

### 1.1 什么是 Redis

Redis（Remote Dictionary Server）是一个开源的、基于内存的键值存储系统，可用作数据库、缓存和消息中间件。

核心特点：
- 单线程模型（6.0 之前网络 IO 也是单线程，6.0 后网络 IO 多线程，命令执行仍单线程）
- 基于内存，读写速度极快（读 11w QPS，写 8w QPS 量级）
- 支持数据持久化（RDB + AOF）
- 支持多种数据结构
- 原子性操作（单线程保证）
- 支持 Lua 脚本、事务、发布订阅、主从复制、哨兵、集群

### 1.2 为什么 Redis 这么快

**面试回答思路：从内存、IO模型、数据结构三个维度展开。**

1. **纯内存操作**：数据存储在内存中，避免磁盘 IO
2. **单线程模型**：避免上下文切换和锁竞争开销
3. **IO 多路复用**：使用 epoll/kqueue 等机制，单线程处理大量并发连接
4. **高效数据结构**：如 SDS、ziplist、quicklist、skiplist 等底层实现经过精心优化
5. **Redis 6.0 多线程**：网络 IO 读写使用多线程，命令执行仍为单线程，进一步提升吞吐

> **与其他组件的联系**：和 MySQL 对比，Redis 是内存型存储，MySQL 是磁盘型存储。实际架构中 Redis 常作为 MySQL 的缓存层，减轻数据库压力。

---

## 二、数据结构

### 2.1 五种基本数据类型

| 类型 | 底层实现 | 典型场景 |
|------|---------|---------|
| String | SDS（Simple Dynamic String） | 缓存、计数器、分布式锁 |
| Hash | ziplist / hashtable | 对象存储（用户信息等） |
| List | quicklist（ziplist + 双向链表） | 消息队列、时间线 |
| Set | intset / hashtable | 标签、共同好友、去重 |
| ZSet（Sorted Set） | ziplist / skiplist + hashtable | 排行榜、延迟队列 |

### 2.2 底层数据结构详解

#### SDS（Simple Dynamic String）

```c
struct sdshdr {
    int len;      // 已使用长度
    int free;     // 剩余可用长度
    char buf[];   // 字节数组
}
```

相比 C 字符串的优势：
- O(1) 获取字符串长度（C 字符串需要遍历）
- 杜绝缓冲区溢出（自动扩容）
- 减少内存重分配（空间预分配 + 惰性释放）
- 二进制安全（不以 `\0` 判断结束）

#### ziplist（压缩列表）

紧凑的连续内存块，节省内存。当元素数量少且元素较小时，Hash、List、ZSet 都会使用 ziplist 作为底层实现。

缺点：插入/删除可能触发连锁更新（cascade update），时间复杂度退化为 O(N²)。

> Redis 7.0 用 listpack 替代了 ziplist，解决了连锁更新问题。

#### skiplist（跳跃表）

ZSet 的核心实现。多层链表结构，支持 O(logN) 的查找、插入、删除。

```
Level 3:  1 -----------------> 9
Level 2:  1 ------> 5 -------> 9
Level 1:  1 -> 3 -> 5 -> 7 -> 9
```

**面试高频问题：为什么 ZSet 用跳表而不用红黑树？**
- 跳表实现更简单，代码更易维护
- 跳表范围查询更方便（直接遍历底层链表）
- 跳表插入/删除只需修改相邻节点指针，红黑树可能需要旋转
- 跳表通过调整层数概率可以灵活平衡时间和空间

### 2.3 高级数据类型

| 类型 | 用途 |
|------|------|
| HyperLogLog | 基数统计（UV 统计），误差约 0.81%，固定 12KB 内存 |
| Bitmap | 位操作，签到、布隆过滤器 |
| GeoSpatial | 地理位置，附近的人 |
| Stream（5.0+） | 消息队列，类似 Kafka 的消费者组 |

---

## 三、持久化

### 3.1 RDB（Redis Database）

将某一时刻的内存快照以二进制形式写入磁盘。

触发方式：
- `SAVE`：阻塞主线程（生产环境禁用）
- `BGSAVE`：fork 子进程执行，利用 COW（Copy-On-Write）机制
- 配置自动触发：`save 900 1`（900秒内至少1次修改）

优点：
- 文件紧凑，适合备份和灾难恢复
- 恢复速度快（直接加载二进制文件）
- fork 子进程不影响主进程

缺点：
- 可能丢失最后一次快照后的数据
- fork 大内存实例时可能短暂阻塞

### 3.2 AOF（Append Only File）

以追加方式记录每条写命令。

写回策略（`appendfsync`）：
| 策略 | 说明 | 数据安全 | 性能 |
|------|------|---------|------|
| always | 每条命令都 fsync | 最高，最多丢1条 | 最低 |
| everysec | 每秒 fsync（默认） | 最多丢1秒数据 | 折中 |
| no | 由 OS 决定 | 可能丢较多 | 最高 |

AOF 重写（`BGREWRITEAOF`）：
- fork 子进程，根据当前内存状态生成新的 AOF 文件
- 重写期间新命令写入 AOF 重写缓冲区，完成后追加到新文件
- 原子替换旧文件

### 3.3 混合持久化（4.0+）

AOF 重写时，前半部分是 RDB 格式的全量数据，后半部分是 AOF 格式的增量命令。兼顾了恢复速度和数据安全。

**面试回答思路**：先说两种机制的原理和优缺点，再说混合持久化是最佳实践，最后结合业务场景说选择。

> **与其他组件的联系**：持久化机制类似 MySQL 的 redo log（AOF）和数据页刷盘（RDB）。理解 WAL（Write-Ahead Logging）思想有助于理解 AOF。

---

## 四、内存管理与淘汰策略

### 4.1 过期删除策略

Redis 采用 **惰性删除 + 定期删除** 的组合：

- **惰性删除**：访问 key 时检查是否过期，过期则删除。节省 CPU 但可能有大量过期 key 占用内存。
- **定期删除**：每 100ms 随机抽取一批设置了过期时间的 key 检查，删除过期的。如果过期比例 > 25%，继续抽取。

### 4.2 内存淘汰策略（8种）

当内存达到 `maxmemory` 时触发：

| 策略 | 范围 | 说明 |
|------|------|------|
| noeviction | - | 不淘汰，写入报错（默认） |
| allkeys-lru | 所有 key | 淘汰最近最少使用的 |
| allkeys-lfu | 所有 key | 淘汰最不经常使用的（4.0+） |
| allkeys-random | 所有 key | 随机淘汰 |
| volatile-lru | 有过期时间的 key | LRU |
| volatile-lfu | 有过期时间的 key | LFU（4.0+） |
| volatile-random | 有过期时间的 key | 随机 |
| volatile-ttl | 有过期时间的 key | 淘汰 TTL 最小的 |

**面试回答思路**：先说过期删除（惰性+定期），再说内存淘汰（兜底机制），最后说生产环境推荐 `allkeys-lfu` 或 `allkeys-lru`。

> **注意**：Redis 的 LRU 是近似 LRU，通过随机采样（默认5个）选出最久未使用的淘汰，而非维护完整的 LRU 链表。LFU 基于 Morris 计数器实现。

---

## 五、缓存问题

### 5.1 缓存穿透

**定义**：查询一个不存在的数据，缓存和数据库都没有，每次请求都打到数据库。

解决方案：
1. **缓存空值**：查询结果为空也缓存，设置较短 TTL（如 2 分钟）
2. **布隆过滤器**：在缓存前加一层布隆过滤器，不存在的数据直接拦截
3. **参数校验**：接口层做合法性校验

### 5.2 缓存击穿

**定义**：热点 key 过期的瞬间，大量并发请求同时打到数据库。

解决方案：
1. **互斥锁**：只允许一个线程查询数据库并回填缓存，其他线程等待
2. **逻辑过期**：不设置 TTL，在 value 中存储过期时间，发现过期后异步更新
3. **热点 key 永不过期**

### 5.3 缓存雪崩

**定义**：大量 key 同时过期，或 Redis 宕机，请求全部打到数据库。

解决方案：
1. **过期时间加随机值**：避免同时过期
2. **多级缓存**：本地缓存（Caffeine/Guava）+ Redis + 数据库
3. **熔断降级**：使用 Sentinel/Hystrix 限流降级
4. **Redis 高可用**：哨兵/集群模式

**面试回答思路**：三者的区别要讲清楚——穿透是数据不存在，击穿是热点key过期，雪崩是大面积过期或宕机。然后针对每种给出2-3个方案。

> **与其他组件的联系**：布隆过滤器在 HBase、Elasticsearch 中也有应用。熔断降级涉及微服务治理（Sentinel、Hystrix）。

---

## 六、缓存一致性

### 6.1 常见策略

| 策略 | 做法 | 问题 |
|------|------|------|
| Cache Aside（旁路缓存） | 读：先缓存后DB；写：先更新DB再删缓存 | 极端情况下短暂不一致 |
| Read/Write Through | 缓存层代理读写 | 实现复杂 |
| Write Behind | 异步批量写回DB | 可能丢数据 |

### 6.2 Cache Aside 详解（最常用）

**为什么是"先更新DB，再删缓存"而不是"先删缓存，再更新DB"？**

先删缓存的问题：
```
线程A 删除缓存
线程B 读缓存 miss，读DB（旧值），写入缓存
线程A 更新DB
→ 缓存中是旧值，DB是新值，不一致
```

先更新DB再删缓存也有极端情况，但概率极低（需要读请求在写请求之前到达且在写请求之后回填缓存）。

### 6.3 延迟双删

```python
def update(key, value):
    redis.delete(key)          # 第一次删除
    db.update(key, value)      # 更新数据库
    time.sleep(delay)          # 延迟（略大于一次读请求的时间）
    redis.delete(key)          # 第二次删除
```

进一步保证一致性，但 sleep 影响性能，可改为异步延迟删除。

### 6.4 基于消息队列的最终一致性

更新 DB 后发送消息到 MQ（如 Canal 监听 binlog），消费者删除/更新缓存。保证最终一致性。

> **与其他组件的联系**：Canal 监听 MySQL binlog 实现缓存同步，涉及 MySQL 主从复制原理。MQ 保证最终一致性涉及分布式事务。

---

## 七、分布式锁

### 7.1 基本实现

```bash
# 加锁（原子操作）
SET lock_key unique_value NX PX 30000

# 解锁（Lua 脚本保证原子性）
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
```

关键点：
- `NX`：key 不存在才设置（互斥）
- `PX`：设置过期时间（防死锁）
- `unique_value`：防止误删别人的锁
- Lua 脚本：保证判断和删除的原子性

### 7.2 存在的问题

1. **锁过期但业务未完成**：业务执行时间超过锁的过期时间
   - 解决：Redisson 的 WatchDog 机制，自动续期（默认每 10 秒续期到 30 秒）

2. **主从切换导致锁丢失**：主节点加锁后宕机，从节点晋升但没有锁数据
   - 解决：RedLock 算法

### 7.3 RedLock 算法

向 N 个独立的 Redis 实例（建议 5 个）加锁：
1. 获取当前时间
2. 依次向 N 个实例加锁，每个实例设置较短超时
3. 如果在大多数实例（N/2 + 1）上加锁成功，且总耗时 < 锁过期时间，则加锁成功
4. 锁的实际有效时间 = 过期时间 - 加锁耗时

**争议**：Martin Kleppmann 指出 RedLock 在网络分区和时钟漂移场景下仍不安全。如果需要强一致性，应使用 ZooKeeper 或 etcd。

**面试回答思路**：先说基本实现，再说问题和解决方案（WatchDog、RedLock），最后提到 RedLock 的争议，展示深度。

> **与其他组件的联系**：分布式锁还可以用 ZooKeeper（临时顺序节点）、etcd（lease + revision）、MySQL（悲观锁/乐观锁）实现。各有优劣。

---

## 八、高可用架构

### 8.1 主从复制

```
Master (写) → Slave1 (读)
            → Slave2 (读)
```

复制过程：
1. **全量复制**：Slave 首次连接 Master，Master 执行 BGSAVE 生成 RDB 发送给 Slave，期间的写命令存入 repl buffer 随后发送
2. **增量复制**：基于 offset 和 repl_backlog_buffer，Slave 断线重连后只同步缺失的部分
3. **命令传播**：Master 每执行一条写命令，异步发送给所有 Slave

关键概念：
- `repl_backlog_buffer`：环形缓冲区，默认 1MB，存储最近的写命令
- `offset`：主从各自维护的复制偏移量
- 如果 Slave 的 offset 不在 backlog 范围内，触发全量复制

### 8.2 哨兵模式（Sentinel）

解决主从模式下 Master 宕机需要手动切换的问题。

功能：
- **监控**：定期 PING 检测 Master/Slave 是否存活
- **通知**：故障时通知管理员或客户端
- **自动故障转移**：Master 宕机时自动选举新 Master

故障判定：
- **主观下线（SDOWN）**：单个 Sentinel 认为节点不可达
- **客观下线（ODOWN）**：超过 quorum 个 Sentinel 认为 Master 不可达

Leader 选举（Raft 算法变体）：
1. 发现 Master 客观下线的 Sentinel 发起投票
2. 获得多数票的 Sentinel 成为 Leader
3. Leader 执行故障转移

新 Master 选举优先级：
1. slave-priority 最小的
2. 复制偏移量最大的（数据最新）
3. runid 最小的

### 8.3 Cluster 集群模式

Redis Cluster 采用去中心化架构，数据分片存储。

**数据分片：哈希槽（Hash Slot）**
- 共 16384 个槽，分配到各节点
- `slot = CRC16(key) % 16384`
- 每个节点负责一部分槽

```
Node A: 0 - 5460
Node B: 5461 - 10922
Node C: 10923 - 16383
```

**Gossip 协议**：
- 节点间通过 Gossip 协议交换状态信息
- MEET、PING、PONG、FAIL 消息
- 最终一致性，收敛时间与节点数相关

**故障转移**：
- 类似哨兵机制，由集群中其他 Master 投票
- Slave 自动晋升为 Master 接管槽

**面试回答思路**：主从 → 哨兵 → 集群，逐步演进。主从解决读写分离，哨兵解决自动故障转移，集群解决数据量和写入瓶颈。

> **与其他组件的联系**：
> - 哈希槽类似一致性哈希（但不完全相同），Cassandra、DynamoDB 使用一致性哈希
> - Gossip 协议在 Cassandra、Consul 中也有应用
> - Raft 算法在 etcd、TiKV 中广泛使用

---

## 九、Redis 事务与 Lua 脚本

### 9.1 事务

```bash
MULTI        # 开始事务
SET key1 v1  # 命令入队
SET key2 v2  # 命令入队
EXEC         # 执行
```

特点：
- 不支持回滚（与 MySQL 事务的重要区别）
- 命令语法错误：整个事务不执行
- 命令运行时错误：其他命令正常执行，出错命令跳过
- WATCH 实现乐观锁：EXEC 时如果被 WATCH 的 key 被修改，事务取消

### 9.2 Lua 脚本

```bash
EVAL "return redis.call('set', KEYS[1], ARGV[1])" 1 mykey myvalue
```

优势：
- 原子性执行多条命令（比 MULTI/EXEC 更强）
- 减少网络往返
- 可复用（EVALSHA）

典型应用：分布式锁的释放、限流器、原子性的复合操作。

---

## 十、实际应用场景

### 10.1 分布式 Session

将 Session 存储在 Redis 中，所有应用服务器共享。Spring Session + Redis 是常见方案。

### 10.2 限流

**滑动窗口限流**（ZSet 实现）：
```bash
# 记录请求时间戳
ZADD rate_limit:{user_id} {timestamp} {unique_id}
# 移除窗口外的记录
ZREMRANGEBYSCORE rate_limit:{user_id} 0 {timestamp - window}
# 统计窗口内请求数
ZCARD rate_limit:{user_id}
```

**令牌桶/漏桶**：Lua 脚本实现原子操作。

### 10.3 延迟队列

使用 ZSet，score 为执行时间戳：
```bash
ZADD delay_queue {execute_timestamp} {task_json}
# 消费者轮询
ZRANGEBYSCORE delay_queue 0 {current_timestamp} LIMIT 0 1
```

### 10.4 排行榜

```bash
ZADD leaderboard {score} {user_id}
ZREVRANGE leaderboard 0 9 WITHSCORES  # Top 10
ZRANK leaderboard {user_id}            # 用户排名
```

### 10.5 消息队列对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| List（LPUSH/BRPOP） | 简单 | 不支持消费者组、消息可能丢失 |
| Pub/Sub | 实时性好 | 消息不持久化、离线消息丢失 |
| Stream（5.0+） | 支持消费者组、消息持久化、ACK | 功能不如专业 MQ |

> **与其他组件的联系**：如果需要可靠的消息队列，应使用 RabbitMQ、Kafka、RocketMQ。Redis Stream 适合轻量级场景。

---

## 十一、性能优化

### 11.1 BigKey 问题

**定义**：String > 10KB，Hash/List/Set/ZSet 元素数 > 5000。

危害：
- 内存不均（集群场景下数据倾斜）
- 阻塞（删除大 key 会阻塞主线程）
- 网络拥塞

解决：
- `redis-cli --bigkeys` 扫描
- `MEMORY USAGE key` 查看内存占用
- 拆分大 key（如按时间、按哈希分片）
- 异步删除：`UNLINK` 代替 `DEL`（4.0+，后台线程删除）

### 11.2 热 Key 问题

解决：
- 本地缓存（JVM 缓存热点数据）
- 读写分离 + 多从节点分摊读压力
- key 加后缀分散到不同节点

### 11.3 Pipeline

批量发送命令，减少网络 RTT：
```python
pipe = redis.pipeline()
for i in range(1000):
    pipe.set(f"key:{i}", f"value:{i}")
pipe.execute()  # 一次网络往返
```

### 11.4 慢查询

```bash
SLOWLOG GET 10          # 查看最近10条慢查询
CONFIG SET slowlog-log-slower-than 10000  # 超过10ms记录
```

避免 O(N) 命令：`KEYS *`（用 `SCAN` 替代）、`HGETALL`（大 Hash 用 `HSCAN`）。

---

## 十二、Redis 与其他技术的关系总结

| 技术 | 与 Redis 的关系 |
|------|----------------|
| MySQL | Redis 作为缓存层，减轻 DB 压力；Canal 监听 binlog 同步缓存 |
| Spring | Spring Cache 抽象、Spring Session、Spring Data Redis |
| MQ（Kafka/RabbitMQ） | Redis 可做轻量级消息队列，重度场景用专业 MQ |
| ZooKeeper/etcd | 分布式锁的替代方案，强一致性场景优先选择 |
| Elasticsearch | 都可做缓存/加速查询，ES 侧重全文搜索，Redis 侧重 KV 和数据结构 |
| Docker/K8s | Redis 容器化部署，注意持久化卷挂载和网络配置 |
| 微服务 | 分布式 Session、分布式锁、限流、配置中心（结合 Nacos 等） |

---

## 十三、面试常见问题速查

1. **Redis 为什么快？** → 内存 + 单线程 + IO多路复用 + 高效数据结构
2. **Redis 和 Memcached 区别？** → 数据结构丰富、支持持久化、支持集群、单线程
3. **缓存穿透/击穿/雪崩？** → 不存在/热点过期/大面积过期，各有对应方案
4. **如何保证缓存一致性？** → Cache Aside + 延迟双删 + MQ 最终一致
5. **分布式锁怎么实现？** → SET NX PX + Lua + WatchDog + RedLock
6. **Redis 集群原理？** → 16384 哈希槽 + Gossip + 故障转移
7. **持久化怎么选？** → 混合持久化（RDB+AOF），兼顾速度和安全
8. **BigKey 怎么处理？** → 扫描发现 + 拆分 + UNLINK 异步删除
9. **Redis 事务和 MySQL 事务区别？** → 不支持回滚，不保证原子性（部分失败继续执行）
10. **为什么用跳表不用红黑树？** → 实现简单、范围查询方便、内存友好

---

## 十四、Python Web + AI 应用场景下 Redis 的角色（重点）

> 以本项目（FastAPI + ChromaDB + Anthropic Claude RAG 应用）为例，讲解 Redis 在真实 AI 应用架构中的定位。

### 14.1 整体架构中 Redis 的位置

```
用户请求
  │
  ▼
┌─────────────┐     ┌───────────┐     ┌──────────────┐
│  FastAPI     │────▶│  Redis    │     │  ChromaDB    │
│  (Web 层)   │     │  (缓存层)  │     │  (向量数据库) │
└──────┬──────┘     └───────────┘     └──────────────┘
       │                                     ▲
       │         ┌──────────────┐            │
       └────────▶│  Anthropic   │   Embedding + Retrieval
                 │  Claude API  │
                 │  (LLM 推理)  │
                 └──────────────┘
```

在这个架构中，Redis 处于 Web 层和下游服务之间，承担缓存、限流、任务队列等多重角色。

### 14.2 Redis 与 FastAPI 的关系

#### 1) API 限流（Rate Limiting）

LLM API 调用成本高，必须限流。Redis 是最常用的限流后端：

```python
# FastAPI + redis 限流示例
import redis.asyncio as aioredis
from fastapi import Request, HTTPException

redis_client = aioredis.from_url("redis://localhost:6379")

async def rate_limit(request: Request, limit: int = 10, window: int = 60):
    """滑动窗口限流"""
    key = f"rate:{request.client.host}"
    current = await redis_client.incr(key)
    if current == 1:
        await redis_client.expire(key, window)
    if current > limit:
        raise HTTPException(status_code=429, detail="请求过于频繁")
```

与 FastAPI 中间件或依赖注入结合，可以做到：
- 按用户/IP 限流
- 按 API 路由限流（`/qa` 接口比 `/health` 更需要限流）
- 按 token 消耗量限流（AI 场景特有）

#### 2) 异步任务队列

大文件 ingest（文档解析 + embedding）是耗时操作，不应阻塞 HTTP 请求：

```python
# 生产者：FastAPI 路由
async def ingest_document(file):
    task_id = str(uuid4())
    await redis_client.lpush("ingest_queue", json.dumps({
        "task_id": task_id,
        "file_path": file.path
    }))
    return {"task_id": task_id, "status": "queued"}

# 消费者：后台 Worker
async def worker():
    while True:
        _, task_json = await redis_client.brpop("ingest_queue")
        task = json.loads(task_json)
        # 执行 document_loader → text_splitter → embedding_service → vector_store
        await redis_client.set(f"task:{task['task_id']}", "completed")
```

> **与 Celery 的关系**：生产环境通常用 Celery + Redis（作为 broker）来管理异步任务，而不是手写队列。Redis 在这里充当消息中间件的角色，类似轻量版 RabbitMQ。

#### 3) Session / 认证状态管理

```python
# 存储用户 session 或 API key 的使用状态
await redis_client.setex(f"session:{session_id}", 3600, user_data_json)

# JWT token 黑名单（用户登出后使 token 失效）
await redis_client.setex(f"blacklist:{token_jti}", token_remaining_ttl, "1")
```

### 14.3 Redis 与 LLM API（Anthropic Claude）的关系

#### 1) LLM 响应缓存（语义缓存）

LLM 调用是整个链路中最贵、最慢的环节。对相同或相似问题缓存响应可以大幅降低成本：

```python
import hashlib

async def cached_llm_call(prompt: str, context: str) -> str:
    # 方案1：精确匹配缓存
    cache_key = f"llm:{hashlib.sha256(f'{prompt}:{context}'.encode()).hexdigest()}"
    cached = await redis_client.get(cache_key)
    if cached:
        return cached.decode()

    # 缓存未命中，调用 Claude API
    response = await anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"}]
    )
    answer = response.content[0].text

    # 缓存结果，设置 TTL（知识可能更新，不宜永久缓存）
    await redis_client.setex(cache_key, 3600, answer)
    return answer
```

进阶方案——语义缓存：
- 对用户问题做 embedding，在 Redis 中用向量相似度搜索（Redis Stack 支持向量搜索）
- 相似度超过阈值则返回缓存结果，避免重复调用 LLM
- 这比精确匹配命中率高得多

#### 2) Token 用量追踪与计费

```python
# 每次 LLM 调用后记录 token 消耗
await redis_client.hincrby(f"usage:{user_id}:{date}", "input_tokens", input_count)
await redis_client.hincrby(f"usage:{user_id}:{date}", "output_tokens", output_count)
await redis_client.hincrby(f"usage:{user_id}:{date}", "requests", 1)

# 检查是否超出配额
total = int(await redis_client.hget(f"usage:{user_id}:{date}", "input_tokens") or 0)
if total > DAILY_TOKEN_LIMIT:
    raise HTTPException(status_code=429, detail="今日 token 配额已用完")
```

#### 3) 流式响应的中间缓冲

Claude API 支持 streaming，多个客户端问同一个问题时可以用 Redis Pub/Sub 广播：

```python
# 第一个请求：调用 LLM 并发布到 channel
async for chunk in stream_response:
    await redis_client.publish(f"stream:{question_hash}", chunk)

# 后续相同请求：订阅 channel 获取结果
pubsub = redis_client.pubsub()
await pubsub.subscribe(f"stream:{question_hash}")
```

### 14.4 Redis 与向量数据库（ChromaDB）的关系

```
用户查询 → Redis 缓存检查 → 未命中 → ChromaDB 向量检索 → 结果写入 Redis
                ↓ 命中
           直接返回缓存的检索结果
```

#### 1) 检索结果缓存

向量检索虽然比 LLM 调用快，但在高并发下仍是瓶颈：

```python
async def cached_retrieval(query: str, top_k: int = 5) -> list:
    cache_key = f"retrieval:{hashlib.md5(query.encode()).hexdigest()}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # ChromaDB 向量检索
    results = vector_store.query(query_embedding, n_results=top_k)

    # 缓存检索结果（TTL 较短，因为文档可能更新）
    await redis_client.setex(cache_key, 300, json.dumps(results))
    return results
```

#### 2) Embedding 缓存

同一段文本的 embedding 是确定性的，可以缓存避免重复计算：

```python
async def cached_embedding(text: str) -> list[float]:
    cache_key = f"emb:{hashlib.sha256(text.encode()).hexdigest()}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    embedding = embedding_model.encode(text).tolist()
    # embedding 不会变，可以长期缓存
    await redis_client.set(cache_key, json.dumps(embedding))
    return embedding
```

这在批量 ingest 文档时特别有用——如果文档部分内容未变，可以跳过 embedding 计算。

#### 3) 文档索引状态管理

```python
# 记录哪些文档已经被索引
await redis_client.sadd("indexed_docs", doc_hash)

# 检查文档是否需要重新索引
if await redis_client.sismember("indexed_docs", doc_hash):
    logger.info("文档已索引，跳过")
    return
```

### 14.5 Redis 与 Celery（异步任务框架）的关系

在 AI 应用中，很多操作是重计算、长耗时的：

```
FastAPI ──任务投递──▶ Redis (Broker) ──▶ Celery Worker
                                            │
                                    ┌───────┴───────┐
                                    │ 文档解析       │
                                    │ Embedding 计算  │
                                    │ 批量向量入库    │
                                    │ LLM 批量推理    │
                                    └───────────────┘
                                            │
                                    Redis (Backend) ◀── 结果存储
```

```python
# celery_app.py
from celery import Celery

app = Celery("tasks", broker="redis://localhost:6379/0",
             backend="redis://localhost:6379/1")

@app.task(bind=True, max_retries=3)
def ingest_task(self, file_path: str):
    """文档摄入任务：解析 → 分块 → embedding → 存入向量库"""
    try:
        docs = document_loader.load(file_path)
        chunks = text_splitter.split(docs)
        embeddings = embedding_service.encode(chunks)
        vector_store.add(chunks, embeddings)
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
```

Redis 在 Celery 中同时扮演两个角色：
- **Broker**（消息中间件）：存储待执行的任务消息
- **Backend**（结果存储）：存储任务执行结果和状态

### 14.6 Redis 与 Docker/容器化部署的关系

结合本项目的 Dockerfile，生产部署通常用 docker-compose 编排：

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - chromadb
    environment:
      - REDIS_URL=redis://redis:6379/0

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data        # 持久化
    command: redis-server --appendonly yes  # 开启 AOF

  chromadb:
    image: chromadb/chroma
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma

volumes:
  redis_data:
  chroma_data:
```

关键点：
- `depends_on` 确保 Redis 先于应用启动
- 挂载 volume 保证 Redis 数据持久化
- 容器间通过服务名（`redis`）通信，不用 IP
- Alpine 镜像体积小，适合生产环境

### 14.7 Python Redis 客户端选型

| 客户端 | 特点 | 适用场景 |
|--------|------|---------|
| redis-py | 官方客户端，同步 | 简单脚本、同步框架（Flask） |
| redis.asyncio（redis-py 内置） | 异步支持 | FastAPI、asyncio 应用 |
| aioredis | 早期异步客户端（已合并入 redis-py） | 历史项目 |
| redis-om-python | 对象映射（类似 ORM） | 需要结构化数据模型 |

FastAPI 项目推荐使用 `redis.asyncio`：

```python
# app/core/redis.py
import redis.asyncio as aioredis
from app.config import settings

redis_pool = aioredis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=20,
    decode_responses=True
)

async def get_redis() -> aioredis.Redis:
    """FastAPI 依赖注入"""
    return aioredis.Redis(connection_pool=redis_pool)
```

### 14.8 完整请求链路中 Redis 的参与点

```
用户提问 "这段代码是什么意思？"
  │
  ▼
[1] FastAPI 接收请求
  │
  ▼
[2] Redis: 限流检查（rate_limit:{ip}）  ← 超限直接返回 429
  │
  ▼
[3] Redis: 查询缓存（llm:{query_hash}） ← 命中直接返回
  │
  ▼
[4] Redis: embedding 缓存检查           ← 命中跳过计算
  │  未命中 → sentence-transformers 计算 embedding → 写入缓存
  ▼
[5] ChromaDB: 向量检索 top-k 相关文档
  │  （检索结果也可缓存到 Redis）
  ▼
[6] prompt_builder: 组装 context + question
  │
  ▼
[7] Anthropic Claude API: LLM 推理生成回答
  │
  ▼
[8] Redis: 缓存 LLM 响应 + 记录 token 用量
  │
  ▼
[9] 返回结果给用户
```

一次请求中 Redis 最多参与 5 个环节（限流、查询缓存、embedding 缓存、检索缓存、结果写回），是整个链路的性能加速器和成本控制器。

### 14.9 面试回答思路总结

当被问到"Redis 在你的 AI 项目中怎么用的"时，按这个框架回答：

1. **先说架构**：FastAPI + Redis + 向量数据库 + LLM API 的整体架构
2. **再说核心场景**：
   - LLM 响应缓存（降本提速，这是 AI 应用最独特的点）
   - API 限流（保护下游 LLM 服务）
   - 异步任务队列（文档 ingest 等重计算任务）
   - Embedding 缓存（避免重复计算）
3. **最后说技术细节**：用了 redis.asyncio 配合 FastAPI 的异步模型，连接池管理，TTL 策略等
4. **加分项**：提到语义缓存（向量相似度匹配）、token 用量追踪、与 Celery 的配合
