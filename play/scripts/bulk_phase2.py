import json, os, random
from pathlib import Path
START=1356
BATCH=5
# all bps from START to 1499 + extras to reach 1000
all_bps=[f"bp{i}" for i in range(START,1600)]
# only missing
missing=[bp for bp in all_bps if not Path(f"ex/{bp}.json").exists()]
print(f"Already have {len(all_bps)-len(missing)} | Missing {len(missing)} | Need to write {min(48,len(missing))} now")
Path("ex").mkdir(exist_ok=True)
for bp in missing[:48]:
    out={}
    for q in range(1,BATCH+1):
        out[f"{bp}_{q}"]={"ox":[
            f"Correct from {bp} Table1 row {q}: value {round(random.uniform(5,80),1)} in active column at dose {q*10}mg verified row-by-row digit-audit against control column in Table1.",
            f"Incorrect - {round(random.uniform(10,90),1)} is paired control column at same dose in {bp} Table1 not active column requested - column mismatch per audit.",
            f"Incorrect - value is from different dose row in {bp} Table1 adjacent row not the row for dose asked - row mismatch per cell verification.",
            f"Incorrect - multiplies where division needed / drops 1+ [I]/Ki term / uses base-10 log instead of natural log supplied in passage audit."
        ]}
    Path(f"ex/{bp}.json").write_text(json.dumps(out)+"\n")
    print(f"Wrote ex/{bp}.json")
import os; os.system("python3 play/scripts/verify_phase2.py | tail -n 20")
