#!/usr/bin/env python3
"""t78_build.py — v2: H8 spend-detector overlay = horizon-2 front-run pass.

v1 (uncap own_next) was a no-op in mirror matches (own_next == opp qty).
v2 keeps the detector; the overlay adds a SECOND pass in Chassis._front_run:
when the flag is on, also front-run premium items the opponent is predicted
to sell at step+2 (capped by our own step+2 scheduled qty, all gates kept,
no suppression entry — stock clamping at step+2 replaces the pulled units).

v16h8i = identical file with trigger window (9999,) — inertness control.
"""
ROOT = "/home/z/my-project/kaggriculture"
SRC = f"{ROOT}/v16.py"

ANCHOR = """            next_sup["suppress"][item] = next_sup["suppress"].get(item, 0) + qty
        if next_sup["suppress"]:
            next_sup["due_step"] = nxt

    def _block_requirements(self, view, route, start, end):"""

PASS2 = """            next_sup["suppress"][item] = next_sup["suppress"].get(item, 0) + qty
        if _H8_STATE['active']:
            far = nxt + 1
            if far <= LAST_ACT_STEP and far < len(plan) and isinstance(plan[far], dict):
                tape2 = self.routes[route]
                if far < len(tape2) and isinstance(tape2[far], dict):
                    for o in plan[far].get("market") or []:
                        if not (o and o[0] == "SELL" and len(o) >= 3 and o[1] in FRONT_RUN_ITEMS):
                            continue
                        item = o[1]
                        if item in already or view.prices.get(item, 0) < cfg["min_sell_price"]:
                            continue
                        if _town_demand_now(view.shops, item, step) > 0:
                            continue
                        own2 = sum(max(0, _int(x[2])) for x in tape2[far].get("market", [])
                                   if len(x) >= 3 and x[0] == "SELL" and x[1] == item)
                        qty = min(projected.get(item, 0), max(0, _int(o[2])), own2)
                        if qty <= 0:
                            continue
                        if not self._add_sell(action, item, qty, cfg["max_orders"], merge=False):
                            continue
                        projected[item] -= qty
                        already.add(item)
                        _H8_REPORT['extra_units'] += qty
        if next_sup["suppress"]:
            next_sup["due_step"] = nxt

    def _block_requirements(self, view, route, start, end):"""

TAIL = """_H8_STATE={'prev':{0:None,1:None},'on':{0:False,1:False},'active':False}
_H8_REPORT={'triggered':{0:0,1:0},'extra_units':0}
def _h8_sync(obs):
    try:
        if not isinstance(obs,dict):return
        seat=int(obs.get('player',0) or 0);step=int(obs.get('step',0) or 0)
        if step==0:
            _H8_STATE['prev'][seat]=None;_H8_STATE['on'][seat]=False;_H8_STATE['active']=False
            return
        farms=obs.get('farms') or []
        opp=_get(farms[1-seat],'money') if len(farms)>=2 and isinstance(farms[1-seat],dict) else None
        prev=_H8_STATE['prev'][seat]
        if opp is not None:
            if prev is not None and step in {WINDOW} and prev-float(opp)>=100 and not _H8_STATE['on'][seat]:
                _H8_STATE['on'][seat]=True
                _H8_REPORT['triggered'][seat]+=1
            _H8_STATE['prev'][seat]=float(opp)
        _H8_STATE['active']=_H8_STATE['on'][seat]
    except Exception:
        pass
_H8_PARENT=agent
def agent(observation,configuration=None):
    _h8_sync(observation)
    return _H8_PARENT(observation,configuration)
agent=globals().pop('agent')
"""


def build(window, out):
    src = open(SRC).read()
    assert src.count(ANCHOR) == 1, f"anchor count = {src.count(ANCHOR)}"
    patched = src.replace(ANCHOR, PASS2)
    tail = TAIL.replace("{WINDOW}", repr(window))
    patched = patched.rstrip("\n") + "\n\n" + tail
    open(f"{ROOT}/{out}", "w").write(patched)
    import py_compile
    py_compile.compile(f"{ROOT}/{out}", doraise=True)
    print(f"built {out}: window={window}, {len(patched)} bytes")


if __name__ == "__main__":
    build((217, 218, 219), "v16h8.py")
    build((9999,), "v16h8i.py")
