# 04 · CPA / CAP 合同与跨平台监控协议

## 文档状态与执行边界

本文件属于 `proposals/2026-11-25-native-android-independent` 候选启动企划，**尚未被用户选定为正式实施基准**。它为独立 Android 仓库提供可执行的协议设计与验收要求，不表示应用、服务、迁移程序或测试已经实现。

唯一代码基线为 [`rinmashiro0529/cpa-quota-ios@80beea9ed251a628307825cba99290b5f246575b`](https://github.com/rinmashiro0529/cpa-quota-ios/tree/80beea9ed251a628307825cba99290b5f246575b)。本方案未阅读、采用或修改 Android 仓库原有企划。iOS PR #33、#34 在本轮核实时仍未合并；本文件不把它们的行为视为主线事实。

以下三种标识用于区别证据与设计：

- **【现状】**：可以在上述固定提交中定位的行为；不等于真实部署已兼容，也不等于本轮执行过测试。
- **【候选决定】**：本企划给出的默认实施方案，必须通过合同评审和后述验证才能进入实现基线。
- **【待验证】**：需要真实 CPA / CAP 实例、Android 设备、推送配置或故障注入才能确认的事项。

“完整移植”包含额度、CAP、账号诊断、连接管理、聊天，以及监控的授权、注册、期限、刷新、停止、恢复、令牌轮换、状态解释与 Android 系统呈现。**仅能读取监控缓存、仅显示通知样式、仅在前台运行，均不满足完整监控发布门槛。** 开发阶段可以分批交付，但最终发布范围不得静默删减。[07-delivery-plan.md](07-delivery-plan.md) 管理交付依赖；[08-verification-and-release.md](08-verification-and-release.md) 管理最终证据。

本文件负责 HTTP、数据语义、业务状态及 Go 服务演进。模块依赖见 [03-architecture.md](03-architecture.md)；聊天请求和存储见 [05-chat-and-storage.md](05-chat-and-storage.md)；Keystore、Android 进程与后台限制、通知权限及分发差异见 [06-android-platform-security.md](06-android-platform-security.md)。

Go 服务的唯一长期源码仍是 iOS 来源仓库的 `Services/QuotaMonitor`，协议 / 兼容改造由 TASK-023、FCM adapter 由 TASK-025 在该仓库提交独立 PR。Android 仓库保存客户端和带来源版本的合同 / 夹具，不复制出第二套长期分叉 Go 服务。合同文件的跨仓同步也必须固定版本，并由 TASK-022 记录唯一权威版本。

## 1. 必须先冻结的合同产物

在实现页面和生产网络调用之前，提交以下可审查产物；这是一组待创建的交付物名称，不表示已有文件：

| 产物 | 内容与验收要求 |
| --- | --- |
| `contracts/cpa/endpoint-matrix.md` | 本章端点、方法、凭据种类、成功形状、错误作用域和明确允许的兼容回退；每项绑定固定源码依据 |
| `contracts/cpa/fixtures/` | inventory、provider、额度 envelope、Codex、xAI、插件、管理与上游错误的合成 JSON；不得含真实密钥或账号 |
| `contracts/cap/fixtures/` | 窗口、独立资源、分页、缺字段、UInt64 边界、成本与 TPS 的输入和规范化输出 |
| `contracts/monitor/v1/` | 现有 HTTP v1、快照、取消和持久记录兼容向量，作为 Go 服务改造的非退化依据 |
| `contracts/monitor/v2/openapi.yaml` | 本章拟议 v2 的完整请求、响应、错误码、认证、大小限制、幂等与状态定义 |
| `contracts/monitor/v2/events/` | 注册、取消先到、重放、令牌轮换、采集与推送回调交错、重启和存储故障的事件序列 |
| `contracts/parity-decisions.md` | Swift / Go 已知差异、Android 默认决定、理由、对应测试，以及尚未批准的差异 |

纯 Kotlin/JVM 合同测试先消费这些夹具；Go 改造也消费同一规范化向量。共享的是版本化合同与测试数据，不要求为了复用 Swift 代码而嵌入另一套运行时。多语言对金额或浮点结果的比较必须声明精度和容差；身份、状态、计数、时间边界与重试次数须精确相等。

## 2. 端点与认证边界

### 2.1 服务器地址是有类型的值

【现状】`CPAServer` 只接受 HTTPS；拒绝 URL 中的 user/password、query、fragment、反斜线、非法端口和解码后形成的 `.` / `..` / 分隔符路径段；规范化 scheme、host、默认 443 端口和尾斜线，并识别已有 `/v0/management`、`/management.html` 后缀。代理部署的路径前缀必须保留。管理密钥经 trim 后非空、最多 4096 UTF-8 字节且不能含控制字符。[S01]

【候选决定】定义 `ServerEndpoint`，只由一个经测试的解析入口构造。以下示例中的 `{base}` 指规范化后仍包含代理前缀的完整基址：

```text
输入：https://quota.example.test/team-a/management.html
基址：https://quota.example.test/team-a
账号：https://quota.example.test/team-a/v0/management/auth-files
模型：https://quota.example.test/team-a/v1/models
```

不能用根路径 `/v0/...` 解析覆盖 `/team-a`；也不能先 URL-decode 全路径再重编码，改变 `%25`、Unicode 或已有编码的含义。域名、端口、IPv6 与路径编码组合应进入合同夹具。HTTPS 证书信任策略由 06 章定义，禁止“兼容自建服务”成为 trust-all 或绕过主机名校验的理由。

### 2.2 凭据种类不得互用

| 凭据 | 用途 | 明确禁止 |
| --- | --- | --- |
| CPA 管理密钥 | inventory、quota providers、quota fetch、api-call、管理统计、读取服务器客户端密钥列表 | 自动作为推理 API Key、搜索 Key、监控 bridge token；写入 URL、通知、日志或诊断导出 |
| CPA 客户端 API Key | 模型目录、聊天推理 | 将推理 401 判为管理凭据失效；为模型请求附带管理密钥 |
| CAP anonymous 访问 | 部署方明确允许的公开统计资源 | 收到 401/403 后自动改用管理密钥 |
| 独立监控 bridge token | 当前 principal 的监控授权、会话与安全缓存 | 当作 CPA 管理密钥或平台 push token；用公开 healthz 替代验证 |
| 平台投递 token | APNs / FCM 等投递寻址 | 当作用户授权凭据；日志明文、URL 参数、跨 principal 复用；对 opaque token 做大小写规范化 |
| 第三方搜索 Key | 对应搜索 provider | 与 CPA 或监控凭据混存于无类型的通用字符串槽位 |

凭据在 Android 的内存、持久化和退出语义见 06 章。协议对象只能持有凭据引用或经过限制的秘密类型；`toString()`、异常信息、HTTP BODY 日志和 Compose 状态输出必须脱敏。

### 2.3 CPA 与推理基础端点

【现状】下表取自客户端实现；它是“当前客户端如何调用”，不是对任意 CLIProxyAPI 版本的兼容承诺。[S02][S03][S04]

| 方法与相对路由 | 认证 / 作用 | 当前成功语义及允许回退 |
| --- | --- | --- |
| `GET v0/management/auth-files` | 管理 Bearer；账号清单 | 权威账号清单；用于初次连接验证。不得因其它可选能力失败而伪造空清单 |
| `GET v0/management/quota/providers` | 管理 Bearer；插件额度能力 | 数组或包含 `providers` 的对象。404/501 表示该可选端点不可用；其它非鉴权、非限流的能力失败可保留清单并显示能力警告 |
| `POST v0/management/quota/fetch` | 管理 Bearer；请求体含 `auth_index` | 已声明支持插件额度的账号优先使用；直接解析插件 payload。501 映射不支持该 provider，不自动再发另一条额度请求 |
| `POST v0/management/api-call` | 管理 Bearer；固定受支持的上游额度读取 | 请求体含 `auth_index`、`method: GET`、固定上游 URL 与所需 header；需解析外层 HTTP 与内层 `status_code` 两层状态 |
| `GET v0/management/api-keys` | 管理 Bearer；发现客户端推理 Key | 当前实现接受 `{"api-keys": [...]}`、null 或数组形状；去除非法值及重复 Key |
| `GET v8/management/config/access/api-keys` | 同上；仅前一步 endpoint-unavailable 时 | 兼容回退。源码把 404 **和 501** 都映射 endpoint-unavailable；两条路由都不可用返回“未发现可用列表”，不是证明服务器没有客户端 Key |
| `GET v1/models` | 客户端 API Key；推理目录 | 读取 `data[].id` 和可选 `owned_by`，去重并排序。独立于管理熔断，不把失败归因到管理 Key |
| `POST v1/chat/completions` 及聊天协议分支 | 客户端推理凭据 | 流式协议、模型与推理参数兼容、Anthropic 分支和禁止重复计费规则由 05 章完整规定 |

`api-call` 当前 Codex 固定目标为 `https://chatgpt.com/backend-api/wham/usage`，xAI 为 `https://cli-chat-proxy.grok.com/v1/billing`。Codex 在 inventory 已证实身份时带对应 `Chatgpt-Account-Id`；`Bearer $TOKEN$` 是交由 CPA 处理的占位机制，不是手机持有或显示上游 OAuth Token。Android 不提供任意 URL 的开放代理界面，不在本移植中新增上游 OAuth 登录或账号修改。[S02]

**允许回退是一张白名单，不是通用“失败就换 API”。** 401、403、429、TLS 错误、响应超限和 HTTP 200 解码失败均不得触发另一套凭据或路由的盲试。没有固定源码或已验证合同支持的全局 `/v0` → `/v8` 切换不得实现。

### 2.4 CAP 端点

【现状】CAP 依赖外部 `cap-token-usage-tracker`。当前仓库合同参考其固定提交，不能据此认定用户真实实例版本。CAP 用量不是额度窗口，也不能按邮箱、昵称、`source` 或模型名强行关联为一个账号。[S05][S06]

所有下表资源均为 GET，查询包含 `range=custom`、RFC3339 `start`、`end`，并保留 `{base}` 前缀：

| 相对路由 | 凭据 | 用途 |
| --- | --- | --- |
| `v0/management/plugins/cap-token-usage-tracker/stats` | 管理 Bearer | 原始统计、维度分组和时间序列；不能自动作为资源接口失败后的隐藏回退 |
| `v0/resource/plugins/cap-token-usage-tracker/stats/initial` | 显式 anonymous 或管理 Bearer | 初始概览、模型汇总、桶宽、保留起点 |
| `v0/resource/plugins/cap-token-usage-tracker/stats/trends` | 同上 | 模型趋势与时间桶 |
| `v0/resource/plugins/cap-token-usage-tracker/stats/groups` | 同上；另带 offset/limit | 单页详细分组、total |
| `v0/resource/plugins/cap-token-usage-tracker/costs` | 同上 | USD 估算、价格覆盖、缺价列表、价格簿版本 |
| `v0/resource/plugins/cap-token-usage-tracker/requests` | 同上；另带 offset/limit | 单页请求明细；有界样本集合由客户端分页组合 |

在首次绑定时固定 `CAPResourceAccess`，重试不改变它。404 为 `PluginUnavailable`；anonymous 401/403 为资源访问拒绝，不清空管理连接。资源与管理权限的实际代理配置必须在受控部署上验证。

## 3. 通用传输、错误与请求协调

### 3.1 网络默认值与边界

【现状】普通读取的 `URLSessionTransport` 默认 75 秒、单响应最多 4,194,304 字节，拒绝全部重定向；禁用共享 cookie、URL cache 和凭据缓存。既检查声明长度，也在接收实际数据时限制大小，取消最多完成一次 continuation。[S07]

【候选决定】Android 管理、CAP、模型目录和监控控制使用可注入的传输接口，以 OkHttp 实现时必须显式配置以下行为：

- 禁止自动 HTTP / HTTPS 重定向；3xx 作为安全的 `RedirectRefused` 返回，不转发 Authorization。
- 无全局 CookieJar；无隐式 HTTP 缓存；需要的业务缓存由 Repository 存储并带身份、时间与状态。
- 普通调用采用 75 秒完整调用预算作为初始兼容值；DNS、连接、读取和取消路径不得留下无限等待。流式推理另按 05 章设计，不使用整个响应缓存和普通总时限。
- 4 MiB 上限针对实际交付解码器的响应字节，不能只相信 Content-Length。压缩、未知长度、chunked 响应也在测试范围。
- 错误采用允许列表类型。任意响应正文、HTTP 认证头、原始网络异常中的 URL/账户信息不进入用户提示或默认日志。
- 客户端重试只用于已明确可重放的读取。创建、停止、令牌轮换等操作按幂等合同对账；不能统一配置“所有失败重试三次”。

这里的额度 / CAP 业务缓存默认是会话内快照，与 03 章一致，不默认写入 Room 或磁盘。用户明确开启的小组件最小投影、必要监控恢复记录有独立持久化合同；若新增全量额度 / CAP 磁盘缓存，先记录保留期限、身份隔离、删除和备份决定。

### 3.2 错误作用域矩阵

| 观察结果 | 规范化错误 / 范围 | Android 必须表现 | 不得执行 |
| --- | --- | --- | --- |
| 管理端点外层 HTTP 401 | `ManagementUnauthorized`；连接的管理作用域 | 阻断该已接受连接的后续管理请求，保留安全的上次数据及重新验证入口 | 用缓存冒充授权仍有效、反复更换端点试 Key |
| 管理端点外层 HTTP 403 | `ManagementForbidden`；同上 | 区别权限不足与网络故障 | 自动转匿名或把错误改为 0 |
| `api-call` 外层 2xx，内层 401/403 | `UpstreamUnauthorized`；指定账号 | 该账号错误；其余允许账号继续 | 熔断整个管理连接、把管理 Key 标为错误 |
| 管理层 429 | `ManagementRateLimited`；共享协调器 | 按有效 Retry-After 及明确的保守策略等待；显示 deadline | force、重新进入页面、换 CAP 路由绕过 |
| 上游内层 429 | `AccountRateLimited`；单账号 | 保留该账号冷却，其他账号仍可读取 | 把一个账号的冷却误扩展到全部管理请求 |
| anonymous CAP 429 | `ResourceRateLimited`；当前 CAP 资源客户端 | 不同 CAP 资源共同遵守该资源冷却 | 改走另一资源路由或附管理 Key 绕过 |
| 可选 quota/providers 404/501 | `CapabilityUnavailable` | 显示清单，按已知 provider 支持范围工作 | 把能力不存在解释为管理鉴权失败 |
| CAP 404 | `PluginUnavailable` | 单独说明插件路由不可用，其它工作区可用 | 显示全零用量 |
| 2xx 但结构不合法 | `InvalidResponse` | 保留上次有效快照，显示本次读取失败 | 自动切认证、路由或产生新“成功观察时间” |
| 响应过大 | `ResponseTooLarge` | 取消传输；显示预算限制 | 无界继续读取或保存原始大正文 |
| 用户取消、会话被替换 | `Cancelled` / `Superseded` | 停止发布，清理 loading，保留既有业务证据 | 显示网络失败、悄悄恢复已关闭候选连接 |

当前 Swift 将外层 401/403 与内层 401/403 分开；监控 bridge 的 401 又是第三个独立授权领域。Repository 必须携带 `ErrorScope`，不能只用 `Int statusCode` 决定全局退出。[S02][S08][S09]

### 3.3 并发、共享调用与取消

【现状】管理调用共享 `CPAManagementRequestCoordinator`，并发上限 3。inventory、额度、CAP 和 Key discovery 不能各自拥有独立预算。清单先显示，额度渐进发布；CAP 四详情端点顺序读取，最多一个详情端点在途。[S02][S10][S11][S12]

【候选决定】每个已接受的连接上下文持有一个 `ManagementRequestCoordinator`，以 `ConnectionId + credentialRevision` 隔离凭据领域，并以规范化服务器身份关联应共享的限流。不同 principal 的 401 不应仅因同域名被广播给其它凭据；同一凭据通过不同页面访问同一服务又不能绕过配额。候选连接有自己的任务代际；何时取代旧连接只能由会话协调器决定。

当前 Swift 同账号 single-flight 的语义是**任一等待者取消会取消整个共享调用**。本企划默认保留这一对外可观察语义，但把共享调用归属明确放在会话的刷新操作中：纯 UI 取消收集 StateFlow 不等于取消业务刷新；用户取消刷新、关闭未提交候选或替换会话才取消对应操作。若改成引用计数订阅者取消，必须作为 `PARITY-02` 行为变更另行评审，不能在实现时悄悄改变。[S02]

每次请求携带不可变的 `RequestContext(connectionId, credentialRevision, generation, operationId)`。传输返回、JSON 解码之后、写缓存之前、发布 UiState 之前均确认上下文仍有效。取消必须传播到底层 call；即使底层无法及时停止，generation 校验仍禁止迟到结果提交。

连接提交顺序固定为：候选输入校验 → 验证权威清单 → 构建关联客户端 → 执行凭据事务 → 检查事务版本与取消状态 → 一次性接受 quota/CAP/chat 绑定 → 渐进加载后续数据。候选失败保留旧连接；关闭候选同步擦除秘密草稿并作废 generation，再执行异步清理。[S13]

### 3.4 Retry-After 与时钟

【现状】管理 429 缺少有效期限时保守等待 60 秒。上游的 `header` / `headers` 键大小写不敏感；Retry-After 可为标量或数组，取第一个可解析项。Swift 与 Go 对过期日期、很短期限的本地保护存在差异，不能宣称两端所有重试策略已相同。[S05][S08][S14]

【候选决定】Android 将 `serverRetryDeadline`、`effectiveRetryDeadline` 与原因分别记录。默认策略为：有效未来 deadline 至少遵守到该时刻；缺失、非法或已经过去的 429 deadline 采用 60 秒保守冷却；剩余时间显示向上取整，不能负数。该决定明确记为 `PARITY-03`，通过固定向量与 Go 比较，避免“解析成功但立即循环请求”。

使用 wall-clock 表达协议绝对时间；使用 monotonic clock 处理当前进程内的超时与最小等待。进程重启后不能用不存在的 monotonic 起点推算旧 deadline。系统时间显著回拨时显示时钟异常，按已保存的安全状态重新验证，不能把旧数据变成新数据或缩短不可缩短的注册重放保护。

## 4. 额度字段、身份与数据保真

### 4.1 身份与数值类型

【现状】清单身份按 `id` → `name` → `auth_index` 选择，查询还依赖 authIndex、provider 与可选 Codex 账户身份。数字身份仅接受可证明无损的安全整数，超过 ±(2^53−1)、布尔、非整值、已经丢精度的浮点来源均不能转成另一个 ID；大身份要求字符串。CAP sequence 有单独 UInt64 合同。[S05][S08]

【候选决定】

- `AccountId`、`AuthIndex`、`SourceId`、`SafeAlias`、`ModelId`、`ApiKeyIdentity` 是不同类型；不得用一个任意字符串进行隐式转换。
- 账号缓存主键包含服务器 / 凭据上下文和完整凭据身份指纹，不只包含展示名。身份指纹为本地或服务端内部材料，不放入通知、公共快照、分析事件。
- 计数与 sequence 使用无损整数处理。JSON 解析器不能将所有数字统一经过 Double；UInt64 最大值、越界值、负值、小数各有测试。
- 金额内部默认采用保留输入精度的十进制表示，格式化时才舍入；既有 Swift Double 夹具使用声明容差比较。额度比例保持合法原值，图形值另行限幅。
- 对读取响应可以忽略无关新增字段以保持兼容，但已使用字段必须严格校验；未知协议版本或影响状态机的新枚举不得当作成功默认值。

### 4.2 快照状态不能压成一个百分比

| 字段 / 情况 | 必须保留的含义 |
| --- | --- |
| `usedFraction = 0` | 有效零使用，不能当 false / nil |
| `usedFraction = 1` | 已读到 100% 使用；是否禁止使用仍由独立 `allowed` / `limitReached` 表示 |
| `usedFraction > 1` | 保留超额原值；剩余图形可限幅到 0，不改写业务数值 |
| 缺失 / null | 未知；不能自动填 0、100% 或无限 |
| `unlimited` / `hasCredits` / `balance` | 各自独立，不以一个字段猜另一个 |
| `fetchedAt` | 本机读取时间 |
| `observedAt` | 来源观测时间；被动读数没有它时不能装成新成功 |
| `resetAt` | 该窗口的重置时间，不是数据过期时间 |
| metadata / plan 变化 | 不自动证明有新的数值观测 |
| unavailable / disabled / 身份变化 | 需要区别临时读取失败与旧身份数据不能继续使用 |

Codex 的 primary、secondary、code review、additional limits 和 credits 都要保留；不能只保留一个进度环。xAI 金额原始口径为 cents 时明确除以 100 形成 USD，不能把 cents 当美元。插件 summary/group 中没有上限或单位的指标不能发明百分比或换成“请求数”。[S15][S16]

### 4.3 `PARITY-01`：无数值成功响应的已知差异

【现状】Go `cpa/client.go` 对 `Remaining == nil && Value == nil` 不产生新成功，保留同身份旧值及原 observed/expiry；有效 0 会更新。Swift `pluginQuota` 只要识别 subscription / summary / groups 结构即可产生无数值快照，随后 `CPAClient` 可直接替换旧快照。因此“两个现有实现已统一无数值缓存语义”是不成立的。[S02][S16][S17]

【候选决定；对应全局 ADR-004】Android 不按文件逐行复制该分歧，采用以下可验证的指标级规则，并在合同中标明为 Android 的明确决定。`PARITY-01` 是本章局部索引，正式裁决以全局 ADR-004 为准：

| 输入 | 同身份旧值 | Android 结果 |
| --- | --- | --- |
| 有效数值，包括 0 | 任意 | 接受该指标新数值和真实来源时间；错误解除仅针对已验证部分 |
| 暂时失败或格式错误 | 存在 | 保留旧值、旧 observedAt、旧 numeric fetchedAt 和旧 expiry，标 stale / 本次失败 |
| HTTP 200、只有 metadata 或空统计 | 存在 | 可以更新独立 metadata；数值仍标上次读数，numeric fetchedAt / observedAt / expiry 均不刷新 |
| HTTP 200、只有 metadata 或空统计 | 不存在 | 展示已知 metadata 和“暂无有效读数”，不填零 |
| 明确变更身份、禁用或移除账号 | 存在 | 不跨身份保留；必要时删去旧身份快照，显示 unavailable |
| 同身份但窗口 / 指标稳定标识缺失或发生歧义 | 存在 | 不按数组位置合并，相关指标显示未知并记录安全诊断 |

该决定不要求本任务修改 iOS，但 Kotlin 的期望结果必须写入共享合同，并明确标记与固定 Swift 基线的差异。最终验收检查差异经过批准，而不是把所有差异判错或全部豁免。真实插件是否提供稳定 key 和来源时间仍属待验证。

最近操作时间 `lastAttemptAt`、元数据读取时间 `metadataFetchedAt` 和数值观察所属的 `fetchedAt` 必须分开。否则在 observedAt 缺失的 live 数值上，metadata-only 响应更新 fetchedAt 仍会间接把旧值“续新”，违背 ADR-004。新鲜度判断只引用该数值自己的观察 / 读取依据。

### 4.4 来源时间需要逐字段校验

时间类型和可信来源不能由一个“自动识别秒或毫秒”的通用转换器猜测：

| 字段来源 | 已知合同 / 候选处理 |
| --- | --- |
| CPA 被动读数 observedAt | 必须来自实际信号的来源观察时间；inventory 读取时间不能补位 |
| Swift 主线插件额度 | 当前 `pluginQuota` 返回 observedAt=nil，以主动读取时间作为已有回退；不能声称已经读取并验证插件 observed_at |
| Go 插件额度 observed_at / observedAt | 当前策略要求显式值为有限、正整数 Unix 秒，严格小于253402300800，且不晚于本轮时间加60秒；两字段同时出现必须一致。非法、null、字符串、小数、疑似毫秒等不作为新成功；仅两字段均缺失时按主动读取合同用接收时间 |
| CAP generated_at | 插件生成该响应的时间，不是每条记录的观测时间，也不证明四资源原子一致 |
| CAP retained_since | 声明的保留起点，不保证之后没有缺口或迟到写入 |
| v1 monitor snapshot expires_at | 数据到期，允许早于当前生成时间；不能误判为一定是坏数据或自动续期 |
| v1 monitor session expires_at | 租约终点；与数据到期分离 |
| 拟议 v2 服务时间 | 采用明确的整数Unix秒与有界范围；传递 observation、snapshot expiry、subscription expiry 三个独立字段；不用客户端显示时区改变合同 |

Go 插件 observed 策略是本仓库的已有校验决定，不是对所有插件部署的权威协议断言。[S14][S16][S17] Android 默认在实服与夹具确认插件字段后采用同样的显式值校验；字段存在但非法时不悄悄回退到接收时间。将这项来源差异记录为 `PARITY-04`，与PARITY-01一起评审。

## 5. CAP 时间、统计与局部恢复

### 5.1 时间窗口

【现状】当前支持 30 分钟快捷项、1–24 小时、1–7 天及 1–12 个 UTC 公历月，已经超出早期的三个固定范围。end 为 `floor(now/60) * 60`；小时 / 天按滚动秒数回推，月份按 UTC 公历回推，目标月无该日时取月末。月份不是固定 30 天，不是本地自然月报表。[S05][S18]

【候选决定】`TimeWindow(startInstant, endInstant, selection)` 是请求不可变参数；展示可用设备时区，但请求不能随页面重组重新计算不同终点。月末、闰年、跨年、UTC 与本地夏令时、时间回拨必须有纯函数夹具。

范围选择面板只提交待查询条件并取消旧请求；取消面板不变更条件、不发请求。旧结果始终携带自己的原始窗口和生成时间，切换范围不能把旧读数重标成新窗口。用户显式刷新才读取该栏目；失败资源重试使用失败时条件，不擅自使用当前最新选择。[S05][S12]

### 5.2 四资源独立状态

`initial`、`trends`、`groups`、`costs` 各保存：`snapshot(value, query, generatedAt)`、`requestedQuery`、`error`、`isLoading`、`showingPreviousResult`。没有整个 CAP 唯一的 `Loading/Success/Error` 取代这些状态。

| 动作 | 请求集合 | 保留规则 |
| --- | --- | --- |
| 刷新完整分析 | 四资源按既有预算顺序读取 | 成功资源立即发布；其它资源失败不撤回成功结果 |
| 重试一个失败区 | 只有该资源 | 重用失败时窗口 / 分页；不清除共享冷却 |
| groups 翻页 | 只有 groups | 保留 total、offset、limit，不能把当前页说成全部 |
| 按月模型概览 | 只有 `stats/initial` | 明确“服务端汇总 · 按模型名”；不自动扫 requests 全历史 |
| 切回小时 / 天概览 | 有界 requests 样本来源 | 与月度汇总分开解释，不拼成同一口径 |
| 替换连接 / 新 generation | 取消旧任务 | 旧回调不允许重新出现；仍需底层取消和提交前校验 |

四资源即使窗口相同，也不能宣称它们来自同一个冻结数据库快照；每个 `generated_at` 原样保留。[S12]

### 5.3 分页与完整性

【现状】单页最多 500 条，自动最多 10 页 / 5000 条，单响应 4 MiB、累计请求页预算 8 MiB。下一页大小未知时预留完整单响应预算，允许提前结束；不能为了“完整报告”读取全历史或数据库备份。响应必须验证 `total >= 0`、返回 offset/limit 与请求相等、items 数量不超过 limit。[S05][S06]

| 完整性 | UI 与计算约束 |
| --- | --- |
| `singlePage` | 本次响应报告的数据落在一页，不保证不存在迟到历史 |
| `offsetUnverified` | 到达报告末页，但 offset 不证明跨页冻结快照 |
| `truncated` | 达预算，或重复 sequence、total 变化、超出 total、短页缺口等；只能描述已取得样本 |

sequence 按 UInt64 去重；没有 sequence 的记录不能伪造稳定 ID 来证明完整性。发生异常时保存可解释的部分结果和原因，不静默展示精确全量平均值。

### 5.4 计量与成本

生成 TPS 使用有效样本加权：`sum(outputTokens) / (sum(latencyNs - ttftNs) / 1e9)`；端到端输出速度单列为 `sum(outputTokens) / (sum(latencyNs) / 1e9)`。已知向量 100 Token/2 秒及 900 Token/30 秒的生成速度为 **31.25 Token/s**，不是 40，也不是除以整个查询窗口秒数。[S05]

只把已知成功、输出口径可确认、TTFT > 0、latency > TTFT 的样本纳入生成 TPS。兼容接口 / Anthropic 已包含 reasoning 的 output 不重复加；独立计量来源按已验证合同加 reasoning，无法确定则排除并显示覆盖率。provider/model/stream 分组不得丢失；失败请求的部分 token 仍属于用量，但不属于成功生成速率样本。不能把来源样本集合不同的 `average_latency_ns - average_ttft_ns` 当生成时长。

成本保留 currency、estimateBasis、priceBookRevision、priced/unpriced requests 和 missingPrices。估算不是真实账单；缺价不算 0 成本。输入输出、cache read/creation、reasoning 统计各自遵守来源定义，未知字段不补 0。[S05][S19]

`retained_since` 只表示服务端声明的历史保留起点。窗口早于保留起点，显示不可用前段；整段早于保留起点，显示没有可用历史；字段未知，显示保留范围未确认。任何一种情况都不等于全量零用量，也不证明后续区间绝对完整。

## 6. 现有 Go 监控 v1：复用与不可直接复用的部分

### 6.1 已有基础与耦合点

【现状】Go 服务已有来源白名单、principal 授权、`Collector` 抽象、同来源合并采样、会话租约、revision/sequence、先持久化再确认、取消墓碑、令牌轮换、退避和安全摘要。上述核心可以在严格回归下复用。[S14][S20]

但通知能力不止是替换一个 `Notifier`：

- HTTP v1 注册强制 `activity_id`，push token 先转小写，再验证非空偶数长度十六进制、最多 4096 字符。
- 账号限定 1–5 个，期限只允许 3600 / 14400 / 28800 秒。
- payload 预算按 ActivityKit 预留静态 512 字节、动态 3584 字节；控制状态也保存 ActivityID。
- `delivery.go` 直接识别 `apns.HTTPError` 和 APNs 特定失效原因。
- `GET /v1/capabilities` 当前没有 platform / provider 投递能力字段。

因此 FCM 等 opaque、区分大小写的 token 不能塞进现有 v1。Android 也不能生成假的 ActivityID 冒充兼容。本企划采用显式 v2，并保留 iOS v1。[S20][S21][S22][S23]

### 6.2 v1 操作合同与状态

所有相对路由都保留监控服务基址前缀，除最小 healthz 外均使用独立 bridge Bearer：

| 当前路由 | 当前语义 |
| --- | --- |
| `GET /v1/capabilities` | 当前身份允许的来源 / 账号及容量；只读，不创建、不采集、不推送；不证明 CPA 或设备链路可用 |
| `POST /v1/monitoring/sessions` | 201；规范化等价请求幂等，不同意图 409；已有取消墓碑阻止创建；新意图容量不足 507 |
| `GET /v1/monitoring/sessions/{id}` | 当前会话；其它 principal 或未知 ID 为 404 |
| `PUT .../{id}/token` | push token + expected revision，CAS 更新；不延长租约 |
| `POST .../{id}/refresh` | 202 只代表刷新意图已接受；重复 pending 不重复全量落盘 |
| `DELETE .../{id}` | 已知会话落盘停止后 200；未知 UUID 为当前 principal 记录墓碑后 204；容量不足 507 不确认取消 |
| `GET /v1/sources/{sourceID}/quota` | 授权缓存，没有缓存 404；不触发网络采集 |
| `GET /healthz` | 最小健康；不能证明鉴权，存储不确定时也返回 503 |

【现状】每来源采集目标间隔为 600 秒，每秒扫描到期不等于每秒采集；首次自动采集约在注册 600 秒后，首次手动刷新可以立即启动，随后受来源节拍与 CPA 冷却控制。刷新控制预算为每会话 10 秒一次、每 principal 滚动 60 秒六次，这不是 10 秒采集承诺。没有有效租约时停止来源采集，最后订阅停止会取消该来源工作。[S14]

`session.revision` 表示控制变化；`snapshot.sequence` 表示数据更新；快照到期、租约到期和平台送达是不同概念。一个 session 的 sequence 不能拿来与另一个 session 比较全局新旧。APNs accepted 也不证明设备已经显示或移除。

## 7. 拟议 Go 监控 v2 合同

**本节全部为候选设计，固定基线没有这些接口。** 正式 OpenAPI、Go 实现与 Kotlin DTO 需要一起评审；未经实现和验收的 provider 不得出现在 capabilities 的可用列表中。

### 7.1 核心模型与所有权

| 模型 | 关键字段与职责 |
| --- | --- |
| `MonitorSubscription` | `subscription_id`、内部 principal、source、按意图排序的 account_ids、starts_at、expires_at、status、control_revision、endpoint_id；代表监控业务授权与有限租约 |
| `DeliveryEndpoint` | endpoint_id、内部 principal、installation_id、provider、provider_config_id、受保护 token、endpoint_revision、状态；代表一个设备投递地址 |
| `QuotaSnapshot` | subscription_id、snapshot_sequence、phase、generated_at、expires_at、safe accounts；没有真实凭据或原始响应 |
| `DeliveryAttempt` | subscription_id、control_revision、snapshot_sequence、endpoint_id、endpoint_revision、event_id、事件类型、结果和 retry_at；用于隔离旧回调 |
| `MutationReceipt` | principal、资源类型 / ID、command kind、前置revision、operation_id、规范化意图hash、提交结果版本与时间；用于响应丢失后的幂等确认；详细回执有界，资源级不可回退版本与取消证据不因回执压缩而丢失 |
| `CancellationTombstone` | principal + subscription_id、确认取消时间及协议版本；阻止迟到或重放的创建 |

一个 endpoint 可以承载本 principal 的多个订阅；停止一个订阅不删除其它订阅或共享 endpoint。token 不是授权证明；server 仍对 source/account 做独立允许列表验证。不得因为两个设备 token 相同就合并不同 principal 的所有权。

APNs ActivityKit 的 activity_id 等字段属于 `provider_metadata`，只有其 adapter 解析；FCM 不要求 ActivityID。opaque token 不做 trim、lowercase 或 Unicode 规范化，按原始 UTF-8 字节保护；provider adapter 决定合法格式，公共层只施加明确的非空、控制字符和字节预算。初始 endpoint token 预算候选为 4096 UTF-8 字节，这是本服务准入选择，不能宣传为所有推送厂商的官方上限。

### 7.2 身份、版本与能力发现

新增候选 `GET /v2/capabilities`，返回至少：

- `protocol_version: 2` 与 schema 标识；服务实现版本另列，不能拿应用版本代替协议版本。
- 当前 principal 授权的 source/account 及安全显示字段。
- `delivery_providers[]`：provider id、可用配置 id、支持事件、token 预算、payload 预算、必要 provider metadata 及是否允许更新。
- `lease_seconds: [3600, 14400, 28800]`、`max_accounts_per_subscription: 5`、请求与状态预算。
- 当前 principal 容量、警告阈值、`can_create_subscription`、`can_record_cancellation`；它们只是预检，不预留容量。
- `features` 中明确 mutation receipts、endpoint CAS、snapshot read、终态确认等协议能力。

响应不返回真实 provider 密钥、token、内部 principal 名称、其它 principal 的容量或源 CPA URL。只有实际加载并可接受配置的 adapter 才声明支持；声明支持也不证明网络或真实设备送达。

客户端先请求 v2 capabilities。404 可再读 v1 capabilities，用于识别“服务需要升级”及保留既有可读取状态；不能把 Android token 注册到 v1。401 不回退公开 healthz；TLS、解码或未知协议错误不触发降级。显式 v2 必需能力缺失时阻止新注册并说明原因；已有待停止意图优先按其原协议进行对账。

### 7.3 拟议端点与 HTTP 结果

下列名称作为 OpenAPI 默认草案，实施前统一冻结；不得在客户端和服务端各自改名：

| 方法 / 路由 | 请求核心 | 成功与约束 |
| --- | --- | --- |
| `GET /v2/capabilities` | Bearer | 200 当前身份能力；严格只读 |
| `POST /v2/delivery-endpoints` | operation_id、endpoint_id、installation_id、provider、provider_config_id、token、metadata | 201 已持久化地址；相同操作和意图可重放，不返回 token |
| `GET /v2/delivery-endpoints/{id}` | Bearer | 200 不含秘密的状态和 endpoint_revision；其它 principal 为 404 |
| `PUT /v2/delivery-endpoints/{id}/token` | operation_id、expected_endpoint_revision、新 token | 200 CAS 成功；旧 revision 409；不改变监控租约 |
| `DELETE /v2/delivery-endpoints/{id}` | operation_id | 没有 active 订阅时禁用；有引用返回 409，提示先停止订阅；不能悄悄停止其它工作 |
| `POST /v2/monitoring/subscriptions` | operation_id、subscription_id、source_id、account_ids、duration_seconds、endpoint_id | 201 首次持久化租约；相同注册不得续租或重设 token |
| `GET /v2/monitoring/subscriptions/{id}` | Bearer | 200 当前控制、数据和投递状态；无权限与未知均 404 |
| `GET /v2/monitoring/subscriptions/{id}/snapshot` | Bearer；可带已知 sequence | 200 当前快照，未采集 404；只读，不采集。若支持 304，必须单独写明 validator 合同 |
| `POST /v2/monitoring/subscriptions/{id}/refresh` | operation_id、expected_refresh_revision | 202 意图持久接受，refresh_revision 加一；仍受刷新控制与来源采集预算；此版本不等于采样sequence |
| `DELETE /v2/monitoring/subscriptions/{id}` | operation_id | 200 已知终态；未知 ID 的取消意图落盘后 204；永不因旧 revision 拒绝有效停止意图 |
| `GET /v2/operations/{operation_id}` | Bearer；query显式携带resource_kind、resource_id、command_kind及该命令适用的precondition_revision | 200 当前principal该完整命令键仍保留的详细回执；404不证明未执行，继续按目标资源与版本对账 |
| `GET /v2/sources/{source_id}/quota` | Bearer | 200 当前授权范围内缓存；没有缓存 404；不能泄漏其它身份的账号快照 |

候选请求体上限沿用 64 KiB，禁止尾随第二份 JSON，变更请求拒绝未知字段；每个错误响应为有限大小的 `code / scope / retry_at? / request_id`。`request_id` 只能用于受控诊断关联，不能夹带地址、Key 或账号内容。

| 状态码 / code | 含义与客户端动作 |
| --- | --- |
| 400 `invalid_request` | 结构、字段、预算或格式非法；不重试相同无效请求 |
| 401 `bridge_unauthorized` | bridge 身份无效；暂停该身份请求，保留需对账的停止意图 |
| 403 `scope_forbidden` | 已认证但 source/account 不被允许；不注册、不转用其它凭据 |
| 404 `not_found` | 不泄漏其它 owner；根据操作语义决定是否继续对账 |
| 409 `intent_conflict` | 同一完整命令键或同一订阅创建ID的不同意图；不得生成新UUID绕过未确认旧注册 |
| 409 `revision_conflict` | token CAS 版本不匹配；GET 当前版本，核对本地操作后再决定 |
| 409 `operation_superseded` | 操作所需版本已经过去且详细回执不再保留；不重新执行，按目标资源当前状态对账 |
| 409 `subscription_cancelled` | 已有永久取消证据；迟到注册不得复活 |
| 422 `unsupported_provider` / `unsupported_capability` | 当前服务没有所需能力；明确升级/配置建议，不伪装成注册成功 |
| 429 `rate_limited` | 独立 request lane 冷却；遵守 Retry-After；不得阻止其他 lane 的安全停止 |
| 503 `state_unavailable` | 存储不确定或服务不可用；保留 unknown，待恢复后对账，不假设已回滚 |
| 507 `capacity_exhausted` | 新意图在提交前被容量拒绝；与磁盘结果不明区别；既有停止与回执仍可用 |

### 7.4 幂等、响应丢失与 token CAS

【候选决定】所有变更都在发送前持久记录本地 `operation_id`、目标资源 ID、所需版本与受保护的意图；网络超时后复用同一 ID 查询或重放，不换 ID 创建替身。完整幂等命令键为 `(principal, resource_kind, resource_id, command_kind, precondition_revision, operation_id)`：create / stop 使用固定无前置版本标记，rotate使用expected_endpoint_revision，refresh使用expected_refresh_revision。operation_id是客户端新生成的关联ID，不能单独被误当全局无限期幂等表的主键。

服务在详细回执仍保留时按该完整键返回原提交证据；同一完整键 / 不同意图为409。详细回执压缩后，必须由永久注册身份、终态、endpoint_revision或独立refresh_revision判定旧命令不可再次执行，返回当前安全状态或operation_superseded，不能把“查不到回执”当成首次请求。旧请求改成新的expected revision已是不同命令，不能被网络自动重试器擅自修改；它只能在当前状态核对后由业务操作明确产生。hash不是日志材料，也不能替代对原始秘密的访问控制。

规范化范围必须严格定义：UUID 可小写、JSON 键顺序和空白不影响意图；account_ids 顺序保留；provider token 字节和大小写影响意图。创建订阅的 intent 绑定 endpoint_id，不绑定后续轮换的 token 内容，因此重新发送最初注册不能把 endpoint 回滚到旧 token。

首次注册的 starts_at / expires_at 与回执在同一持久化提交中确定。重试、GET、token 轮换、app 重装和服务重启均不得延长旧租约。再次启动监控需要一个用户明确的新意图；不能在后台自动补建新 UUID。

控制状态至少区分三个独立版本：`control_revision` 属于订阅租约 / 终态，`endpoint_revision` 属于地址，`refresh_revision` 属于已接受的刷新命令。刷新命令提交时独立递增 refresh_revision，而采集完成才推进 snapshot_sequence；v1 的控制版本语义不受此 v2 字段影响。发送投递时捕获订阅和地址版本及 snapshot_sequence。旧 token 失效回调只能失效同 endpoint_revision；旧快照成功回调只能确认对应 attempt，不能把当前新数据标成 accepted。版本到整数上限必须失败关闭或通过新协议迁移，禁止回绕。

若 operation 回执比当前状态版本旧，客户端只确认“该操作曾提交”，不得用旧回执覆盖更新的状态；随后 GET 当前资源对账。停止不应被“用户未拿到最新 control_revision”阻断：删除本身份订阅是幂等的终止意图，权限、存储和取消证据仍必须检查。

### 7.5 控制、数据、投递与呈现状态分离

| 维度 | 候选状态 | 解释 |
| --- | --- | --- |
| 本地控制意图 | draft / pending / confirmed / unknown / rejected | unknown 表示请求可能已提交，不能显示“已停止”或自动换 ID |
| 服务端订阅 | active / stopped / expired / revoked | 终态不能由迟到 update 或重放 create 回到 active |
| 数据 | not_collected / ready / partial / stale / failed / cooling_down | 数据新旧与订阅是否 active 分开；过期数据不能靠重新推送变新 |
| endpoint | active / invalid / disabled | token 失效不同于服务端 provider 凭据失效 |
| 投递 | disabled / pending / platform_accepted / retry_wait / permanent_failure / unknown | accepted 仅为推送平台接受；unknown 保留不确定性 |
| 本机呈现 | permission_denied / channel_disabled / received / presentation_requested / expired_locally | 本机系统调用成功也不证明用户已看见 |

UI 同时表达必要维度，例如“监控已停止，移除通知的投递待确认”，而不是把服务端停止与设备显示关闭合并成一个布尔值。关闭本机显示不能宣称服务端已停止；服务端已停止但终态通知未达也不能继续把旧通知显示为持续采集中。

本地恢复句柄至少包含monitorServerIdentifier、原监控凭据引用与credentialRevision、经验证的授权绑定、protocolVersion、endpointId、subscriptionId、待确认命令键和用户期望终态。CPA切换不得替换这些字段；监控连接更换后旧句柄仍以原目的地进行查询 / 停止。若原秘密已失效或用户选择忘记，保留非秘密的未确认停止证据并明确说明需要重新提供原服务授权；不从当前CPA管理密钥或另一监控身份猜测凭据。清除已确认终态记录与放弃仍unknown的恢复能力是不同操作，必须有不同结果说明。[S09][S13]

## 8. 通知有效负载、adapter 与 Android 等价呈现

### 8.1 安全快照与事件

【候选决定】业务快照和厂商消息外壳分开。内部事件包含不可复用 event_id、subscription_id、control_revision、snapshot_sequence、endpoint_revision、event kind、generated_at、snapshot_expires_at、subscription_expires_at 以及安全账号摘要。只有 adapter 能把它编码成 APNs / FCM 外壳。

通知允许的业务内容是安全别名、provider、明确窗口、有限数值 / 单位、读数状态和观测时间。禁止真实账号 id、email、auth_index、CPA URL、管理 Key、bridge token、push token、原始失败正文和内部身份指纹。完整账号授权 ID 仅存在受认证的控制选择接口和内部状态。

安全摘要和事件标识需保持可被设备幂等处理：相同 event 不重复提示；旧 control_revision / sequence 不覆盖新状态；stopped / expired / revoked 具有终态优先级；新事件不能延长已持久租约。设备断网恢复后从受认证快照接口对账，不信任无限期留存的推送内容。

平台 payload 预算由 adapter 单独验证。APNs v1 保留 3584 动态 / 4096 总体边界；FCM 的实际字段与厂商限制需在实现时依据官方文档及真实测试冻结，不把 APNs 预算机械当成 FCM 合同。v2 通用快照初始预算可继续保守限定为 3584 字节以维持 1–5 账号等价；若要放宽，必须同时重算持久容量与各 adapter 分片 / 退化策略，不能静默截断账号。

### 8.2 失效分级

| adapter 规范化结果 | 服务动作 | 不能做的事 |
| --- | --- | --- |
| `accepted` | 只确认本 attempt 平台接受 | 宣称设备已显示、用户已阅读 |
| `endpoint_invalid` | 仅在捕获 endpoint_revision 仍当前时持久失效 token；等待有效新 token CAS | 因旧 token 回调封禁新 token |
| `provider_auth_invalid` | 标配置问题，暂停相应 provider 的发送并给管理员安全诊断 | 删除用户 endpoint 或要求重新生成全部 token |
| `retryable` | 持久 retry_at、attempt 次数；尊重更晚 Retry-After | 立即循环、重启后缩短退避 |
| `permanent_payload_failure` | 保留失败证据，修正编码 / 大小 / 版本后对账 | 自动反复发送同一个无效 payload |
| `delivery_unknown` | 标不确定；按事件幂等性重试或对账 | 把网络超时写成 accepted 或 guaranteed_not_sent |
| `disabled` | 明确未发送；区分 dry-run、撤权和显式禁用 | dry-run 宣称全离线或投递通过 |

Go 领域层只依赖上述结果，不 import APNs / FCM 具体错误。现有 APNs `410`、`BadDeviceToken`、`DeviceTokenNotForTopic` 仍由 adapter 映射 endpoint_invalid；`ExpiredProviderToken` 是 provider JWT 相关，不能误判设备 token。现有每活动 60/120/240/480/600 秒退避为初始兼容基线；v2 必须决定按 subscription + endpoint revision 保存的精确键，并测试多订阅共享 endpoint 时不形成重试风暴。[S21]

### 8.3 Android 监控等价要求

Android 完整实现至少覆盖：选来源和 1–5 账号、1/4/8 小时租约、能力与容量预检、显式注册、渐进快照、刷新请求、停止、停止未确认恢复、token 更新、通知可用性说明、锁屏隐私、通知点入正确连接 / 工作区、退出或撤权后的本机数据清理，以及小组件读取经过脱敏的已验证快照。

FCM能力不能以“预留接口”记为完成。完整移植结论严格采用01章的支持矩阵：默认在符合条件的GMS设备验证完整投递；无GMS / FCM不可用设备提供明确声明的降级功能，不宣称其后台推送完整等价。因此本章“完整投递门槛”适用于01章声明全能力的设备范围，不把“核心功能可运行”误解为所有设备都承诺实时推送。若用户选定的发行范围要求指定无GMS设备也全能力，ENH-03须升级为该发行版必需项，完成实际provider和真机验证。是否启用常驻通知、WorkManager或前台服务由Android系统限制和用户意图决定；不得把系统调度当成固定十分钟精确闹钟。

监控通知和聊天生成是两条业务链路。现有 QuotaMonitor 不提供后台聊天任务、token 代理或回复存储；如 05 章需要服务端聊天接管，它必须有独立合同、权限与计费语义，不能附带混进 monitor v2。

## 9. 容量、持久化、墓碑与重放

### 9.1 现有容量与存储事实

【现状】v1 默认 max_sessions=1024、max_tombstones=4096、max_principal_intents=256；终态会话和墓碑仍计数。state 文件最大 32 MiB，注册预留未来 token、快照、身份指纹和投递状态空间。容量不足拒绝新意图为 507；不等于写盘结果不明。已知 GET / 停止 / token 轮换 / 幂等请求仍应工作。[S14][S24]

现有 FileStore 使用 AES-256-GCM、随机 nonce、认证头、临时文件、fsync、原子替换、目录同步及单写者 OS 锁。磁盘提交结果不确定时服务失败关闭，停止采集并返回 503，包括 healthz；不能继续工作或恢复旧文件冒充没有发生过取消。[S25]

### 9.2 v2 默认容量决定

【候选决定】第一版 v2 保持有界、单写者、明确预算的持久化模型，不在移植初期同时引入分布式数据库或多主写入。新增 endpoint、operation receipts 和投递状态必须纳入真实最坏序列化预算；不能沿用旧计数而忽略新增对象。

容量按 principal 和全局分别限制。创建订阅时预留该订阅全部可接受后续变更空间，包括 token 轮换关联成本、快照、终态、重试和必要回执；已确认的停止不能因“新回执配额满”无法记录。创建 endpoint 的孤立记录有独立上限和可审计禁用流程；不得以无界 endpoint 注册绕过订阅配额。

为使上述预算可以实现，详细 operation 回执不能无界追加。默认每个资源仅保留固定数量的最近回执（候选 16 条，最终按序列化上限核定），并保留如下不可压缩的安全摘要：创建资源的原始意图 hash；订阅终态 / 取消墓碑；endpoint 当前 revision 与最近成功轮换意图；refresh_revision 与最近接受刷新意图。更早的带旧 expected revision 的 rotate / refresh 永不再次执行；重复 create 由永久实体身份与原意图判断；重复 stop 由永久终态判断。回执 GET 不能找到已压缩详细响应时按 7.4 的规则对账。该压缩不回收注册或取消安全证据，也不等于 9.3 所述历史意图 GC。固定回执窗口、压缩前后重放与并发操作必须有专门测试；若无法证明旧操作不重执行，则不得启用压缩或宣称容量预算已完成。

capabilities 只做有界读取，不编码 / 写完整状态、不采集、不把终态 GC 混入 GET。capacity 的预检不是 reservation；并发注册的最终原子准入仍可能 507。正确容量、大小上限和告警百分比以新数据格式的负载验证确定，在配置示例中明确，不宣传未经测试的“无限期运行”。

### 9.3 墓碑与回收的默认选择

【候选决定 `MON-04`】首版 v2 **不启用历史意图自动 GC**。沿用永久取消证据与容量受控拒绝：同 principal + subscription_id 的取消确认后，迟到或重放 create 永远不能复活；终态不能重新 active。此决定保持现有安全能力，不增加原项目未有的自动回收承诺。

HTTP v2、v2 持久记录与安全 GC 是不同版本概念。为了跨平台通知引入 v2，不代表已经有可验证的重放截止。客户端提供一个 `expires_at`、删除旧行或给墓碑加 TTL 均不足以安全回收。

后续若启用 GC，必须作为单独协议门槛同时完成：

1. 服务签发并验证绑定 principal、不可复用意图 ID 与不可延长截止的注册凭证；同旧 ID 不得重签更晚期限。
2. 取消先到也能验证凭证，并保留墓碑直到所有可能有效注册窗口关闭；活跃租约、停止对账和必要投递未完成不得回收。
3. 持久、单调不回退的安全时间下界与回收在同一提交；时间回拨、重启或签名密钥轮换不能重新打开窗口。
4. 无截止证明的 v1 / 首版 v2 历史意图继续保留旧重放保护，不按年龄自动改成可回收。
5. 可验证的签名密钥轮换、mixed-version 状态和不兼容二进制拒绝；安全回退不能丢已确认取消。
6. 以取消先到、旧凭证、相同 ID 改期限、跨 principal、时钟回拨、重启和 GC 边界的对抗事件序列证明非复活。

这些是未来功能的准入条件，不是当前已经通过的测试。若产品决定“无人管理的长期无界监控”属于首发目标，则需要先把安全 GC 或经验证的分区留存设计提升为首发范围，不能靠扩大容量数字掩盖。

### 9.4 v1 兼容与持久化迁移

现有 Go durable record `Version == 2` 只表示 token-invalid 的持久化升级，**现有 HTTP 仍是 v1**；禁止把该数字误认为已有跨平台 HTTP v2。[S20]

【候选决定】新增明确的顶层 storage_schema_version，并为旧 v1 会话标注来源协议。保留旧 API 的 ActivityKit 字段、大小写、期限、token 验证和响应语义；adapter 转换不改变旧 request hash 或已确认墓碑。迁移时不得给旧租约续期、给旧快照换 observed_at、把 v1 opaque 式 reinterpretation 用到十六进制 token，或把旧永久记录移入新 GC 域。

迁移流程是离线验证副本 → 校验身份 / 状态 / 容量 / 最坏预算 → 受保护一致性备份 → 单写者受控升级 → 校验所有取消与终态 → 启动只读检查 → 开启采集 / 投递。每步记录非秘密摘要。新格式须让旧二进制明确拒绝启动，不能忽略未知字段后丢安全状态。

回退优先前向修复或使用理解新格式的兼容版本。恢复陈旧备份会丢失之后确认的停止，不是允许的普通“回滚”；若必须灾难恢复，需通过明确恢复协议重建安全时间 / 回执边界，未完成前保持服务失败关闭。

## 10. 可执行合同测试清单

每个编号必须关联实现测试和实际回执；“有测试文件”不等于测试通过。纯 JVM / Go 测试使用虚拟时钟、可控传输和故障点，避免靠 sleep 竞态证明正确性。真实链路测试遵循 08 章的授权、凭据与证据要求。

本节的NET / QTA / CAP / MON编号是**本章局部测试号**，记录证据时使用`04/NET-01`、`04/MON-01`等带章节的test_ref。它们不是feature-parity.json中的同名能力ID；feature_id与TASK映射仍以结构化索引为准。第11节的PARITY / MON决定号同样是局部索引，不能替代全局ADR编号。

| ID | 输入 / 事件 | 必须断言 |
| --- | --- | --- |
| NET-01 | 带代理前缀、默认端口、编码路径、Unicode、IPv6 的基址 | 精确 endpoint 不丢前缀、不双重编码；非法段拒绝 |
| NET-02 | 管理端点 301/302/307/308 到同域、跨域、HTTP | 均不跟随；第二服务未收到认证头 |
| NET-03 | 伪 Content-Length、无长度、压缩与流式超 4 MiB | 边接收边终止，解码器不持有超预算正文 |
| NET-04 | inventory 未返回就关闭 / 返回 / 切连接；稍后返回成功 | 凭据与会话未提交；草稿清空；旧响应不发布 |
| NET-05 | quota / CAP / key discovery 混合请求 | 同连接管理并发峰值 ≤3；单 CAP 详情最多 1 |
| NET-06 | 外层管理 401、内层账号 401、模型目录 401 | 三种正确作用域；只有应阻断的域停止 |
| NET-07 | 429 有未来 / 过去 / 非法 / 数组 Retry-After | 遵守明确 deadline；force 和换路由不绕过 |
| NET-08 | key discovery 首选 404/501、401、200坏JSON | 仅白名单情况回退一次；其它情况不附加请求 |
| QTA-01 | 0、null、缺字段、100%、125%、unknown unit | 数据语义正确，超额原值不丢，未知不填零 |
| QTA-02 | 同 id 改 authIndex/provider/owner，旧请求晚到 | 不继承旧身份数据，不发布晚到结果 |
| QTA-03 | 成功数值 → metadata-only → 失败 → 有效0 | PARITY-01 指标级缓存与 observedAt 精确符合决定 |
| QTA-04 | 大整数身份、2^53 边界、布尔、小数、UInt64 sequence 上界 | 无损与拒绝边界分字段执行，不经过 Double 污染 |
| CAP-01 | 四资源各自成功 / 失败的组合 | 成功区立即可见，失败区保旧窗口，单区重试只发该请求 |
| CAP-02 | 选新范围、取消、明确刷新 | 选择和取消本身零请求；请求使用冻结绝对窗口 |
| CAP-03 | 3月31日回推、闰年、12个月、设备时区变化 | UTC日历月语义，不按30天或本地自然月替代 |
| CAP-04 | 重复sequence、total变化、短页、超预算 | 标 truncated，保留部分样本，不宣称全量 |
| CAP-05 | 月度概览 | 只读 stats/initial；没有隐式全历史请求 |
| CAP-06 | TPS已知向量、reasoning口径、失败token、缺价 | 31.25向量正确；覆盖率、成本未知与估算标签保留 |
| MON-01 | capabilities读取、healthz成功但授权失败 | 无写盘、采集、注册或推送；health不作为鉴权 |
| MON-02 | 相同operation同意图、相同ID不同意图、响应丢失 | 幂等确认不重复租约；冲突不换ID绕过 |
| MON-03 | DELETE先到，随后POST；停止后重启再重放POST | 墓碑隔离principal，终态不复活 |
| MON-04 | 旧token发送中轮换；旧token失效/成功回调晚到 | 不污染新endpoint_revision；不延租约 |
| MON-05 | 新snapshot先到，旧snapshot随后accepted | 只更新对应attempt，不把新快照标为已送 |
| MON-06 | 多订阅同源，部分停止，最后订阅停止 | 合并采样；保留有效订阅；最后停止取消来源作业 |
| MON-07 | 10秒刷新控制与600秒采样节拍 | 202不承诺新采样；重复pending不写放大 |
| MON-08 | 容量边界与capabilities预检后并发注册 | 最终原子507；已知停止、轮换、对账仍可用 |
| MON-09 | fsync/rename/目录同步结果不明、加密损坏、第二写者 | 503失败关闭；不恢复陈旧状态继续服务 |
| MON-10 | 旧v1混合新v2、旧record-v2、来源变更或撤权 | 旧协议语义保留；错误二进制拒绝；撤权脱敏、终止 |
| MON-11 | FCM/对应provider token大小写、控制字符、超预算 | opaque token不被规范化；adapter验证而非v1 hex验证 |
| MON-12 | 后台、进程死亡、断网、权限拒绝、channel关闭、token轮换 | 服务端租约与本机呈现独立、可恢复、无虚假完成 |
| MON-13 | APNs旧客户端与Android新客户端同时运行 | 两条完整链路均通过；没有以Android上线牺牲iOS兼容 |

## 11. 本章实施顺序与完成标准

1. **合同提交**：端点矩阵、类型、错误作用域、字段 fixture、PARITY-01/02/03 决定及 v1 兼容测试先完成。审核必须能从夹具看见缺字段、限流、取消和身份切换的期望行为。
2. **Kotlin 读链路**：纯 JVM 网络和规范化模块、连接事务、额度、CAP 独立恢复完成，再接 Compose 状态。网络模拟不得替代最终实服验证。
3. **Go 重构但保持 v1**：将平台错误、payload 和地址验证搬到 adapter；旧 v1 的合同与测试完全保持；这一步本身不意味着 Android 通知完成。
4. **v2 与持久化**：端点、CAS、回执、容量、迁移和失败关闭完成；旧 v1 与新 v2 混合状态通过故障序列。
5. **Android 全监控流程**：注册、刷新、停止未知恢复、期限、token 生命周期、通知与小组件、深链和隐私完整接入，符合 06 章设备范围。
6. **真实端到端与候选发布**：至少一个支持范围内真实 Android 设备、真实受控 CPA/CAP、真实推送配置与旧 iOS 兼容证据齐备；再按 08 章验收。运行过模拟器不能改记为真机，平台接受不能改记为设备显示。

以下默认决定需要在启动评审中明确记录，但不应成为开发者无限期等待的空白：

| 决定 | 本文件默认方案 | 改变时必须补充 |
| --- | --- | --- |
| PARITY-01 无数值快照 | 指标级保留旧值与原时间，metadata独立更新 | 真实业务理由、输入/输出夹具及用户可见差异 |
| PARITY-02 single-flight取消 | 保持显式业务取消终止共享调用；UI停止收集不取消业务 | 若改引用计数，提交取消所有权和并发回归 |
| PARITY-03 429期限 | 无效/过期期限保守60秒，未来期限不提前 | 两端规范化向量与防请求风暴证据 |
| PARITY-04 插件来源时间 | 已确认合同中的显式observed严格校验；两字段皆缺失才允许主动读取回退 | 插件真实版本证据、秒/毫秒/冲突字段向量和与Swift差异说明 |
| MON-01 协议演进 | 独立HTTP v2 + 原v1兼容 | 如果只改v1，须证明旧客户端、未知字段拒绝与token语义仍兼容；默认不接受 |
| MON-02 provider支持 | 01章声明全能力的设备范围必须有实际链路；默认无GMS为公开降级范围 | 不可仅预留FCM；指定无GMS全能力时将ENH-03转必需并增加真机证据 |
| MON-03 首发存储 | 单写者、有界持久状态；重新计算新增对象预算 | 引入数据库/多实例需补事务、锁、迁移和故障模型 |
| MON-04 历史回收 | 首版不自动GC，永久重放保护与容量告警 | 安全截止凭证、单调时间、混合版本和不可复活证明 |

“完成本章”要求所有首发合同有实现、有针对性自动验证、有真实链路证据、已知差异明确并经过评审；保留监控为“以后再做”不能通过完整移植发布门槛。

## 12. 固定源码依据

以下链接均固定到本企划的 iOS 基线；编号仅为本文件内部参考。对真实服务器能力的最终判断仍取决于授权实服验证。

- [S01 · CPAServer.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAServer.swift)：地址、路径与管理密钥验证。
- [S02 · CPAClient.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAClient.swift)：端点、provider选择、single-flight、epoch、身份和缓存。
- [S03 · CPAAPIKeyDiscovery.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAAPIKeyDiscovery.swift)：Key列表与404/501兼容回退。
- [S04 · CPAModelCatalogClient.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAModelCatalogClient.swift)：推理认证与模型目录。
- [S05 · CAP_USAGE_BACKEND.md](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/docs/CAP_USAGE_BACKEND.md)：CAP时间、口径、分页和完整性合同。
- [S06 · CAPUsageClient.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CAPUsageClient.swift)：资源认证、管理/资源限流和预算。
- [S07 · HTTPTransport.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/HTTPTransport.swift)：取消、重定向、大小、缓存和安全异常。
- [S08 · WireDecoding.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/WireDecoding.swift)：双层状态、身份无损解析和时间。
- [S09 · MonitoringClient.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/MonitoringClient.swift)：bridge身份、v1调用、独立冷却lane。
- [S10 · QuotaRequestLimiter.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/QuotaRequestLimiter.swift)：管理3并发、共享阻断。
- [S11 · CPAQuotaStore.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAQuotaStore.swift)：清单优先、渐进结果、取消与操作证据。
- [S12 · CAPUsageStore.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CAPUsageStore.swift)：独立资源状态和局部重试。
- [S13 · CPAQuotaSession.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/CPAQuotaSession.swift)：候选连接、凭据事务与提交版本。
- [S14 · MONITOR_SERVICE.md](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/docs/MONITOR_SERVICE.md)：v1授权、调度、控制、容量、取消及已知边界。
- [S15 · Models.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/Models.swift)：未知、超额、来源时间和快照。
- [S16 · QuotaParsing.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/QuotaParsing.swift)：Codex/xAI/plugin/passive语义。
- [S17 · Go cpa/client.go](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/cpa/client.go)：来源身份、无数值缓存、观测时间和冷却。
- [S18 · CAPUsageWindow.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CAPUsageWindow.swift)：1–12公历月及有界范围。
- [S19 · CAPUsageCosts.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CAPUsageCosts.swift)：估算和价格覆盖字段。
- [S20 · Go service.go](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/service.go)：注册、hex token、租约、墓碑、revision/sequence和持久record v2。
- [S21 · Go delivery.go](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/delivery.go)：APNs错误耦合、令牌失效和退避。
- [S22 · Go capabilities.go](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/capabilities.go)：当前只读授权与容量字段。
- [S23 · Go payload.go](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/payload.go)：活动最坏payload准入。
- [S24 · Go capacity.go](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/capacity.go)：有界意图、最大状态预算及不回收墓碑。
- [S25 · Go storage.go](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/storage.go)：加密单写者文件与持久化提交。

[S01]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAServer.swift
[S02]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAClient.swift
[S03]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAAPIKeyDiscovery.swift
[S04]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAModelCatalogClient.swift
[S05]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/docs/CAP_USAGE_BACKEND.md
[S06]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CAPUsageClient.swift
[S07]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/HTTPTransport.swift
[S08]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/WireDecoding.swift
[S09]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/MonitoringClient.swift
[S10]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/QuotaRequestLimiter.swift
[S11]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAQuotaStore.swift
[S12]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CAPUsageStore.swift
[S13]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/CPAQuotaSession.swift
[S14]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/docs/MONITOR_SERVICE.md
[S15]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/Models.swift
[S16]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/QuotaParsing.swift
[S17]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/cpa/client.go
[S18]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CAPUsageWindow.swift
[S19]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CAPUsageCosts.swift
[S20]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/service.go
[S21]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/delivery.go
[S22]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/capabilities.go
[S23]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/payload.go
[S24]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/capacity.go
[S25]: https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/storage.go

