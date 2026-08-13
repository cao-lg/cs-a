# 示例单元（内容模板范本）

本目录是《需求补充规格 v0.2》的**可直接复制的内容范本**，演示三层新增需求（单元前/后测、阅读中交互检查点、探索+挑战）在一个真实单元里如何落地。

## 目录结构（与平台 public/data 对齐）

```
examples/sample-unit/
├── courses/
│   ├── sample-course.json      # 课程 + 章节 + units 结构
│   └── u01-temperature.md      # 单元学习正文（含 :::checkpoint / :::explore / :::challenge）
└── assessments/
    └── u01-temperature.json    # 单元前测(pre) / 后测(post)
```

接入平台时，将 `courses/` 与 `assessments/` 整体复制到项目根 `public/data/` 下对应目录即可。

## 结构要点

- `chapter` 下用 `units[]` 承载**最小闭环单元**（需求规格第 5 节）。
- `unit` 通过 `preAssessment` / `postAssessment` 指向 `assessments` 文件 id。
- 正文 Markdown 用三条指令嵌入互动：
  - `:::checkpoint` —— 阅读中检查点（`predict` / `fill` / `mc`），即时反馈、**零惩罚**。
  - `:::explore` —— 探索分支（可选、轻量引导，诱发兴趣）。
  - `:::challenge` —— 进阶挑战（更难、可选）；**编程课可改用 `type="output"` 代码题**。

## 解析约定（给前端）

- `LearnChapter.tsx` 需用 `react-markdown` 自定义组件解析上述指令。
- 检查点 / 挑战的作答与正误写入 `checkpoint_records`（`kind = 'checkpoint' | 'challenge'`），纳入离线同步队列。
- 前/后测走 `/api/assessment`，结果写入 `assessment_records`，`/api/stats` 计算 `learningGain = post − pre`。

## 密度自检（防泛滥）

- 本示例单元正文约 10 分钟阅读，含 **2 个检查点 + 1 探索 + 1 挑战**，符合"每 3–5 分钟 / 每个知识点 ≤ 1 检查点"的硬性规则。
