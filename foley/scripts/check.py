#!/usr/bin/env python3
"""Pass/fail table from an earshot timeline JSON: |offset| <= 40 ms and >= 6 dB over the bed.
usage: check.py timeline.json id1,id2,... [check.json]"""
import json, sys

d = json.load(open(sys.argv[1]))
ids = sys.argv[2].split(",")
items = d["sync"]["cues"]["items"]
ok_all = True
rows = []
for name, it in zip(ids, items):
    off, prom = it.get("offset_ms"), it.get("event_prominence_db")
    ok = off is not None and abs(off) <= 40 and prom is not None and prom >= 6
    ok_all &= ok
    rows.append({"id": name, "cue": it["t"], "event_t": it.get("event_t"), "offset_ms": off,
                 "over_bed_db": prom, "status": it.get("status"), "event": it.get("event"), "pass": ok})
    print(f"{name:<9} cue {it['t']:.3f}  heard {it.get('event_t')}  offset {off:+} ms  over bed {prom} dB  "
          f"[{it.get('status')}] {it.get('event')}  -> {'PASS' if ok else 'FAIL'}")
lo = d.get("loudness", {})
print("loudness:", {k: lo.get(k) for k in ("integrated_lufs", "true_peak_dbtp", "clipping") if k in lo} or list(lo)[:12])
print("ALL PASS" if ok_all else "NOT YET")
if len(sys.argv) > 3:
    json.dump(rows, open(sys.argv[3], "w"), indent=1)
