#!/usr/bin/env python3
"""Render VIDEO-sfx.mp4 from a plan. The picture is copied, never re-encoded.
plan = {"video": "film.mp4", "out": "film-sfx_v1.mp4", "limit": 0.9,
        "ambience": {"file", "start", "gain_db"} | null,
        "events": [{"id", "cue", "file", "trim_start", "trim_end", "sync_in_clip", "nudge", "gain_db"}]}
Each event is placed so its sync point (seconds into the trimmed clip; attack for hits, loudest point for whooshes) lands on cue + nudge."""
import json, subprocess, sys
plan = json.load(open(sys.argv[1]))
v = plan['video']
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', v], capture_output=True, text=True).stdout)
inputs, fl, labels = ['-i', v], [], []
k = 1
if plan.get('ambience'):
    a = plan['ambience']; inputs += ['-i', a['file']]
    fl.append(f"[{k}:a]atrim=start={a['start']}:duration={dur},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,volume={a['gain_db']}dB,afade=t=in:d=0.3,afade=t=out:st={max(dur - .3, 0)}:d=0.3[amb]")
    labels.append('[amb]'); k += 1
for ev in plan['events']:
    inputs += ['-i', ev['file']]
    start = ev['cue'] + ev.get('nudge', 0.0) - ev['sync_in_clip']; ts = ev['trim_start']
    if start < 0: ts -= start; start = 0.0
    length = ev['trim_end'] - ts; ms = round(start * 1000)
    fl.append(f"[{k}:a]atrim=start={ts}:end={ev['trim_end']},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,volume={ev['gain_db']}dB,afade=t=out:st={max(length - .03, 0)}:d=0.03,adelay={ms}:all=1[e{k}]")
    labels.append(f'[e{k}]'); print(f"{ev['id']:<10} cue {ev['cue']:.3f}  starts {start:.3f}  gain {ev['gain_db']:+.1f} dB"); k += 1
fl.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{dur},alimiter=limit={plan.get('limit', 0.9)}:level=0[aout]")
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(fl), '-map', '0:v', '-map', '[aout]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', str(dur), plan['out']], check=True)
print('wrote', plan['out'])
