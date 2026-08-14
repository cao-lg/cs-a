# -*- coding: utf-8 -*-
"""ss-a 全量质量审计：扫描 courses/*.md、assessments/*.json、exams/*.json。"""
import json, re, os, glob

ROOT = r"D:\workbuddy\chain_supply\sales-platform"
COURSES = os.path.join(ROOT, "public", "data", "courses")
ASSESS  = os.path.join(ROOT, "public", "data", "assessments")
EXAMS   = os.path.join(ROOT, "public", "data", "exams")

SEV = {"CRIT": "❌ 严重", "WARN": "⚠️ 警告", "INFO": "ℹ️ 提示"}

# 营销/无关残留（真正的教材话术，不含"表X-X"交叉引用——后者是教材合理内容）
JUNK_RE = re.compile(
    r"(【AI助训】|指测闯关|想快速|扫码挑战|快来完成|闯关题|无论你是想|现在就扫码|✅|实训练习|拓展活动|本项目小结|学习评价|课后练习|【指标速记】)"
)
# Explore 应含真实企业/品牌/年份
ENTITY_RE = re.compile(r"(焕新家电|某电商|某平台|淘宝|京东|拼多多|抖音|小红书|快手|天猫|阿里巴巴|京东物流|顺丰|菜鸟|某品牌|某品质电商|20\d{2}年)")
# 定义腔（疑似把定义段当案例）
DEFINE_RE = re.compile(r"是\s*[^。]{0,40}过程|通过\s*[^。]{0,40}数据")

PLAIN_WARN = 350   # 普通段落长度警告阈值
PLAIN_CRIT = 600   # 严重阈值

issues = []   # (file, kind, sev, detail)

def add(file, kind, sev, detail):
    issues.append((file, kind, sev, detail))

def extract_attr(line, key):
    """从 `key="..."` 或 `key=[...]` 提取属性值（处理转义引号）。"""
    m = re.search(re.escape(key) + r'=', line)
    if not m:
        return None
    i = m.end()
    s = line[i:]
    if s.startswith('"'):
        buf = []; j = 1
        while j < len(s):
            ch = s[j]
            if ch == '\\' and j + 1 < len(s):
                buf.append(s[j+1]); j += 2; continue
            if ch == '"':
                break
            buf.append(ch); j += 1
        return ''.join(buf)
    if s.startswith('['):
        depth = 0; buf = []
        for ch in s:
            buf.append(ch)
            if ch == '[': depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    return ''.join(buf)
        return ''.join(buf)
    return s.strip()

# ---------------- courses/*.md ----------------
md_files = sorted(glob.glob(os.path.join(COURSES, "*.md")))
for path in md_files:
    fname = os.path.basename(path)
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")

    # 1) 营销/无关残留
    for j, ln in enumerate(lines, 1):
        if JUNK_RE.search(ln):
            add(fname, "营销残留", "WARN", f"第{j}行含应删除的教材话术：{JUNK_RE.search(ln).group(0)}")

    # 2) thought 双问号/怪 artifacts
    for j, ln in enumerate(lines, 1):
        if ln.strip().startswith("thought=") and ("？？" in ln or "？。" in ln or "。。?" in ln):
            add(fname, "文案artifact", "WARN", f"第{j}行 thought 含异常标点")

    # 3) 解析 directives（scene/checkpoint/explore/challenge）与正文段落
    inside = None          # 当前 directive 类型
    plain_paras = []       # 正文（非 directive 内）普通段落
    plain_count = 0
    cur = []
    in_directive = False

    def flush_para(block_lines):
        global plain_count
        if not block_lines:
            return
        joined = "\n".join(block_lines).strip()
        if not joined:
            return
        first = block_lines[0].strip()
        # 跳过纯 directive 边界
        if first.startswith(":::") or joined == "}":
            return
        if first.startswith("#"):
            return  # 标题块，正常
        if all(l.strip().startswith("- ") for l in block_lines if l.strip()):
            return  # 列表块，正常
        # 跳过 markdown 表格（表格行以 | 开头且含 |）
        if all(l.strip().startswith("|") and "|" in l.strip() for l in block_lines if l.strip()):
            return  # 表格是合法呈现，不算大段文字
        if first.startswith("|") and "|" in first:
            return
        if first.startswith(">"):
            if len(joined) > 500:
                add(fname, "引用过长", "INFO", f"blockquote 长 {len(joined)} 字，可能信息密度过高")
            return
        # 普通段落
        plain_count += 1
        L = len(joined)
        if L > PLAIN_CRIT:
            add(fname, "大段文字", "CRIT", f"普通段落 {L} 字（> {PLAIN_CRIT}），缺乏结构拆解")
        elif L > PLAIN_WARN:
            add(fname, "大段文字", "WARN", f"普通段落 {L} 字（> {PLAIN_WARN}），建议拆分/列表化")

    for ln in lines:
        st = ln.strip()
        if st.startswith(":::") and not st.startswith(":::{"):
            # 关闭上一个 directive
            inside = None
            in_directive = False
            continue
        if st.startswith(":::scene{") or st.startswith(":::checkpoint{") or st.startswith(":::explore{") or st.startswith(":::challenge{"):
            # 关闭上一个正文段落采集
            flush_para(cur); cur = []
            inside = st[3:st.index("{")]
            in_directive = True
            if inside == "explore":
                # 提取 scenario 检查
                scen_line = next((x for x in lines if x.strip().startswith("scenario=")), "")
                scen = extract_attr(scen_line, "scenario") or ""
                if len(scen) < 40:
                    add(fname, "Explore偏短", "WARN", f"explore scenario 仅 {len(scen)} 字，疑似举例/定义句")
                elif not ENTITY_RE.search(scen) or DEFINE_RE.search(scen[:80]):
                    add(fname, "Explore疑似定义段", "WARN", f"explore scenario 不含真实企业/年份或带定义腔：{scen[:50]}…")
            continue
        if st == "}":
            inside = None
            in_directive = False
            continue
        if in_directive:
            # 检查 directive 内 options / answer 一致性（仅 checkpoint/challenge）
            if inside in ("checkpoint", "challenge"):
                if "options=" in ln:
                    raw = extract_attr(ln, "options")
                    try:
                        opts = json.loads(raw) if raw else []
                    except Exception:
                        opts = []
                        add(fname, "坏选项JSON", "CRIT", f"options 解析失败：{raw[:40]}…")
                    for o in opts:
                        if "|" in o:
                            add(fname, "表格碎片选项", "CRIT", f"选项含表格竖线：{o[:40]}…")
                        if o.startswith("#") or o.startswith("- "):
                            add(fname, "标记选项", "WARN", f"选项含 markdown 标记：{o[:40]}…")
                        if len(o) > 95:
                            add(fname, "选项过长", "WARN", f"选项 {len(o)} 字：{o[:40]}…")
                        if len(o) < 6:
                            add(fname, "选项过短", "WARN", f"选项仅 {len(o)} 字：{o!r}")
                if "answer=" in ln:
                    ans = extract_attr(ln, "answer")
                    # 取最近一个 options
                    opts_ctx = None
                    for x in lines:
                        if "options=" in x:
                            r2 = extract_attr(x, "options")
                            try: opts_ctx = json.loads(r2)
                            except Exception: opts_ctx = None
                    if opts_ctx and ans not in opts_ctx:
                        add(fname, "答案不在选项", "CRIT", f"answer 不在 options 内：{ans[:30]}…")
            continue
        # 正文行
        if ln.strip() == "":
            flush_para(cur); cur = []
        else:
            cur.append(ln)
    flush_para(cur)
    if plain_count >= 5:
        add(fname, "正文缺乏结构", "INFO", f"正文含 {plain_count} 个无结构普通段落，建议增加标题/列表")

# ---------------- assessments/*.json + exams/*.json ----------------
def check_item(item, src):
    itype = item.get("type")
    if itype == "multiple_choice":
        opts = item.get("options", [])
        ans = item.get("answer", "")
        # 坏选项
        seen = set()
        for o in opts:
            if "|" in o:
                add(src, "表格碎片选项", "CRIT", f"id={item.get('id')} 选项含竖线：{o[:40]}…")
            if o.startswith("#") or o.startswith("- "):
                add(src, "标记选项", "WARN", f"id={item.get('id')} 选项含 markdown 标记：{o[:40]}…")
        if len(o) > 110:
            add(src, "选项过长", "WARN", f"id={item.get('id')} 选项 {len(o)} 字：{o[:40]}…")
        # 真碎片：极短(<4字)或含明显的填空式残句，而不是指标名/数值
        if len(o) < 4 or re.search(r"但通常|情况下，并不建议|无实际业务意义", o):
            add(src, "选项碎片", "WARN", f"id={item.get('id')} 疑似碎片选项：{o!r}")
            if o in seen:
                add(src, "重复选项", "WARN", f"id={item.get('id')} 选项重复：{o[:30]}…")
            seen.add(o)
        if ans and ans not in opts:
            add(src, "答案不在选项", "CRIT", f"id={item.get('id')} answer 不在 options：{ans[:30]}…")
        if len(opts) < 2:
            add(src, "选项过少", "CRIT", f"id={item.get('id')} 仅 {len(opts)} 个选项")
    elif itype == "fill":
        if not item.get("answer"):
            add(src, "填空无答案", "CRIT", f"id={item.get('id')} 填空无 answer")

for path in sorted(glob.glob(os.path.join(ASSESS, "*.json"))):
    fname = os.path.basename(path)
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        add(fname, "JSON解析失败", "CRIT", str(e)); continue
    for phase in ("pre", "post"):
        for it in data.get(phase, {}).get("items", []):
            check_item(it, fname)

for path in sorted(glob.glob(os.path.join(EXAMS, "*.json"))):
    fname = os.path.basename(path)
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        add(fname, "JSON解析失败", "CRIT", str(e)); continue
    for it in data.get("pool", []):
        check_item(it, fname)

# ---------------- 输出 ----------------
from collections import defaultdict
by_file = defaultdict(list)
for f, k, s, d in issues:
    by_file[f].append((k, s, d))

print(f"扫描文件：md={len(md_files)}，共发现 {len(issues)} 条问题\n")
order = {"CRIT": 0, "WARN": 1, "INFO": 2}
for f in sorted(by_file):
    lst = sorted(by_file[f], key=lambda x: order.get(x[1], 9))
    print(f"【{f}】 {len(lst)} 条")
    for k, s, d in lst:
        print(f"   {SEV[s]} [{k}] {d}")
    print()

# 汇总
summary = defaultdict(int)
for _, k, s, _ in issues:
    summary[(s, k)] += 1
print("=== 汇总（按严重度/类型）===")
for (s, k), n in sorted(summary.items(), key=lambda x: order.get(x[0][0], 9)):
    print(f"  {SEV[s]} [{k}] × {n}")

crit_files = sorted({f for f, k, s, _ in issues if s == "CRIT"})
print(f"\n涉及严重问题的文件数：{len(crit_files)}")
