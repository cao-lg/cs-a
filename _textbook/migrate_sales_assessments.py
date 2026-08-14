# -*- coding: utf-8 -*-
# 把项目四题库（u42~u45 的 testConfig 格式）迁移为供应链框架兼容格式：
#   {pre:{items:[{id,type,question,options,answer,points}]}, post:{items:[...]}}
# - 去掉选项字母前缀 "A. "
# - expected 字母 -> 对应选项完整文本作为 answer
# - u41 已是标准格式，原样保留
import json, re, glob, os

DIR = r'D:\workbuddy\chain_supply\sales-platform\public\data\assessments'
LETTER = re.compile(r'^[A-Da-d][.、)]\s*')

def strip_letter(o):
    return LETTER.sub('', o).strip()

def conv_block(block):
    # 已是标准格式 {items:[...]}
    if isinstance(block, dict) and 'items' in block:
        items = block['items']
        out = []
        for it in items:
            # 清洗可能残留的字母前缀
            if it.get('type') == 'multiple_choice' and it.get('options'):
                new_opts = [strip_letter(o) for o in it['options']]
                ans = it.get('answer', '')
                if ans and ans not in new_opts and LETTER.match(ans):
                    idx = 'ABCD'.index(ans[0].upper())
                    if idx < len(new_opts):
                        ans = new_opts[idx]
                out.append({**it, 'options': new_opts, 'answer': strip_letter(ans) if isinstance(ans, str) else ans})
            else:
                out.append(it)
        return {'items': out}
    # testConfig 列表格式
    out = []
    for it in block:
        tc = it.get('testConfig', {})
        q = it.get('title', '') or it.get('instruction', '')
        if 'options' in tc:
            raw = tc['options']
            opts = [strip_letter(o) for o in raw]
            exp = tc.get('expected', '')
            if isinstance(exp, str) and len(exp) == 1 and exp.upper() in 'ABCD' and exp.upper() < 'E':
                ans = opts['ABCD'.index(exp.upper())] if 'ABCD'.index(exp.upper()) < len(opts) else ''
            elif exp in raw:
                ans = strip_letter(exp)
            else:
                ans = exp
            out.append({'id': it['id'], 'type': 'multiple_choice', 'question': q,
                        'options': opts, 'answer': ans, 'points': 10})
        else:
            out.append({'id': it['id'], 'type': 'fill', 'question': q,
                        'answer': tc.get('expected', ''), 'points': 10})
    return {'items': out}

def validate(d):
    for sec in ('pre', 'post'):
        for it in d[sec]['items']:
            if it['type'] == 'multiple_choice':
                assert it['answer'] in it['options'], f"{it['id']} answer 不在 options: {it['answer']}"

for f in sorted(glob.glob(os.path.join(DIR, 'u*.json'))):
    d = json.load(open(f, encoding='utf-8'))
    if isinstance(d.get('pre'), list) or (isinstance(d.get('pre'), dict) and 'items' not in d.get('pre', {})):
        # 需要转换
        new = {'unitId': d['unitId'], 'pre': conv_block(d['pre']), 'post': conv_block(d['post'])}
        validate(new)
        json.dump(new, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        np = len(new['pre']['items']); nq = len(new['post']['items'])
        print(f"{os.path.basename(f)}: 已转换 pre={np} post={nq}")
    else:
        # u41 标准格式，仅校验
        validate(d)
        print(f"{os.path.basename(f)}: 已是标准格式，校验通过")
print('MIGRATION DONE')
