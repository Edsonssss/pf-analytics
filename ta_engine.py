#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Расчёт технических индикаторов и уровней по каждой бумаге портфеля."""
import json, os, statistics, datetime, html
os.chdir(os.path.dirname(os.path.abspath(__file__)))

DATA = json.load(open('stock_data.json'))
IDX = json.load(open('imoex_series.json'))

# ---------------- базовые индикаторы ----------------
def sma(a, n):
    return [sum(a[i-n+1:i+1])/n if i >= n-1 else None for i in range(len(a))]

def ema(a, n):
    if len(a) < n: return [None]*len(a)
    k = 2/(n+1); e = sum(a[:n])/n
    out = [None]*(n-1) + [e]
    for x in a[n:]:
        e = x*k + e*(1-k); out.append(e)
    return out

def rsi(a, n=14):
    if len(a) < n+1: return [None]*len(a)
    out = [None]*n
    g = [max(a[i]-a[i-1], 0) for i in range(1, len(a))]
    l = [max(a[i-1]-a[i], 0) for i in range(1, len(a))]
    ag = sum(g[:n])/n; al = sum(l[:n])/n
    out.append(100 - 100/(1+ag/al) if al else 100)
    for i in range(n, len(g)):
        ag = (ag*(n-1)+g[i])/n; al = (al*(n-1)+l[i])/n
        out.append(100 - 100/(1+ag/al) if al else 100)
    return out

def stoch(h, l, c, n=14, k=3, d=3):
    out = [None]*len(c)
    for i in range(n-1, len(c)):
        hh = max(h[i-n+1:i+1]); ll = min(l[i-n+1:i+1])
        out[i] = 100*(c[i]-ll)/(hh-ll) if hh != ll else 50
    ks = [None]*len(c)
    for i in range(k-1, len(out)):
        w = [x for x in out[i-k+1:i+1] if x is not None]
        if len(w) == k: ks[i] = sum(w)/k
    ds = [None]*len(c)
    for i in range(len(ks)):
        w = [x for x in ks[i-d+1:i+1] if x is not None]
        if len(w) == d: ds[i] = sum(w)/d
    return out, ks, ds

def atr(h, l, c, n=14):
    out = [None]*len(c)
    trs = []
    for i in range(1, len(c)):
        trs.append(max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1])))
    if len(trs) < n: return out
    a = sum(trs[:n])/n
    out[n] = a
    for i in range(n, len(trs)):
        a = (a*(n-1)+trs[i])/n
        out[i+1] = a
    return out

def macd(c, f=12, s=26, sig=9):
    ef, es = ema(c, f), ema(c, s)
    m = [ef[i]-es[i] if (ef[i] is not None and es[i] is not None) else None for i in range(len(c))]
    vals = [x for x in m if x is not None]
    sg = ema(vals, sig)
    off = len(m)-len(sg)
    out = [None]*len(m)
    for i, v in enumerate(sg): out[off+i] = v
    hist = [m[i]-out[i] if (m[i] is not None and out[i] is not None) else None for i in range(len(m))]
    return m, out, hist

def ichimoku(h, l, c):
    i = len(c)-1
    if i < 51: return None
    t = (max(h[i-8:i+1])+min(l[i-8:i+1]))/2
    k = (max(h[i-25:i+1])+min(l[i-25:i+1]))/2
    a = (max(h[i-51:i+1])+min(l[i-51:i+1]))/2
    return {'tenkan': t, 'kijun': k, 'senkouA': (t+k)/2, 'senkouB': a}

# ---------------- уровни ----------------
def swings(recs, n=3, look=180):
    res, sup = [], []
    d = recs[-look:]
    for i in range(n, len(d)-n):
        if d[i]['h'] == max(x['h'] for x in d[i-n:i+n+1]): res.append((d[i]['date'], d[i]['h']))
        if d[i]['l'] == min(x['l'] for x in d[i-n:i+n+1]): sup.append((d[i]['date'], d[i]['l']))
    return res, sup

def cluster(values, tol):
    """объединяет близкие цены в кластеры, возвращает (центр, min, max, кол-во)"""
    vs = sorted(values)
    out = []
    for v in vs:
        if out and abs(v - out[-1][-1]) <= tol:
            out[-1].append(v)
        else:
            out.append([v])
    return [(sum(g)/len(g), min(g), max(g), len(g)) for g in out]

def volume_profile(recs, n=120, bins=28):
    d = recs[-n:]
    lo = min(r['l'] for r in d); hi = max(r['h'] for r in d)
    if hi <= lo: return []
    step = (hi-lo)/bins
    b = [0.0]*bins
    for r in d:
        typ = (r['h']+r['l']+r['c'])/3
        k = min(bins-1, int((typ-lo)/step))
        b[k] += r['v']
    tot = sum(b) or 1
    return [{'lo': lo+step*i, 'hi': lo+step*(i+1), 'v': b[i], 'pct': b[i]/tot*100} for i in range(bins)]

def fib_levels(lo, hi):
    return {f: lo+(hi-lo)*f for f in (0.236, 0.382, 0.5, 0.618, 0.786)}

# ---------------- анализ одной бумаги ----------------
def step_round(px):
    if px >= 1000: st = 500
    elif px >= 500: st = 100
    elif px >= 100: st = 25
    elif px >= 20: st = 10
    elif px >= 5: st = 2.5
    elif px >= 1: st = 0.5
    elif px >= 0.1: st = 0.05
    else: st = 0.005
    base = int(px/st)*st
    return [base+k*st for k in range(-3, 4)]

def nf_safe(x, d):
    return round(x, d)

def dec_for(price):
    if price >= 1000: return 1
    if price >= 100: return 2
    if price >= 10: return 2
    if price >= 1: return 3
    if price >= 0.1: return 4
    return 5

def clean(recs):
    out = []
    for r in recs:
        if r.get('c') is None: continue
        rr = dict(r)
        rr['o'] = r.get('o') or r['c']
        rr['h'] = r.get('h') or max(rr['o'], r['c'])
        rr['l'] = r.get('l') or min(rr['o'], r['c'])
        rr['v'] = r.get('v') or 0
        out.append(rr)
    return out

def adj_split(recs):
    """ретроактивная коррекция сплита/консолидации (например, T-Технологии 1:10 от 17.04.2026)"""
    facs = [1.0]*len(recs)
    for i in range(1, len(recs)):
        p, q = recs[i-1]['c'], recs[i]['c']
        if p and q and p > 0:
            ch = q/p - 1
            if ch < -0.6: f = q/p
            elif ch > 1.6: f = q/p
            else: f = None
            if f:
                for j in range(i): facs[j] *= f
    out = []
    for r, f in zip(recs, facs):
        rr = dict(r)
        for k in ('o', 'h', 'l', 'c'):
            rr[k] = r[k]*f if r[k] is not None else None
        out.append(rr)
    return out, any(abs(f-1) > 1e-9 for f in facs)

def analyze(sec, recs_raw):
    recs, split = adj_split(clean(recs_raw))
    c = [r['c'] for r in recs]; h = [r['h'] for r in recs]; l = [r['l'] for r in recs]
    last = recs[-1]; px = c[-1]; dec = dec_for(px)
    s20, s50, s200 = sma(c, 20), sma(c, 50), sma(c, 200)
    e50, e200 = ema(c, 50), ema(c, 200)
    r14 = rsi(c); m, ms, mh = macd(c)
    sd = [statistics.pstdev(c[i-19:i+1]) if i >= 19 else None for i in range(len(c))]
    bbU = [s20[i]+2*sd[i] if s20[i] else None for i in range(len(c))]
    bbL = [s20[i]-2*sd[i] if s20[i] else None for i in range(len(c))]
    at = atr(h, l, c); sk, sd_, ss_ = stoch(h, l, c)
    ich = ichimoku(h, l, c)
    i = len(c)-1
    hi52 = max(h[-250:]); lo52 = min(l[-250:])
    piv = (last['h']+last['l']+last['c'])/3
    R1, R2, R3 = 2*piv-last['l'], piv+(last['h']-last['l']), last['h']+2*(piv-last['l'])
    S1, S2, S3 = 2*piv-last['h'], piv-(last['h']-last['l']), last['l']-2*(last['h']-piv)

    vp = volume_profile(recs)
    hot = [b for b in vp if b['pct'] >= max(x['pct'] for x in vp)*0.7]
    vp_hot_pre = hot or vp[-3:]
    res_sw, sup_sw = swings(recs)
    fib_lo = min(l[-250:]); fib_hi = max(h[-250:])
    fibs = fib_levels(fib_lo, fib_hi)
    # недавние свинги (90 сессий) — более значимы
    res_sw_r = [v for d, v in res_sw if d >= recs[-90]['date']]
    sup_sw_r = [v for d, v in sup_sw if d >= recs[-90]['date']]
    step = max((hi52-lo52)/100, px*0.002)
    cands = []
    def add(v, w, src):
        if v and v > 0: cands.append((v, w, src))
    for v in res_sw_r: add(v, 3.0, 'свинг')
    for v in sup_sw_r: add(v, 3.0, 'свинг')
    for _, v in res_sw: add(v, 1.4, 'свинг')
    for _, v in sup_sw: add(v, 1.4, 'свинг')
    for x, nm in ((s20[i], 'SMA20'), (s50[i], 'SMA50'), (sma(c, 100)[i], 'SMA100'),
                  (s200[i], 'SMA200'), (e200[i], 'EMA200'), (bbU[i], 'BB верх'), (bbL[i], 'BB низ')):
        add(x, 2.0, nm)
    if ich:
        for x, nm in ((ich['tenkan'], 'Тенкан'), (ich['kijun'], 'Киджун'),
                      (ich['senkouA'], 'Сенкоу A'), (ich['senkouB'], 'Сенкоу B')):
            add(x, 1.6, nm)
    for x, nm in ((R1, 'R1 пивот'), (R2, 'R2 пивот'), (R3, 'R3 пивот'),
                  (S1, 'S1 пивот'), (S2, 'S2 пивот'), (S3, 'S3 пивот'), (piv, 'пивот')):
        add(x, 1.2, nm)
    for f, v in fibs.items(): add(v, 1.8, f'Fib {f:g}')
    add(hi52, 2.2, 'максимум 52 нед'); add(lo52, 2.2, 'минимум 52 нед')
    add(h[-60:].__iter__().__next__() and max(h[-60:]), 1.6, 'максимум 3 мес')
    add(min(l[-60:]), 1.6, 'минимум 3 мес')
    for b in vp_hot_pre: add((b['lo']+b['hi'])/2, 1.5*b['pct']/max(x['pct'] for x in vp_hot_pre) + 0.5, 'узел объёма')
    # круглые числа
    rnd = step_round(px)
    for x in rnd: add(x, 1.3, 'круглый уровень')
    # кластеризация
    cands = [x for x in cands if 0.7*px < x[0] < 1.4*px]
    cands.sort()
    groups = []
    tol = max(0.25*at[i], px*0.0022)
    for v, w, src in cands:
        if groups and abs(v-groups[-1]['hi']) <= tol:
            g = groups[-1]; g['hi'] = max(g['hi'], v); g['lo'] = min(g['lo'], v)
            g['w'] += w; g['n'] += 1; g['src'].append(src)
        else:
            groups.append({'lo': v, 'hi': v, 'w': w, 'n': 1, 'src': [src]})
    for g in groups:
        g['p'] = (g['lo']+g['hi'])/2
        g['src'] = list(dict.fromkeys(x.replace(' пивот','').replace('Fib 0.','Fib ') for x in g['src']))[:5]
    rc = sorted([g for g in groups if g['p'] > px*1.004], key=lambda z: z['p'])[:5]
    sc = sorted([g for g in groups if g['p'] < px*0.996], key=lambda z: -z['p'])[:5]

    def perf(k):
        return (px/c[-1-k]-1)*100 if len(c) > k else None

    out = {
        'sec': sec, 'date': last['date'], 'dec': dec, 'px': px, 'split': split,
        'chg_day': (px/c[-2]-1)*100, 'chg_week': perf(5), 'chg_month': perf(21),
        'chg_3m': perf(63), 'ytd': (px/[r['c'] for r in recs if r['date'] >= '2026-01-01'][0]-1)*100,
        'hi52': hi52, 'lo52': lo52, 'from_hi': (px/hi52-1)*100, 'from_lo': (px/lo52-1)*100,
        'sma20': s20[i], 'sma50': s50[i], 'sma100': sma(c, 100)[i], 'sma200': s200[i],
        'ema50': e50[i], 'ema200': e200[i],
        'rsi': r14[i], 'rsi_prev': r14[i-1],
        'macd': m[i], 'macd_sig': ms[i], 'macd_hist': mh[i], 'macd_hist_prev': mh[i-1],
        'bb_up': bbU[i], 'bb_mid': s20[i], 'bb_low': bbL[i],
        'bb_width': (bbU[i]-bbL[i])/s20[i]*100 if s20[i] else None,
        'atr': at[i], 'atr_pct': at[i]/px*100,
        'stoch_k': sk[i], 'stoch_d': sd_[i], 'stoch_s': ss_[i],
        'ich': ich, 'pivot': piv, 'R1': R1, 'R2': R2, 'R3': R3, 'S1': S1, 'S2': S2, 'S3': S3,
        'res': [{'p': z['p'], 'lo': z['lo'], 'hi': z['hi'], 'w': round(z['w'], 1), 'n': z['n'], 'src': z['src']} for z in rc],
        'sup': [{'p': z['p'], 'lo': z['lo'], 'hi': z['hi'], 'w': round(z['w'], 1), 'n': z['n'], 'src': z['src']} for z in sc],
        'fibs': {str(k): v for k, v in fibs.items()}, 'fib_lo': fib_lo, 'fib_hi': fib_hi,
        'vp_hot': [{'lo': b['lo'], 'hi': b['hi'], 'pct': b['pct']} for b in hot],
        'vol_last': last['v'], 'vol_avg20': sum(r['v'] for r in recs[-20:])/20,
        'vol_ratio': last['v']/(sum(r['v'] for r in recs[-20:])/20 or 1),
        'up_days_20': sum(1 for k in range(len(c)-20, len(c)) if c[k] >= c[k-1]),
    }
    # --- скоринг ---
    sc_trend = 0
    if out['sma20'] and px > out['sma20']: sc_trend += 1
    if out['sma50'] and px > out['sma50']: sc_trend += 1
    if out['sma200'] and px > out['sma200']: sc_trend += 1
    if out['sma20'] and out['sma50'] and out['sma20'] > out['sma50']: sc_trend += 1
    if out['sma50'] and out['sma200'] and out['sma50'] > out['sma200']: sc_trend += 1
    sc_mom = 0
    if out['rsi'] and out['rsi'] > 55: sc_mom += 1
    if out['rsi'] and out['rsi'] > 70: sc_mom -= 1
    if out['macd'] and out['macd_sig'] and out['macd'] > out['macd_sig']: sc_mom += 1
    if out['macd'] and out['macd'] > 0: sc_mom += 1
    if out['macd_hist'] is not None and out['macd_hist_prev'] is not None and out['macd_hist'] > out['macd_hist_prev']: sc_mom += 1
    sc_pos = 0
    if out['hi52'] > out['lo52']:
        pos = (px-out['lo52'])/(out['hi52']-out['lo52'])
        out['range_pos'] = pos*100
        if pos > 0.8: sc_pos -= 1
        elif pos < 0.25: sc_pos += 1
    total = sc_trend*2 + sc_mom + sc_pos
    out['score'] = {'trend': sc_trend, 'mom': sc_mom, 'pos': sc_pos, 'total': total}
    out['verdict'] = ('бычий' if total >= 8 else 'умеренно бычий' if total >= 4 else
                      'нейтральный' if total >= 0 else 'умеренно медвежий' if total >= -4 else 'медвежий')
    out['overbought'] = bool((out['stoch_k'] and out['stoch_k'] > 88) or (out['rsi'] and out['rsi'] > 72))
    out['oversold'] = bool((out['stoch_k'] and out['stoch_k'] < 12) or (out['rsi'] and out['rsi'] < 30))
    out['hot'] = bool((out['stoch_k'] and out['stoch_k'] > 78) or (out['rsi'] and out['rsi'] > 68))
    out['above_bb'] = bool(out['bb_up'] and px >= out['bb_up']*0.995)
    out['below_bb'] = bool(out['bb_low'] and px <= out['bb_low']*1.005)
    # ближайшие уровни (как есть, без привязки к ATR) — для отображения
    out['r1'] = out['res'][0]['p'] if out['res'] else None
    out['r2'] = out['res'][1]['p'] if len(out['res']) > 1 else None
    out['s1'] = out['sup'][0]['p'] if out['sup'] else None
    out['s2'] = out['sup'][1]['p'] if len(out['sup']) > 1 else None
    out['dist_r1'] = (out['r1']/px-1)*100 if out['r1'] else None
    out['dist_s1'] = (1-out['s1']/px)*100 if out['s1'] else None
    out['s1d'] = out['s1']; out['r1d'] = out['r1']
    out['s2d'] = out['s2']; out['r2d'] = out['r2']
    # --- план заявок ---
    a = out['atr'] or px*0.02
    # цели: сопротивления не ближе 1,2×ATR к цене (иначе «цель» уже в цене)
    tgs = [z['p'] for z in out['res'] if z['p'] >= px + 1.2*a]
    if not tgs: tgs = [z['p'] for z in out['res']] or [px+2*a]
    out['t1'] = round(tgs[0], dec)
    out['t2'] = round(tgs[1] if len(tgs) > 1 else tgs[0] + 2*a, dec)
    out['t3'] = round(tgs[2] if len(tgs) > 2 else out['t2'] + 2*a, dec)
    # входы: поддержки не ближе 0,8×ATR, с разносом между собой ≥ 0,8×ATR
    cands_e = [z['p'] for z in out['sup'] if z['p'] <= px - 0.8*a]
    if out['sma20'] and out['sma20'] <= px - 0.8*a: cands_e.append(out['sma20'])
    cands_e = sorted(set(cands_e), reverse=True)
    entries = []
    for e in cands_e:
        if not entries or (entries[-1] - e) >= 0.8*a: entries.append(e)
        if len(entries) == 3: break
    while len(entries) < 2:
        nxt = (entries[-1] if entries else px) - 1.5*a
        entries.append(round(nxt, dec))
    out['entries'] = [round(e, dec) for e in entries]
    out['entry1'] = out['entries'][0]
    out['entry2'] = out['entries'][1]
    out['entry3'] = out['entries'][2] if len(out['entries']) > 2 else None
    base = out['entry2']
    out['stop'] = round(min(base - 1.4*a, out['entry1'] - 2.2*a), dec)
    out['entries'] = [e for e in out['entries'] if e > out['stop'] + 0.35*a] or out['entries'][:2]
    out['entry1'] = out['entries'][0]
    out['entry2'] = out['entries'][1] if len(out['entries']) > 1 else round(out['entry1'] - 1.5*a, dec)
    out['entry3'] = out['entries'][2] if len(out['entries']) > 2 else None
    risk = out['entry1'] - out['stop']
    out['risk'] = risk
    out['risk_pct'] = risk/out['entry1']*100
    out['rr1'] = (out['t1']-out['entry1'])/risk if risk > 0 else None
    out['rr2'] = (out['t2']-out['entry1'])/risk if risk > 0 else None
    out['rr3'] = (out['t3']-out['entry1'])/risk if risk > 0 else None
    out['avg_entry'] = round(sum(out['entries'][:3])/min(3, len(out['entries'])), dec)
    return out

res = {}
for sec, recs in DATA.items():
    if isinstance(recs, dict) or not recs:
        print('skip', sec); continue
    try:
        res[sec] = analyze(sec, recs)
        r = res[sec]
        print(f"{sec:7s} px={r['px']:<10.4g} день {r['chg_day']:+.2f}% нед {r['chg_week']:+.2f}% мес {r['chg_month']:+.2f}% "
              f"RSI {r['rsi']:.0f} тренд {r['score']['trend']}/5 итог {r['score']['total']:+d} ({r['verdict']}) "
              f"S1 {r['s1']:.4g} R1 {r['r1']:.4g} от макс52 {r['from_hi']:+.1f}%")
    except Exception as e:
        import traceback; traceback.print_exc()
        print('ERR', sec, e)

# индекс — для контекста
idx = IDX['daily']
res['_IMOEX'] = analyze('IMOEX', idx)
json.dump(res, open('ta_all.json', 'w'), ensure_ascii=False)
print('\nsaved ta_all.json', os.path.getsize('ta_all.json'))
