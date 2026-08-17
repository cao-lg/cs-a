# 画像页愉悦层同步 + 综合测试独立入口

## 完成内容（两站：cs-a 供应链 / ss-a 销售，均已同步）

### 1. 综合测试独立入口
- **顶栏新增「测试中心」**：`Layout.jsx` 加 `<Link to={/tests/:courseId}>`，active 按 `/tests/` 前缀。
- **画像页新增「去测验中心」卡片**：`Profile.jsx` 顶部一键直达 `/tests/:courseId`，文案覆盖单元测试 / 项目阶段考 / 结业大考。
- 入口靠 `api.js` 新增 `defaultCourseId()`（记忆化取 `manifest.courses[0]`）拼出课程 id。

### 2. 画像页（我的进步）愉悦层三件套
- **XP 进度条填充 + count-up**：`0% → 目标` 宽度过渡；XP 总量与 `xpInto` 数字 count-up（requestAnimationFrame，reduced-motion 直接定值）。
- **多步 Celebration 复用**：挂载时比对 localStorage `profile:seen:v1` 快照，检测升级 / 新徽章即触发（entry→xp→level→badges→finale）。
- **新解锁徽章高亮**：`.badge.is-new`（pop + 薄荷扫光）。
- **错题本微交互**：`.wb-item` / `.wb-redo` hover 上浮。
- 全部动效尊重 `prefers-reduced-motion`（CSS 媒体查询 + JS detect 双重降级）。

## 关键修复
`defaultCourseId` 首版误取 `courses?.[0]?.id`（对象属性），但 `manifest.courses` 是**id 字符串数组**，修正为 `courses?.[0]`。

## 验证（agent-browser 实开预览）
- 顶栏「测试中心」渲染 ✓
- 画像页「去测验中心」卡片 href=`#/tests/supply-chain` ✓
- 注入 xp=200 + 新徽章后 reload：多步 Celebration 弹出、等级升「入门学徒」、`.badge.is-new` 高亮、XP 条 `0%→33%` ✓

## 构建与推送
- 两站 `npm run build` 均 0 error（900 modules）。
- cs-a `b27a4ca`（内联 token 推送，remote 保持 token-free）。
- ss-a `c096be3`（用 remote 内嵌 token 鉴权后，已将本地 remote 改回 token-free）。

## ⚠️ 安全提醒
**ss-a 远端 token `ghp_YXPn…` 已暴露，且仍具 GitHub 仓库写权限，请立即到 GitHub 撤销并轮换新 token。** 本会话已把两站本地 remote URL 改为干净形式。
