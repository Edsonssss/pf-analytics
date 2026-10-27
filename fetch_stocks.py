import datetime
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Загрузка дневной истории по всем бумагам портфеля из ISS Мосбиржи."""
import urllib.request, json, os, time, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))

TICK = ("SBER YDEX T X5 GAZP LKOH MOEX TRNFP OZON GMKN MSRS SIBN PHOR BANEP MTSS "
        "FESH MRKU NLMK FEES PLZL AFLT VTBR PMSB MVID MTLRP").split()

def get(url, tries=5):
    last = None
    for att in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            last = e
            time.sleep(2 + 3*att)
    raise last

def fetch(sec, market='shares', board='TQBR'):
    out = []
    start = 0
    import datetime as _d
    FROM = (_d.date.today() - _d.timedelta(days=660)).isoformat()
    TILL = (_d.date.today() + _d.timedelta(days=2)).isoformat()
    while True:
        u = (f'https://iss.moex.com/iss/history/engines/stock/markets/{market}/securities/{sec}.json'
             f'?from={FROM}&till={TILL}&iss.meta=off&board={board}&start={start}')
        d = get(u)
        h = d['history']
        cols = h['columns']
        i = {c: n for n, c in enumerate(cols)}
        data = h['data']
        if not data:
            break
        for r in data:
            close = r[i['CLOSE']] or r[i['LEGALCLOSEPRICE']] or r[i['WAPRICE']]
            if close is None:
                continue
            out.append({'date': r[i['TRADEDATE']], 'o': r[i['OPEN']], 'h': r[i['HIGH']],
                        'l': r[i['LOW']], 'c': close, 'v': r[i['VALUE']] or 0,
                        'n': r[i['NUMTRADES']] or 0})
        if len(data) < 100:
            break
        start += len(data)
        if start > 3000:
            break
    # дедуп по дате
    seen = {}
    for r in out:
        seen[r['date']] = r
    return [seen[k] for k in sorted(seen)]

def fetch_index(sec='IMOEX'):
    """дневная история индекса МосБиржи"""
    import datetime as _d
    out = []
    start = 0
    _f = (_d.date.today() - _d.timedelta(days=660)).isoformat()
    _t = (_d.date.today() + _d.timedelta(days=2)).isoformat()
    while True:
        u = (f'https://iss.moex.com/iss/history/engines/stock/markets/index/securities/{sec}.json'
             f'?from={_f}&till={_t}&iss.meta=off&start={start}')
        d = get(u)
        h = d['history']; cols = h['columns']; i = {c: n for n, c in enumerate(cols)}
        data = h['data']
        if not data: break
        for r in data:
            close = r[i['CLOSE']]
            if close is None: continue
            out.append({'date': r[i['TRADEDATE']], 'o': r[i['OPEN']], 'h': r[i['HIGH']],
                        'l': r[i['LOW']], 'c': close, 'v': r[i['VALUE']] or 0, 'n': 0})
        if len(data) < 100: break
        start += len(data)
    seen = {}
    for r in out: seen[r['date']] = r
    return [seen[k] for k in sorted(seen)]

res = {}
for t in TICK:
    try:
        rows = fetch(t)
        res[t] = rows
        print(f'{t:7s} {len(rows):4d} сессий  {rows[0]["date"] if rows else "-"} .. {rows[-1]["date"] if rows else "-"}  close={rows[-1]["c"] if rows else "-"}', flush=True)
    except Exception as e:
        res[t] = {'error': str(e)}
        print(f'{t:7s} ERROR {e}', flush=True)
    time.sleep(0.03)

# повторная попытка для упавших тикеров (важно в CI)
for t in [k for k, v in res.items() if isinstance(v, dict)]:
    for att in range(3):
        try:
            rows = fetch(t)
            res[t] = rows
            print(f'{t:7s} retry ok: {len(rows)} сессий', flush=True)
            break
        except Exception as e:
            print(f'{t:7s} retry {att+1} fail: {e}', flush=True)
            time.sleep(5)
bad = [k for k, v in res.items() if isinstance(v, dict)]
if bad:
    print('НЕ ЗАГРУЖЕНО:', bad, flush=True)
    sys.exit(1)

# ---------- наблюдаемые инструменты (watchlist), например фьючерсы ----------
WATCH = {
    'GOLD': dict(pattern='GOLD-', name='Фьючерс на золото (MOEX FORTS)'),
}

def resolve_futures(pattern):
    d = get('https://iss.moex.com/iss/engines/futures/markets/forts/securities.json?iss.meta=off&iss.only=securities')
    cols = d['securities']['columns']; i = {c: n for n, c in enumerate(cols)}
    today = datetime.date.today().isoformat()
    cands = [r for r in d['securities']['data']
             if str(r[i['SHORTNAME']]).upper().startswith(pattern) and str(r[i['LASTTRADEDATE']]) >= today]
    if not cands:
        raise RuntimeError('нет активного контракта ' + pattern)
    r = min(cands, key=lambda x: str(x[i['LASTTRADEDATE']]))
    return {c: r[i[c]] for c in ('SECID', 'SHORTNAME', 'LASTTRADEDATE', 'DECIMALS', 'INITIALMARGIN', 'STEPPRICE', 'PREVPRICE') if c in i}

def fetch_futures(secid):
    out = []
    start = 0
    import datetime as _d
    FROM = (_d.date.today() - _d.timedelta(days=660)).isoformat()
    TILL = (_d.date.today() + _d.timedelta(days=2)).isoformat()
    while True:
        u = (f'https://iss.moex.com/iss/history/engines/futures/markets/forts/securities/{secid}.json'
             f'?from={FROM}&till={TILL}&iss.meta=off&start={start}')
        d = get(u)
        h = d['history']; cols = h['columns']; i = {c: n for n, c in enumerate(cols)}
        data = h['data']
        if not data: break
        for r in data:
            if r[i['CLOSE']] is None: continue
            out.append({'date': r[i['TRADEDATE']], 'o': r[i['OPEN']], 'h': r[i['HIGH']],
                        'l': r[i['LOW']], 'c': r[i['CLOSE']], 'v': r[i['VALUE']] or 0,
                        'n': r[i['NUMTRADES']] or 0})
        if len(data) < 100: break
        start += len(data)
    seen = {}
    for r in out: seen[r['date']] = r
    return [seen[k] for k in sorted(seen)]

watch_meta = {}
for wt, w in WATCH.items():
    try:
        meta = resolve_futures(w['pattern'])
        rows = fetch_futures(meta['SECID'])
        res[wt] = rows
        watch_meta[wt] = {**meta, 'name': w['name']}
        print(f'{wt:7s} {len(rows):4d} сессий  контракт {meta["SECID"]} ({meta["SHORTNAME"]}) до {meta["LASTTRADEDATE"]}  close={rows[-1]["c"]}', flush=True)
    except Exception as e:
        res[wt] = {'error': str(e)}
        print(f'{wt:7s} ERROR {e}', flush=True)
if watch_meta:
    json.dump(watch_meta, open('watch_meta.json', 'w'), ensure_ascii=False, indent=1)

# индекс — отдельной загрузкой (другой рынок в ISS)
try:
    idx = fetch_index('IMOEX')
    res['IMOEX'] = idx
    print(f'{"IMOEX":7s} {len(idx):4d} сессий  {idx[0]["date"]} .. {idx[-1]["date"]}  close={idx[-1]["c"]}', flush=True)
except Exception as e:
    print('IMOEX ERROR', e, flush=True)

json.dump(res, open('stock_data.json', 'w'))
print('saved stock_data.json', os.path.getsize('stock_data.json'))

# imoex_series.json (daily + weekly) — для ta_engine и недельного графика
if 'IMOEX' in res:
    import datetime as _dt
    daily = res['IMOEX']
    wk = {}
    for r in daily:
        d = _dt.date.fromisoformat(r['date'])
        key = (d - _dt.timedelta(days=d.weekday())).isoformat()
        if key not in wk:
            wk[key] = {'date': key, 'o': r['o'], 'h': r['h'], 'l': r['l'], 'c': r['c'], 'v': r['v']}
        else:
            w = wk[key]
            w['h'] = max(w['h'], r['h']); w['l'] = min(w['l'], r['l']); w['c'] = r['c']; w['v'] += r['v']
    weekly = [wk[k] for k in sorted(wk)]
    json.dump({'daily': daily, 'weekly': weekly}, open('imoex_series.json', 'w'))
    print('saved imoex_series.json', len(daily), 'daily /', len(weekly), 'weekly')
