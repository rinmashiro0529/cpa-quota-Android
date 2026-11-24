# 02 · 来源审计与完整功能对齐

本章由 tools/render_indexes.py 根据结构化清单生成。能力编号与验收以 [feature-parity.json](manifests/feature-parity.json) 为结构化索引；改变范围后必须重新生成本章。

## 1. 固定来源与审计边界

- 基线：[cpa-quota-ios@80beea9](https://github.com/rinmashiro0529/cpa-quota-ios/tree/80beea9ed251a628307825cba99290b5f246575b)；这是功能合同的比较对象。
- 审阅了主线的关键模型、协议、UI、存储、监控服务和合同测试；来源对象索引不代表每个文件均已逐行审阅，更不代表执行过测试。
- 未读取目标 Android 仓库原有企划正文；本提案的分析不以旧企划为输入。
- 上游 #33 与 #34 仍以观察时的未合并提案记录；不把它们的行为或性能结论算入主线。
- 已观察源 CI：[run 45400721543](https://github.com/rinmashiro0529/cpa-quota-ios/actions/runs/45400721543) 总体失败，Duo UI shard 2/3 失败；Go、Swift package/Release 与 iPhone 18 Pro UI 通过。这些是既有运行记录，本任务没有重新执行。
- 本文中的 Android 架构和修复选择属于候选决策；系统平台事实来源见 06，源端差异处置见 04/05/10。

## 2. 范围计数与完成规则

共 97 个规范能力 ID：82 项源版本对齐能力、11 项 Android 实现质量要求，以及 4 项基线外增强。93 项 release_required=true 共同构成完整版本门槛。

一个能力 ID 可以包含多项有联系的用户操作，数量不代表复杂度或自动测试数量。跨团队使用本章 ID；04 的合同用例、05 的 CHAT/C 编号和06的平台用例是展开细节，不计为重复功能。

所有实现状态初始为 not_started。映射到多个任务表示多个职责共同覆盖，最终审定任务不能代替具体实现证据。涉及安全与失败的场景必须与成功场景同时完成。

## 3. 平台映射

| 源能力 | Android 交付 | 对齐边界 |
| --- | --- | --- |
| SwiftUI 五工作区/独立路径 | Compose + 独立导航栈 + adaptive pane | 保留选中项、返回和恢复语义；视图随窗口调整 |
| Keychain / 记住或临时连接 | Keystore + SecretStore + 显式保存事务 | 秘密持久化失败真实反馈，禁止明文回退 |
| WidgetKit / App Group 投影 | Glance / AppWidget + 最小安全投影 | 默认不共享；无选中账号时不能换成他人账号 |
| ActivityKit 远端监控 | 新监控协议 + FCM + Android 通知/小组件 | 保留状态、停止和恢复；不承诺所有系统同一锁屏视觉 |
| beginBackgroundTask 有界收尾 | 退后台 checkpoint + 最多30秒尽力收尾 | 系统可提前回收；进程死亡不自动重发 |
| 原生富文本与静态 HTML | 原生 Markdown/代码/数学 + 隔离静态预览 | 禁止脚本/外网/本地读取，不能由关闭功能来冒充安全等价 |
| 源端整文件聊天存储 | Room + 私有附件 + 迁移与恢复 | 保留内容语义，独立改善持久化；跨端导入导出另列增强 |

## 4. 完整能力矩阵

### 导航与入口

| ID | 能力与范围 | 验收要求 | 实现任务 |
| --- | --- | --- | --- |
| NAV-01 | 五工作区与独立返回栈（必需） | 保持额度、CAP、聊天、诊断、连接五入口；跨工作区往返不重置各自详情。 | TASK-003, TASK-028 |
| NAV-02 | 未配置入口与连接引导（必需） | 未连接页面有统一连接入口，验证期间状态真实。 | TASK-003, TASK-006 |
| NAV-03 | 深链与通知冷启动路由（必需） | 额度/监控深链和聊天通知只携带业务ID，冷启动、失效ID和迟到恢复均安全。 | TASK-003, TASK-026, TASK-028 |

### 连接与网络

| ID | 能力与范围 | 验收要求 | 实现任务 |
| --- | --- | --- | --- |
| CON-01 | HTTPS地址规范化与路径前缀（必需） | 拒绝危险URL与编码路径；反代前缀、默认端口和管理后缀有黄金样本。 | TASK-005 |
| CON-02 | 管理连接验证与渐进进入（必需） | 账号清单验证成功后进入；额度慢账号不阻塞入口。 | TASK-006 |
| CON-03 | 记住连接与临时连接（必需） | 持久与仅内存两种模式明确；安全存储失败不静默降级。 | TASK-004, TASK-006 |
| CON-04 | 候选取消、回滚与迟到拒绝（必需） | 返回、关闭、深链、换密钥使旧候选无效且保留原连接。 | TASK-006 |
| CON-05 | 重连、换服务与凭据代际（必需） | 同账号ID更换身份或凭据后旧结果、能力和缓存失效。 | TASK-006 |
| CON-06 | 忘记连接与删除失败反馈（必需） | 删除失败不能声称忘记成功；不误删独立监控/其他服务历史。 | TASK-004, TASK-006 |
| CON-07 | 请求隔离与响应预算（必需） | 无凭据重定向泄漏；实际接收大小受限；取消传播且错误脱敏。 | TASK-005, TASK-031 |
| CON-08 | 共享限流、鉴权阻断与single flight（必需） | 管理401/403、429和并发预算跨入口一致；force不能绕过。 | TASK-005, TASK-031 |

### 额度

| ID | 能力与范围 | 验收要求 | 实现任务 |
| --- | --- | --- | --- |
| QUO-01 | 账号清单与可用能力（必需） | 空清单、禁用账号、可选能力失败可区分且账号身份稳定。 | TASK-007, TASK-008 |
| QUO-02 | 渐进刷新与每账号结果（必需） | 先发布清单，每个结果到达即更新，慢/失败账号不清空其他成功值。 | TASK-008 |
| QUO-03 | 多供应商归一化与窗口（必需） | 保留Codex窗口、code-review/额外限制以及现有插件、内建读取器所有路径。 | TASK-007, TASK-008 |
| QUO-04 | 零、未知、元数据与超额（必需） | 0有效；未知非0；超额真实值保留；无数值响应按ADR-004统一保留原数值。 | TASK-007, TASK-008 |
| QUO-05 | 来源、新鲜度与旧缓存（必需） | live/passive、fetchedAt/observedAt分离；读缓存不更新观察时间。 | TASK-007, TASK-008 |
| QUO-06 | 搜索、提供方与状态筛选（必需） | 邮箱/名称查询及现有分类、注意状态筛选组合正确。 | TASK-008 |
| QUO-07 | 已用/剩余显示与汇总（必需） | 显示模式切换不修改底层数值；窗口不错误求和。 | TASK-008 |
| QUO-08 | 账号详情与单账号刷新（必需） | 全部窗口、指标、状态、时间、错误和修复入口可达。 | TASK-008 |
| QUO-09 | 取消、冷却与安全重试（必需） | 取消保留已完成结果；用户重试遵守共享阻断和账号冷却。 | TASK-008 |
| QUO-10 | 单位、credits与服务限制（必需） | 单位/币种按来源保真；余额不当订阅百分比；读数100%与明确limitReached区分。 | TASK-007, TASK-008 |

### CAP用量

| ID | 能力与范围 | 验收要求 | 实现任务 |
| --- | --- | --- | --- |
| CAP-01 | 插件能力与资源认证模式（必需） | 插件缺失非0；anonymous/management显式选择，失败不自动加管理密钥。 | TASK-009, TASK-010 |
| CAP-02 | 30分钟、小时、天与日历月范围（必需） | 30m、1–24h、1–7d、1–12 UTC日历月；月末/闰年/时区与整分钟边界正确。 | TASK-009, TASK-010 |
| CAP-03 | 模型样本概览与分组（必需） | provider/model/stream维度保留，样本完整性与来源可见。 | TASK-009, TASK-010 |
| CAP-04 | 月份服务端模型汇总（必需） | 月份概览只用initial汇总，不自动扫描全历史或混入样本TPS。 | TASK-009, TASK-010 |
| CAP-05 | initial/trends/groups/costs独立状态（必需） | 各资源独立窗口、时间、loading、error与快照；单区失败/重试局部化。 | TASK-009, TASK-010 |
| CAP-06 | 趋势图与完整数据表（必需） | 可切指标和组；不可解析时间仍在完整表保留并提示。 | TASK-009, TASK-010 |
| CAP-07 | 分组分页与详情（必需） | 页大小/上一页/下一页只请求groups，保留失败页的上下文。 | TASK-009, TASK-010 |
| CAP-08 | 费用、缺价与覆盖范围（必需） | 估算、缺失价格和覆盖范围明确，未知价格不当免费。 | TASK-009, TASK-010 |
| CAP-09 | 请求记录分页及请求详情（必需） | 请求状态、token、延迟、TTFT、模型、传输和来源字段可查。 | TASK-009, TASK-010 |
| CAP-10 | 管理统计与资源统计对比（必需） | 两条来源独立，不用一处数据补成另一处的权威结果。 | TASK-009, TASK-010 |
| CAP-11 | 读取预算与完整性（必需） | 页数、条数、字节预算受控；offsetUnverified/truncated/singlePage语义保留。 | TASK-009, TASK-010 |
| CAP-12 | 统计公式与失败样本（必需） | 有效输出/有效生成时间加权TPS；失败请求部分用量不混入成功速度。 | TASK-009, TASK-010 |
| CAP-13 | 范围选择、取消与旧窗口重试（必需） | 改范围不自动请求；取消面板不改变窗口；失败区域按原失败窗口重试。 | TASK-009, TASK-010 |

### 诊断与偏好

| ID | 能力与范围 | 验收要求 | 实现任务 |
| --- | --- | --- | --- |
| DIA-01 | 管理连接及能力诊断（必需） | 连接失败、可选能力告警、空账号分别展示。 | TASK-011 |
| DIA-02 | 账号授权与读取能力诊断（必需） | 禁用、上游授权、支持状态和账号级错误不误判为管理密钥失效。 | TASK-011 |
| DIA-03 | 原生错误文案与修复入口（必需） | 普通说明可操作；原始响应、凭据和邮箱不泄入诊断日志。 | TASK-011 |
| DIA-04 | 系统/浅色/深色主题（必需） | 主题持久化，前后台和配置变化保持一致。 | TASK-011 |
| DIA-05 | 邮箱遮罩与显示偏好（必需） | 额度、CAP、诊断及系统展示按同一隐私策略处理。 | TASK-011 |
| DIA-06 | 只读管理边界（必需） | 保留原有读取能力；不新增OAuth登录、启停上游账号或额度重置操作。 | TASK-011 |

### AI对话

| ID | 能力与范围 | 验收要求 | 实现任务 |
| --- | --- | --- | --- |
| CHA-01 | 管理接口发现推理Key（必需） | 按对应端点已验证的404/501接口不可用分支发现；401/403单独拒绝；不能把管理密钥当推理密钥。 | TASK-013 |
| CHA-02 | 手填、选择、保存及移除推理Key（必需） | 密钥作用域与保存/删除失败真实，临时模式不落盘。 | TASK-013 |
| CHA-03 | 模型目录与新会话模型策略（必需） | 刷新、固定/策略选择、模型消失与所记档位按当前行为恢复。 | TASK-013, TASK-015 |
| CHA-04 | 会话列表、搜索、新建、重命名与删除（必需） | 创建、重命名、删除与标题/正文包含搜索；中文子串、代码、%/_字面值及组合字符符合冻结Unicode合同，搜索不读取图片；不得用分词FTS结果直接替代。 | TASK-012, TASK-017 |
| CHA-05 | 逐会话草稿与编辑取消（必需） | 切页保留文字和附件，编辑取消恢复；进程死亡持久恢复作为Android质量改进。 | TASK-012, TASK-017 |
| CHA-06 | 图片选择、移除、缩略图与纯图片提问（必需） | 至少保留源端最多4张及纯图发送能力，大小/格式边界与取消可靠。 | TASK-012, TASK-017 |
| CHA-07 | 双协议流式生成与完成判定（必需） | Chat Completions与Anthropic Messages均完整；EOF不冒充完成；不可达分支不算已交付。 | TASK-014 |
| CHA-08 | 推理档位与兼容降级（必需） | automatic/off/low/medium/high/xhigh/max及实际applied/downgraded/omitted有明示。 | TASK-013, TASK-015 |
| CHA-09 | 停止、续写、attempt及用量累积（必需） | 父消息/尝试关联、边界去重、Unicode和用量累计正确。 | TASK-016 |
| CHA-10 | 编辑重发与重新生成（必需） | 确认及分支/替换语义明确；旧任务和排队写入不得覆盖新回复。 | TASK-016, TASK-017 |
| CHA-11 | 复制、删除消息与加入记忆（必需） | 动作全部可达，删除确认、复制反馈和副作用状态真实。 | TASK-017, TASK-019 |
| CHA-12 | 全局指令与会话system prompt（必需） | 修改缓冲与持久化正确；明确跨服务作用域和发送内容边界。 | TASK-013, TASK-019 |
| CHA-13 | 联网搜索五提供方与独立凭据（必需） | 迁移源码五提供方全部能力；搜索未配置、失败、零结果、中断分别建模。 | TASK-018 |
| CHA-14 | 来源展示与检索快照（必需） | 保留来源、完成标记和冻结query；外部文本按不可信引用隔离。 | TASK-018 |
| CHA-15 | 记忆新增编辑删除置顶及开关（必需） | 加入记忆、手工编辑、置顶排序、关闭与加载失败安全默认可验收。 | TASK-019 |
| CHA-16 | 斜杠技能CRUD与命令冲突（必需） | 技能提示词展开快照固定；重复命令拒绝，后改技能不改变原轮重试语义。 | TASK-019 |
| CHA-17 | 原生富文本、代码、表格和公式（必需） | 保留实际渲染能力和文本选择/复制，长流式下历史不整体重建。 | TASK-017, TASK-030 |
| CHA-18 | 静态HTML预览与源代码（必需） | 脚本、网络、本地文件、原生桥和导航隔离有真实负例，保留源代码查看/复制。 | TASK-020, TASK-031 |
| CHA-19 | 自动标题与用户标题优先（必需） | 标题开关与失败安全；迟到标题不覆盖用户已改标题。 | TASK-019 |
| CHA-20 | 后台有界收尾与完成通知（必需） | 退后台先保存、最多30秒尽力收尾、可更早中断；通知不带会话正文。 | TASK-021 |
| CHA-21 | 跨服务器历史发送确认（必需） | 确认绑定服务器和credential revision，旧确认失效且不损坏历史。 | TASK-016, TASK-031 |
| CHA-22 | 持久化失败与删除全部unknown恢复（必需） | 生成状态与保存状态独立；未知删除/写入结果保留并可核对。 | TASK-012, TASK-016, TASK-021 |
| CHA-23 | Token用量与省略历史提示（必需） | 输入/输出/推理用量和history omission保真；字符预算不误称token预算。 | TASK-016, TASK-017 |
| CHA-24 | 冷启动中断恢复与迟到拒绝（必需） | 未完成streaming恢复为interrupted；不自动重复计费请求。 | TASK-016, TASK-021 |

### 监控

| ID | 能力与范围 | 验收要求 | 实现任务 |
| --- | --- | --- | --- |
| MON-01 | 独立监控连接与凭据（必需） | 临时/记住、验证/更换/忘记独立于CPA连接，失败保留原操作能力。 | TASK-022, TASK-024 |
| MON-02 | 授权来源、账号和容量发现（必需） | capabilities鉴权只读；旧404有升级提示；预检不冒充名额预留。 | TASK-022, TASK-023, TASK-024 |
| MON-03 | 账号选择与有限租约（必需） | 现有1/4/8小时、最多5账号约束及来源授权有合同和UI。 | TASK-022, TASK-023, TASK-024 |
| MON-04 | 开始、取消启动与幂等注册（必需） | 取消先于迟到注册安全，重复启动不创建重复订阅。 | TASK-022, TASK-023, TASK-024 |
| MON-05 | 手动刷新与控制预算（必需） | 202只表示接受意图；刷新预算不等于采样频率。 | TASK-022, TASK-023, TASK-024 |
| MON-06 | 状态核对与来源缓存读取（必需） | 状态、revision、sequence和新鲜度保真；缓存读取不触发采集。 | TASK-022, TASK-023, TASK-024 |
| MON-07 | 远端停止、本机关闭与忘记（必需） | 三种动作分别展示结果；远端未知结果保留恢复记录。 | TASK-022, TASK-023, TASK-024 |
| MON-08 | 投递端点轮换与CAS（必需） | Android端点token不透明保真，旧回调不能替换新revision。 | TASK-022, TASK-023, TASK-024, TASK-025, TASK-026 |
| MON-09 | 原服务会话与恢复诊断（必需） | 更换连接后的detached handle、持久恢复记录仍可查询/停止/清除终态。 | TASK-022, TASK-023, TASK-024 |
| MON-10 | 持久取消、墓碑与重放防护（必需） | 不擅自添加TTL或丢失跨身份保护；重启不续租。 | TASK-022, TASK-023, TASK-024, TASK-031 |
| MON-11 | iOS v1与Android新协议兼容（必需） | 新增协议经协商，旧客户端行为维持；未部署新服务时Android明确不可新建而非伪成功。 | TASK-022, TASK-023, TASK-024 |
| MON-12 | Android推送与权限能力状态（必需） | 采集/平台接受/设备显示分离；GMS完整投递及无GMS明确降级。 | TASK-022, TASK-025, TASK-026 |

### 系统展示

| ID | 能力与范围 | 验收要求 | 实现任务 |
| --- | --- | --- | --- |
| WID-01 | 小组件共享默认关闭（必需） | 仅显式开启后投影；关停或切来源立即使旧展示不可用。 | TASK-027 |
| WID-02 | 概况与账号主要读数选择（必需） | 账号由opaque ID选择，失效选择不静默切换到其他账号。 | TASK-027 |
| WID-03 | 可调整尺寸与原生替代形态（必需） | Android桌面小组件支持紧凑/中/大空间；Apple锁屏形态映射有说明。 | TASK-027 |
| WID-04 | 新鲜度、未知与更新时间（必需） | 更新调度不保证实时；过期和无观察时间不伪装为新结果。 | TASK-027 |
| WID-05 | 小组件与监控通知深链（必需） | 点击恢复正确工作区/来源，冷启动失效ID安全。 | TASK-027 |
| WID-06 | 系统展示隐私与别名（必需） | 安全投影、邮箱遮罩、别名和删除/换来源清理一致；锁屏默认最小信息。 | TASK-027 |

### Android质量

| ID | 能力与范围 | 验收要求 | 实现任务 |
| --- | --- | --- | --- |
| AND-01 | SDK与工具链可重现（必需） | min26/compile37/target37作为候选，锁定实测兼容的JDK/Gradle/AGP/Kotlin/Compose矩阵。 | TASK-002 |
| AND-02 | 窗口、铰链、IME与现代返回（必需） | 真实窗口缩放/折叠/IME/back不能丢状态或重复请求。 | TASK-003, TASK-028 |
| AND-03 | 进程死亡与任务所有权（必需） | 持久状态、轻量导航状态、会话任务区分；system kill与force-stop分开验证。 | TASK-021, TASK-029 |
| AND-04 | Keystore和失败恢复（必需） | 凭据加密、失效分类和重新连接不导致聊天库被清空。 | TASK-004, TASK-029, TASK-031 |
| AND-05 | 云备份与设备转移边界（必需） | 旧/新备份规则、D2D及密钥缺失恢复均有验证。 | TASK-004, TASK-029, TASK-031 |
| AND-06 | 局域网运行时权限（必需） | Android17 target37 LAN拒绝/撤销有独立状态且不放松TLS。 | TASK-002, TASK-006, TASK-029 |
| AND-07 | 通知、GMS与后台限制（必需） | 通知权限、投递能力、监控运行分开；无GMS不误报全功能推送。 | TASK-021, TASK-026, TASK-029 |
| AND-08 | 原生无障碍与中文文案（必需） | TalkBack、最大支持字体、48dp触控、对比度、读序与图表文字等价。 | TASK-028 |
| AND-09 | 数据库和附件迁移一致性（必需） | 导出schema；文件与DB恢复、升级保留历史和非破坏迁移通过。 | TASK-012, TASK-029 |
| AND-10 | Release性能与资源预算（必需） | 固定真机、数据集、release profile及网络/内存/写放大测量有可追踪证据。 | TASK-030 |
| AND-11 | 签名、升级与隐私发布（必需） | 签名APK/AAB、升级、声明和包身份固定；候选SHA证据齐全。 | TASK-032 |

### 基线外增强

| ID | 能力与范围 | 验收要求 | 实现任务 |
| --- | --- | --- | --- |
| ENH-01 | 跨端历史交换与导入导出（可选增强） | 源版本未证明存在原生导出入口；额外设计versioned交换包、附件校验和默认无密钥导出。 | TASK-035 |
| ENH-02 | 跨进程持久聊天作业（可选增强） | 需要新服务端job/status/cancel合同，超出iOS当前最多约30秒best effort。 | TASK-036 |
| ENH-03 | 无GMS实时厂商推送（可选增强） | 仅在明确支持的厂商/分发渠道与测试设备上扩展，不冒充FCM替代已存在。 | TASK-037 |
| ENH-04 | 跨设备云同步（可选增强） | 另立身份、端到端加密、冲突合并与删除语义；不作为本次完全移植前置。 | TASK-038 |

## 5. 按能力定位源文件

以下路径来自固定提交；不能将同名 main 文件的后续变化混进本次合同。跨文件语义与测试向量见04/05。Android专有要求和增强不会虚构一个对应的Swift实现。

| 能力 | 固定源文件 |
| --- | --- |
| NAV-01 | [Sources/CPAQuotaUI/CPAQuotaRootView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/CPAQuotaRootView.swift) |
| NAV-02 | [Sources/CPAQuotaUI/CPAQuotaRootView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/CPAQuotaRootView.swift) |
| NAV-03 | [Sources/CPAQuotaActivity/CPAQuotaDeepLink.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaActivity/CPAQuotaDeepLink.swift) |
| CON-01 | [Sources/CPAQuotaKit/CPAServer.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAServer.swift) |
| CON-02 | [Sources/CPAQuotaUI/CPAQuotaSession.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/CPAQuotaSession.swift) |
| CON-03 | [Sources/CPAQuotaUI/LoginOnboardingView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/LoginOnboardingView.swift) |
| CON-04 | [Sources/CPAQuotaUI/CPAQuotaSession.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/CPAQuotaSession.swift) |
| CON-05 | [Sources/CPAQuotaKit/CPAClient.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAClient.swift) |
| CON-06 | [Sources/CPAQuotaUI/ConnectionManagementTabView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/ConnectionManagementTabView.swift) |
| CON-07 | [Sources/CPAQuotaKit/HTTPTransport.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/HTTPTransport.swift) |
| CON-08 | [Sources/CPAQuotaKit/QuotaRequestLimiter.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/QuotaRequestLimiter.swift) |
| QUO-01 | [Sources/CPAQuotaKit/CPAClient.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAClient.swift) |
| QUO-02 | [Sources/CPAQuotaKit/CPAQuotaStore.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAQuotaStore.swift) |
| QUO-03 | [Sources/CPAQuotaKit/QuotaParsing.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/QuotaParsing.swift) |
| QUO-04 | [Sources/CPAQuotaKit/Models.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/Models.swift)；[Sources/CPAQuotaKit/QuotaParsing.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/QuotaParsing.swift)；[Sources/CPAQuotaKit/CPAClient.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAClient.swift)；[Services/QuotaMonitor/cpa/client.go](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/cpa/client.go) |
| QUO-05 | [Sources/CPAQuotaKit/Models.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/Models.swift) |
| QUO-06 | [Sources/CPAQuotaUI/QuotasOverviewTabView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/QuotasOverviewTabView.swift) |
| QUO-07 | [Sources/CPAQuotaUI/QuotasOverviewTabView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/QuotasOverviewTabView.swift) |
| QUO-08 | [Sources/CPAQuotaUI/AccountDetailSheetView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/AccountDetailSheetView.swift) |
| QUO-09 | [Sources/CPAQuotaKit/CPAQuotaStore.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAQuotaStore.swift) |
| QUO-10 | [Sources/CPAQuotaKit/QuotaParsing.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/QuotaParsing.swift) |
| CAP-01 | [Sources/CPAQuotaUI/CAPUsageTabView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/CAPUsageTabView.swift) |
| CAP-02 | [Sources/CPAQuotaKit/CAPUsageWindow.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CAPUsageWindow.swift) |
| CAP-03 | [Sources/CPAQuotaUI/CAPUsageTabView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/CAPUsageTabView.swift) |
| CAP-04 | [Sources/CPAQuotaUI/CAPUsageTabView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/CAPUsageTabView.swift) |
| CAP-05 | [Sources/CPAQuotaKit/CAPUsageStore.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CAPUsageStore.swift) |
| CAP-06 | [Sources/CPAQuotaUI/CAPUsageDetailViews.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/CAPUsageDetailViews.swift) |
| CAP-07 | [Sources/CPAQuotaUI/CAPUsageDetailViews.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/CAPUsageDetailViews.swift) |
| CAP-08 | [Sources/CPAQuotaKit/CAPUsageCosts.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CAPUsageCosts.swift) |
| CAP-09 | [Sources/CPAQuotaUI/CAPUsageDetailViews.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/CAPUsageDetailViews.swift) |
| CAP-10 | [Sources/CPAQuotaUI/CAPUsageTabView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/CAPUsageTabView.swift) |
| CAP-11 | [Sources/CPAQuotaKit/CAPUsageClient.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CAPUsageClient.swift) |
| CAP-12 | [Sources/CPAQuotaKit/CAPUsageAnalytics.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CAPUsageAnalytics.swift) |
| CAP-13 | [Sources/CPAQuotaUI/CAPUsageCoordinator.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/CAPUsageCoordinator.swift) |
| DIA-01 | [Sources/CPAQuotaUI/AccountsDiagnosticsTabView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/AccountsDiagnosticsTabView.swift) |
| DIA-02 | [Sources/CPAQuotaUI/AccountDiagnosticPresentation.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/AccountDiagnosticPresentation.swift) |
| DIA-03 | [Sources/CPAQuotaUI/ErrorPresentation.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/ErrorPresentation.swift) |
| DIA-04 | [Sources/CPAQuotaUI/AppearanceAndPreferences.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/AppearanceAndPreferences.swift) |
| DIA-05 | [Sources/CPAQuotaUI/ConnectionManagementTabView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/ConnectionManagementTabView.swift) |
| DIA-06 | [Sources/CPAQuotaKit/CPAClient.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAClient.swift) |
| CHA-01 | [Sources/CPAQuotaKit/CPAAPIKeyDiscovery.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAAPIKeyDiscovery.swift) |
| CHA-02 | [Sources/CPAQuotaUI/Chat/ChatSettingsView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/Chat/ChatSettingsView.swift) |
| CHA-03 | [Sources/CPAQuotaKit/CPAModelCatalogClient.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/CPAModelCatalogClient.swift) |
| CHA-04 | [Sources/CPAQuotaUI/Chat/ChatWorkspaceView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/Chat/ChatWorkspaceView.swift) |
| CHA-05 | [Sources/CPAQuotaUI/Chat/ChatComposerView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/Chat/ChatComposerView.swift) |
| CHA-06 | [Sources/CPAQuotaUI/Chat/ChatComposerView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/Chat/ChatComposerView.swift) |
| CHA-07 | [Sources/CPAQuotaChat/AnyLanguageModelChatEngine.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaChat/AnyLanguageModelChatEngine.swift) |
| CHA-08 | [Sources/CPAQuotaChat/ChatReasoningPolicy.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaChat/ChatReasoningPolicy.swift) |
| CHA-09 | [Sources/CPAQuotaChat/ChatContinuation.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaChat/ChatContinuation.swift) |
| CHA-10 | [Sources/CPAQuotaUI/Chat/ChatMessageView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/Chat/ChatMessageView.swift) |
| CHA-11 | [Sources/CPAQuotaUI/Chat/ChatMessageView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/Chat/ChatMessageView.swift) |
| CHA-12 | [Sources/CPAQuotaChat/ChatPromptBuilder.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaChat/ChatPromptBuilder.swift) |
| CHA-13 | [Sources/CPAQuotaChat/ChatSearch.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaChat/ChatSearch.swift) |
| CHA-14 | [Sources/CPAQuotaChat/ChatPromptBuilder.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaChat/ChatPromptBuilder.swift) |
| CHA-15 | [Sources/CPAQuotaUI/Chat/ChatLibraryViews.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/Chat/ChatLibraryViews.swift) |
| CHA-16 | [Sources/CPAQuotaUI/Chat/ChatLibraryViews.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/Chat/ChatLibraryViews.swift) |
| CHA-17 | [Sources/CPAQuotaUI/Chat/ChatMessageView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/Chat/ChatMessageView.swift) |
| CHA-18 | [Sources/CPAQuotaUI/Chat/IsolatedChatHTMLWebView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/Chat/IsolatedChatHTMLWebView.swift) |
| CHA-19 | [Sources/CPAQuotaChat/ChatWorkspaceModel.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaChat/ChatWorkspaceModel.swift) |
| CHA-20 | [Sources/CPAQuotaChat/ChatBackgroundRunner.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaChat/ChatBackgroundRunner.swift) |
| CHA-21 | [Sources/CPAQuotaChat/ChatModels.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaChat/ChatModels.swift) |
| CHA-22 | [Sources/CPAQuotaChat/ChatPersistence.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaChat/ChatPersistence.swift) |
| CHA-23 | [Sources/CPAQuotaChat/ChatModels.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaChat/ChatModels.swift) |
| CHA-24 | [Sources/CPAQuotaChat/ChatWorkspaceModel.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaChat/ChatWorkspaceModel.swift) |
| MON-01 | [Sources/CPAQuotaUI/MonitoringTabView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/MonitoringTabView.swift) |
| MON-02 | [Sources/CPAQuotaKit/MonitoringCapabilities.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/MonitoringCapabilities.swift) |
| MON-03 | [Sources/CPAQuotaUI/MonitoringTabView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/MonitoringTabView.swift) |
| MON-04 | [Sources/CPAQuotaKit/MonitoringStore.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/MonitoringStore.swift) |
| MON-05 | [Sources/CPAQuotaKit/MonitoringClient.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/MonitoringClient.swift) |
| MON-06 | [Sources/CPAQuotaKit/MonitoringSnapshot.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/MonitoringSnapshot.swift) |
| MON-07 | [Sources/CPAQuotaUI/MonitoringTabView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/MonitoringTabView.swift) |
| MON-08 | [Sources/CPAQuotaKit/MonitoringSession.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaKit/MonitoringSession.swift) |
| MON-09 | [Sources/CPAQuotaUI/MonitoringTabView.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/MonitoringTabView.swift) |
| MON-10 | [Services/QuotaMonitor/service.go](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/service.go) |
| MON-11 | [Services/QuotaMonitor/capabilities.go](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/capabilities.go) |
| MON-12 | [Services/QuotaMonitor/delivery.go](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Services/QuotaMonitor/delivery.go) |
| WID-01 | [Sources/CPAQuotaUI/QuotaWidgetPublisher.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/QuotaWidgetPublisher.swift) |
| WID-02 | [Sources/CPAQuotaActivity/CPAQuotaWidget.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaActivity/CPAQuotaWidget.swift) |
| WID-03 | [Sources/CPAQuotaActivity/CPAQuotaWidget.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaActivity/CPAQuotaWidget.swift) |
| WID-04 | [Sources/CPAQuotaActivity/QuotaWidgetSnapshot.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaActivity/QuotaWidgetSnapshot.swift) |
| WID-05 | [Sources/CPAQuotaActivity/CPAQuotaDeepLink.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaActivity/CPAQuotaDeepLink.swift) |
| WID-06 | [Sources/CPAQuotaUI/AppearanceAndPreferences.swift](https://github.com/rinmashiro0529/cpa-quota-ios/blob/80beea9ed251a628307825cba99290b5f246575b/Sources/CPAQuotaUI/AppearanceAndPreferences.swift) |
| AND-01 | Android要求或候选增强；见06/10 |
| AND-02 | Android要求或候选增强；见06/10 |
| AND-03 | Android要求或候选增强；见06/10 |
| AND-04 | Android要求或候选增强；见06/10 |
| AND-05 | Android要求或候选增强；见06/10 |
| AND-06 | Android要求或候选增强；见06/10 |
| AND-07 | Android要求或候选增强；见06/10 |
| AND-08 | Android要求或候选增强；见06/10 |
| AND-09 | Android要求或候选增强；见06/10 |
| AND-10 | Android要求或候选增强；见06/10 |
| AND-11 | Android要求或候选增强；见06/10 |
| ENH-01 | Android要求或候选增强；见06/10 |
| ENH-02 | Android要求或候选增强；见06/10 |
| ENH-03 | Android要求或候选增强；见06/10 |
| ENH-04 | Android要求或候选增强；见06/10 |

## 6. 后续来源变动的处理

TASK-034 在发布前比较冻结提交与当时上游，逐项登记新增功能、修复、协议变化和已合并提案。只有安全阻断、兼容风险或经确认的新范围进入当前发布；进入后需同步能力、合同、任务和证据。若未摄取，应准确声明“对固定提交完整”，不能宣称对任何未来 iOS 版本完整。

已知差异包括 metadata-only 数值缓存、插件来源时间、Retry-After 解析、Unicode 预算和未合并附件方案。它们必须由明确决策处理，不能以机械跨语言翻译决定。
