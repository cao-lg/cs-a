import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import { getCourse, getUnitContent, getAssessment, getAssessmentStatus, submitAssessment } from '../lib/api'
import { parseDirectives } from '../lib/mdParser'
import { updateProgress, getStoredAssessment, saveTime } from '../lib/storage'
import Checkpoint from './Checkpoint'
import Explore from './Explore'
import Challenge from './Challenge'
import AssessmentModal from './AssessmentModal'
import Scene from './Scene'
import { Reveal, Magnetic, motion, AnimatePresence } from './motion'

// 兼容两种测验数据结构：{ items: [...] }（u41）或直接 [... ]（u42~u45）
function extractItems(block) {
  if (!block) return []
  if (Array.isArray(block)) return block
  if (Array.isArray(block.items)) return block.items
  return []
}

export default function LearnUnit() {
  const { courseId, unitId } = useParams()
  const navigate = useNavigate()
  const [course, setCourse] = useState(null)
  const [unit, setUnit] = useState(null)
  const [blocks, setBlocks] = useState([])
  const [assessment, setAssessment] = useState({ pre: [], post: [] })
  const [status, setStatus] = useState({ hasPre: false, hasPost: false })
  const [ready, setReady] = useState(false)
  const [showPre, setShowPre] = useState(false)
  const [showPost, setShowPost] = useState(false)
  const [summary, setSummary] = useState(null)

  useEffect(() => {
    ;(async () => {
      const c = await getCourse(courseId)
      const u = c.chapters.flatMap((ch) => ch.units).find((x) => x.id === unitId)
      const md = await getUnitContent(u.path)
      const a = await getAssessment(unitId)
      const st = await getAssessmentStatus(unitId)
      setCourse(c)
      setUnit(u)
      setBlocks(parseDirectives(md))
      setAssessment(a)
      setStatus(st)
      if (!st.hasPre) setShowPre(true)
      setReady(true)
    })()
  }, [courseId, unitId])

  // 学习时长计时：挂载期间每 10s 累加该单元时长，隐藏标签页暂停，卸载时 flush
  useEffect(() => {
    if (!ready || !unitId) return
    let last = Date.now()
    const flush = () => {
      const now = Date.now()
      const dt = now - last
      last = now
      if (dt > 0 && document.visibilityState === 'visible') saveTime(unitId, dt)
    }
    const tick = setInterval(flush, 10000)
    const onVis = () => {
      if (document.visibilityState === 'hidden') flush()
    }
    document.addEventListener('visibilitychange', onVis)
    return () => {
      clearInterval(tick)
      document.removeEventListener('visibilitychange', onVis)
      flush()
    }
  }, [ready, unitId])

  async function refresh() {
    setStatus(await getAssessmentStatus(unitId))
  }

  async function doSubmit(phase, answers) {
    return await submitAssessment(unitId, phase, answers)
  }

  function closePre() {
    setShowPre(false)
    refresh()
  }

  async function closePost() {
    setShowPost(false)
    const st = await getAssessmentStatus(unitId)
    setStatus(st)
    const gain = st.gain ?? 0
    await updateProgress((p) => ({
      ...p,
      xp: p.xp + 20 + Math.max(0, gain),
      streak: p.streak + 1,
      badges: p.badges.includes('unit-done') ? p.badges : [...p.badges, 'unit-done']
    }))
    setSummary({
      gain,
      preMastered: st.preMastered,
      pre: st.preScore,
      post: st.postScore,
      preTotal: st.preTotal,
      postTotal: st.postTotal
    })
  }

  if (!ready || !unit) return <div className="state">加载中…</div>

  // 学习旅程进度轨：前测 → 学习中 → 探索挑战 → 后测
  const railSegs = [
    { done: status.hasPre, label: '前测' },
    { done: true, label: '学习' },
    { done: blocks.some((b) => b.kind === 'explore' || b.kind === 'challenge'), label: '探索' },
    { done: status.hasPost, label: '后测' },
  ]

  return (
    <div className="learn">
      <div className="learn-head">
        <Link to={`/course/${courseId}`} className="back">← {course?.title}</Link>
        <h1>{unit.title}</h1>
        <div className="meta">{unit.duration}</div>
        <ul className="objectives">
          {unit.objectives.map((o, i) => (
            <li key={i}>{o}</li>
          ))}
        </ul>
        <div className="phase-info">
          <span className="phase-pill">课前测 <b>{status.hasPre ? `${status.preScore}/${status.preTotal}` : '未做'}</b></span>
          <span className="phase-pill">课后测 <b>{status.hasPost ? `${status.postScore}/${status.postTotal}` : '未做'}</b></span>
        </div>
        <div className="progress-rail" aria-label="学习进度">
          {railSegs.map((s, i) => (
            <div key={i} className={`seg ${s.done ? 'done' : ''}`} title={s.label} />
          ))}
        </div>
      </div>

      <div className="learn-body">
        {blocks.map((b, idx) => {
          if (b.type === 'md') {
            return (
              <Reveal key={idx} delay={0.02}>
                <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
                  {b.content}
                </ReactMarkdown>
              </Reveal>
            )
          }
          if (b.kind === 'checkpoint') return <Reveal key={idx}><Checkpoint unitId={unitId} {...b.attrs} /></Reveal>
          if (b.kind === 'explore') return <Reveal key={idx}><Explore {...b.attrs} /></Reveal>
          if (b.kind === 'challenge') return <Reveal key={idx}><Challenge key={idx} unitId={unitId} {...b.attrs} /></Reveal>
          if (b.kind === 'scene') return <Scene key={idx} {...b.attrs} />
          return null
        })}
      </div>

      <div className="learn-foot">
        {!status.hasPre && (
          <button className="btn" onClick={() => setShowPre(true)}>
            重做课前测
          </button>
        )}
        {!status.hasPost ? (
          <Magnetic>
            <button className="btn primary" onClick={() => setShowPost(true)}>
              完成后测 →
            </button>
          </Magnetic>
        ) : (
          <Magnetic>
            <button className="btn primary" onClick={() => setShowPost(true)}>
              重做后测
            </button>
          </Magnetic>
        )}
        {status.hasPost && (
          <button className="btn" onClick={() => navigate('/profile')}>
            查看我的进步
          </button>
        )}
      </div>

      {showPre && (
        <AssessmentModal
          title="课前测（低利害 · 可跳过）"
          items={extractItems(assessment.pre)}
          allowSkip={true}
          onClose={closePre}
          onSubmit={(a) => doSubmit('pre', a)}
        />
      )}
      {showPost && (
        <AssessmentModal
          title="课后测（测掌握度）"
          items={extractItems(assessment.post)}
          allowSkip={false}
          onClose={closePost}
          onSubmit={(a) => doSubmit('post', a)}
        />
      )}

      <AnimatePresence>
        {summary && (
          <motion.div
            className="modal-backdrop"
            onClick={() => setSummary(null)}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <motion.div
              className="modal gain-modal"
              onClick={(e) => e.stopPropagation()}
              initial={{ opacity: 0, scale: 0.92, y: 16 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            >
            <h2>本单元学习增益</h2>
            {summary.preMastered ? (
              <>
                <div className="gain-num mastered">✓ 已掌握</div>
                <p>
                  课前 {summary.pre}/{summary.preTotal} → 课后 {summary.post}/{summary.postTotal}
                </p>
                <p className="hint">
                  课前测已是满分，说明本单元对你大都是已知内容。想挑战更高阶，可以去试试单元里的「挑战」任务。
                </p>
              </>
            ) : (
              <>
                <div className={`gain-num ${summary.gain > 0 ? 'up' : summary.gain < 0 ? 'down' : 'flat'}`}>
                  {summary.gain >= 0 ? '+' : ''}
                  {summary.gain}
                  <span>%</span>
                </div>
                <p>
                  课前 {summary.pre}/{summary.preTotal} → 课后 {summary.post}/{summary.postTotal}
                </p>
                <p className="hint">
                  {summary.gain > 0
                    ? '有效学习！继续保持。'
                    : summary.gain === 0
                    ? '持平，可复习薄弱点。'
                    : '提示退步，建议重学本单元。'}
                </p>
              </>
            )}
            <button className="btn primary" onClick={() => setSummary(null)}>
              好的
            </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
