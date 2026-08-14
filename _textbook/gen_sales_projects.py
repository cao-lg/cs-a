# -*- coding: utf-8 -*-
"""
把 初稿6.18 的 5 个项目（项目一/二/三/五/六）拆解进 sales-platform。
读取 projects_structure.json（extract_docx.py 产出），生成：
  public/data/courses/sales-projectX.json        课程树
  public/data/courses/<unitId>.md                单元正文（场景剧 + 检查点 + 探索 + 挑战）
  public/data/assessments/<unitId>.json          课前/课后诊断
  public/data/exams/chXX.json                    任务阶段考
  public/data/exams/final.json（每项目）          结业大考
沿用 sales-project4 的「小北 / mentor / 焕新家电」故事圣经，主角为小北成长线。
"""
import json, re, os, random

ROOT = r"D:\workbuddy\chain_supply\sales-platform"
COURSES = os.path.join(ROOT, "public", "data", "courses")
ASSESS  = os.path.join(ROOT, "public", "data", "assessments")
EXAMS   = os.path.join(ROOT, "public", "data", "exams")
os.makedirs(COURSES, exist_ok=True)
os.makedirs(ASSESS, exist_ok=True)
os.makedirs(EXAMS, exist_ok=True)

STRUCT = json.load(open(r"D:\workbuddy\chain_supply\_textbook\projects_structure.json", encoding="utf-8"))

COMPANY = "焕新家电"

# 每项目：小北所处阶段 + 一句话设定
PROJECT_STORY = {
    "sales-project1": ("小北刚入职", "小北刚踏进「焕新家电」电商部，mentor 说：先把'数据驱动'这件事想明白。"),
    "sales-project2": ("小北轮岗到选品组", "小北被调到选品组，mentor 丢给她一句话：挑品，决定了一家店一半的命。"),
    "sales-project3": ("小北轮岗到推广组", "小北来到推广投放组，mentor 问：钱花出去了，到底值不值，你拿什么证明？"),
    "sales-project5": ("小北轮岗到用户体验组", "小北转岗到客户服务与体验组，mentor 说：投诉不是麻烦，是生意在'漏水'的地方。"),
    "sales-project6": ("小北轮岗到物流组", "小北被安排到物流履约组，mentor 撂下一句：货跑得又快又省，才是真本事。"),
}

# 每任务：专属焦点问题（决定 scene 的 focusQ）
FOCUSQ = {
    "1.1": "数据到底是怎么'驱动'一家电商公司赚到钱的？",
    "1.2": "拿到一堆杂乱的业务数据，第一步该按什么流程把它变成决策？",
    "2.1": "怎么判断一个品类市场够大、竞争还没杀红眼？",
    "2.2": "面对海量商品数据，怎么快速初筛出真正值得做的品？",
    "2.3": "怎么用热度、结构这些指标判断一个商品到底有没有潜力？",
    "2.4": "怎么用波士顿矩阵把商品分成'明星 / 现金牛 / 问题 / 瘦狗'？",
    "2.5": "怎么用 RPA 把竞品和市场的公开数据自动抓回来？",
    "3.1": "推广投了钱，怎么用指标体系判断到底值不值？",
    "3.2": "抖音、小红书、直通车各说各话，怎么把多渠道数据打通对齐？",
    "3.3": "怎么用趋势 / 漏斗 / 归因看出推广到底哪一环掉了链子？",
    "3.4": "怎么把推广效果做成老板一眼就懂的图？",
    "5.1": "客户服务数据能告诉我们生意哪里在'漏水'？",
    "5.2": "客户数据里的异常（刷单、乱填）怎么清洗掉？",
    "5.3": "怎么从投诉和满意度里挖出最该先改的问题？",
    "5.4": "怎么用分析结果反过来优化客服策略？",
    "5.5": "怎么用飞书多维表格 + AI 把客户关系管起来？",
    "6.1": "物流好不好，到底该盯哪几个核心指标？",
    "6.2": "海量物流数据太杂，怎么'瘦身'又不丢关键信息？",
    "6.3": "怎么分析物流的时效、成本和质量，哪里还能更省？",
    "6.4": "怎么用 Power BI 把物流数据变成会说话的看板？",
}

DOMAIN = ["数据","分析","指标","客户","销售","商品","选品","营销","推广","物流","库存",
          "服务","转化","漏斗","归因","趋势","清洗","预测","电商","平台","用户","订单",
          "复购","客单","毛利","转化率","满意度","履约","RFM","波士顿","热度","结构",
          "市场","竞争","采集","可视化","决策","效率","成本","质量"]

def esc_attr(s):
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    s = s.replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()
    return s[:300]

def clean_title(t):
    t = re.sub(r'^\s*任务\s*\d+\.\d+\s*', '', t)
    t = re.sub(r'^\s*[一二三四五六七八九十]+、', '', t)
    t = re.sub(r'^\s*（?[一二三四五六七八九十]+）?\s*', '', t)
    t = re.sub(r'^\s*\d+[\.\、]\s*', '', t)
    return t.strip()

def short_title(t, n=18):
    """精简标题：截到第一个句号/逗号/分号前，最长 n 字，用于 focus/question，避免堆整段定义。"""
    t = clean_title(t)
    for sep in ("。", "；", "：", "，", ";"):
        i = t.find(sep)
        if 0 < i < n:
            return t[:i]
    return t[:n]

# ---------- 句子 / 关键句 ----------
def split_sentences(text):
    return [x.strip() for x in re.split(r"[。！？\n;；]", text) if x.strip()]

MARKER = re.compile(r"^(思考|任务|实训|自测|练习|拓展|活动|案例|标杆|AI|【)")
INLINE_HEADING = re.compile(r"^\s*\d+\.\d+\s+\S")
CAPTION_RE = re.compile(r"^(图|表)\s*\d")
HEADING_RE = re.compile(r"^\s*\d+[．\.、]\s*")

def is_junk(s):
    if len(s) < 18 or len(s) > 120: return True
    if CAPTION_RE.match(s) or HEADING_RE.match(s): return True
    if "待编辑" in s or "待美化" in s: return True
    if re.match(r"^\s*[（(]\d+[)）]\s*", s): return True
    # 形如 "1. 能够..." 的目标列表句也跳过（会进 objectives）
    return False

# ---------- 教材原文结构化约束 ----------
# 这些段落与学习无关，直接丢弃
JUNK_PARA_RE = re.compile(
    r"^(【AI助训】|指测闯关|想快速|扫码挑战|快来完成|闯关题|无论你是想|现在就扫码|✅|实训练习|拓展活动|本项目小结|学习评价|课后练习|【指标速记】|表\d+[\-—]\d+)",
    re.I,
)
# 层级标题："（一）服务规模层（广度）：解决..." / "（1）精准评估..."
SECTION_HEAD_RE = re.compile(r"^\s*（[一二三四五六七八九十]+）\s*(.+)$")
SECTION_HEAD_NUM_RE = re.compile(r"^\s*（(\d+)）\s*(.+)$")
# 编号列表项："1.咨询量：..." / "1．首次响应..." / "1、xxx"
LIST_ITEM_RE = re.compile(r"^\s*(\d+)[\.．、]\s*(.+)$")

def is_junk_para(p):
    """判断是否应丢弃的教材营销/无关段落。"""
    if not p or not p.strip():
        return True
    if JUNK_PARA_RE.match(p):
        return True
    # 纯引用废句（"下面以表5-3中数据为例进行数据分析""参见表6-2"），短且无知识点
    if re.search(r"表\d+[\-—]\d+", p) and len(p.strip()) < 45:
        return True
    # 只有emoji或特殊符号的也丢弃
    if re.match(r"^[✅✓✔⭐\s]+$", p):
        return True
    return False

def structure_paras(paras):
    """
    把教材里扁平的 paras 数组结构化：
    - 层级标题 → ### 小标题
    - 编号列表项 → - 列表项
    - 营销/无关段落 → 删除
    - 普通段落保留
    返回 markdown 字符串。
    """
    out = []
    i = 0
    while i < len(paras):
        p = paras[i].strip()
        if is_junk_para(p):
            i += 1
            continue

        # 层级标题（中文数字）
        m = SECTION_HEAD_RE.match(p)
        if m:
            title = m.group(1).strip().rstrip("：:").strip()
            # 如果标题后还有正文内容（如"解决..."），保留在同一个小标题内
            body = p[m.end():].strip()
            if body and body != title:
                out.append(f"### {title}：{body}")
            else:
                out.append(f"### {title}")
            i += 1
            continue

        # 层级标题（阿拉伯数字括号）："（1）标题：内容" 拆成标题+段落
        m2 = SECTION_HEAD_NUM_RE.match(p)
        if m2:
            body = m2.group(2).strip()
            # 按第一个全角/半角冒号拆分标题与正文
            parts = re.split(r"[：:]", body, 1)
            if len(parts) == 2 and parts[1].strip() and len(parts[0]) <= 25:
                title = parts[0].strip()
                content = parts[1].strip()
                out.append(f"### {title}")
                out.append(content)
            else:
                out.append(f"### {body.rstrip('：:').strip()}")
            i += 1
            continue

        # 编号列表项：连续出现则聚成紧凑 markdown 列表（items 之间无空行）
        if LIST_ITEM_RE.match(p):
            items = []
            while i < len(paras) and LIST_ITEM_RE.match(paras[i].strip()):
                item_text = LIST_ITEM_RE.match(paras[i].strip()).group(2).strip()
                items.append(f"- {item_text}")
                i += 1
            out.append("\n".join(items))
            out.append("")
            continue

        # 启发式：很短的段首句（无句号）大概率是子标题
        if len(p) <= 26 and "。" not in p and i + 1 < len(paras) and len(paras[i + 1].strip()) > 50:
            out.append(f"### {p}")
            i += 1
            continue

        # 普通段落：切掉句尾的表格引用引导语 / 列表引导尾巴（"……如表2-2：" / "……核心指标包括："），保留前半句知识点
        cleaned = re.sub(r"[\s，,。.：:；;]*表\d+[\-—]\d+[\s，,。.：:；;]*$", "", p)
        cleaned = re.sub(r"[\s，,。.]*?(核心指标包括|核心功能包括|实现以下目标|主要包括|具体包括|具体表现为|主要体现在|体现在|包括|包括：)[:：]?$", "", cleaned)
        out.append(cleaned)
        i += 1

    return "\n\n".join(out)

def key_sentences(blocks):
    out, seen = [], set()
    for b in blocks:
        sources = []
        if "md" in b:
            sources.append(b["md"])
        elif "sub" in b:
            sources.extend(b["sub"].get("paras", []))
            for src in sources:
                for sent in split_sentences(src):
                    if is_junk(sent): continue
                    s = sent.strip()
                    # 表格片段、层级标题、编号项、列表项、表格引用句、营销话 不能当关键句/选项
                    if "|" in s or "#" in s or "如表" in s or ("汇总" in s and "指标" in s): continue
                    if SECTION_HEAD_RE.match(s) or SECTION_HEAD_NUM_RE.match(s): continue
                    if LIST_ITEM_RE.match(s): continue
                    if s.startswith("-"): continue
                    if re.match(r"^[（(]\d+[)）]", s): continue
                    # 表格编号引用残句（"如需要根据表5-2..."）不要
                    if re.search(r"表\d+[\-—]\d+", s): continue
                    # 填空残句（"但通常情况下，并不建议删除"）不要
                    if re.match(r"^但(通常)?(情况下)?[，,]", s) or "情况下，并不建议" in s: continue
                    # 思政/职业理念腔（"作为…从业者""数智赋能""乡村振兴"等）不是知识点，排除
                    if re.search(r"作为.{0,8}从业者|数智赋能|匠心守护|乡村振兴|职业理念|社会责任|民生|课程思政", s): continue
                    # 操作手册字段说明段（"本项目提供名为…xlsx""工作表""核心字段如下"）排除
                    if re.search(r"本项目提供名为|Excel文件|工作表|核心字段如下|字段如下", s): continue
                    if is_junk_para(s): continue
                    if not any(k in s for k in DOMAIN): continue
                    if s not in seen:
                        seen.add(s); out.append(s)
    return out

# ---------- 表格 ----------
def table_to_md(tbl):
    if not tbl: return ""
    ncol = len(tbl[0])
    if ncol > 10: return ""
    avg = sum(len("".join(r)) for r in tbl) / max(1, sum(len(r) for r in tbl))
    if avg <= 1.2: return ""
    lines = ["| " + " | ".join(tbl[0]) + " |", "| " + " | ".join(["---"]*ncol) + " |"]
    for row in tbl[1:]:
        row = (list(row) + [""]*ncol)[:ncol]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)

# ---------- 评测题 ----------
def trunc(s, n=34):
    s = s.strip()
    return s if len(s) <= n else s[:n] + "…"

def clean_option(o):
    """选项必须干净：不能是表格片段、markdown 标题、填空式残句、过长过短。"""
    o = o.strip()
    if not o or "|" in o: return None
    # 把换行/多个空格统一处理
    o = o.replace("\n", " ")
    o = re.sub(r"\s+", " ", o)
    # 去掉 markdown 列表前缀
    o = re.sub(r"^[-•*]\s+", "", o)
    # 去掉首尾多余标点和编号
    o = re.sub(r"^[（(]?\d+[)）]?[\.．、]?\s*", "", o)
    o = o.strip()
    # 过滤掉 markdown 标题开头的垃圾（如 "### 无价值数据 指..."）
    if o.startswith("#"):
        return None
    # 过滤掉 "但通常情况下，并不建议删除" 这类填空残句
    if re.match(r"^但(通常)?(情况下)?[，,]", o) or "情况下，并不建议" in o:
        return None
    # 过滤掉表格编号引用残句（"如需要根据表5-2..."）
    if re.search(r"表\d+[\-—]\d+", o):
        return None
    # 去掉不完整的尾部引号/标点
    if o.startswith(("“", "\"", "「", "《")) and not o.endswith(("”", "\"", "」", "》")):
        pass
    else:
        o = o.rstrip("，,；;。. ")
    # 小标题形式的选项太浅，不要
    if o.startswith("（") and "）" in o and len(o) < 35:
        return None
    if len(o) < 10 or len(o) > 75:
        return None
    return o

def build_mcq(correct, others, seed, topic=None):
    rnd = random.Random(seed)
    # 先过滤 others，挑一个干净的作正确答案候选池
    clean_others = [clean_option(o) for o in others]
    clean_others = [o for o in clean_others if o and 10 <= len(o) <= 75]
    # 优先选 20-60 字的关键句作正确答案，避免被截断成 "…"
    cand_correct = correct if isinstance(correct, str) else (correct[0] if correct else "")
    if isinstance(correct, (list, tuple)):
        sized = [c for c in correct if 20 <= len(c) <= 60]
        cand_correct = sized[0] if sized else correct[0]
    elif not (20 <= len(cand_correct) <= 60):
        sized = [o for o in clean_others if 20 <= len(o) <= 60]
        if sized:
            cand_correct = sized[0]
    correct_t = clean_option(cand_correct)
    # 如果正确答案也脏（含 #/换行/碎片），从干净候选池里换一个，绝不用 trunc 兜底污染
    if not correct_t and clean_others:
        correct_t = rnd.choice(clean_others)
    if not correct_t:
        # 实在没有干净句，返回一个安全的占位（不应发生）
        return {"type":"multiple_choice","question":(f"关于「{topic}」，下列说法正确的是？" if topic else "学习本单元后，下列说法正确的是？"),
                "options":["选项数据暂缺，请稍后重试","该选项把相关关系误当成了因果关系","这是把范围说大了，并非本单元讨论的重点","这一说法与数据驱动的思路正好相反"],
                "answer":"选项数据暂缺，请稍后重试","points":10}
    keys = set(k for k in DOMAIN if k in correct_t)
    pool = []
    seen_opts = {correct_t}
    for o in others:
        if o == correct: continue
        ot = clean_option(o)
        if not ot or ot in seen_opts: continue
        # 与正确答案太像（重合度高）的不要
        shared = len(set(k for k in DOMAIN if k in o) & keys)
        if shared >= max(1, len(keys)) and len(ot) > 30:
            continue
        pool.append((shared, ot))
        seen_opts.add(ot)
    pool.sort(key=lambda x: (-x[0], rnd.random()))
    distractors = [p[1] for p in pool[:3]]
    generic = [
        "这更像传统做法，不是本单元强调的方向",
        "该选项把相关关系误当成了因果关系",
        "这是把范围说大了，并非本单元讨论的重点",
        "这一说法与数据驱动的思路正好相反",
    ]
    rnd.shuffle(generic)
    while len(distractors) < 3:
        d = generic.pop()
        if d not in distractors and d != correct_t:
            distractors.append(d)
    opts = distractors + [correct_t]
    rnd.shuffle(opts)
    q = f"关于「{topic}」，下列说法正确的是？" if topic else "学习本单元后，下列说法正确的是？"
    return {"type":"multiple_choice","question":q,
            "options":opts,"answer":correct_t,"points":10}

def build_fill(sents, seed):
    rnd = random.Random(seed)
    cand = []
    for s in sents:
        st = s.rstrip()
        if not st.endswith(("。", "！", "？")):
            continue
        # 负向环视：数字不能是 "X-Y单位" 这种区间的一部分，避免 "近1-_____" 之类别扭空
        m = re.search(r"(?<![\d\-])([0-9]+(?:\.[0-9]+)?\s*(?:%|倍|天|元|个|项|类|年|月|万元|亿元|次|小时|分钟|折))", s)
        if not m:
            continue
        num = m.group(1).strip()
        q = s.replace(num, "_____", 1)
        if len(q) < 16 or q.rstrip().endswith("_____") or len(q) > 130:
            continue
        cand.append((q, num))
    if not cand:
        return None
    q, num = rnd.choice(cand)
    return {"type": "fill", "question": q, "answer": num, "points": 10}

def make_assessment(sents, uid):
    if len(sents) < 2:
        sents = sents + sents
    pre_items, post_items = [], []
    n = len(sents)
    pre_idx = list(range(0, min(2, n)))
    post_idx = list(range(min(2, n), min(5, n))) or pre_idx
    for i in pre_idx:
        q = build_mcq(sents[i], sents, seed=hash(uid+"pre"+str(i)) & 0xffff)
        q["id"] = f"{uid}_pre{len(pre_items)+1}"
        pre_items.append(q)
    for i in post_idx:
        q = build_mcq(sents[i], sents, seed=hash(uid+"post"+str(i)) & 0xffff)
        q["id"] = f"{uid}_post{len(post_items)+1}"
        post_items.append(q)
    f = build_fill(sents, seed=hash(uid+"fill") & 0xffff)
    if f:
        f["id"] = f"{uid}_post{len(post_items)+1}"
        post_items.append(f)
    return {"unitId":uid,
            "pre":{"title":"课前测：你现在的直觉","description":"不用背定义，凭直觉选。测测你对这一主题的原有认知。","items":pre_items},
            "post":{"title":"课后测：看看你掌握了什么","description":"学完本单元后，检验关键概念是否真的入脑。","items":post_items}}

# ---------- 故事化辅助（提升细腻度） ----------
THOUGHTS = [
    lambda tq, t: f"小北盯着屏幕，心里犯嘀咕：{tq} 这答案到底藏在哪一行数据里？",
    lambda tq, t: f"小北在草稿纸上写写画画——『{t}』听着不陌生，真要讲清楚还得再想一层。",
    lambda tq, t: f"小北有点紧张：mentor 的题不难，难的是把『{t}』和手里的数据对上号。",
    lambda tq, t: f"小北抿了口咖啡，盘算着汇报时得用最少的数字把『{t}』这件事说圆。",
    lambda tq, t: f"小北皱起眉：数据一大堆，可哪几个才真正答得了『{tq}』？",
]
CP1_SCEN = [
    "小北看着后台数据，mentor 问了她一个本单元的核心问题。",
    "mentor 把刚学的概念抛回给小北：你说，这事儿关键到底在哪？",
    "周末复盘会上，mentor 点名让小北先给个结论。",
]
CP2_SCEN = [
    "学完这一节，mentor 想确认你是不是真懂了。",
    "mentor 换了种问法，看小北能不能换个角度答出来。",
    "小北刚想松口气，mentor 又追了一问。",
]
EXPLORE_SETS = [
    [{"text":"这家公司的做法值得借鉴","feedback":"有眼光。","insight":"真实业务里，方法往往是从案例里长出来的。"},
     {"text":"我更关心它背后的指标怎么算","feedback":"更专业。","insight":"把案例拆成可量化的指标，才算真正学会。"},
     {"text":"先记住结论，细节以后再说","feedback":"也可以，但别只记结论。","insight":"结论会过时，方法才不会。"}],
    [{"text":"这个方法我们部门也能用","feedback":"有落地意识。","insight":"能迁移的方法，才是真学会了。"},
     {"text":"我想先弄清数据从哪来","feedback":"抓住了根。","insight":"没有数据来源，再漂亮的方法也落不了地。"},
     {"text":"先看看里面有什么坑","feedback":"谨慎是对的。","insight":"案例里的风险，往往比做法本身更值钱。"}],
    [{"text":"它的指标口径和我理解的一致吗","feedback":"很较真。","insight":"口径不一致，数字就不可比。"},
     {"text":"换个项目它还成立吗","feedback":"在想能不能泛化。","insight":"能泛化的才是规律，不是巧合。"},
     {"text":"我先按它的方法算一遍","feedback":"动手派。","insight":"亲手算过一遍，比看十遍记得牢。"}],
]
def gen_thought(topic, focusq, seed):
    tq = focusq.rstrip("？！。")
    return random.Random(seed).choice(THOUGHTS)(tq, topic)

# ---------- 单元 md ----------
def blocks_from_section(sec):
    """把 section 的 直接内容 + subs 拍平成渲染块列表：{md} / {sub}。"""
    blocks = []
    if sec.get("paras") or sec.get("tables"):
        parts = []
        if sec.get("paras"):
            structured = structure_paras(sec["paras"])
            if structured.strip():
                parts.append(structured)
        if sec.get("tables"):
            parts.append("\n\n".join(table_to_md(t) for t in sec["tables"]))
        if parts:
            blocks.append({"md": "\n\n".join(parts)})
    for sub in sec.get("subs", []):
        blocks.append({"sub": sub})
    return blocks

def render_sub(sub):
    title = clean_title(sub.get("title","")) or "要点"
    L = [f"## {title}", ""]
    if sub.get("paras"):
        structured = structure_paras(sub["paras"])
        if structured.strip():
            L.append(structured); L.append("")
    for t in sub.get("tables", []):
        md = table_to_md(t)
        if md: L.append(md); L.append("")
    return L

def gen_unit_md(cid, task, sec, uid, is_single, unit_title):
    story_phase, story_line = PROJECT_STORY[cid]
    task_title = clean_title(task["title"])
    blocks = blocks_from_section(sec)
    sents = key_sentences(blocks)
    # 学习目标
    objs = []
    for b in blocks:
        if "sub" in b:
            t = clean_title(b["sub"].get("title",""))
            if t and t not in objs: objs.append(t)
    if not objs:
        objs = [unit_title]
    objs = objs[:6]
    focusq = FOCUSQ.get(task["id"], f"为什么「{task_title}」是这一步绕不开的？")
    short_t = short_title(unit_title)

    L = []
    L.append(f"# {esc_attr(unit_title)}")
    L.append("")
    L.append("## 学习目标")
    L.append("")
    for o in objs:
        L.append(f"- {esc_attr(o)}")
    L.append("")
    # 场景剧
    setup = f"{story_line} 这周的真实任务就是：{task_title}。"
    line = f"别把它当课本。做完这个任务，你要能独立回答一个问题——{focusq}"
    focus = f"{short_t}：从现象到决策"
    thought = gen_thought(unit_title, focusq, hash(uid) & 0xffff)
    L.append(":::scene{")
    L.append(f'  setup="{esc_attr(setup)}"')
    L.append('  speaker="mentor"')
    L.append(f'  line="{esc_attr(line)}"')
    L.append(f'  focus="{esc_attr(focus)}"')
    L.append(f'  focusQ="{esc_attr(focusq)}"')
    L.append(f'  thought="{esc_attr(thought)}"')
    L.append("  revealDelay=0.6")
    L.append("  stagger=0.8")
    L.append("  duration=0.95")
    L.append('  trigger="0px 0px -22% 0px"')
    L.append("}")
    L.append("")

    # 正文 + 检查点
    cp_count = 0
    case_used = False
    for bi, b in enumerate(blocks):
        if "md" in b:
            L.append(b["md"]); L.append("")
        elif "sub" in b:
            L += render_sub(b["sub"])
        # 在第一个/第三个块后注入检查点
        if cp_count == 0 and bi == 0 and sents:
            q = build_mcq(sents[0], sents, seed=hash(uid+"cp1") & 0xffff, topic=short_t)
            L.append(":::checkpoint{")
            L.append('  type="multiple_choice"')
            L.append(f'  scenario="{esc_attr(random.Random(hash(uid+"cp1")&0xffff).choice(CP1_SCEN))}"')
            L.append(f'  question="{esc_attr(q["question"])}"')
            L.append(f'  options={json.dumps(q["options"], ensure_ascii=False)}')
            L.append(f'  answer="{esc_attr(q["answer"])}"')
            L.append(f'  hints={json.dumps(["回忆本单元强调的核心认知。","先想清楚这个概念要解决什么业务问题。"], ensure_ascii=False)}')
            L.append(f'  feedback="{esc_attr("这正是本单元强调的核心认知，记住它，后面会反复用到。")}"')
            L.append(f'  unlock="{esc_attr("你已经开始用分析师的眼光看数据了。")}"')
            L.append("}")
            L.append("")
            cp_count += 1
        elif cp_count == 1 and bi >= 2 and len(sents) > 2:
            q = build_mcq(sents[2], sents, seed=hash(uid+"cp2") & 0xffff, topic=short_t)
            L.append(":::checkpoint{")
            L.append('  type="multiple_choice"')
            L.append(f'  scenario="{esc_attr(random.Random(hash(uid+"cp2")&0xffff).choice(CP2_SCEN))}"')
            L.append(f'  question="{esc_attr(q["question"])}"')
            L.append(f'  options={json.dumps(q["options"], ensure_ascii=False)}')
            L.append(f'  answer="{esc_attr(q["answer"])}"')
            L.append(f'  hints={json.dumps(["回到本单元开头那个真问题想一想。","正确答案就藏在前面讲过的概念里。"], ensure_ascii=False)}')
            L.append(f'  feedback="{esc_attr("很好，这一节的关键点你抓到了。")}"')
            L.append(f'  unlock="{esc_attr("继续往下，概念会越来越连成一张网。")}"')
            L.append("}")
            L.append("")
            cp_count += 1
        # 案例 → explore（只取真正讲案例/标杆的段落，且 scenario 不能太短）
        if not case_used:
            for b in blocks:
                txt = b.get("md","")
                if not txt or len(txt) < 60:
                    continue
                if "案例" not in txt and "标杆" not in txt and "镜鉴" not in txt:
                    continue
                # 避免把定义段落/举例句误判为案例段落：
                # 案例段落应提到具体企业/品牌/年份；纯定义段落没有这些
                ENTITY_RE = re.compile(r"(焕新家电|某电商|某平台|淘宝|京东|拼多多|抖音|小红书|快手|天猫|阿里巴巴|京东物流|顺丰|菜鸟|某品牌|某品质电商|20\d{2}年)")
                if not ENTITY_RE.search(txt):
                    continue
                # 如果段落前 60 字里有明显定义腔（"是...过程" / "通过...数据"），跳过
                head = txt[:80]
                if re.search(r"是\s*[^。]{0,40}过程", head) or re.search(r"通过\s*[^。]{0,40}数据", head):
                    continue
                # 提取含"案例/标杆/镜鉴"的完整句子作为 scenario，至少 40 字
                sents = [x.strip() for x in re.split(r"[。！？]", txt) if x.strip()]
                snippet = None
                for s in sents:
                    if ("案例" in s or "标杆" in s or "镜鉴" in s) and len(s) >= 40:
                        # 案例句本身应包含具体企业/品牌/年份才可信
                        if ENTITY_RE.search(s):
                            snippet = s[:220]
                            break
                if not snippet:
                    continue
                snippet = snippet[:220]
                L.append(":::explore{")
                L.append(f'  title="{esc_attr("真实案例")}"')
                L.append(f'  scenario="{esc_attr(snippet)}"')
                choices = EXPLORE_SETS[hash(uid + "ex") % len(EXPLORE_SETS)]
                L.append(f'  choices={json.dumps(choices, ensure_ascii=False)}')
                L.append("}")
                L.append("")
                case_used = True
                break

    # 挑战
    f = build_fill(sents, seed=hash(uid+"ch") & 0xffff)
    if f:
        L.append(":::challenge{")
        L.append(f'  id="{uid}_c1"')
        L.append('  type="fill"')
        L.append(f'  title="{esc_attr("转正小考")}"')
        L.append(f'  scenario="{esc_attr("mentor 给了小北一组真实数据，让她当场算一个数。")}"')
        L.append(f'  instruction="{esc_attr(f["question"])}"')
        L.append(f'  answer="{esc_attr(f["answer"])}"')
        L.append(f'  hints={json.dumps(["这题考的是本单元里出现的一个关键数字/口径。","回到正文，找到带这个数字的句子再读一遍。","先定位它属于哪个指标，再确认数值。"], ensure_ascii=False)}')
        L.append(f'  feedback="{esc_attr("算对了！你已能把本单元的方法用到真实数据上。")}"')
        L.append(f'  unlock="{esc_attr("这一关过了，这个任务的硬本事你就拿到了。")}"')
        L.append("}")
    else:
        q = build_mcq(sents[-1] if sents else unit_title, sents or [unit_title], seed=hash(uid+"ch") & 0xffff, topic=short_t)
        L.append(":::challenge{")
        L.append(f'  id="{uid}_c1"')
        L.append('  type="multiple_choice"')
        L.append(f'  title="{esc_attr("转正小考")}"')
        L.append(f'  scenario="{esc_attr("mentor 出了一道综合题，考你这个任务到底学没学透。")}"')
        L.append(f'  question="{esc_attr(q["question"])}"')
        L.append(f'  options={json.dumps(q["options"], ensure_ascii=False)}')
        L.append(f'  answer="{esc_attr(q["answer"])}"')
        L.append(f'  hints={json.dumps(["把本任务的知识点串起来想。","正确答案就在你刚学的内容里。"], ensure_ascii=False)}')
        L.append(f'  feedback="{esc_attr("答对了，这个任务的核心你已经掌握。")}"')
        L.append(f'  unlock="{esc_attr("下一关，你会遇到更复杂的真实场景。")}"')
        L.append("}")
    L.append("")
    L.append("---")
    L.append("")
    L.append("> 学完这一单元，回到课程页可以看到你的「学习增益」——课前测与课后测的对比，就是你的成长曲线。")
    return "\n".join(L), objs, sents

# ---------- 主流程 ----------
SUMMARY = []
SITE_FINAL_POOL = []   # 全站统一的结业大考题库（跨 6 个项目）
for cid, proj in STRUCT.items():
    title = proj["title"]
    tasks = proj["tasks"]
    course = {"id": cid, "title": title,
              "description": f"跟随新人「小北」在「{COMPANY}」电商部的成长，完成《{title}》的全部任务：从真实业务问题出发，把数据变成能落地的决策。",
              "chapters": []}
    all_chapter_sents = {}   # chapterId -> sents (用于阶段考)
    ch_units = {}            # chapterId -> [unitId...]
    for ti, task in enumerate(tasks, start=1):
        tid = task["id"].replace(".","")          # "11","21"...
        ch_id = f"ch{tid}"
        ch_title = f"任务{task['id']} {clean_title(task['title'])}"
        sections = task["sections"]
        if not sections:
            sections = [{"title": clean_title(task["title"]), "subs":[], "paras":[], "tables":[]}]
        is_single = len(sections) == 1
        chapter = {"id": ch_id, "title": ch_title, "order": ti, "units": []}
        chapter_sents = []
        ch_units[ch_id] = []
        for si, sec in enumerate(sections, start=1):
            uid = f"u{tid}-{si}"
            md_path = f"{uid}.md"
            raw_sec_title = clean_title(sec.get("title","")) or clean_title(task["title"])
            is_overview = raw_sec_title.startswith("(概述)") or raw_sec_title == clean_title(task["title"])
            unit_title = clean_title(task["title"]) if (is_single or is_overview) else raw_sec_title
            md_text, objs, sents = gen_unit_md(cid, task, sec, uid, is_single, unit_title)
            with open(os.path.join(COURSES, md_path), "w", encoding="utf-8") as f:
                f.write(md_text)
            assess = make_assessment(sents, uid)
            with open(os.path.join(ASSESS, f"{uid}.json"), "w", encoding="utf-8") as f:
                json.dump(assess, f, ensure_ascii=False, indent=2)
            duration = f"约 {8 + 3*max(1,len(sec.get('subs',[])))} 分钟"
            chapter["units"].append({"id": uid, "title": unit_title,
                                     "path": md_path, "duration": duration, "objectives": objs,
                                     "preAssessment": uid, "postAssessment": uid})
            chapter_sents.extend(sents)
            ch_units[ch_id].append(uid)
        course["chapters"].append(chapter)
        all_chapter_sents[ch_id] = chapter_sents
    # 写课程树
    with open(os.path.join(COURSES, f"{cid}.json"), "w", encoding="utf-8") as f:
        json.dump(course, f, ensure_ascii=False, indent=2)
    # 阶段考（每任务一套）；结业考题汇入 SITE_FINAL_POOL（在循环外统一生成）
    fidx = 0
    for ti, task in enumerate(tasks, start=1):
        tid = task["id"].replace(".","")
        ch_id = f"ch{tid}"
        sents = all_chapter_sents[ch_id]
        pool = []
        for k in range(min(10, max(6, len(sents)))):
            q = build_mcq(sents[k % len(sents)] if sents else title, sents or [title], seed=hash(ch_id+"exam"+str(k)) & 0xffff)
            qid = f"{ch_id}-q{k+1}"
            q["id"] = qid
            q["unitId"] = ch_units[ch_id][0] if ch_units[ch_id] else uid
            q["concept"] = clean_title(task["title"])
            pool.append(q)
        exam = {"chapterId": ch_id, "courseId": cid,
                "title": f"任务{task['id']} {clean_title(task['title'])} · 阶段考试",
                "description": "完成本任务全部单元后解锁，检验你是否真的能独立解决这个业务问题。",
                "passScore": 60, "pick": min(8, len(pool)), "pool": pool}
        with open(os.path.join(EXAMS, f"{ch_id}.json"), "w", encoding="utf-8") as f:
            json.dump(exam, f, ensure_ascii=False, indent=2)
        # 结业考：每章取前 6，汇入全站统一题库
        for it in pool[:6]:
            fidx += 1
            SITE_FINAL_POOL.append({"id": f"final-{ch_id}-q{fidx}", "type": it["type"], "unitId": it["unitId"],
                               "chapter": ch_id, "concept": it["concept"], "courseId": cid, "question": it["question"],
                               "options": it["options"], "answer": it["answer"], "points": it["points"]})
    # 注意：不在项目循环内写 final.json（所有项目共用一个全局 final，放循环外统一生成）

    n_units = sum(len(c["units"]) for c in course["chapters"])
    SUMMARY.append((cid, title, len(course["chapters"]), n_units))
    print(f"{cid}: chapters={len(course['chapters'])} units={n_units} exams={len(course['chapters'])}")

    n_units = sum(len(c["units"]) for c in course["chapters"])
    SUMMARY.append((cid, title, len(course["chapters"]), n_units))
    print(f"{cid}: chapters={len(course['chapters'])} units={n_units} exams={len(course['chapters'])+1}")

print("\n=== 汇总 ===")
for s in SUMMARY:
    print(" ", s)

# 全站统一的结业大考（跨 6 个项目）。UI 仅识别全局 chapterId="final"。
# 并入项目四（sales-project4）已有的阶段考题库，保证结业考覆盖全部六个项目。
import glob as _glob
for _ep in _glob.glob(os.path.join(EXAMS, "ch4*.json")):
    try:
        _ej = json.load(open(_ep, encoding="utf-8"))
    except Exception:
        continue
    for _it in _ej.get("pool", []):
        SITE_FINAL_POOL.append({**_it, "courseId": "sales-project4"})

final = {"chapterId":"final","courseId":"sales-platform",
         "title":"全站结业大考","description":"跨《数字化销售数据分析》全部六个项目的综合性最终考核，通关后获得结业认证。",
         "passScore":60,"pick":min(30,len(SITE_FINAL_POOL)),"pool":SITE_FINAL_POOL}
with open(os.path.join(EXAMS, "final.json"), "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)
print(f"final.json: pool={len(SITE_FINAL_POOL)} pick={final['pick']} (全局唯一, 含项目四)")
print("DONE")
