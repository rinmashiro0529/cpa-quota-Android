# CPA Quota 原生 Android 完整移植：独立启动企划

**候选编号：native-android-independent-20261125 · 版本：1.0.0 · 状态：待用户选择，尚未成为仓库基准。**

本方案依据用户本轮指令、固定的 iOS 源码与官方 Android 资料独立形成。目标仓库原有 README、AGENTS、PROJECT_CONSTITUTION 和 docs 中的规划正文均未读取、未引用、未改写；只读取目录和 Git 元数据用于避让与校验。候选目录中的文档不自动覆盖仓库现行规则。用户将选择其中一份企划作为后续基准。

## 目标与范围

在独立仓库 **rinmashiro0529/cpa-quota-Android** 完成原生 Kotlin/Compose 客户端，完整承接 iOS 基线的五工作区、额度、CAP、账号诊断、完整 AI 对话、独立监控、小组件与系统展示能力。通过 Android 等价机制实现 Apple 专有能力，并保留安全、失败、恢复和可访问性语义。

- 功能来源：[cpa-quota-ios@80beea9](https://github.com/rinmashiro0529/cpa-quota-ios/tree/80beea9ed251a628307825cba99290b5f246575b)。
- 93 项发布必需能力：82 项源版本能力与 11 项 Android 质量要求。
- 38 个可分派工作项：34 项必需任务、4 项独立增强。
- 当前仅完成规划。所有 App/服务实现、构建、安装、迁移、推送和真机验收状态均为 not_started。
- 核查时间：2026-11-25，Asia/Shanghai。上游 #33/#34 均未合并；主线对应 CI 有 Duo UI 失败，详见来源台账。

**可安装里程碑不是完整移植完成。只有所有必需能力、平台映射和发布门禁都有准确版本证据，才能声明对该固定 iOS 版本完成移植。**

## 阅读顺序

| 读者/目的 | 必读 |
| --- | --- |
| 用户选择候选、负责人确认范围 | [01 项目目标与范围](01-charter-and-scope.md)、[02 来源与功能对齐](02-source-parity.md)、[10 决策与风险](10-decisions-risks-and-references.md) |
| 架构与基础工程 | [03 架构](03-architecture.md)、[04 协议与监控](04-protocols-and-monitoring.md)、[06 Android 平台与安全](06-android-platform-security.md) |
| 聊天开发 | [05 聊天、持久化与渲染](05-chat-and-storage.md)，并读 03/06 的身份和生命周期边界 |
| 任务负责人/agent | [07 执行计划](07-delivery-plan.md)、[09 Agent 执行手册](09-agent-playbook.md)、对应任务卡 |
| 测试与发布审阅者 | [08 验证与发布](08-verification-and-release.md)、功能矩阵、证据模板和准确候选代码 |

## 可机器读取的执行输入

| 文件 | 用途 |
| --- | --- |
| [feature-parity.json](manifests/feature-parity.json) | 规范能力 ID、来源、验收、任务映射；全量范围的唯一结构化索引 |
| [work-items.json](manifests/work-items.json) | 依赖 DAG、职责、产物、验收、仓库和初始状态 |
| [source-baseline.json](manifests/source-baseline.json) | 固定源码 SHA、对象索引、PR 和已有 CI 观察 |
| [target-preservation.json](manifests/target-preservation.json) | 原有九个文件的 Git 对象标识，用于确认本提案仅新增独立目录 |
| [evidence-template.json](manifests/evidence-template.json) | 实现与真实验证的证据记录格式 |
| [plan-manifest.json](plan-manifest.json) | 本方案版本、选择状态、入口和内容完整性清单 |

章节中的 CHAT/C/SP 等局部编号用于本章细节；跨团队交付和覆盖计算统一使用 feature-parity.json 的能力 ID 与 work-items.json 的 TASK 编号。人类阅读表由结构化索引生成；修改范围/依赖时两者必须同时更新。

## 采用流程

1. 用户明确选定本候选；在一次独立 PR 中记录选定的方案版本、目录和提交。
2. 将仓库根入口和协作规则更新为指向选定基准，同时保留其他候选的历史。此次提案提交不执行该步骤。
3. 执行 TASK-001 与 TASK-002：冻结业务合同并用实际环境验证版本矩阵。
4. 根据依赖图领取任务，逐项完成可审阅 PR。发布资格由 TASK-033 最终审定。

不自动合并候选、不创建数十个远端 issue、不触发部署或发布。后续 agent 若未看到用户选定记录，只能研究或完善候选，不能将它自称为已选基准。

## 本文档包校验

从仓库根运行：

```sh
python3 proposals/2026-11-25-native-android-independent/tools/validate_plan.py
```

校验器只检查本地文档完整性、ID/依赖/引用/覆盖和摘要，不联网、不启动模拟器、不执行应用测试。它通过不能证明 Android 产品已经正确，也不能替代任何运行时门禁。

后续有意修订本候选时，先修改结构化索引和章节，再运行以下命令；摘要刷新不代替内容审阅：

```sh
python3 proposals/2026-11-25-native-android-independent/tools/render_indexes.py
python3 proposals/2026-11-25-native-android-independent/tools/update_integrity.py
python3 proposals/2026-11-25-native-android-independent/tools/validate_plan.py
```

本候选位于独立分支 `proposal/native-android-independent-20261125`。采用前可在该分支阅读和评审；主分支原规划保持原样。用户选择后通过单独采用PR设置根入口，后续开发者再按本目录09领取任务。

## 开工时最先得到的结果

第一个业务里程碑应可安装并完成：安全连接 → 账号清单 → 渐进额度 → 详情 → 取消/错误恢复，同时验证手机与宽窗口。随后完成 CAP/诊断、完整聊天、监控/小组件，最后执行平台、性能、安全和发布审定。最终范围不会因阶段性版本可演示而缩减。

