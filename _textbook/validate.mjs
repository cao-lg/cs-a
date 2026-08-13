// 用平台真实的 mdParser 校验所有生成的单元 md 能否正确解析
import { parseDirectives } from '/d/workbuddy/chain_supply/learning-platform/src/lib/mdParser.js'
import { readFileSync, readdirSync } from 'fs'

const dir = '/d/workbuddy/chain_supply/learning-platform/public/data/courses'
const files = readdirSync(dir).filter(f => f.startsWith('sc-') && f.endsWith('.md'))
let problems = 0
for (const f of files) {
  const md = readFileSync(`${dir}/${f}`, 'utf8')
  try {
    const blocks = parseDirectives(md)
    const kinds = {}
    for (const b of blocks) {
      if (b.type === 'directive') kinds[b.kind] = (kinds[b.kind] || 0) + 1
      else {
        // 检测未被解析的裸 ::: 指令残留
        if (/:::(scene|checkpoint|explore|challenge)/.test(b.content)) kinds['RAW_' + (b.content.match(/:::(\w+)/)||[])[1]] = (kinds['RAW_'+(b.content.match(/:::(\w+)/)||[])[1]]||0)+1
      }
    }
    console.log(`OK  ${f}  blocks=${blocks.length}  directives=${JSON.stringify(kinds)}`)
  } catch (e) {
    problems++
    console.log(`ERR ${f}: ${e.message}`)
  }
}
console.log(problems ? `\n${problems} FILES FAILED` : '\nALL MD PARSED OK')
