%%writefile build/layer1_preguard.py

# ---- v44y pre-guard: quote at hour 21,22 what the hour-23 day-end storage guard (EXP-154) would dump ----
# The guard sells shed stock by price desc once shed+carried exceeds 99 at hour 23. Selling those lots
# a step earlier stays in the same town-consumption price window and quotes before a same-tape rival.
_PG_HOST=[v for v in list(globals().values()) if callable(v)][-1]
_Y_HOURS=(21, 22)
_Y_ITEMS=('MILK', 'STRAWBERRY', 'MELON', 'WOOL', 'TOMATO')
_Y_MIN_DAY=1
_Y_MARGIN=-6
_PG_REPORT={'preguard_turns':0,'preguard_units':0,'preguard_errors':0}

def _y_preguard(obs,action):
    step=int(obs['step'])
    if step%24 not in _Y_HOURS or step//24<_Y_MIN_DAY or step>=696:return action
    orders=[list(o) for o in (action.get('market') or [])]
    if len(orders)>=10:return action
    farm,private=_r127_fields(obs,action)
    stock,_,_=_r97_market_stock(private['shed'],orders)
    carried=sum(max(0,int(n)) for bag in private['inventories'] for n in bag.values())
    needed=sum(max(0,int(v)) for v in stock.values())+carried-99-_Y_MARGIN
    if needed<=0:return action
    prices=obs['market']['prices'];extra=[]
    for item in sorted(PRODUCTS,key=lambda it:-int(prices.get(it,0))):
        avail=max(0,int(stock.get(item,0)));qty=min(needed,avail)
        if qty<=0:continue
        if item in _Y_ITEMS and int(prices.get(item,0))>=2:extra.append(['SELL',item,qty])
        needed-=qty
        if needed<=0:break
    if not extra or len(orders)+len(extra)>10:return action
    _PG_REPORT['preguard_turns']+=1;_PG_REPORT['preguard_units']+=sum(o[2] for o in extra)
    return dict(action,market=orders+extra)

def agent_v44y_preguard(observation,configuration=None):
    action=_PG_HOST(observation,configuration)
    try:
        standard=configuration is None or all(configuration.get(k,v)==v for k,v in [('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10)])
        if standard:action=_y_preguard(observation,action)
    except Exception:_PG_REPORT['preguard_errors']+=1
    return action
agent_v44y_preguard.telemetry=_PG_REPORT

