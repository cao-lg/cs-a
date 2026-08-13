# -*- coding: utf-8 -*-
import json, sys, os
book = json.load(open(r"D:\workbuddy\chain_supply\_textbook\book.json", encoding="utf-8"))
unit_by_num = {}
for p in book:
    for u in p.get("units", []):
        unit_by_num[u["num"]] = u

def legit_table(tb):
    if not tb: return None
    if len(tb[0]) > 10: return None
    return tb

nums = sys.argv[1:]
os.makedirs(r"D:\workbuddy\chain_supply\_textbook\dump", exist_ok=True)
for num in nums:
    u = unit_by_num.get(num)
    if not u:
        print("NO UNIT", num); continue
    lines = []
    lines.append(f"# UNIT {num}")
    for s in u.get("subs", []):
        lines.append(f"\n## SUB {s['num']}  {s['title']}")
        for para in s.get("paras", []):
            lines.append(para)
        for tb in s.get("tables", []):
            t = legit_table(tb["table"])
            if t:
                lines.append("\n[TABLE]")
                for r in t:
                    lines.append(" | ".join(r))
    out = r"D:\workbuddy\chain_supply\_textbook\dump\%s.txt" % num.replace(".","-")
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    print("wrote", out, "chars", len("\n".join(lines)))
