#!/usr/bin/env python3
"""Pull episodes + agent logs for submission 56386175 (v27.2) from Kaggle."""
import json, os, sys, urllib.request

TOKEN = open(os.path.expanduser('~/.kaggle/access_token')).read().strip()
BASE = 'https://www.kaggle.com/api/v1'
HDRS = {'Authorization': f'Bearer {TOKEN}'}
SUB_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 56386175

def get(path):
    req = urllib.request.Request(BASE + path, headers=HDRS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

def main():
    raw = get(f'/competitions/submissions/{SUB_ID}/episodes')
    data = json.loads(raw)
    eps = data.get('episodes', data if isinstance(data, list) else [])
    print(f'== {len(eps)} episodes for submission {SUB_ID} ==')
    out = '/home/z/my-project/kaggriculture/bench/t112_sub_debug/eps'
    os.makedirs(out, exist_ok=True)
    for e in eps:
        print(json.dumps(e, default=str)[:500])
    with open(out + '/episodes.json', 'w') as f:
        json.dump(data, f, indent=1, default=str)
    n = 0
    for e in eps[:2]:
        eid = e.get('id') or e.get('episode_id') or e.get('EpisodeId')
        if not eid:
            continue
        n += 1
        try:
            rep = get(f'/competitions/episodes/{eid}/replay')
            open(f'{out}/replay_{eid}.json', 'wb').write(rep)
            print(f'replay {eid}: {len(rep)} bytes')
        except Exception as ex:
            print(f'replay {eid} FAIL: {ex}')
        for idx in (0, 1):
            try:
                log = get(f'/competitions/episodes/{eid}/agents/{idx}/logs')
                open(f'{out}/logs_{eid}_{idx}.txt', 'wb').write(log)
                print(f'logs {eid}/{idx}: {len(log)} bytes')
            except Exception as ex:
                print(f'logs {eid}/{idx} FAIL: {ex}')
    print('saved replays+logs:', n)

if __name__ == '__main__':
    main()
