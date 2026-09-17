#!/usr/bin/env python3
"""t76_build.py — Task 76 builder.

From the current v16.py (Task 75, comments intact, in git history):
  * v16.py        := comment-stripped v16 (same semantics, no comments/docstrings)
  * v16h5.py      := stripped v16 + H5 (1-NN conditional memory reorder, Kaito v21.1)
  * v16h7.py      := v16 with the R37 SELL-ranking key replaced by the exact
                     engine price-impact model + impact_slots mode (Kaito v43)
  * v16h57.py     := H7 patch + H5 block combined

H5 prototypes: the 30 fit-only top-30 farm signatures + sales sets extracted
from Kaito v21.1's _PROTOTYPES blob, re-encoded compactly (flat int lists) and
LZMA+base85 embedded (~52KB vs Kaito's 371KB zlib blob).

Every output is compile-checked; the stripped base is AST-verified against the
original minus docstrings.
"""
import ast
import base64
import json
import lzma
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from strip_comments import strip_source, expected_ast  # noqa: E402

V16 = os.path.join(ROOT, 'v16.py')
KAITO = os.path.join(ROOT, 'research', 'kaito_extracted', 'v211_main.py')

FUNC1_NEW = '''def _r37_quote_priority(observation, order, stock):
    item = order[1]
    quantity = min(max(0, int(order[2])), int(stock.get(item, 0) or 0))
    if not quantity or item not in _R37_MARKET_PARAMS:
        return 0.0
    market = observation['market']
    inventory = int(market['inventory'][item])
    params = {k: dict(v) for k, v in _R37_MARKET_PARAMS.items()}
    for k, patch in (market.get('params', {}) or {}).items():
        if k in params:
            params[k].update(patch)
    now = float(market['prices'].get(item, _r37_market_price(item, inventory, params)) or 0)
    later = float(_r37_market_price(item, inventory + quantity, params))
    return quantity * max(0.0, now - later)
'''

FUNC2_NEW = '''def _r37_reorder_sales(observation, action):
    stock = projected_shed(action, FarmView(observation))

    def _is(o):
        return isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL' and o[1] in _R37_MARKET_PARAMS

    market = [list(o) for o in (action.get('market') or [])]
    rows = [(_r37_quote_priority(observation, o, stock), -i, o) for i, o in enumerate(market) if _is(o)]
    if len(rows) < 2:
        return action
    rows.sort(reverse=True)
    fill = iter([row[2] for row in rows])
    orders = [next(fill) if _is(o) else o for o in market]
    if orders != market:
        _R37_STATS['quote_reordered_turns'] += 1
        action = dict(action, market=orders)
    return action
'''


def apply_h7(src):
    i1 = src.find('def _r37_quote_priority')
    i2 = src.find('def _r37_reorder_sales')
    i3 = src.find('# EXP175')
    if i3 < 0:
        i3 = src.find('_R44_PROBES')
    assert 0 < i1 < i2 < i3, (i1, i2, i3)
    return src[:i1] + FUNC1_NEW + '\n\n' + FUNC2_NEW + '\n\n' + src[i3:]


def build_blob():
    src = open(KAITO, encoding='utf-8').read()
    i = src.find('_PROTOTYPES = json.loads')
    strs = re.findall(r"'([^']*)'", src[i:])
    acc = ''
    for s in strs:
        acc += s
        try:
            import zlib
            raw = zlib.decompress(base64.b85decode(acc))
            break
        except Exception:
            continue
    protos = json.loads(raw.decode())
    items = ['WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY', 'MELON', 'EGG', 'MILK', 'WOOL', 'FERTILIZER']
    idx = {it: k for k, it in enumerate(items)}

    def enc_sig(s):
        return ([int(s['workers']), int(s['unlocks'])]
                + [int(x) for x in s['positions']]
                + [int(x) for x in s['counts']]
                + [int(x) for x in s['yields']])

    def enc_sales(sl):
        out = []
        for it, q in (sl or {}).items():
            if it in idx and int(q) > 0:
                out += [idx[it], int(q)]
        return out

    data = [[[enc_sig(s) for s in p['signatures']],
             [enc_sales(s) for s in p['sales']]] for p in protos]
    local_path = os.path.join(HERE, 't76_local_bank.json')
    n_local = 0
    if os.path.exists(local_path):
        for p in json.load(open(local_path)):
            data.append([p['sigs'], p['sales']])
            n_local += 1
    cj = json.dumps(data, separators=(',', ':'))
    blob = base64.b85encode(lzma.compress(cj.encode(), preset=9)).decode()
    return blob, len(protos) + n_local, n_local


def build_h5_block(blob):
    lines = [blob[i:i + 110] for i in range(0, len(blob), 110)]
    body = '\n'.join("    '%s'" % ln for ln in lines)
    return '''

try:
    import lzma as _lzma
except Exception:
    _lzma = None
_H5_BLOB = (
%s
)
_H5_ITEMS = ('WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY', 'MELON', 'EGG', 'MILK', 'WOOL', 'FERTILIZER')
_H5_MAX_ACTORS = 13
_H5_QUADRANTS = ('NW', 'NE', 'SW', 'SE')
_H5_CROPS = ('WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY', 'MELON')
_H5_ANIMALS = ('COW', 'SHEEP', 'GOOSE')
_H5_KINDS = ('PASTURE', 'COOP')
_H5_MAX_DISTANCE = 48.0
_H5_REPORT = dict(games=0, queries=0, abstains=0, fires=0, moves=0, errors=0)


def _h5_load():
    if _lzma is None:
        return []
    try:
        raw = json.loads(_lzma.decompress(base64.b85decode(_H5_BLOB)).decode('utf-8'))
    except Exception:
        return []
    out = []
    for sigs, sales in raw:
        ss = []
        for s in sigs:
            ss.append({'workers': s[0], 'unlocks': s[1], 'positions': s[2:28],
                       'counts': s[28:39], 'yields': s[39:47]})
        sl = []
        for s in sales:
            d = {}
            for k in range(0, len(s), 2):
                d[_H5_ITEMS[s[k]]] = s[k + 1]
            sl.append(d)
        out.append({'signatures': ss, 'sales': sl})
    return out


_H5_PROTOTYPES = _h5_load()


def _h5_position(value):
    try:
        return (int(value[0]), int(value[1]))
    except (IndexError, TypeError, ValueError):
        return (-1, -1)


def _h5_signature(farm):
    hands = list(_get(farm, 'hands', []) or [])
    unlocks = set(_get(farm, 'unlocked_quadrants', []) or [])
    positions = [_h5_position(_get(farm, 'farmer', (-1, -1)))]
    positions.extend(_h5_position(item) for item in hands)
    positions = (positions + [(-1, -1)] * _H5_MAX_ACTORS)[:_H5_MAX_ACTORS]
    counts = {key: 0 for key in (*_H5_CROPS, *_H5_ANIMALS, *_H5_KINDS, 'WEED')}
    yields = {key: 0 for key in (*_H5_CROPS, *_H5_ANIMALS)}
    for row in (_get(farm, 'tiles', []) or []):
        for tile in row if isinstance(row, list) else [row]:
            if not isinstance(tile, dict):
                continue
            crop = str(tile.get('crop', '') or '').upper()
            animal = str(tile.get('animal', '') or '').upper()
            kind = str(tile.get('kind', '') or '').upper()
            if crop in counts:
                counts[crop] += 1
                yields[crop] += max(0, int(tile.get('yield_units', 0) or 0))
            if animal in counts:
                counts[animal] += 1
                yields[animal] += max(0, int(tile.get('yield_units', 0) or 0))
            if kind in _H5_KINDS:
                counts[kind] += 1
            if kind == 'WEED':
                counts['WEED'] += 1
    return {'workers': len(hands),
            'unlocks': sum(1 << i for i, n in enumerate(_H5_QUADRANTS) if n in unlocks),
            'positions': [c for p in positions for c in p],
            'counts': [counts[k] for k in (*_H5_CROPS, *_H5_ANIMALS, *_H5_KINDS, 'WEED')],
            'yields': [yields[k] for k in (*_H5_CROPS, *_H5_ANIMALS)]}


def _h5_distance(left, right):
    total = 12.0 * abs(int(left['workers']) - int(right['workers']))
    total += 7.0 * (int(left['unlocks']) ^ int(right['unlocks'])).bit_count()
    lp = list(left['positions'])
    rp = list(right['positions'])
    for a in range(_H5_MAX_ACTORS):
        o = 2 * a
        l = lp[o:o + 2]
        r = rp[o:o + 2]
        if l == [-1, -1] and r == [-1, -1]:
            continue
        total += (0.8 if a == 0 else 0.25) * sum(abs(x - y) for x, y in zip(l, r))
    lc = list(left['counts'])
    rc = list(right['counts'])
    for i, (x, y) in enumerate(zip(lc, rc)):
        total += (0.25 if i == len(lc) - 1 else 3.0) * abs(x - y)
    total += 0.15 * sum(abs(x - y) for x, y in zip(left['yields'], right['yields']))
    return total


def _h5_reorder(observation, action):
    if not _H5_PROTOTYPES:
        return action
    step = int(observation['step'])
    market = list(action.get('market') or [])
    if len(market) < 2:
        return action
    if not any(isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL' for o in market):
        return action
    player = int(observation['player'])
    farms = list(observation.get('farms') or [])
    if len(farms) < 2:
        return action
    opponent = farms[1 - player]
    observed = _h5_signature(opponent)
    _H5_REPORT['queries'] += 1
    best = None
    bi = -1
    for i, p in enumerate(_H5_PROTOTYPES):
        sigs = p['signatures']
        if step >= len(sigs):
            continue
        d = _h5_distance(observed, sigs[step])
        if best is None or d < best:
            best = d
            bi = i
    if best is None or best > _H5_MAX_DISTANCE:
        _H5_REPORT['abstains'] += 1
        return action
    sales = _H5_PROTOTYPES[bi]['sales']
    pred = sales[step] if step < len(sales) else {}
    collided = [(-oi, o) for oi, o in enumerate(market)
                if isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL' and o[1] in pred]
    if not collided:
        return action
    collided.sort(reverse=True)
    ids = {id(r[1]) for r in collided}
    re_ = [r[1] for r in collided]
    re_.extend(o for o in market if id(o) not in ids)
    _H5_REPORT['fires'] += 1
    _H5_REPORT['moves'] += len(collided)
    return dict(action, market=re_)


_H5_PARENT = agent


def agent(observation, configuration=None):
    result = _H5_PARENT(observation, configuration)
    if not isinstance(observation, dict):
        return result
    try:
        if int(observation.get('step', 0)) == 0:
            _H5_REPORT['games'] += 1
        if isinstance(result, dict) and isinstance(result.get('market'), list):
            result = _h5_reorder(observation, result)
    except Exception:
        _H5_REPORT['errors'] += 1
    return result

agent = globals().pop('agent')
''' % body


def verify_stripped(original, stripped_text):
    compile(stripped_text, '<stripped>', 'exec')
    if ast.dump(expected_ast(original)) != ast.dump(ast.parse(stripped_text)):
        raise SystemExit('AST mismatch — stripped base rejected')


def main():
    original = open(V16, encoding='utf-8').read()
    h7_src = apply_h7(original)

    base, c1, d1 = strip_source(original)
    verify_stripped(original, base)
    h7, c2, d2 = strip_source(h7_src)
    verify_stripped(h7_src, h7)

    blob, nproto, n_local = build_blob()
    print(f'H5 blob: {len(blob)} b85 chars, {nproto} prototypes ({n_local} local + {nproto - n_local} Kaito)')
    h5_block = build_h5_block(blob)

    h5 = base + h5_block
    h57 = h7 + h5_block
    for name, text in (('v16.py', base), ('v16h5.py', h5), ('v16h7.py', h7), ('v16h57.py', h57)):
        compile(text, name, 'exec')
        open(os.path.join(ROOT, name), 'w', encoding='utf-8').write(text)
        print(f'wrote {name}: {len(text)} bytes')
    print(f'stripped base: {c1} comments + {d1} docstrings removed; '
          f'H7 base: {c2} comments + {d2} docstrings removed')
    print('all outputs compile OK')


if __name__ == '__main__':
    main()
