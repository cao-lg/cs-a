import re, json
from docx import Document
from docx.oxml.ns import qn
from docx.document import Document as _Doc
from docx.table import Table
from docx.text.paragraph import Paragraph

doc = Document(r"D:\workbuddy\chain_supply\_textbook\textbook.docx")
body = doc.element.body

def is_heading(p):
    s = p.style
    name = (s.name or "") if s else ""
    return name.startswith("Heading") or name in ("Title",)

def heading_level(p):
    s = p.style
    name = (s.name or "") if s else ""
    if name in ("Title",): return 0
    m = re.match(r"Heading\s*(\d+)", name)
    return int(m.group(1)) if m else None

PREFIX_RE = re.compile(r"^\s*(\d+)\.(\d+)(?:\.(\d+))?")
PROJ_RE = re.compile(r"^\s*项目\s*([一二三四五六七八九十]+)")
CN_NUM = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}

def table_to_text(tbl):
    rows = []
    for r in tbl.rows:
        cells = [c.text.strip().replace("\n"," ") for c in r.cells]
        rows.append(" | ".join(cells))
    return rows

projects = []   # list of dicts
cur_proj = None
cur_unit = None   # X.Y
cur_sub = None    # X.Y.Z
cur_any = lambda: cur_sub if cur_sub is not None else (cur_unit if cur_unit is not None else cur_proj)

def new_proj(title):
    return {"type":"project","title":title,"num":0,"part":"","units":[]}
def new_unit(num,title):
    return {"type":"unit","num":num,"title":title,"subs":[],"extra":[]}
def new_sub(num,title):
    return {"type":"sub","num":num,"title":title,"paras":[],"tables":[],"cases":[]}

for child in body.iterchildren():
    if child.tag == qn('w:p'):
        p = Paragraph(child, doc)
        txt = p.text.strip()
        if not txt:
            continue
        if is_heading(p):
            m = PREFIX_RE.match(txt)
            pm = PROJ_RE.match(txt)
            if pm:
                pn = CN_NUM.get(pm.group(1), 0)
                cur_proj = new_proj(txt)
                cur_proj["num"] = pn
                projects.append(cur_proj)
                cur_unit = None; cur_sub = None
            elif m:
                a,b,c = m.groups()
                if c:  # X.Y.Z subsection
                    unum = f"{a}.{b}"
                    if cur_unit is None or cur_unit["num"] != unum:
                        cur_unit = new_unit(unum, unum)
                        if cur_proj: cur_proj["units"].append(cur_unit)
                    cur_sub = new_sub(f"{a}.{b}.{c}", txt)
                    cur_unit["subs"].append(cur_sub)
                else:  # X.Y unit
                    cur_unit = new_unit(f"{a}.{b}", txt)
                    if cur_proj: cur_proj["units"].append(cur_unit)
                    cur_sub = None
            else:
                # non-numbered heading: part name (篇) or case study title
                title = txt
                if "篇" in title:
                    if cur_proj is None:
                        cur_proj = new_proj(txt); projects.append(cur_proj)
                    cur_proj["part"] = title
                    cur_unit = None; cur_sub = None
                    continue
                if cur_proj is None:
                    cur_proj = new_proj(txt); projects.append(cur_proj)
                # attach as case study to current sub or unit
                target = cur_sub if cur_sub is not None else cur_unit
                if target is not None:
                    target.setdefault("cases",[]).append({"title":title,"paras":[]})
                    target["_case_open"] = title
                else:
                    cur_proj.setdefault("intro",[]).append(title)
        else:
            # 内联编号小节标题（源文档未设为标题样式，如“1.1.2 供应链的结构”）
            # 仅对三级编号 X.Y.Z 生效，避免把“4.1 拓展知识”这类二级补充行误判为单元
            m_inline = re.match(r'^\s*(\d+)\.(\d+)\.(\d+)\s+\S', txt)
            if m_inline and len(txt) <= 80:
                a,b,c = m_inline.groups()
                unum = f"{a}.{b}"
                if cur_unit is None or cur_unit["num"] != unum:
                    cur_unit = new_unit(unum, unum)
                    if cur_proj: cur_proj["units"].append(cur_unit)
                cur_sub = new_sub(f"{a}.{b}.{c}", txt)
                cur_unit["subs"].append(cur_sub)
                continue
            # normal paragraph
            # route to open case if any
            target = cur_sub if cur_sub is not None else (cur_unit if cur_unit is not None else cur_proj)
            if target is None:
                continue
            case_open = target.get("_case_open")
            if case_open:
                for cs in target.get("cases",[]):
                    if cs["title"]==case_open:
                        cs["paras"].append(txt); break
            else:
                if isinstance(target,dict) and target.get("type")=="sub":
                    target["paras"].append(txt)
                elif isinstance(target,dict) and target.get("type")=="unit":
                    target["extra"].append(txt)
                elif isinstance(target,dict) and target.get("type")=="project":
                    target.setdefault("intro",[]).append(txt)
    elif child.tag == qn('w:tbl'):
        tbl = Table(child, doc)
        rows = table_to_text(tbl)
        target = cur_sub if cur_sub is not None else (cur_unit if cur_unit is not None else cur_proj)
        if target is None: continue
        case_open = target.get("_case_open")
        entry = {"table":rows}
        if case_open:
            for cs in target.get("cases",[]):
                if cs["title"]==case_open: cs.setdefault("tables",[]).append(entry); break
        else:
            if isinstance(target,dict) and target.get("type")=="sub":
                target["tables"].append(entry)
            elif isinstance(target,dict) and target.get("type")=="unit":
                target["extra_tables"]=target.get("extra_tables",[])+[entry]
            elif isinstance(target,dict) and target.get("type")=="project":
                target.setdefault("intro_tables",[]).append(entry)

# cleanup helper flags
def clean(o):
    if isinstance(o,dict):
        o.pop("_case_open",None)
        for k,v in list(o.items()):
            if isinstance(v,list):
                o[k]=[clean(x) for x in v]
            elif isinstance(v,dict):
                o[k]=clean(v)
    return o

projects = clean(projects)

# summary
print("PROJECTS:", len(projects))
for p in projects:
    print(f"\n### {p['title']}  (units={len(p.get('units',[]))})")
    for u in p.get("units",[]):
        nsub = len(u.get("subs",[]))
        ncase = sum(len(s.get("cases",[])) for s in u.get("subs",[]))
        print(f"   - {u['num']} {u['title']}  | subs={nsub} cases={ncase}")

with open(r"D:\workbuddy\chain_supply\_textbook\book.json","w",encoding="utf-8") as f:
    json.dump(projects,f,ensure_ascii=False,indent=1)
print("\nSAVED book.json")
