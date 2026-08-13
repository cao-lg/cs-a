import { Link } from 'react-router-dom'
import { Reveal } from './motion'

// 小北在 sales-project4 里的成长剧本：单元 id -> 一句"职场进度"标签
const STAGE_LABELS = {
  'u41-indicators': '入职第一天 · 看懂老板要的"几个数字"',
  'u42-clean': '入职第二周 · 给订单表做一次体检',
  'u43-compare': '轮岗市场部 · 把"对比"讲清楚',
  'u43-cross': '轮岗运营 · 双十一复盘交叉看',
  'u44-level': '支援供应链 · 下周销量怎么估',
  'u44-season': '生鲜采销 · 月饼到底备多少',
  'u44-trend': '增长分析会 · 明年规模敢外推吗',
  'u45-agent': '独当一面 · 让智能体替我下判断',
}

export default function GrowthJourney({ course, status, courseId }) {
  const stages = []
  course.chapters.forEach((ch) => ch.units.forEach((u) => stages.push(u)))

  return (
    <Reveal>
      <div className="growth">
        <div className="growth-head">
          <span className="growth-kicker">📈 小北的成长路线</span>
          <p className="growth-sub">从入职第一天到独当一面，每一关都是一次真实任务。完成度会随着你的课前/课后测自动点亮。</p>
        </div>
        <div className="growth-track">
          {stages.map((u, i) => {
            const rec = status[u.id] || {}
            const done = rec.pre && rec.post
            const active = rec.pre && !rec.post
            const state = done ? 'done' : active ? 'active' : 'locked'
            const label = STAGE_LABELS[u.id] || u.title.replace(/^单元：/, '')
            return (
              <Link
                key={u.id}
                to={`/learn/${courseId}/${u.id}`}
                className={`growth-node ${state}`}
              >
                <span className="growth-dot">{done ? '✓' : i + 1}</span>
                <div className="growth-body">
                  <div className="growth-title">{u.title.replace(/^单元：/, '')}</div>
                  <div className="growth-label">{label}</div>
                  <div className="growth-meta">
                    <span className={`growth-state ${state}`}>
                      {state === 'done' ? '已完成' : state === 'active' ? '进行中' : '未开始'}
                    </span>
                    <span className="growth-sep">·</span>
                    <span>{u.duration}</span>
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      </div>
    </Reveal>
  )
}
