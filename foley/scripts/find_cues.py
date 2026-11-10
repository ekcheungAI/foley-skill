#!/usr/bin/env python3
"""Motion peaks + contact sheets to help pick sound cues.
usage: find_cues.py VIDEO [--out foley/cues-candidates.json]"""
import json, os, subprocess, sys
v = sys.argv[1]; out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else 'foley/cues-candidates.json'
d = os.path.dirname(out) or '.'; os.makedirs(os.path.join(d, 'sheets'), exist_ok=True)
probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate,nb_frames:format=duration', '-of', 'json', v], capture_output=True, text=True).stdout)
num, den = map(int, probe['streams'][0]['r_frame_rate'].split('/')); fps = num / den; dur = float(probe['format']['duration'])
txt = subprocess.run(['ffmpeg', '-v', 'error', '-i', v, '-vf', 'scale=320:-1,format=gray,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-', '-f', 'null', '-'], capture_output=True, text=True).stdout
vals = [float(l.split('=')[1]) for l in txt.splitlines() if 'YAVG' in l]
peaks = []
for i in range(2, len(vals) - 2):
    if vals[i] == max(vals[i - 2:i + 3]) and vals[i] > sorted(vals)[int(len(vals) * .75)]:
        peaks.append({'frame': i + 1, 't': round((i + 1) / fps, 3), 'motion': round(vals[i], 2)})
per = 32
for k in range(0, int(dur * fps) + 1, per):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-vf', f"select='between(n\\,{k}\\,{k + per - 1})',scale=240:-1,tile=8x4", '-frames:v', '1', os.path.join(d, 'sheets', f'frames_{k:05d}-{k + per - 1:05d}.png')], capture_output=True)
json.dump({'fps': fps, 'duration': dur, 'motion_peaks': peaks}, open(out, 'w'), indent=1)
print(f'{len(peaks)} motion peaks at fps {fps:.3f}:', ', '.join(f"{p['t']}s(f{p['frame']})" for p in peaks))
print('contact sheets (8x4 tiles, left-to-right then down; the file name gives the frame range):', os.path.join(d, 'sheets'))
