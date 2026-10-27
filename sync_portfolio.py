#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Автосинхронизация состава портфеля с сайтом-источником.

Тянет https://edsonssss.github.io/pf-site-1b1590de4c/portfolio_data.json и складывает
нормализованный снимок в portfolio_sync.json: количества, рекомендации, целевые цены,
дивиденды, фонды, кэш, заблокированные активы. Рыночные цены сюда НЕ входят —
их отдельно качает fetch_stocks.py с ISS Мосбиржи.
"""
import json, os, time, urllib.request
os.chdir(os.path.dirname(os.path.abspath(__file__)))

SRC = 'https://edsonssss.github.io/pf-site-1b1590de4c/portfolio_data.json'

def get(url, tries=4):
    last = None
    for att in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            last = e
            time.sleep(2 + 3*att)
    raise last

d = get(SRC)
out = {
    'src_date': d.get('meta', {}).get('date'),
    'src_prices_note': d.get('meta', {}).get('sources', {}).get('prices'),
    'stocks': [],
    'funds': [],
    'cash': d.get('cash') or {},
    'blocked': d.get('blocked') or [],
    'family': d.get('family') or {},
    'summary': d.get('summary') or {},
}
for st in d.get('stocks', []):
    out['stocks'].append({
        'ticker': st.get('ticker'), 'name': st.get('name'), 'qty': st.get('qty'),
        'current_price': st.get('current_price'), 'value': st.get('value'),
        'rec': st.get('recommendation'), 'target': st.get('target_price'),
        'upside': st.get('upside_pct'), 'range_min': st.get('range_min'), 'range_max': st.get('range_max'),
        'div_next': st.get('dividend_next'), 'div_date': st.get('dividend_date'),
        'div_status': st.get('dividend_status'), 'dy': st.get('div_yield_12m_pct'),
        'note': st.get('note'),
    })
for f in d.get('funds', []):
    perf = f.get('performance_pct') or {}
    out['funds'].append({
        'name': f.get('name'), 'manager': f.get('manager'), 'type': f.get('type'),
        'qty': f.get('qty'), 'nav': f.get('current_nav'), 'value': f.get('value'),
        'm1': perf.get('m1'), 'm3': perf.get('m3'), 'm6': perf.get('m6'), 'y1': perf.get('y1'),
        'nav_date': f.get('nav_date'), 'forecast': f.get('forecast'),
    })

prev = {}
if os.path.exists('portfolio_sync.json'):
    try:
        prev = {s['ticker']: s for s in json.load(open('portfolio_sync.json')).get('stocks', [])}
    except Exception:
        prev = {}
changed = []
for s in out['stocks']:
    p = prev.get(s['ticker'])
    if p is None:
        changed.append(f"+{s['ticker']}")
    elif (p.get('qty') or 0) != (s.get('qty') or 0) or p.get('target') != s.get('target'):
        changed.append(f"{s['ticker']}: {p.get('qty')}→{s.get('qty')} шт"
                       + (f", цель {p.get('target')}→{s.get('target')}" if p.get('target') != s.get('target') else ''))
for t in prev:
    if t not in {s['ticker'] for s in out['stocks']}:
        changed.append(f"-{t}")

json.dump(out, open('portfolio_sync.json', 'w'), ensure_ascii=False, indent=1)
print(f"синхронизировано: {len(out['stocks'])} акций, {len(out['funds'])} фондов, "
      f"кэш {out['cash'].get('value')}, дата источника {out['src_date']}")
print('изменения к прошлому снимку:', '; '.join(changed) if changed else 'нет')
