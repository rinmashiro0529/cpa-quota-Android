# 10 · 决策记录、风险与来源

以下决定构成本候选的建议基准。状态均为 proposed；用户选择本方案后成为项目默认，工程中更改必须版本化记录理由、影响能力、替代方案与验证。它们不是已实现事实。

## 1. 候选核心决策

| ID | 默认决定 | 理由、代价与退出条件 |
| --- | --- | --- |
| ADR-001 | 原生Kotlin/Compose，独立Android仓库根目录 | 符合用户完整原生开发目标；Swift提供行为合同，不要求跨语言业务运行时 |
| ADR-002 | 纯Kotlin领域/协议 + data/platform实现 + feature界面 | 保持可测边界；复杂操作有coordinator，避免为每个getter增加空use case |
| ADR-003 | ConnectionContext与attempt identity显式代际；CPA/monitor独立 | 防迟到提交、跨服务历史误发、旧监控失去停止入口；由竞争条件测试证明 |
| ADR-004 | metadata-only独立更新元数据；保留旧numeric及原observedAt/numeric fetchedAt | 明确解决Swift/Go差异。没有数值不能伪装新额度，0仍有效；元数据自身时间另记，对应04 PARITY-01 |
| ADR-005 | 显式业务取消可终止共享single-flight；UI退订不等于业务取消 | 保留源端对外取消语义，修清所有权；改引用计数须单独行为变更，对应PARITY-02 |
| ADR-006 | 429未来deadline至少遵守到期；缺失/非法/已过期按60秒保守冷却 | 防请求风暴，明确区别源实现差异；固定时钟向量，对应PARITY-03 |
| ADR-007 | 插件显式来源时间严格校验，缺字段与非法值分开 | 不将无效数据包装成新观察；需确认实际插件合同，对应PARITY-04 |
| ADR-008 | Room + 私有附件 + 明确schema迁移；草稿持久化 | 改善源端整文件/内联图片成本；数据库与文件事务复杂度必须用故障协议承担 |
| ADR-009 | 生成由会话coordinator拥有；后台最多30秒尽力收尾 | 对齐iOS现有边界；立即checkpoint，系统可提前终止，不引入必需聊天服务器 |
| ADR-010 | SSE/双协议显式adapter；计费POST禁透明重试 | 有界兼容只在已分类拒绝发生，输出/用量后不回退；保留unknown与手动决策 |
| ADR-011 | 原生富文本；静态HTML单独隔离且必须交付 | 不让不可信HTML成为应用主体；必须同时验证功能和安全正负例 |
| ADR-012 | Go服务单一来源；v2订阅/端点模型兼容v1 | FCM不能套APNs token/ActivityID；跨仓库发布协调成本用合同和兼容测试控制 |
| ADR-013 | 取消终态和墓碑持久；禁止未经设计的TTL回收 | 防迟到注册或重启复活；容量耗尽显式拒绝；operation receipt有限保留依靠永久身份/单调revision防重放 |
| ADR-014 | GMS完整能力范围与无GMS降级范围明确分开 | 首版监控投递用FCM；若目标发行含无GMS完整实时推送，ENH-03升级为必需并加对应provider证据 |
| ADR-015 | min26/compile37/target37作为候选；稳定依赖组合经spike锁定 | 官方示例和release说明存在时间差；不从单个alpha示例推导生产组合 |
| ADR-016 | 秘密分类型；记住模式加密、临时模式仅内存；备份默认排除敏感内容 | Keystore丢钥不等于删除聊天；通知只用最小投影，持久化失败可恢复 |
| ADR-017 | 97能力/38任务结构化索引；93能力和34任务是默认发布必需 | 防止MVP被称完整；所有状态初始not_started，测试证据独立存放 |
| ADR-018 | 固定源SHA；PR33/34与后续上游变化显式摄取 | 可复现移植对象；不把未合并提案或未来变化混入主线 |
| ADR-019 | 中文和任意正文子串搜索保留包含语义 | Room/FTS只是实现选择；不能因tokenizer改变而漏掉原可见结果 |
| ADR-020 | 额度/CAP默认会话内；小组件仅许可投影；Android持久聊天与恢复有独立策略 | 不因统一数据库方便就把所有远端数据永久缓存；增加保存范围须有保留/删除合同 |

05 CHAT-ADR 是聊天局部展开，06 PLAT 是平台细则。若与本表出现实质不一致，应修订并记录；不能由实施者静默选一边。本表不替代04/05/06中更具体的输入、状态和失败边界。

## 2. 已识别源差异与移植陷阱

| 问题 | 已知事实/候选处置 | 负责人任务 |
| --- | --- | --- |
| 无数值快照 | Swift与Go缓存行为不完全同；按ADR-004拆元数据和numeric观察 | 001、007 |
| 插件时间 | 字段存在但非法与完全缺失不同；真实插件版本需确认 | 001、007 |
| Key接口兼容 | 源实现endpointUnavailable包含404/501，不能把所有接口错误一律回退 | 001、013 |
| 协议类型与可达能力 | OpenAI Chat Completions与Anthropic Messages可达；Responses类型存在不代表当前入口支持 | 001、014 |
| reasoning与参数 | 已核实的reasoning策略移植；无证据的temperature/top_p/seed不冒称必需源功能 | 013、015 |
| Unicode预算 | Swift Character不是Kotlin UTF-16 length；60k字符和续写UTF-8约束分别固定向量 | 001、014、016 |
| APNs与FCM | token校验、payload、身份和回调不同；adapter不改变订阅核心终态 | 022–026 |
| UI测试现状 | 主线总CI失败；#33/#34开放，不能用现有绿色局部job声称全绿 | 001、029、034 |
| 聊天磁盘布局 | 主线整JSON/内联图片；Android独立Room设计，不声称已经采纳未合并#34 | 012、016 |
| 隐私与后台 | 本地聊天完成通知不依赖FCM；固定文案不含标题正文；后台收尾不是持久生成 | 021、026 |
| 文档中的版本示例 | release表和代码示例可处于不同发布阶段；先实际构建安装，再锁版本 | 002 |

完整原始路径与对象标识见source-baseline，逐条证据见04/05。某条疑点尚未通过实服验证时，应保留该限定，不能把代码观察扩张成所有部署的权威合同。

## 3. 风险登记与解除条件

| 风险 | 影响与信号 | 负责任务 | 解除条件 |
| --- | --- | --- | --- |
| R01 目标平台/工具链不兼容 | 构建通过但LAN/窗口/后台行为错误 | 002、029 | 版本锁、最小/目标系统安装及关键spike证据 |
| R02 迟到响应/身份混淆 | 新连接被旧数据覆盖或历史误发 | 005、006、016 | barrier并发测试及实际请求目的地证据 |
| R03 额外推理请求 | 断流后重复计费、兼容回退失控 | 014–016 | 真实传输计数及所有unknown/部分输出负例 |
| R04 附件和迁移损坏 | 悬空引用、删除复活、低存储丢记录 | 012、029 | 各崩溃点恢复、schema升级、低存储报告 |
| R05 监控v1回归 | 新FCM改动破坏现有iOS/APNs | 022、023、025 | 固定v1 fixtures与真实兼容环境、旧数据迁移 |
| R06 FCM/设备输入缺失 | 合成成功但真实系统链未交付 | 026、029 | 获授权项目/真机投递、权限与无GMS状态验证 |
| R07 停止或token旧回调失效 | 已取消订阅复活，新端点被旧错误撤销 | 023–026 | 永久终态、CAS、refresh revision、重启/迟到用例 |
| R08 HTML/日志/备份泄露 | 用户内容或密钥离开原边界 | 004、020、031 | 正负安全测试、日志审计、备份恢复抽查 |
| R09 原生UI只适配单手机 | 折叠/输入法/大字体导致操作不可达 | 017、027、028 | 真机窗口连续流、TalkBack及200%字号证据 |
| R10 全量历史与渲染性能 | 首屏、长会话、图片内存不可用 | 012、017、030 | Release基准、分页/按需附件与写放大证据 |
| R11 上游漂移 | 交付时比较对象变成“最新”而证据未更新 | 034 | 差异清单、显式摄取、发布声明固定SHA |
| R12 规划被误当代码完成 | 文档全面但功能缺漏/假通过 | 033 | 93项实现证据、34任务状态及最终代码独立审阅 |
| R13 基准冲突 | 多份旧/新企划被混读执行 | 采用PR、09执行手册 | 用户选定记录、根入口清晰、候选保留版本 |
| R14 分发与升级不可逆 | 签名不连续、schema降级失败 | 032 | 签名覆盖升级、前向修复与恢复演练 |

风险负责人是任务角色，实际人员开工后登记。未有外部资源时先完成可独立交付部分；依赖资源的门禁保持blocked，不反复停住其他可做工作。

## 4. 首轮工程决策与实施自主权

TASK-001/002先给出合同fixture、实际版本锁和短技术原型，再定细节。默认候选不留空白来阻止开工：SDK、模块、存储、生命周期、推送通路、功能范围和最终门禁均有明确建议。

仅需据实补齐的实施输入包括：

- 可用开发机/CI与测试硬件；明确需要完整承诺的发行设备范围。
- CPA/插件/监控测试服务版本与合成数据；付费调用测试预算。
- 获授权的FCM项目、测试设备和服务凭据；秘密不进入文档。
- 应用包名、签名和发行渠道。包名与签名会影响升级和推送，应在外部注册前确定，不能随意占用他人标识。
- 上游Go服务变更的合并与部署负责人。

这些输入不要求在企划提交前全部获得。负责人能用安全默认推进的实现不必重新请示；涉及新增外部账户、费用、生产部署等才按当前授权处理。

## 5. 来源与事实引用方法

源码来源统一锁定：
[cpa-quota-ios@80beea9ed251a628307825cba99290b5f246575b](https://github.com/rinmashiro0529/cpa-quota-ios/tree/80beea9ed251a628307825cba99290b5f246575b)。

- [源对象与既有CI/PR台账](manifests/source-baseline.json)
- [能力到源路径的映射](02-source-parity.md)
- [协议与Go服务逐条来源](04-protocols-and-monitoring.md)
- [聊天与存储逐条来源](05-chat-and-storage.md)
- [Android官方来源、版本与核查时间](06-android-platform-security.md)

官方技术依据优先使用：

| 范围 | 官方资料 |
| --- | --- |
| 架构与状态 | [Android架构建议](https://developer.android.com/topic/architecture/recommendations) |
| API37与目标行为 | [Android17设置](https://developer.android.com/about/versions/17/setup-sdk)、[目标行为变化](https://developer.android.com/about/versions/17/behavior-changes-17) |
| 局域网 | [本地网络权限](https://developer.android.com/privacy-and-security/local-network-permission) |
| 原生导航 | [Navigation3发布记录](https://developer.android.com/jetpack/androidx/releases/navigation3) |
| 后台与省电 | [WorkManager工作定义](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work)、[Doze与App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby) |
| 推送 | [FCM Android接入](https://firebase.google.com/docs/cloud-messaging/android/get-started) |
| 秘密与备份 | [Keystore](https://developer.android.com/privacy-and-security/keystore)、[Auto Backup](https://developer.android.com/identity/data/autobackup) |
| 数据迁移 | [Room迁移](https://developer.android.com/training/data-storage/room/migrating-db-versions) |
| 系统展示 | [Glance](https://developer.android.com/develop/ui/compose/glance) |
| 性能 | [Macrobenchmark](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) |

核查日期为2026-11-25（Asia/Shanghai）。平台文档会变化：实施者应重新验证版本和发行政策，保留当次资料链接和核查日期。具体版本的兼容性以实际构建安装证据为准。

