#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Загрузка дневной истории по всем бумагам портфеля из ISS Мосбиржи."""
import urllib.request, json, os, time
os.chdir(os.path.dirname(os.path.abspath(__file__)))

TICK = ("SBER YDEX T X5 GAZP LKOH MOEX TRNFP OZON GMKN MSRS SIBN PHOR BANEP MTSS "
        "FESH MRKU NLMK FEES PLZL AFLT VTBR PMSB MVID MTLRP").split()

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=25))

def fetch(sec, market='shares', board='TQBR'):
    out = []
    start = 0
    while True:
        u = (f'https://iss.moex.com/iss/history/engines/stock/markets/{market}/securities/{sec}.json'
             f'?from=2025-01-01&till=2026-10-18&iss.meta=off&board={board}&start={start}')
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

json.dump(res, open('stock_data.json', 'w'))
print('saved stock_data.json', os.path.getsize('stock_data.json'))
