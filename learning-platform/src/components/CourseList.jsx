import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listCourses, getCourse } from '../lib/api'
import { Reveal, Stagger, StaggerItem, Magnetic, Tilt } from './motion'

const FLOW = [
  { icon: '📋', label: '单元前测 · 摸清起点' },
  { icon: '📖', label: '情境学习 · 互动检查点' },
  { icon: '🧭', label: '探索 & 挑战 · 点燃好奇' },
  { icon: '📈', label: '单元后测 · 看见增益' },
]

export default function CourseList() {
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    ;(async () => {
      const ids = await listCourses()
      const list = await Promise.all(ids.map((id) => getCourse(id)))
      setCourses(list)
      setLoading(false)
    })()
  }, [])

  if (loading) return <div className="state">正在点亮学习地图…</div>

  return (
    <div className="course-list">
      <section className="hero">
        <div>
          <span className="hero-badge">✦ 自适应学习闭环</span>
          <h1>
            让每一单元<span className="grad"> 学得有痕</span>
            <br />练得有趣
          </h1>
          <p className="lead">
            先测起点，再带着情境去探索，最后用后测看见自己的成长。把枯燥的知识点，变成一场边玩边记的旅程。
          </p>
          <div className="hero-cta">
            <Magnetic>
              <Link to={`/course/${courses[0]?.id}`} className="btn primary">
                开始第一个单元 →
              </Link>
            </Magnetic>
            <Link to="/profile" className="btn">查看我的进步</Link>
          </div>
          <div className="hero-stats">
            <div className="hs"><b>{courses.length}</b><span>门课程</span></div>
            <div className="hs"><b>{courses.reduce((n, c) => n + c.chapters.reduce((m, ch) => m + ch.units.length, 0), 0)}</b><span>学习单元</span></div>
            <div className="hs"><b>3</b><span>互动环节</span></div>
          </div>
        </div>

        <Reveal delay={0.15}>
          <div className="hero-card">
            <div className="hc-title">一次完整的学习旅程</div>
            <div className="flow">
              {FLOW.map((s, i) => (
                <div key={i}>
                  <div className="flow-step">
                    <span className="flow-dot">{s.icon}</span>
                    {s.label}
                  </div>
                  {i < FLOW.length - 1 && <div className="flow-arrow">↓</div>}
                </div>
              ))}
            </div>
          </div>
        </Reveal>
      </section>

      <div className="section-head">
        <h2>精选课程</h2>
        <span className="sub">挑一门，开始你的探索</span>
      </div>

      <Stagger className="grid" mount>
        {courses.map((c) => (
          <StaggerItem key={c.id}>
            <Tilt className="card course-card" max={5}>
              <Link to={`/course/${c.id}`} style={{ color: 'inherit', display: 'block' }}>
                <div className="course-thumb" />
                <h3>{c.title}</h3>
                <p>{c.description}</p>
                <div className="cc-foot">
                  <span className="meta">{c.chapters.length} 章 · {c.chapters.reduce((n, ch) => n + ch.units.length, 0)} 单元</span>
                  <span className="cc-arrow">→</span>
                </div>
              </Link>
            </Tilt>
          </StaggerItem>
        ))}
      </Stagger>
    </div>
  )
}
