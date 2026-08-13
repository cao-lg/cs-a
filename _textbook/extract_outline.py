import docx
from docx import Document
from docx.oxml.ns import qn

doc = Document(r"D:\workbuddy\chain_supply\_textbook\textbook.docx")

# Map style -> level
def style_level(p):
    s = p.style
    name = (s.name or "") if s else ""
    if name.startswith("Heading"):
        try:
            return int(name.replace("Heading","").strip())
        except:
            return None
    if name in ("Title",):
        return 0
    return None

# Walk body in order
from docx.document import Document as _Doc
from docx.table import Table
from docx.text.paragraph import Paragraph

body = doc.element.body
outline = []
para_count = 0
tbl_count = 0
for child in body.iterchildren():
    if child.tag == qn('w:p'):
        p = Paragraph(child, doc)
        para_count += 1
        lvl = style_level(p)
        txt = p.text.strip()
        if lvl is not None and txt:
            outline.append((lvl, txt))
    elif child.tag == qn('w:tbl'):
        tbl_count += 1

print("TOTAL_PARAGRAPHS", para_count)
print("TOTAL_TABLES", tbl_count)
print("HEADING_COUNT", len(outline))
print("="*60)
# Print outline, but only levels 0-3 to keep readable
for lvl, txt in outline:
    if lvl is not None and lvl <= 4:
        indent = "  "*(lvl if lvl>=0 else 0)
        print(f"{indent}{lvl}|{txt}")
