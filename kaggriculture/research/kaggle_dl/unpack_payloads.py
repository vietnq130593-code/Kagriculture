#!/usr/bin/env python3
"""Unpack Base85+zlib packed agent payloads from kaggle_dl notebooks (Task 74-e)."""
import base64, json, re, sys, zlib
from pathlib import Path

DL = Path('/home/z/my-project/kaggriculture/research/kaggle_dl')
OUT = Path('/home/z/my-project/kaggriculture/research/kaggle_dl/unpacked')
OUT.mkdir(exist_ok=True)

files = [
    'guruprasaathas111__kaggriculture-master-engine-v3.py',
    'pilkwang__kaggriculture-structured-economic-policy.py',
    'reyhanksatria__kaggriculture-dynamic-route-agent.py',
    'lynnsakurai__farming-score-v3-replay-revised.py',
]

for fname in files:
    src = (DL / fname).read_text(errors='replace')
    # find b85 payload(s): _X=json.loads(zlib.decompress(base64.b85decode('...')))
    matches = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*json\.loads\(zlib\.decompress\(base64\.b85decode\('([^']+)'\)\)\)", src)
    if not matches:
        # try raw b85 decode of long quoted strings near "b85decode"
        print(f"{fname}: NO b85-json payload pattern found")
        continue
    tag = fname.split('__')[0]
    for i, (var, blob) in enumerate(matches):
        try:
            data = json.loads(zlib.decompress(base64.b85decode(blob)))
            outname = OUT / f"{tag}_payload{i}.json"
            outname.write_text(json.dumps(data, indent=1)[:8_000_000])
            print(f"{fname}: var={var} -> {outname} ({len(blob)} b85 chars, json keys={list(data)[:8] if isinstance(data, dict) else type(data).__name__})")
        except Exception as e:
            print(f"{fname}: var={var} FAILED: {e}")
