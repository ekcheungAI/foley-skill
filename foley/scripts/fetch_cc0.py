#!/usr/bin/env python3
"""Search Openverse for CC0 sounds (Freesound) and download them with a source log.
usage: fetch_cc0.py "search words" OUT_DIR [--limit 8] [--max-seconds 10]"""
import json, os, re, sys, time, urllib.parse, urllib.request
q, out = sys.argv[1], sys.argv[2]
lim = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else 8
maxs = float(sys.argv[sys.argv.index('--max-seconds') + 1]) if '--max-seconds' in sys.argv else 10
os.makedirs(out, exist_ok=True)
url = 'https://api.openverse.org/v1/audio/?' + urllib.parse.urlencode({'q': q, 'license': 'cc0', 'source': 'freesound', 'page_size': lim})
d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'foley-skill/1.0'}), timeout=30))
log_path = os.path.join(os.path.dirname(out.rstrip('/')) or '.', 'sources.json')
log = json.load(open(log_path)) if os.path.exists(log_path) else []
n = 0
for r in d.get('results', []):
    if r.get('license') != 'cc0' or r.get('source') != 'freesound':
        continue
    if r.get('duration') and r['duration'] / 1000 > maxs and 'amb' not in out:
        continue
    slug = re.sub(r'[^A-Za-z0-9]+', '_', r['title']).strip('_')[:40]
    path = os.path.join(out, f"{r['id'][:8]}_{slug}.{(r.get('filetype') or 'mp3').lower()}")
    if not os.path.exists(path):
        try:
            with urllib.request.urlopen(urllib.request.Request(r['url'], headers={'User-Agent': 'foley-skill/1.0'}), timeout=60) as s, open(path, 'wb') as f:
                f.write(s.read())
        except Exception as e:
            print('skip', r['title'], e); continue
        time.sleep(.4)
    log.append({'file': path, 'query': q, 'title': r['title'], 'creator': r.get('creator'), 'license': 'CC0 ' + str(r.get('license_version') or ''),
                'source_page': r.get('foreign_landing_url'), 'openverse_id': r['id']})
    n += 1; print('ok', path)
json.dump(log, open(log_path, 'w'), ensure_ascii=False, indent=1)
print(f'{n} CC0 files for "{q}" (Openverse found {d.get("result_count")}); sources -> {log_path}')
