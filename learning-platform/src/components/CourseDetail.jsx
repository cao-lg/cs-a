import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getCourse, getAllExamResults } from '../lib/api'
import { getStoredAssessment } from '../lib/storage'
import { Reveal, Stagger, StaggerItem } from './motion'
import GrowthJourney from './GrowthJourney'

export default function CourseDetail() {
  const { courseId } = useParams()
  const [course, setCourse] = useState(null)
  const [status, setStatus] = useState({})
  const [exams, setExams] = useState({})

  useEffect(() => {
    ;(async () => {
      const c = await getCourse(courseId)
      setCourse(c)
      const s = {}
      for (const ch of c.chapters) {
        for (const u of ch.units) {
          s[u.id] = await getStoredAssessment(u.id)
        }
      }
      setStatus(s)
      setExams(await getAllExamResults())
    })()
  }, [courseId])

  if (!course) return <div className="state">加载中…</div>

  return (
    <div className="course-detail">
      <Reveal>
        <Link to="/" className="back">← 返回课程</Link>
        <h1>{course.title}</h1>
        <p className="desc">{course.description}</p>
      </Reveal>

      <GrowthJourney course={course} status={status} courseId={courseId} />

      {course.chapters.map((ch) => {
        const chapterDone = ch.units.every((u) => status[u.id]?.pre && status[u.id]?.post)
        const examRec = exams[ch.id] || {}
        return (
          <section key={ch.id} className="chapter">
            <h2>{ch.title}</h2>
            <Stagger className="units">
              {ch.units.map((u) => {
                const rec = status[u.id] || {}
                const done = rec.pre && rec.post
                return (
                  <StaggerItem key={u.id}>
                    <Link to={`/learn/${courseId}/${u.id}`} className="card unit-card">
                      <div className="unit-head">
                        <span>{u.title}</span>
                        {done && <span className="badge done">✓ 已完成</span>}
                      </div>
                      <div className="meta">
                        {u.duration} · {u.objectives.length} 目标
                      </div>
                    </Link>
                  </StaggerItem>
                )
              })}
              <StaggerItem>
                <Link
                  to={`/exam/${courseId}/${ch.id}`}
                  className={`card exam-card ${examRec.passed ? 'done' : ''}`}
                >
                  <div className="unit-head">
                    <span>🏁 阶段考试</span>
                    {examRec.passed ? (
                      <span className="badge done">✓ 已通关 {examRec.bestScore}%</span>
                    ) : chapterDone ? (
                      <span className="badge">可参加</span>
                    ) : (
                      <span className="badge locked">🔒 待解锁</span>
                    )}
                  </div>
                  <div className="meta">
                    {examRec.passed
                      ? '点开可换卷重考刷分'
                      : chapterDone
                      ? '本章单元已学完，来检验掌握度'
                      : '完成本章全部单元前/后测后解锁'}
                  </div>
                </Link>
              </StaggerItem>
            </Stagger>
          </section>
        )
      })}
    </div>
  )
}
