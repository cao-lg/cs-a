// 模拟后端 API：前端直接读 public/data 静态内容 + IndexedDB 持久化，
// 等价实现《需求补充规格 v0.2》中的 /api/assessment、/api/assessment/status 等端点。
import { getStoredAssessment, saveAssessment, getOrCreateUser } from './storage'
import { judgeItem } from './judge'

const DATA = import.meta.env.BASE_URL + 'data'

export async function listCourses() {
  const r = await fetch(`${DATA}/courses/manifest.json`)
  const j = await r.json()
  return j.courses
}

export async function getCourse(id) {
  const r = await fetch(`${DATA}/courses/${id}.json`)
  return r.json()
}

export async function getUnitContent(path) {
  const r = await fetch(`${DATA}/courses/${path}`)
  return r.text()
}

export async function getAssessment(unitId) {
  const r = await fetch(`${DATA}/assessments/${unitId}.json`)
  if (!r.ok) return { unitId, pre: { items: [] }, post: { items: [] } }
  return r.json()
}

// POST /api/assessment —— 提交 pre/post
export async function submitAssessment(unitId, phase, answers) {
  const user = await getOrCreateUser()
  const data = await getAssessment(unitId)
  const items = data[phase]?.items || []
  let score = 0
  const graded = items.map((it) => {
    const correct = judgeItem(it, answers[it.id])
    if (correct) score++
    return { id: it.id, correct }
  })
  const record = {
    unitId,
    phase,
    userId: user.id,
    score,
    total: items.length,
    answers,
    graded,
    completed_at: Date.now()
  }
  await saveAssessment(unitId, phase, record)
  return record
}

// GET /api/assessment/status —— { hasPre, hasPost, preScore, postScore, gain, preMastered }
export async function getAssessmentStatus(unitId) {
  const rec = await getStoredAssessment(unitId)
  const pre = rec.pre
  const post = rec.post
  let gain = null
  // 前测满分：说明本单元对学员已是已知内容，增益含义为"已掌握"而非"持平"
  const preMastered = !!(pre && pre.total > 0 && pre.score === pre.total)
  if (pre && post && post.total > 0) {
    const prePct = pre.total ? pre.score / pre.total : 0
    const postPct = post.total ? post.score / post.total : 0
    gain = Math.round((postPct - prePct) * 100)
  }
  return {
    hasPre: !!pre,
    hasPost: !!post,
    preScore: pre?.score,
    preTotal: pre?.total,
    postScore: post?.score,
    postTotal: post?.total,
    gain,
    preMastered
  }
}
