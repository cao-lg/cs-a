# 项目四：销售交易数据分析 —— 拆解示例

本目录是用 `curriculum-decomposer` 技能，把《项目四：销售交易数据分析3.docx》按《需求补充规格 v0.2》拆解后的**可运行范本**。

## 映射关系（教材 → 框架）

| 教材原文 | 框架单元 | 说明 |
|---|---|---|
| 任务4.1 基本认知（五层指标） | `u41-indicators`（已完整拆解） | 含 5 个 checkpoint + 1 explore + 1 challenge + pre/post |
| 任务4.2 逻辑错误数据清洗 | `u42-clean` | 三类错误识别 + 标注/清洗（可出 Python 清洗挑战） |
| 任务4.3 分析方法与可视化 | `u43-compare` / `u43-cross` | 对比五维度、交叉分析，图表选型 checkpoint |
| 任务4.4 趋势预测 | `u44-level` / `u44-season` / `u44-trend` | 移动平均/指数平滑/季节指数/图表法，公式 fill + 代码挑战 |
| 任务4.5 智能体综合预测 | `u45-agent` | 多模型匹配 + 备货决策 challenge |

教材自带的【AI导学/助学/助训/加速/拓学】标记，已对位转成 前测 / checkpoint / challenge / explore（见技能 `references/framework.md` 的"教材标记映射"表）。

## 本目录内容

- `courses/sales-project4.json` —— 课程+章节+units 完整骨架（4.1–4.5 全覆盖）
- `courses/u41-indicators.md` —— **任务4.1 完整拆解单元**（含三条指令）
- `assessments/u41-indicators.json` —— 任务4.1 前测/后测

> `u42`–`u45` 仅给出单元骨架（objectives + 路径），正文与评测可按同一模板补全。

## 接入方式

将 `courses/` 与 `assessments/` 复制到平台项目根 `public/data/` 下对应目录即可。
