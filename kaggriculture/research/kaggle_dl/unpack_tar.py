#!/usr/bin/env python3
"""Extract main.py from tar.gz-style packed submissions (pilkwang, lynnsakurai, reyhanksatria)."""
import base64, io, json, re, tarfile, zlib
from pathlib import Path

DL = Path('/home/z/my-project/kaggriculture/research/kaggle_dl')
OUT = DL / 'unpacked'
OUT.mkdir(exist_ok=True)

for fname in ['pilkwang__kaggriculture-structured-economic-policy.py',
              'lynnsakurai__farming-score-v3-replay-revised.py',
              'reyhanksatria__kaggriculture-dynamic-route-agent.py']:
    src = (DL / fname).read_text(errors='replace')
    tag = fname.split('__')[0]
    # Pattern A: PAYLOAD = '<b64>' with b64decode + gzip/zlib
    m = re.search(r"PAYLOAD\s*=\s*'([A-Za-z0-9+/=]+)'", src)
    if not m:
        m = re.search(r"PAYLOAD\s*=\s*'([^']+)'", src)
    if not m:
        print(f'{fname}: no PAYLOAD var'); continue
    blob = m.group(1)
    raw = None
    # try b64 -> zlib/gzip
    try:
        dec = base64.b64decode(blob)
        try: raw = zlib.decompress(dec)
        except Exception: raw = dec
    except Exception:
        pass
    if raw is None:
        try:
            raw = zlib.decompress(base64.b85decode(blob))
        except Exception as e:
            print(f'{fname}: decode failed: {e}'); continue
    # it may be a tar.gz
    try:
        with tarfile.open(fileobj=io.BytesIO(raw)) as t:
            names = t.getnames()
            print(f'{fname}: tar members = {names}')
            for n in names:
                data = t.extractfile(n).read()
                out = OUT / f'{tag}__{Path(n).name}'
                out.write_bytes(data)
                print(f'  -> {out} ({len(data)} bytes, {len(data.splitlines())} lines)')
    except Exception as e:
        # maybe raw python source
        out = OUT / f'{tag}__main.py'
        out.write_bytes(raw)
        print(f'{fname}: not tar; wrote raw source -> {out} ({len(raw)} bytes)')
