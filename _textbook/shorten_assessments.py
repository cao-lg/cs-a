# -*- coding: utf-8 -*-
"""
把现有 supply-chain 评测（sc-*.json）的 MCQ 选项截短到更友好的长度（默认 32 字），
同步更新 answer，并保证同一题的截断后选项不重复。
不影响填空题/代码题，也不影响 markdown 课程内容。
"""
import json, glob, os

ASSESS_DIR = r"D:\workbuddy\chain_supply\learning-platform\public\data\assessments"
N = 32

def trunc(s, n):
    s = s.strip()
    return s if len(s) <= n else s[:n] + "…"

def unique_shorten(options, n):
    new = []
    for raw in options:
        L = n
        cand = trunc(raw, L)
        while cand in new and L < len(raw):
            L += 1
            cand = trunc(raw, L)
        new.append(cand)
    return new

def shorten_file(path, n=N):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    changed = False
    for sec in ["pre", "post"]:
        block = data.get(sec, {})
        for it in block.get("items", []):
            if it.get("type") != "multiple_choice":
                continue
            opts = it["options"]
            ans = it["answer"]
            idx = None
            if ans in opts:
                idx = opts.index(ans)
            else:
                for i, o in enumerate(opts):
                    if o.strip() == str(ans).strip():
                        idx = i
                        break
            if idx is None:
                print(f"[WARN] answer not found: {path} {it['id']}")
                continue
            new_opts = unique_shorten(opts, n)
            new_ans = new_opts[idx]
            if new_opts != opts:
                it["options"] = new_opts
                it["answer"] = new_ans
                changed = True
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return changed

if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(ASSESS_DIR, "sc-*.json")))
    changed = 0
    for p in files:
        if shorten_file(p, N):
            changed += 1
    print(f"处理 {len(files)} 个文件，其中 {changed} 个发生截短（截断长度 {N} 字）。")
