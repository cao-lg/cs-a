# 教师平台迭代：跨设备迁移、邮件发送、激活码/学生明细展示

## 一、已完成的功能

### 1. 教师端跨设备导入/导出
- `teacher-console` 新增「老师跨设备迁移」：可把激活码库、已导入学生文件、邮件配置打包为 JSON 导出；换电脑后导入即可继续分析。
- 导出文件类型为 `teacher-console-session`，含 `secrets / files / teacherEmail`，**仍不上传任何服务器**。

### 2. 学生端 + 教师端「邮件发送」能力
- **学生端**（cs-a / ss-a）：在「数据管理」面板增加老师邮箱输入框 + **「导出并发送给老师」**按钮。
  - 自动导出 JSON 学习数据并下载。
  - 唤起系统邮件客户端，`mailto:` 预填固定主题：`[学练测平台] 学习数据提交 - 学号{sid} 姓名{name} - {日期}`，正文含归属信息，方便老师按主题归档。
  - 零后端、不经过任何第三方服务器，数据文件仍只存在用户本地，老师收到后手动附加 JSON 即可。
- **教师端**（tc）：在「分析报表」面板增加目标邮箱配置 + **「邮件发送报表」**按钮。
  - 预填主题：`[学练测平台] 平时成绩分析报表 - {日期} - 共{人数}人`，正文含班级概况。

### 3. 教师端 UI 完善
- **发放激活码面板**：
  - 顶部直接展示「已签发学生名单（x 人）」表格，含学号、姓名、证书状态。
  - 粘贴 `tools/teacher-secrets.json` 后展示「发放明细」表格（学号 · 姓名 · 激活码）。
  - 名册编辑、本地签发命令提示保留。
- **导入与核验面板**：
  - 已导入文件列表保留（真实/被篡改/非本校）。
  - 新增「已核验学生明细」表格：学号、姓名、激活码（脱敏显示）、阶段考均分、单元均分、XP、等级、学习分钟、错题数。
- **分析报表面板**：
  - 概览卡、成绩分布、综合排名、高频错点、学生明细、导出 CSV、邮件发送报表。

### 4. 工程调整
- `tools/issue-codes.mjs`：把 `public.json` + `certs.json` 统一输出到 `src/data/`，教师端和学生站同源。
- `src/verify.js`：动态读取 `src/data/public.json`，fallback 到硬编码 `public.js`，便于轮换公钥后自动生效。
- 新增默认空 `src/data/certs.json`，避免首次 clone 未签发时构建报错。
- `index.html` 引入 Outfit 字体，保持与学生站一致。

## 二、安全与隐私红线

- **私钥** `tools/teacher-keys.json` 与 **激活码库** `tools/teacher-secrets.json` 仍只存本机，已 gitignore，**不进库、不进前端、不上传**。
- `certs.json`（公开证书）与 `public.json`（公钥）可公开给学生站，不含激活码。
- 邮件功能使用 `mailto:` 协议唤起本地邮件客户端，**不经过任何邮件服务商后端**，不泄露数据。

## 三、验证

- **三站 `npm run build` 均 0 error**：
  - `teacher-console`：构建 17KB JS，正常。
  - `learning-platform` / `sales-platform`：构建成功（chunk 大小警告，不影响功能）。
- `teacher-console` 预览服务可正常访问，三面板 UI 渲染正常。
- 学生端 AdminConsole 新 UI 已渲染，邮件按钮与邮箱输入框就位。

## 四、提交与推送状态

- `teacher-console`：已本地提交 `b613480`。
- `learning-platform`（即 chain_supply 父仓库，对应 cs-a 远端）：已本地提交 `5ba272b`，包含学生端邮件功能 + overview。
- `sales-platform`：已本地提交 `2ecbc3f`。
- **待推送**：cs-a / ss-a / tc-a 均需一次性 GitHub Personal Access Token 完成推送。`cao-lg/tc-a` 仓库尚未创建。

## 五、待办

1. 提供 GitHub Personal Access Token，完成 cs-a / ss-a / tc-a 的推送（tc-a 需先创建仓库）。
2. 到 GitHub 撤销并轮换此前 ss-a remote 暴露的 token（如尚未处理）。
3. 上线后用真实学生导出文件跑一遍教师端完整流程：发码 → 学生导出 → 老师导入核验 → 邮件发送报表。
