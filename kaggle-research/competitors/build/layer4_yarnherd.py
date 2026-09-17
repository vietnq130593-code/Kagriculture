
# ==== v44y shop-aware herd wrapper (appended after the public V44 file; host entry captured first) ====
_Y_HOST=[v for v in list(globals().values()) if callable(v)][-1]
_Y_CFG={'yarnsheep': True, 'yarngeese': True, 'days': (8, 11)}
import copy as _y_copy
_Y_PRODUCT={'COW':'MILK','SHEEP':'WOOL','GOOSE':'EGG'}
_Y_STRUCT={'COW':'PASTURE','SHEEP':'PASTURE','GOOSE':'COOP'}
_Y_COST={'COW':400,'SHEEP':500,'GOOSE':300}
_Y_SEED={'WHEAT':10,'CARROT':20,'TOMATO':50,'STRAWBERRY':100,'MELON':80}
_Y_STATES={}
_Y_REPORT={'swaps':0,'pick':0,'place':0,'harvest':0,'boost':0,'errors':0,'coop':0,'declined':0}

def _y_new_state():
    return {'last':-1,'pending':[],'credit':{},'sites':{},'sale':{},'coop_swap':0}

def _y_target(kind,shops,cfg):
    yarn='YARN_STORE' in shops
    egg=('BAKERY' in shops) or ('BRUNCH_SPOT' in shops)
    milk=sum(s in ('PIZZA_SHOP','ICE_CREAM_SHOP','SMOOTHIE_SHOP') for s in shops)
    if kind=='SHEEP' and cfg.get('nosheep') and not yarn and milk>=cfg.get('min_milk',0):return 'COW'
    if kind=='COW' and cfg.get('yarnsheep') and yarn:return 'SHEEP'
    if kind=='GOOSE' and cfg.get('nogeese') and not egg:return 'SHEEP' if yarn else 'COW'
    if kind=='GOOSE' and cfg.get('yarngeese') and yarn:return 'SHEEP'
    return None

def _y_fib(n):
    a,b=1,1
    for _ in range(n):a,b=b,a+b
    return a

def _y_cash(obs,action,market):
    farm=obs['farms'][int(obs['player'])];prices=obs['market']['prices'];shed=obs['private']['shed']
    try:shed=projected_shed({'farmer':action.get('farmer') or ['PASS'],'hands':action.get('hands') or [],'market':[]},FarmView(obs))
    except Exception:pass
    cash=float(farm['money']);cost=0.0;hires=int(farm.get('hires_today',0) or 0)
    quads=len(farm.get('unlocked_quadrants',[]) or [])
    for o in market:
        if not o:continue
        op=o[0]
        if op=='SELL' and len(o)>=3:
            cash+=0.8*min(max(0,int(o[2])),int(shed.get(o[1],0)))*float(prices.get(o[1],0))
        elif op=='BUY_ANIMAL' and len(o)>=3:cost+=int(o[2])*_Y_COST.get(o[1],500)
        elif op=='BUY_PRODUCT' and len(o)>=3:cost+=int(o[2])*(float(prices.get(o[1],0))+10)
        elif op=='BUY_SEED' and len(o)>=3:cost+=int(o[2])*_Y_SEED.get(o[1],100)
        elif op=='BUY_LAND':cost+=(1000,2000,4000)[min(2,max(0,quads-1))]
        elif op=='HIRE':cost+=_y_fib(hires);hires+=1
    return cash-cost

def _y_controller(obs,action,state,cfg):
    step=int(obs['step']);day=step//24;seat=int(obs['player'])
    farm=obs['farms'][seat];private=obs['private'];shed=private['shed'];inventories=private.get('inventories',[])
    shops=list((obs.get('town') or {}).get('unlocked_shops',[]) or [])
    tiles=farm['tiles'];n=len(tiles);center=n//2
    # 1. confirm last step's swapped purchases (physical shed gain)
    gained={}
    for p in state['pending']:
        to=p['to']
        if to not in gained:gained[to]=max(0,int(shed.get(to,0))-p['before'])
        got=min(p['qty'],gained[to]);gained[to]-=got
        if got>0:
            key=(p['from'],to);state['credit'][key]=state['credit'].get(key,0)+got
            if _Y_STRUCT[p['from']]!=_Y_STRUCT[to]:state['coop_swap']+=got
    state['pending']=[]
    result=_y_copy.deepcopy(action)
    market=result.get('market') or []
    result['market']=market
    # 2. purchase-point substitution by unlocked shops (cash-checked)
    if cfg['days'][0]<=day<=cfg['days'][1]:
        for o in market:
            if len(o)>=3 and o[0]=='BUY_ANIMAL' and o[1] in _Y_COST and 1<=int(o[2])<=cfg.get('maxq',2):
                to=_y_target(o[1],shops,cfg)
                if to is None or to==o[1]:continue
                trial=[list(x) if isinstance(x,list) else x for x in market]
                for t in trial:
                    if isinstance(t,list) and t==o:t[1]=to
                if _y_cash(obs,result,trial)<cfg.get('margin',100):
                    _Y_REPORT['declined']+=1;continue
                state['pending'].append({'from':o[1],'to':to,'qty':int(o[2]),'before':int(shed.get(to,0))})
                _Y_REPORT['swaps']+=int(o[2]);o[1]=to
    # 3. worker command rewrites (PICKUP / PLACE / BUILD_COOP) and harvest credit
    workers=[result.get('farmer') or ['PASS'],*(result.get('hands') or [])]
    positions=[farm['farmer'],*farm['hands']]
    avail={k:int(shed.get(k,0)) for k in _Y_COST}
    seen=set();occupied=set()
    for actor,work in enumerate(workers[:len(positions)]):
        if not work or not isinstance(work,list):continue
        inv=inventories[actor] if actor<len(inventories) else {}
        x,y=positions[actor];tile=tiles[y][x];site=(x,y);op=work[0]
        if op=='PICKUP' and len(work)>=2 and work[1] in _Y_COST:
            kind=work[1];qty=max(1,int(work[2])) if len(work)>2 else 1
            if avail.get(kind,0)>=qty:avail[kind]-=qty;continue
            if not (x in (center-1,center) and y in (center-1,center)):continue
            if any(inv.get(a,0) for a in _Y_COST):continue
            for (frm,to),c in list(state['credit'].items()):
                if frm==kind and c>=qty and avail.get(to,0)>=qty:
                    work[1]=to;state['credit'][(frm,to)]=c-qty;avail[to]-=qty;_Y_REPORT['pick']+=qty;break
        elif op=='PLACE' and len(work)>=2 and work[1] in _Y_COST:
            kind=work[1]
            if inv.get(kind,0)>0:continue
            for to in ('COW','SHEEP','GOOSE'):
                if (to!=kind and inv.get(to,0)>0 and isinstance(tile,dict) and tile.get('kind')==_Y_STRUCT[to]
                        and not tile.get('animal') and site not in occupied):
                    work[1]=to;state['sites'][site]=to;occupied.add(site);_Y_REPORT['place']+=1;break
        elif op=='BUILD_COOP' and state['coop_swap']>0:
            work[0]='BUILD_PASTURE';_Y_REPORT['coop']+=1
        elif op=='HARVEST' and site in state['sites'] and site not in seen:
            if isinstance(tile,dict) and tile.get('animal')==state['sites'][site]:
                units=max(0,int(tile.get('yield_units',0) or 0))
                if units:
                    prod=_Y_PRODUCT[tile['animal']];state['sale'][prod]=state['sale'].get(prod,0)+units;_Y_REPORT['harvest']+=units
            seen.add(site)
    result['farmer'],result['hands']=workers[0],workers[1:]
    # 4. sell the extra production at the tape's own existing sale slots (never add new orders)
    if cfg.get('boost',True):
        for prod,credit in list(state['sale'].items()):
            credit=min(credit,int(shed.get(prod,0)))
            state['sale'][prod]=credit
            if credit<=0:continue
            planned=sum(max(0,int(o[2])) for o in market if len(o)>=3 and o[0]=='SELL' and o[1]==prod)
            if planned<=0:continue
            extra=min(credit,int(shed.get(prod,0))-planned)
            if extra<=0:continue
            for o in market:
                if len(o)>=3 and o[0]=='SELL' and o[1]==prod and int(o[2])>0:
                    o[2]=int(o[2])+extra;state['sale'][prod]=credit-extra;_Y_REPORT['boost']+=extra;break
    return result

def _y_agent_shopherd(observation,configuration=None):
    action=_Y_HOST(observation,configuration)
    try:
        seat=int(observation['player']);step=int(observation['step'])
        state=_Y_STATES.get(seat)
        if state is None or step<=state['last']:state=_Y_STATES[seat]=_y_new_state()
        state['last']=step
        return _y_controller(observation,action,state,_Y_CFG)
    except Exception:
        _Y_REPORT['errors']+=1
        return action
