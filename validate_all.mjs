import { parseDirectives } from './sales-platform/src/lib/mdParser.js'
import fs from 'node:fs'
import path from 'node:path'

function checkFile(file) {
  const md = fs.readFileSync(file, 'utf8')
  const blocks = parseDirectives(md)
  const issues = []
  let qchainCount = 0, qCount = 0
  for (const b of blocks) {
    if (b.type !== 'directive') continue
    const a = b.attrs || {}
    if (b.kind === 'cards' && a.items != null && !Array.isArray(a.items))
      issues.push(`cards.items not array (${typeof a.items})`)
    if (b.kind === 'steps' && a.steps != null && !Array.isArray(a.steps))
      issues.push(`steps.steps not array (${typeof a.steps})`)
    if (b.kind === 'compare') {
      if (a.rows != null && !Array.isArray(a.rows)) issues.push(`compare.rows not array`)
      if (a.left != null && typeof a.left !== 'object') issues.push(`compare.left not object`)
      if (a.right != null && typeof a.right !== 'object') issues.push(`compare.right not object`)
    }
    if (b.kind === 'qchain') {
      qchainCount++
      const child = b.body ? parseDirectives(b.body) : []
      const qs = child.filter(x => x.kind === 'question' || x.kind === 'q')
      if (qs.length === 0) issues.push(`qchain has 0 questions`)
      qs.forEach((q, i) => {
        const inner = q.body ? parseDirectives(q.body) : []
        const hasViz = inner.some(x => ['compare','cards','steps','kpi','funnel','flow','formula','qchain'].includes(x.kind))
        if (!q.attrs.title) issues.push(`qchain Q${i+1} missing title`)
        if (!hasViz && inner.length === 0) issues.push(`qchain Q${i+1} empty body`)
      })
    }
    if (b.kind === 'question' || b.kind === 'q') qCount++
  }
  return { issues, qchainCount, qCount, blockCount: blocks.length }
}

const dirs = [
  './sales-platform/public/data/courses',
  './learning-platform/public/data/courses',
]
let totalIssues = 0, totalQchain = 0
for (const dir of dirs) {
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'))
  for (const f of files) {
    const r = checkFile(path.join(dir, f))
    totalQchain += r.qchainCount
    if (r.issues.length) {
      totalIssues += r.issues.length
      console.log(`ISSUE ${dir}/${f}:`, r.issues.join('; '))
    }
  }
  console.log(`${dir}: ${files.length} files scanned`)
}
console.log(`\nTotal qchain blocks: ${totalQchain}`)
console.log(totalIssues === 0 ? 'PASS: no parsing regressions' : `FAIL: ${totalIssues} issues`)
