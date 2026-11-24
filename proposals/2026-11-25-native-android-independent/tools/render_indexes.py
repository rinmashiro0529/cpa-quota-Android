#!/usr/bin/env python3
"""Render the two human-readable indexes from the candidate's JSON records."""
from pathlib import Path
from collections import Counter
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]

def read(name):
    return json.loads((ROOT / "manifests" / name).read_text(encoding="utf-8"))

def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")

def feature_document():
    data = read("feature-parity.json")
    features = data["features"]
    source = read("source-baseline.json")
    groups = list(dict.fromkeys(f["group"] for f in features))
    lines = [
        "# 02 · 来源审计与完整功能对齐", "",
        "本章由 tools/render_indexes.py 根据结构化清单生成。能力编号与验收以 [feature-parity.json](manifests/feature-parity.json) 为结构化索引；改变范围后必须重新生成本章。", "",
        "## 1. 固定来源与审计边界", "",
        f"- 基线：[cpa-quota-ios@{source['source_commit'][:7]}]({source['source_url']})；这是功能合同的比较对象。",
        "- 审阅了主线的关键模型、协议、UI、存储、监控服务和合同测试；来源对象索引不代表每个文件均已逐行审阅，更不代表执行过测试。",
        "- 未读取目标 Android 仓库原有企划正文；本提案的分析不以旧企划为输入。",
        "- 上游 #33 与 #34 仍以观察时的未合并提案记录；不把它们的行为或性能结论算入主线。",
        f"- 已观察源 CI：[run {source['observed_ci']['run_id']}]({source['observed_ci']['url']}) 总体失败，Duo UI shard 2/3 失败；Go、Swift package/Release 与 iPhone 18 Pro UI 通过。这些是既有运行记录，本任务没有重新执行。",
        "- 本文中的 Android 架构和修复选择属于候选决策；系统平台事实来源见 06，源端差异处置见 04/05/10。", "",
        "## 2. 范围计数与完成规则", "",
        "共 97 个规范能力 ID：82 项源版本对齐能力、11 项 Android 实现质量要求，以及 4 项基线外增强。93 项 release_required=true 共同构成完整版本门槛。", "",
        "一个能力 ID 可以包含多项有联系的用户操作，数量不代表复杂度或自动测试数量。跨团队使用本章 ID；04 的合同用例、05 的 CHAT/C 编号和06的平台用例是展开细节，不计为重复功能。", "",
        "所有实现状态初始为 not_started。映射到多个任务表示多个职责共同覆盖，最终审定任务不能代替具体实现证据。涉及安全与失败的场景必须与成功场景同时完成。", "",
        "## 3. 平台映射", "",
        "| 源能力 | Android 交付 | 对齐边界 |",
        "| --- | --- | --- |",
        "| SwiftUI 五工作区/独立路径 | Compose + 独立导航栈 + adaptive pane | 保留选中项、返回和恢复语义；视图随窗口调整 |",
        "| Keychain / 记住或临时连接 | Keystore + SecretStore + 显式保存事务 | 秘密持久化失败真实反馈，禁止明文回退 |",
        "| WidgetKit / App Group 投影 | Glance / AppWidget + 最小安全投影 | 默认不共享；无选中账号时不能换成他人账号 |",
        "| ActivityKit 远端监控 | 新监控协议 + FCM + Android 通知/小组件 | 保留状态、停止和恢复；不承诺所有系统同一锁屏视觉 |",
        "| beginBackgroundTask 有界收尾 | 退后台 checkpoint + 最多30秒尽力收尾 | 系统可提前回收；进程死亡不自动重发 |",
        "| 原生富文本与静态 HTML | 原生 Markdown/代码/数学 + 隔离静态预览 | 禁止脚本/外网/本地读取，不能由关闭功能来冒充安全等价 |",
        "| 源端整文件聊天存储 | Room + 私有附件 + 迁移与恢复 | 保留内容语义，独立改善持久化；跨端导入导出另列增强 |", "",
        "## 4. 完整能力矩阵", "",
    ]
    for group in groups:
        lines.extend([f"### {group}", "", "| ID | 能力与范围 | 验收要求 | 实现任务 |", "| --- | --- | --- | --- |"])
        for f in features:
            if f["group"] != group:
                continue
            tasks = [i for i in f["work_items"] if i not in {"TASK-001", "TASK-033", "TASK-034"}]
            label = "必需" if f["release_required"] else "可选增强"
            lines.append(f"| {f['id']} | {cell(f['title'])}（{label}） | {cell(f['acceptance'])} | {', '.join(tasks)} |")
        lines.append("")
    lines.extend([
        "## 5. 按能力定位源文件", "",
        "以下路径来自固定提交；不能将同名 main 文件的后续变化混进本次合同。跨文件语义与测试向量见04/05。Android专有要求和增强不会虚构一个对应的Swift实现。", "",
        "| 能力 | 固定源文件 |",
        "| --- | --- |",
    ])
    for f in features:
        refs = [f"[{path}](https://github.com/{source['source_repository']}/blob/{source['source_commit']}/{path})" for path in f["source_paths"]]
        lines.append(f"| {f['id']} | {'；'.join(refs) if refs else 'Android要求或候选增强；见06/10'} |")
    lines.extend([
        "", "## 6. 后续来源变动的处理", "",
        "TASK-034 在发布前比较冻结提交与当时上游，逐项登记新增功能、修复、协议变化和已合并提案。只有安全阻断、兼容风险或经确认的新范围进入当前发布；进入后需同步能力、合同、任务和证据。若未摄取，应准确声明“对固定提交完整”，不能宣称对任何未来 iOS 版本完整。", "",
        "已知差异包括 metadata-only 数值缓存、插件来源时间、Retry-After 解析、Unicode 预算和未合并附件方案。它们必须由明确决策处理，不能以机械跨语言翻译决定。", "",
    ])
    return "\n".join(lines)

def task_document():
    data = read("work-items.json")
    tasks = data["work_items"]
    lines = [
        "# 07 · 交付路径、依赖与可领取任务", "",
        "任务卡由 tools/render_indexes.py 从 [work-items.json](manifests/work-items.json) 生成。每个工作项是可追踪的交付责任；L 级任务应拆成数个依赖明确的 PR，不要求一个巨大 PR。当前所有任务尚未启动、尚未分派。", "",
        "## 1. 执行顺序", "",
        "先冻结协议与工具链，再做安全连接—账号—额度的完整纵向链。CAP、聊天、服务端监控在基础接口稳定后并行；系统展示与真实推送随后汇合。最后覆盖真实系统故障、升级、性能、安全与源版本漂移，达到完整发布条件。", "",
        "以下图是职责汇合关系，具体阻塞依赖以任务卡 depends_on 为准。M2/M3/M4 是能力里程碑，并不意味着整个团队必须串行做完一个阶段才开始下一个。", "",
        "```mermaid",
        "flowchart TD",
        '    A["合同与工具链"] --> B["安全基础与额度"]',
        '    A --> C["监控v2合同与Go实现"]',
        '    B --> D["CAP与诊断"]',
        '    B --> E["完整聊天与本地数据"]',
        '    B --> F["Android监控与小组件"]',
        '    C --> F',
        '    D --> G["设备、升级、性能、安全"]',
        '    E --> G',
        '    F --> G',
        '    G --> H["来源漂移与完整发布审定"]',
        "```", "",
        "## 2. 里程碑及退出条件", "",
        "| 阶段 | 可演示成果 | 必须通过的退出条件 |",
        "| --- | --- | --- |",
        "| M0 | 固定合同与最小真实原生工程 | 源SHA/差异决策、可构建版本矩阵、SDK/LAN/SSE/后台/渲染预研结果 |",
        "| M1 | 安装后连接、查询全部额度、详情与恢复 | 凭据事务、身份代际、限流、取消、未知与旧数据保真；手机和宽窗口可走完整链 |",
        "| M2 | CAP四栏目与全部诊断设置 | 独立资源窗口、分页预算、统计完整性、只读边界 |",
        "| M3 | 完整聊天工作区 | 消息所有操作、五搜索、记忆/技能、双协议、推理、富文本/HTML、存储与后台收尾全部可用 |",
        "| M4 | 完整监控与系统展示 | Go v1兼容/v2、真实FCM、token轮换、停止/恢复、小组件与隐私 |",
        "| M5 | 可审阅Release候选 | 声明设备矩阵、升级恢复、性能预算、安全审阅、签名与运营材料 |",
        "| M6 | 对固定源版本的完整移植 | 93项必需能力证据、34项必需任务verified、最终SHA/二进制/服务版本一致 |", "",
        "## 3. 团队与 agent 并行边界", "",
        "| 工作流 | 主要任务 | 独占接口/共享协调 |",
        "| --- | --- | --- |",
        "| 基础与合同 | 001–008、031 | ConnectionContext、RequestCoordinator、错误、版本catalog；修改须通知受影响负责人 |",
        "| CAP与原生工作区 | 009–011、028 | CAPResourceState、时间窗口、设计token；不复制数据客户端 |",
        "| 聊天与数据 | 012–021 | Room schema、附件事务、GenerationCoordinator；schema按序迁移 |",
        "| 监控服务与客户端 | 022–027 | v2 wire合同、Go兼容、push adapter；跨仓库合同版本先锁定 |",
        "| 质量与发布整合 | 029–034 | 集成环境、证据、Release产物、来源漂移；审阅者不得仅为实现者自证 |", "",
        "1–2名开发者时依上述路径逐段推进；3–4名可在共同合同稳定后分别负责CAP、聊天、监控，保留一名整合负责人。agent数量不等于交付速度：同一schema、版本catalog或状态机只设一个变更协调者。", "",
        "技术调查可在依赖未verified时先做；正式集成不能把未合并的接口猜测当成已经稳定。若使用临时mock，PR必须标明其覆盖边界，mock绿灯不能关闭真实服务或设备门禁。", "",
        "## 4. 工作量与排期方法", "",
        "S/M/L 是相对复杂度，不是承诺日期：S为局部可审阅成果，M涉及数个组件或一个系统边界，L涉及并发、协议、迁移或跨平台链。开工后先完成M0和额度纵向链，再根据实际吞吐、真实设备与服务可用性估算日历时间。", "",
        "预留明确的集成、升级、安全与返工容量；不能把38个任务平均分天。FCM配置、真机、签名材料和服务部署环境是交付前置，取得时间应登记负责人和日期。缺失时可推进合成合同，但相应门禁保持blocked。", "",
        "## 5. 工作项索引", "",
        "| ID | 任务 | 阶段 | 大小 | 依赖 | 仓库 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for t in tasks:
        repo = "Go源仓库" if t["repository"].endswith("-ios") else "Android"
        lines.append(f"| {t['id']} | {cell(t['title'])} | {t['milestone']} | {t['size']} | {', '.join(t['depends_on']) or '无'} | {repo} |")
    lines.extend(["", "## 6. 可直接领取的任务卡", ""])
    for t in tasks:
        lines.extend([
            f"### {t['id']} · {t['title']}", "",
            f"- 仓库：{t['repository']}；阶段：{t['milestone']}；相对规模：{t['size']}；{'发布必需' if t['release_required'] else '可选增强'}。",
            f"- 前置：{', '.join(t['depends_on']) or '无'}。",
            f"- 能力：{', '.join(t['feature_ids'])}。",
            "- 状态：not_started；负责人：未分派；证据：尚无。",
            "", "**交付物**", "",
        ])
        lines.extend(f"- {d}" for d in t["deliverables"])
        lines.extend(["", "**验收**", ""])
        lines.extend(f"- {a}" for a in t["acceptance"])
        lines.extend(["", "关闭此工作项前，按 [证据模板](manifests/evidence-template.json) 记录代码提交、命令、环境、结果及独立审阅，不以企划本身作为实现证据。", ""])
    lines.extend([
        "## 7. 每项任务如何关闭", "",
        "状态只能按 not_started → in_progress → in_review → verified 推进；发现阻塞可进入blocked并记录解除条件。文档编写完成不能使产品任务verified。通过代码审阅但缺设备/服务证据时仍保持in_review或blocked。已验证后发生影响性变更必须重新打开对应门禁。", "",
        "当前企划被选择后，任务负责人使用 [task-brief.md](templates/task-brief.md) 建立本次范围；PR使用 [implementation-pr.md](templates/implementation-pr.md)。不必一次创建全部远端Issue，先领取依赖满足的工作项。", "",
    ])
    return "\n".join(lines)

def outputs():
    return {"02-source-parity.md": feature_document(), "07-delivery-plan.md": task_document()}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    bad = []
    for name, content in outputs().items():
        if args.check:
            if not (ROOT / name).is_file() or (ROOT / name).read_text(encoding="utf-8") != content:
                bad.append(name)
        else:
            (ROOT / name).write_text(content, encoding="utf-8")
    if bad:
        raise SystemExit("Generated indexes are stale: " + ", ".join(bad))
    print("Index consistency OK" if args.check else "Rendered 02-source-parity.md and 07-delivery-plan.md")

