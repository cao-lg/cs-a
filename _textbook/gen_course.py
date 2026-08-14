# -*- coding: utf-8 -*-
"""
教材 → 鲜活学习平台 课程生成器
读取 book.json（结构化教材），按「故事圣经（小北 / 周师傅）」生成：
  - public/data/courses/sc-*.md          22 个情境剧单元
  - public/data/assessments/sc-*.json     22 套课前/课后诊断评测
  - public/data/courses/supply-chain.json  课程树（7 章 22 单元）
并回写 manifest.json 注册课程。
"""
import json, re, os, random

ROOT = r"D:\workbuddy\chain_supply\learning-platform"
COURSES = os.path.join(ROOT, "public", "data", "courses")
ASSESS = os.path.join(ROOT, "public", "data", "assessments")
os.makedirs(COURSES, exist_ok=True)
os.makedirs(ASSESS, exist_ok=True)

book = json.load(open(r"D:\workbuddy\chain_supply\_textbook\book.json", encoding="utf-8"))

# ---------- 1. 单元编号 → 单元对象 ----------
unit_by_num = {}
for p in book:
    for u in p.get("units", []):
        unit_by_num[u["num"]] = u

def clean_title(t):
    return re.sub(r"^\s*\d+(\.\d+)*\s*", "", t).strip()

# ---------- 2. 课程结构（章节 / 单元 / 人文标题） ----------
# 项目 → 章；X.Y 小组 → 单元。7.x 在原书并入项目六，这里单独拆成「项目七 前沿视野篇」。
CHAPTERS = [
    ("ch1", "项目一 探索数字供应链运营新升级", "基础认知篇", [
        ("1.1", "供应链概念的演变"),
        ("1.2", "数字化供应链的范式革新"),
        ("1.3", "供应链协同与数字化协作"),
    ]),
    ("ch2", "项目二 实现需求计划数字化精准化", "实战技能篇", [
        ("2.1", "从“以产定销”到“以销定产”：市场驱动转型"),
        ("2.2", "供应链用户画像：从营销视角到供应链视角"),
        ("2.3", "客户订单解析与需求预测"),
        ("2.4", "数字化 CRM 的供应链视角"),
        ("2.5", "需求计划的数字化交付"),
    ]),
    ("ch3", "项目三 打造数字化采购新优势", "实战技能篇", [
        ("3.1", "采购的数字化演进与策略"),
        ("3.2", "采购计划与数据驱动的需求分析"),
        ("3.3", "供应商选择与绩效评估"),
    ]),
    ("ch4", "项目四 构建数智化生产管理新范式", "实战技能篇", [
        ("4.1", "从经验驱动到数据驱动的智能制造"),
        ("4.2", "数据驱动的智能排程"),
        ("4.3", "动态 MRP 与可视化生产监控"),
    ]),
    ("ch5", "项目五 重塑端到端智慧物流新路径", "实战技能篇", [
        ("5.1", "智慧物流的概念演变与技术架构"),
        ("5.2", "智能仓储：数据驱动的仓储优化"),
        ("5.4", "在途管理与物流全程可视化"),
    ]),
    ("ch6", "项目六 创建供应链风险智能预警新格局", "实战技能篇", [
        ("6.1", "供应链风险管理的智能转型"),
        ("6.2", "供应链舆情与风险感知"),
        ("6.3", "风险量化与智能预警模型"),
    ]),
    ("ch7", "项目七 前沿视野：AI+供应链与人才", "前沿视野篇", [
        ("7.1", "“人工智能+供应链”的内涵与路径"),
        ("7.2", "数字供应链的技术架构与技术闭环"),
        ("7.3", "AI 应用的边界与渗透深度"),
        ("7.4", "供应链人才需求的结构性升级"),
    ]),
]

# ---------- 3. 故事圣经（小北 / 周师傅）每章情境剧开场 ----------
ARC = {
    "ch1": dict(
        setup="入职第一天，周师傅把小北带到一面贴满便签的「供应链全景墙」前，墙上是密密麻麻的箭头与节点。",
        line="小北，先别急着学工具。今天你只要搞懂一件事：供应链到底是什么，它为什么非数字化不可。",
        thought="💭 我以前以为供应链就是『进货、卖货』，原来它是一条会呼吸、会卡顿的长链。",
        focus="一张图：从原材料到消费者，链路到底有多长",
        focusQ="如果中间某一环『看不见』，会发生什么？",
    ),
    "ch2": dict(
        setup="第二周，小北被轮岗到需求计划组。桌上堆着去年双十一的爆仓复盘，周师傅推过来一杯咖啡。",
        line="需求计划是供应链的『指挥棒』。做错了，要么积压、要么断货。今天带你把『拍脑袋』换成『看数据』。",
        thought="💭 原来卖多少不是靠猜，而是靠把客户的声音翻译成数字。",
        focus="一个核心问题：到底该生产 / 备多少货？",
        focusQ="凭感觉定产量，风险藏在哪一环？",
    ),
    "ch3": dict(
        setup="月末，小北跟着采购部的师姐去参加一场供应商大会，会场外停满了物流车。",
        line="采购不再是『买东西』，而是用数据和策略为企业『买未来』。选址、谈价、控风险，每一步都有学问。",
        thought="💭 同样的钱，怎么花出更大的确定性？采购也能创造价值。",
        focus="采购的三道关：计划、寻源、供应商",
        focusQ="为什么『便宜』不一定是好采购？",
    ),
    "ch4": dict(
        setup="走进合作工厂的『智能车间』，机械臂在灯光下有序舞动，大屏上跳动着实时产量。",
        line="生产管理正从『老师傅经验』走向『数据说了算』。今天你看清车间里的黑箱是怎么被照亮的。",
        thought="💭 一条产线原来可以像生命体一样被实时感知和调度。",
        focus="工厂里的『数据神经』：排程、物料、监控",
        focusQ="当订单突然变了，产线怎么不慌？",
    ),
    "ch5": dict(
        setup="台风预警那晚，小北守在物流监控大屏前，盯着一条迟迟未更新的在途货车。",
        line="物流是供应链的『手脚』。智慧物流让每一件货『看得见、调得动、算得清』。",
        thought="💭 货物在路上的每一公里，其实都能被数据捕捉到。",
        focus="端到端的『看得见』：仓储 + 在途",
        focusQ="如果一车货失联了，系统能提前知道吗？",
    ),
    "ch6": dict(
        setup="一条突发的供应商违约新闻冲上热搜，周师傅把小北拉进应急会议室。",
        line="风险不可怕，可怕的是『看不见』。今天教你用舆情和数据，把隐患量化成预警。",
        thought="💭 原来危机来临前，数据早就给过信号，只是我们没听懂。",
        focus="把模糊的风险，变成可计量的数字",
        focusQ="当负面舆情出现，怎样在 6 小时内判断要不要预警？",
    ),
    "ch7": dict(
        setup="轮岗结束，小北站在公司顶楼，看城市灯火。周师傅递给他一份行业白皮书。",
        line="未来的供应链，拼的是『驾驭趋势』的能力。AI 不是来替代你，是来放大你的判断力。",
        thought="💭 我想成为那个既能看懂数据、也能把握方向的人。",
        focus="从『执行操作』到『驾驭趋势』",
        focusQ="AI 时代，供应链人最该升级的是什么？",
    ),
}

# ---------- 4. 文本工具 ----------
def esc(s):
    """转义用于 :::指令 属性字符串的值。"""
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    s = s.replace("\n", " ").replace("\r", " ").replace("'", "’")
    return s.strip()

MARKER = re.compile(r"^(思考|任务|实训|自测|练习|拓展|活动)")
INLINE_HEADING = re.compile(r"^\s*\d+\.\d+\s+\S")  # 内联节标题，如“1.2  范式革新……”

def split_sentences(text):
    return [x.strip() for x in re.split(r"[。！？\n;；]", text) if x.strip()]

DOMAIN = ["供应链", "数字化", "数据", "需求", "采购", "生产", "物流", "风险",
          "预警", "客户", "供应商", "订单", "智能", "AI", "库存", "协同", "可视化"]

CAPTION_RE = re.compile(r"^(图|表)\s*\d")
HEADING_RE = re.compile(r"^\s*\d+[．\.、]\s*")

def is_junk_sentence(s):
    if len(s) < 18 or len(s) > 110:
        return True
    if CAPTION_RE.match(s):
        return True
    if HEADING_RE.match(s):
        return True
    if "待编辑美化" in s:
        return True
    # 拒绝纯列举/标号开头
    if re.match(r"^\s*[（(]\d+[)）]\s*", s):
        return True
    return False

def key_sentences(unit):
    out = []
    seen = set()
    for s in unit.get("subs", []):
        for para in s.get("paras", []):
            if MARKER.match(para):
                continue
            if INLINE_HEADING.match(para) and len(para) <= 80:
                continue
            for sent in split_sentences(para):
                if is_junk_sentence(sent):
                    continue
                if not any(k in sent for k in DOMAIN):
                    continue
                if sent not in seen:
                    seen.add(sent)
                    out.append(sent)
    return out

def table_to_md(tbl):
    if not tbl:
        return ""
    ncol = len(tbl[0])
    # 教材里大量"伪表格"是用竖线排版的文本，被 python-docx 拆成每个汉字一格（列数远超 10）
    # 这类直接丢弃，避免渲染成一长串乱码；只保留真正规整的多列表。
    if ncol > 10:
        return ""
    avg_cell = sum(len("".join(r)) for r in tbl) / max(1, sum(len(r) for r in tbl))
    if avg_cell <= 1.2:
        return ""
    lines = []
    lines.append("| " + " | ".join(tbl[0]) + " |")
    lines.append("| " + " | ".join(["---"] * ncol) + " |")
    for row in tbl[1:]:
        # 补齐全行（防缺列导致 markdown 表格错位）
        row = (list(row) + [""] * ncol)[:ncol]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)

def sub_to_blocks(sub):
    """把小节正文拆成 md 段落 与 互动块（思考/任务/实训 → Explore）。"""
    blocks = []
    md_buf = []
    in_inter = None
    def flush():
        if md_buf:
            blocks.append({"md": "\n".join(md_buf)})
            md_buf.clear()
    for t in sub.get("paras", []):
        # 跳过图/表题注（图片未提取，表格已单独渲染）
        if re.match(r'^(图|表)\s*\d', t) and len(t) <= 24:
            continue
        # 跳过被排版进本节末尾的下一节内联标题
        if INLINE_HEADING.match(t) and len(t) <= 80:
            continue
        if MARKER.match(t):
            flush()
            in_inter = {"marker": t, "body": []}
            blocks.append({"inter": in_inter})
            continue
        if in_inter is not None:
            in_inter["body"].append(t)
        else:
            md_buf.append(t)
    flush()
    # 表格
    for tb in sub.get("tables", []):
        blocks.append({"md": table_to_md(tb["table"])})
    # 案例 → Explore 反思
    for cs in sub.get("cases", []):
        body = " ".join(cs.get("paras", []))[:260]
        blocks.append({"explore": {"title": "案例：" + cs["title"], "body": body}})
    return blocks

# ---------- 5. 评测生成 ----------
def trunc(s, n=32):
    s = s.strip()
    return s if len(s) <= n else s[:n] + "…"

def build_mcq(correct, others, seed):
    rnd = random.Random(seed)
    correct_t = trunc(correct)
    # 优先选与本句共享主题词的干扰项，避免主题跳跃
    correct_keys = set([k for k in DOMAIN if k in correct])
    pool = []
    for o in others:
        if o == correct or len(o) <= 8:
            continue
        ot = trunc(o)
        if ot == correct_t:
            continue
        # 共享主题词或长度相近的优先
        shared = len(set([k for k in DOMAIN if k in o]) & correct_keys)
        pool.append((shared, ot))
    pool.sort(key=lambda x: (-x[0], rnd.random()))
    distractors = [p[1] for p in pool[:3]]
    # 若本单元句子不足 3 个，用通用反面表述补足
    generic = [
        "该说法把原因和结果颠倒了，不符合本单元逻辑",
        "这描述的是传统供应链的做法，不是本单元强调的方向",
        "该选项扩大了适用范围，并非本单元讨论的重点",
    ]
    rnd.shuffle(generic)
    while len(distractors) < 3:
        d = generic.pop()
        if d not in distractors:
            distractors.append(d)
    opts = distractors + [correct_t]
    rnd.shuffle(opts)
    return {
        "id": "",
        "type": "multiple_choice",
        "question": "学习本单元后，下列说法正确的是？",
        "options": opts,
        "answer": correct_t,
        "points": 10,
    }

def build_fill(unit, others, seed):
    rnd = random.Random(seed)
    # 找带数字的事实句
    for s in unit["_sents"]:
        m = re.search(r"([0-9]+(?:\.[0-9]+)?\s*(?:%|倍|天|元|个|项|类|年|月))", s)
        if m:
            num = m.group(1).strip()
            q = s.replace(num, "_____", 1)
            if 12 <= len(q) <= 90:
                return {
                    "id": "",
                    "type": "fill",
                    "question": trunc(q, 70),
                    "answer": num,
                    "points": 10,
                }
    return None

def make_assessment(unit, unit_id):
    sents = unit["_sents"]
    if len(sents) < 2:
        # 兜底：用单元目标句
        sents = [clean_title(s["title"]) for s in unit.get("subs", [])]
    pre_items, post_items = [], []
    n = len(sents)
    pre_idx = list(range(0, min(2, n)))
    post_idx = list(range(min(2, n), min(5, n)))
    if not post_idx:  # 句子不足时复用
        post_idx = pre_idx
    for i in pre_idx:
        q = build_mcq(sents[i], sents, seed=hash(unit_id + "pre" + str(i)) & 0xffff)
        q["id"] = f"{unit_id}_pre{len(pre_items)+1}"
        pre_items.append(q)
    for i in post_idx:
        q = build_mcq(sents[i], sents, seed=hash(unit_id + "post" + str(i)) & 0xffff)
        q["id"] = f"{unit_id}_post{len(post_items)+1}"
        post_items.append(q)
    # 课后补一道填空题（若有数字事实）
    f = build_fill(unit, sents, seed=hash(unit_id + "fill") & 0xffff)
    if f:
        f["id"] = f"{unit_id}_post{len(post_items)+1}"
        post_items.append(f)
    return {
        "unitId": unit_id,
        "pre": {
            "title": "课前测：先摸清你的起点",
            "description": "不用背定义，凭直觉选。测测你对这一主题的原有认知。",
            "items": pre_items,
        },
        "post": {
            "title": "课后测：看看你掌握了什么",
            "description": "学完本单元后，检验关键概念是否真的入脑。",
            "items": post_items,
        },
    }

# ---------- 6. 单元 md 生成 ----------
def gen_unit_md(chapter_key, unit_num, human_title):
    unit = unit_by_num[unit_num]
    subs = unit.get("subs", [])
    arc = ARC[chapter_key]
    # 学习目标 = 各小节标题
    objectives = [clean_title(s["title"]) for s in subs][:6]
    L = []
    L.append(f"# {esc(human_title)}")
    L.append("")
    L.append("> **本单元学习目标**")
    for o in objectives:
        L.append(f"> - {esc(o)}")
    L.append("")
    # 情境剧开场
    focusQ = esc(arc["focusQ"])
    setup = esc(arc["setup"])
    line = esc(arc["line"])
    focus = esc(arc["focus"])
    thought = esc(arc["thought"])
    L.append(":::scene{")
    L.append(f'  setup="{setup}"')
    L.append('  speaker="周师傅"')
    L.append(f'  line="{line}"')
    L.append(f'  focus="{focus}"')
    L.append(f'  focusQ="{focusQ}"')
    L.append(f'  thought="{thought}"')
    L.append("}")
    L.append("")
    # 小节
    for s in subs:
        sub_title = esc(clean_title(s["title"]))
        L.append(f"## {sub_title}")
        L.append("")
        blocks = sub_to_blocks(s)
        for b in blocks:
            if "md" in b:
                L.append(b["md"])
                L.append("")
            elif "inter" in b:
                it = b["inter"]
                body = it["marker"] + "\n" + "\n".join(it["body"])
                mtitle = esc(it["marker"][:2])
                bbody = esc(body)
                L.append(":::explore{")
                L.append(f'  title="{mtitle}"')
                L.append("  reflect=true")
                L.append(f'  body="{bbody}"')
                L.append("}")
                L.append("")
            elif "explore" in b:
                ex = b["explore"]
                extitle = esc(ex["title"][:30])
                exbody = esc(ex["body"])
                L.append(":::explore{")
                L.append(f'  title="{extitle}"')
                L.append("  reflect=true")
                L.append(f'  body="{exbody}"')
                L.append("}")
                L.append("")
    # 课间小测（检查点）：取单元关键句生成 1-2 道选择题
    sents = unit.get("_sents", [])
    if sents:
        for k in range(min(2, len(sents))):
            correct = sents[k]
            q_obj = build_mcq(correct, sents, seed=hash(unit_id_for(unit_num) + "cp" + str(k)) & 0xffff)
            L.append(":::checkpoint{")
            L.append('  type="multiple_choice"')
            L.append(f'  question="{esc(q_obj["question"])}"')
            L.append(f'  options={json.dumps(q_obj["options"], ensure_ascii=False)}')
            L.append(f'  answer="{esc(q_obj["answer"])}"')
            L.append(f'  feedback="{esc("这正是本单元强调的核心认知，记住它，后面会反复用到。")}"')
            L.append("}")
            L.append("")
    L.append("---")
    L.append("")
    L.append("> 学完这一单元，回到课程页可以看到你的「学习增益」——课前测与课后测的对比，就是你的成长曲线。")
    return "\n".join(L), objectives

def unit_id_for(num):
    return "sc-" + num.replace(".", "-")

# ---------- 7. 预计算每单元关键句 ----------
for n, u in unit_by_num.items():
    u["_sents"] = key_sentences(u)

# ---------- 8. 写出所有文件 + 课程树 ----------
course = {
    "id": "supply-chain",
    "title": "数字化供应链运营（AI 智慧学习版）",
    "description": "从供应链基础认知到需求计划、采购、生产、物流、风险预警与 AI 前沿的完整学习闭环，跟随新人「小北」在「智链优选」供应链运营中心的成长，把知识点变成一场边玩边记的旅程。",
    "chapters": [],
}

unit_records = []  # (unit_id, md_path, title, objectives, duration)
for ci, (ch_key, ch_title, ch_part, units) in enumerate(CHAPTERS, start=1):
    chapter = {"id": ch_key, "title": ch_title, "order": ci, "units": []}
    for (num, human) in units:
        uid = unit_id_for(num)
        md_path = f"{uid}.md"
        md_text, objectives = gen_unit_md(ch_key, num, human)
        with open(os.path.join(COURSES, md_path), "w", encoding="utf-8") as f:
            f.write(md_text)
        # 评测
        assess = make_assessment(unit_by_num[num], uid)
        with open(os.path.join(ASSESS, f"{uid}.json"), "w", encoding="utf-8") as f:
            json.dump(assess, f, ensure_ascii=False, indent=2)
        duration = f"约 {12 + 4*len(unit_by_num[num].get('subs',[]))} 分钟"
        chapter["units"].append({
            "id": uid,
            "title": f"单元：{human}",
            "path": md_path,
            "duration": duration,
            "objectives": objectives,
            "preAssessment": uid,
            "postAssessment": uid,
        })
        unit_records.append((uid, md_path, human, objectives, duration))
    course["chapters"].append(chapter)

with open(os.path.join(COURSES, "supply-chain.json"), "w", encoding="utf-8") as f:
    json.dump(course, f, ensure_ascii=False, indent=2)

# ---------- 9. 回写 manifest ----------
manifest_path = os.path.join(COURSES, "manifest.json")
manifest = json.load(open(manifest_path, encoding="utf-8"))
if "supply-chain" not in manifest["courses"]:
    manifest["courses"].append("supply-chain")
    manifest["courses"].sort()
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("DONE. units:", len(unit_records))
for r in unit_records:
    print(" ", r[0], r[2], r[4])
