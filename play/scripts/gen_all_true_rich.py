import json, os, sys, re
ROOT = "play"
OUT_DIR = os.path.join(ROOT, "json", "phase2", "true_rich_4150")
os.makedirs(OUT_DIR, exist_ok=True)

# import gen_phase2 functions
import importlib.util
spec = importlib.util.spec_from_file_location("gen_phase2", os.path.join(ROOT, "scripts", "gen_phase2.py"))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

data = json.load(open(os.path.join(ROOT, "bank", "BP.json"), encoding="utf-8"))
# ALL real bp passages
all_bp = [p for p in data["passages"] if p["id"].startswith("bp")]
all_bp.sort(key=lambda p: int(p["id"][2:]))
print(f"Total real bp passages: {len(all_bp)}")
print(f"Range: {all_bp[0]['id']} to {all_bp[-1]['id']}")

flat = [(p, i, q) for p in all_bp for i, q in enumerate(p["qs"])]
print(f"Total Qs (true rich possible): {len(flat)}")

entries = {}
meta = {}
order = []

for idx, (p, i, q) in enumerate(flat):
    try:
        ox, m = gen.compose(q, p)
        k = f"{p['id']}_{i}"
        entries[k] = {"ox": ox}
        meta[k] = m
        order.append(k)
    except Exception as e:
        print(f"Error at {p['id']}_{i}: {e}")
        entries[f"{p['id']}_{i}"] = {"ox": [f"Correct. The passage supports {q['o'][q['a']][0][:80]}.", "Incorrect. Not supported.", "Incorrect. Not supported.", "Incorrect. Not supported."]}
    if idx % 200 == 0:
        print(f"  ... {idx}/{len(flat)}")

# Write batch files 15 per file
file_no = 0
for start in range(0, len(order), 15):
    chunk_keys = order[start:start+15]
    chunk = {k: entries[k] for k in chunk_keys}
    lo_id = int(chunk_keys[0].split('_')[0][2:])
    hi_id = int(chunk_keys[-1].split('_')[0][2:])
    out_path = os.path.join(OUT_DIR, f"batch_{lo_id:04d}_{hi_id:04d}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(chunk, f, ensure_ascii=False, separators=(",",":"))
    file_no += 1

print(f"Wrote {file_no} batch files to {OUT_DIR}")

final_list = [{"id": k, "ox": entries[k]["ox"]} for k in order]
with open("final_4150_true_rich.json", "w", encoding="utf-8") as f:
    json.dump(final_list, f)

with open("final_4150_true_rich_dict.json", "w", encoding="utf-8") as f:
    json.dump(entries, f)

import os as _os
print(f"final_4150_true_rich.json: {len(final_list)} Qs, {_os.path.getsize('final_4150_true_rich.json')/1024/1024:.2f} MB")
print(f"First: {final_list[0]['id']}, Last: {final_list[-1]['id']}")
print(f"Sample: {final_list[0]['ox'][0][:200]}")
no_table = sum(1 for k in order if not meta.get(k, {}).get("table", True))
print(f"Stats: total {len(order)}, no_table {no_table}, table {len(order)-no_table}")
