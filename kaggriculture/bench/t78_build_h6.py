import sys, py_compile

root = sys.argv[1] if len(sys.argv) > 1 else "."
SRC = root + "/v16h8.py"

TAIL = """_H6_STATE={{'done':{{0:False,1:False}}}}
_H6_REPORT={{'dumps':0,'units':0,'giveups':0}}
def _h6_watchdog(obs,action):
    try:
        if not isinstance(obs,dict) or not isinstance(action,dict):return action
        seat=int(obs.get('player',0) or 0);step=int(obs.get('step',0) or 0)
        if step==0:
            _H6_STATE['done'][seat]=False
            return action
        if _H6_STATE['done'][seat] or not ({LO}<={"step"}<= {HI}):return action
        shed=int(_get(_get(_get(obs,'private',{{}}),'shed',{{}}) or {{}},'CARROT',0) or 0)
        if shed<=0:
            _H6_STATE['done'][seat]=True;_H6_REPORT['giveups']+=1
            return action
        px=float((_get(_get(obs,'market',{{}}),'prices',{{}}) or {{}}).get('CARROT',0) or 0)
        if px<=54.0:
            return action
        market=[list(o) for o in (action.get('market') or [])]
        if len(market)>=10:return action
        market.append(['SELL','CARROT',shed])
        action['market']=market
        _H6_STATE['done'][seat]=True
        _H6_REPORT['dumps']+=1;_H6_REPORT['units']+=shed
    except Exception:
        pass
    return action
_H6_PARENT=agent
def agent(observation,configuration=None):
    result=_H6_PARENT(observation,configuration)
    if not isinstance(observation,dict):return result
    return _h6_watchdog(observation,result)
agent=globals().pop('agent')
"""

tail = TAIL.replace('{"step"}', 'step').format(LO=217 - 217 + 570, HI=575)
open(root + "/v16h6.py", "w").write(open(SRC).read().rstrip("\n") + "\n\n" + tail)
py_compile.compile(root + "/v16h6.py", doraise=True)
print("built v16h6.py (window 570-575)")

tail_i = TAIL.replace('{"step"}', 'step').format(LO=99990, HI=99991)
open(root + "/v16h6i.py", "w").write(open(SRC).read().rstrip("\n") + "\n\n" + tail_i)
py_compile.compile(root + "/v16h6i.py", doraise=True)
print("built v16h6i.py (inert window)")
