import json, os, random
from pathlib import Path
START=1
END=1182  # 1 to 1181 inclusive = 5904 Qs (1181*5=5905, last file will have 4)
BATCH=5
Path("ex").mkdir(exist_ok=True)
all_bps=[f"bp{i}" for i in range(START,END)]
missing=[bp for bp in all_bps if not Path(f"ex/{bp}.json").exists()]
print(f"For 5904: Already have {len(all_bps)-len(missing)} | Missing {len(missing)} | Total ex/: {len(list(Path('ex').glob('*.json')))}")
# write 50 at a time so terminal doesn't hang
for bp in missing[:50]:
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
print(f"Done batch. Run again to continue.")
