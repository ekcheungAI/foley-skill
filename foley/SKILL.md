---
name: foley
description: Give a silent or rough video its sound effects end to end — find every moment that needs a sound, fetch CC0 sounds from Openverse (no account, no credit needed), pick and trim them with earshot, place them on the exact frame with ffmpeg, then listen back with earshot and fix anything late, buried or clipping until every cue passes. Use when someone asks to add, design, sync or fix sound effects / foley / SFX for a video.
---

# foley: sound effects that land on the frame

You cannot hear. earshot is your ears: never say a sound "fits" or "is in sync" without an earshot number.
`SKILL_DIR` below = this skill's own folder (shown as its base directory when the skill loads). Work in the video's folder. Keep everything you make under `foley/` next to the video.

## Needs
- `ffmpeg` and `ffprobe` on PATH, Python 3.10+.
- `earshot` on PATH: `uv tool install "earshot[mcp] @ git+https://github.com/Leonxlnx/earshot"` then `earshot doctor --fetch` (~1.1 GB models, CPU only).
- Internet for Openverse (anonymous limit: about 20 requests a minute, 200 a day).

## 1. Find the cues (look, then measure)
1. `python3 SKILL_DIR/scripts/find_cues.py VIDEO --out foley/cues-candidates.json` prints motion peaks (frame-to-frame change) and writes contact sheets to `foley/sheets/`.
2. Read the contact sheets. Name each moment that needs a sound (hit, step, door, whoosh on a fast turn, crash, ambience bed) and pick its exact frame; use the motion peaks to narrow it, but trust what you see. Skip contacts you cannot actually see.
3. Write `foley/cues.json`: `[{"id": "hit1", "t": 0.625, "kind": "hit", "what": "fist meets open palm"}, ...]`.

## 2. Fetch CC0 sounds
For each kind, 2–4 search words: `python3 SKILL_DIR/scripts/fetch_cc0.py "punch impact" foley/sounds/hit --limit 8`.
It only keeps `license=cc0` results from `source=freesound` and logs title, creator, licence and source page in `foley/sounds/sources.json`. CC0 needs no credit, but tell the user to open the source page if the use is commercial: Openverse does not guarantee licence accuracy.

## 3. Pick and trim with earshot
- `earshot rank "<what the moment sounds like>" foley/sounds/<kind> --top 3 --out foley/rank-<kind>.json`. Describe the sound, not the picture ("a short sharp slap of a fist on an open palm").
- `earshot find FILE "<same words>" --kind event --top 3 --out foley/find-<id>.json` for one-shots; `--kind texture` for an ambience bed. Reject trims marked head cut / tail cut.
- Note each trim's sync point: for hits it is the attack (start + ~5 ms); for whooshes it is the loudest point, not the start.

## 4. Place
Write `foley/plan_v1.json` (see `scripts/mix.py` header) and run `python3 SKILL_DIR/scripts/mix.py foley/plan_v1.json`. The picture is copied, never re-encoded.

## 5. Listen back and fix (the important part)
1. `earshot timeline OUT.mp4 --cues "t1,t2,..." --out foley/timeline_v1.json`
2. `python3 SKILL_DIR/scripts/check.py foley/timeline_v1.json id1,id2,... foley/check_v1.json`
   A cue passes when the heard onset is within 40 ms of the frame and at least 6 dB over the bed.
3. Fix only what failed, by the measured amount:
   - late / early → shift that event by the offset (whooshes are usually late because their peak comes after the start);
   - buried (< 6 dB over bed) → raise it or lower the bed;
   - true peak above −1 dBTP or clipping → lower the loudest hit (a limiter cannot catch a transient on the first samples).
4. Write `plan_v2.json`, render, listen again. Repeat until ALL PASS and true peak ≤ −1 dBTP.
5. Loudness: a sound-effects-only track is peaky and usually measures about −20 LUFS with true peak ≤ −1 dBTP. That is expected; set the final loudness later, in the edit with voice/music. Do not push it louder here.

## 6. Report
Write `foley/report.md`: every cue (time, frame, what), the file used (title, creator, CC0 source page), the first listen's offset and level, what you changed, and the final numbers. Say plainly that the checks are earshot measurements, not human listening, and suggest the user listens once.

## Rules
- Only CC0 sounds unless the user asks otherwise. Never use a sound without its `sources.json` row.
- Do not invent a hit you cannot see. Do not claim a sound "sounds right"; quote earshot.
- Keep the original video untouched; write `<name>-sfx.mp4`.
