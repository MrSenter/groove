# 工作流训练参考源

用途：给 agent-workflow-init 的流程训练设计提供外部依据。这里的来源只保留能转成工作流动作的内容；不把专注力课程、习惯打卡或脑训练游戏塞进生成工作区。

## 可吸收原则

| 来源 | 可吸收原则 | 在本项目里的落点 |
|---|---|---|
| Anders Ericsson / deliberate practice | 清晰目标、即时反馈、纠错重复；一次只练一个弱项 | `Agent执行手册.md` 的"工作流训练环"；`workflow.md` 的"本轮训练点" |
| Dunlosky 等学习技术综述 | 练习测试、间隔练习比重读/划重点更可靠 | 巡查时先回忆流程，再查文档，记录漏项 |
| Roediger & Karpicke / retrieval practice | 测试本身是学习动作 | A/B/C 流程升级前用 5 行复述入口、输入、步骤、读回、失败分支 |
| Sweller / cognitive load and worked examples | 新手先看范例，熟练后逐步撤脚手架 | `candidates.md` 保留完整示例，成熟后压缩成短执行卡 |
| Cal Newport / Deep Work | 聚焦工作块，减少上下文污染 | 开工前声明本轮只读哪些文件，不顺手扩读完整手册 |
| Gollwitzer / implementation intentions | "如果 X，就做 Y" 的触发句 | 失败分支写成触发句：字段不一致就停、读回、问用户 |
| Lally 等习惯形成研究 | 自动化来自稳定情境下重复执行 | 2 次候选、3 次草案、5 次不卡点才考虑极速 |
| WHO Surgical Safety Checklist | 高风险场景用短检查点，不靠长手册 | 不可逆动作只保留对象、数量/字段、提交前确认 |
| AHRQ TeamSTEPPS | brief/debrief、沟通闭环、情境监控 | 接手前 5 件事：流程、已读资料、输入权限、风险停点、成功读回 |
| Simons 等脑训练综述 | 通用认知训练的远迁移证据弱 | 不做注意力分数，只看真实任务少错、少读、能接手 |
| specialized training pattern | 限时 subagent 验证、3 轮刹车、1 分钟规则、冷门分支延后 | `Agent执行手册.md` 的"专项训练模式"；执行记录的专项训练记录 |

## 不吸收

- 不做"提升专注力"课程。
- 不做番茄钟、习惯打卡、动机模型或人格模型。
- 不做通用脑力训练、注意力小游戏或分数看板。
- 不把外部方法整套搬进来；只能转成触发、动作、读回、停点、巡查压缩。

## 当前内化方式

本项目采用轻量"工作流训练环"：

1. 开工前 30 秒：5 行复述入口、输入、步骤、读回、风险停点。
2. 执行中：只练 1 个弱项。
3. 收尾 3 行：漏了什么、下次触发句、是否进候选/主流程。
4. 巡查压缩：2-3 次真实任务验证后再固化，未验证继续观察。

遇到慢、脆弱、反复卡住的流程时，才启用"专项训练模式"：

1. subagent 只按文档跑 1 个样本。
2. routine 步骤超过 1 分钟即记为流程缺口。
3. 主 agent 修文档后最多重复 3 轮。
4. 主路径能跑就停，冷门分支延后到未来执行日志。

## 参考链接

- Ericsson, Prietula, Cokely, "The Making of an Expert": https://hbr.org/2007/07/the-making-of-an-expert
- Ericsson & Pool, `Peak`: https://www.harpercollins.com/products/peak-anders-ericssonrobert-pool
- Dunlosky et al., learning techniques review: https://doi.org/10.1177/1529100612453266
- Roediger & Karpicke, testing effect: https://doi.org/10.1111/j.1467-9280.2006.01693.x
- Cal Newport writing/books: https://calnewport.com/writing/
- Atul Gawande, `The Checklist Manifesto`: https://atulgawande.com/book/the-checklist-manifesto/
- WHO Surgical Safety Checklist: https://www.who.int/publications/i/item/9789241598590
- AHRQ TeamSTEPPS: https://www.ahrq.gov/teamstepps-program/index.html
- Coursera, `Learning How to Learn`: https://www.coursera.org/learn/learning-how-to-learn
- Simons et al., brain-training critique: https://doi.org/10.1177/1529100616661983
