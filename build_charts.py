#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерация SVG-графиков и HTML-отчёта по IMOEX."""
import json, statistics, html, datetime, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


S = json.load(open('imoex_series.json'))
daily = S['daily']
weekly = S['weekly']
closes = [r['c'] for r in daily]
highs = [r['h'] for r in daily]
lows = [r['l'] for r in daily]
LAST = daily[-1]
CLOSE = LAST['c']

# ---------- индикаторы ----------
def sma_series(a, n):
    out = [None]*(n-1)
    for i in range(n-1, len(a)):
        out.append(sum(a[i-n+1:i+1])/n)
    return out

def ema_series(a, n):
    k = 2/(n+1)
    e = sum(a[:n])/n
    out = [None]*(n-1) + [e]
    for x in a[n:]:
        e = x*k + e*(1-k)
        out.append(e)
    return out

def rsi_series(a, n=14):
    out = [None]*n
    gains = []; losses = []
    for i in range(1, len(a)):
        ch = a[i]-a[i-1]
        gains.append(max(ch, 0)); losses.append(max(-ch, 0))
    ag = sum(gains[:n])/n; al = sum(losses[:n])/n
    out.append(100 - 100/(1+ag/al) if al else 100)
    for i in range(n, len(gains)):
        ag = (ag*(n-1)+gains[i])/n
        al = (al*(n-1)+losses[i])/n
        out.append(100 - 100/(1+ag/al) if al else 100)
    return out

sma20 = sma_series(closes, 20)
sma50 = sma_series(closes, 50)
sma200 = sma_series(closes, 200)
ema200 = ema_series(closes, 200)
rsi14 = rsi_series(closes)
sd20 = [statistics.pstdev(closes[i-19:i+1]) if i >= 19 else None for i in range(len(closes))]
bb_up = [sma20[i]+2*sd20[i] if sma20[i] else None for i in range(len(closes))]
bb_dn = [sma20[i]-2*sd20[i] if sma20[i] else None for i in range(len(closes))]

# ATR
trs = []
for i in range(1, len(daily)):
    trs.append(max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1])))
ATR = sum(trs[-14:])/14

# MACD
e12 = ema_series(closes, 12); e26 = ema_series(closes, 26)
macd = [e12[i]-e26[i] if (e12[i] is not None and e26[i] is not None) else None for i in range(len(closes))]
sig_raw = ema_series([m for m in macd if m is not None], 9)
macd_sig = sig_raw[-1]

VALS = dict(
    close=CLOSE, chg_day=round((CLOSE/daily[-2]['c']-1)*100, 2),
    chg_week=round((CLOSE/daily[-6]['c']-1)*100, 2),
    chg_month=round((CLOSE/daily[-22]['c']-1)*100, 2),
    ytd=round((CLOSE/2757.09-1)*100, 2),
    sma20=round(sma20[-1], 1), sma50=round(sma50[-1], 1),
    sma100=round(sum(closes[-100:])/100, 1), sma200=round(sma200[-1], 1),
    ema200=round(ema200[-1], 1),
    rsi=round(rsi14[-1], 1), rsi_prev=round(rsi14[-2], 1),
    bb_up=round(bb_up[-1], 1), bb_mid=round(sma20[-1], 1), bb_dn=round(bb_dn[-1], 1),
    atr=round(ATR, 1), atrp=round(ATR/CLOSE*100, 2),
    macd=round(macd[-1], 1), macd_sig=round(macd_sig, 1),
    macd_hist=round(macd[-1]-macd_sig, 1),
)

# ---------- уровни ----------
RES = [
    (2550, 2566, 'Максимум июня + закрытие мая', 'strong'),
    (2500, 2525, 'Круглый 2500 · SMA200 (2515) · Fib 61,8% (2525) · цель аналитиков 2510', 'strong'),
    (2445, 2470, 'Максимум недели 2445,6 · EMA200 (2452) · верхняя BB (2445) · Fib 50% (2461) · R2 (2469)', 'key'),
    (2439, 2445, 'Хай пятницы 2439,2 + верхняя полоса Боллинджера', 'near'),
]
SUP = [
    (2400, 2412, 'Пивот 2420 · S1 2401 · Fib 50% отскока (2405) · зона консолидации 9–16.10', 'near'),
    (2370, 2385, 'S2 2371 · Тенкан-сен 2373 · SMA10 2375 · минимум 15.10 (2384)', 'key'),
    (2335, 2355, 'Середина BB 2327 · Киджун 2335 · Сенкоу A 2354 · краткосрочная поддержка аналитиков 2335', 'key'),
    (2280, 2300, 'EMA50 2299 · максимум плотности объёма (2250–2300) · Fib 38,2% (2286) · EMA20 недельная', 'strong'),
    (2225, 2250, 'Минимумы 22–29.09 · узел объёма · нижняя BB (2208) рядом', 'strong'),
]

# ---------- SVG-чарт ----------
def esc(s): return html.escape(str(s), quote=True)

def candle_chart(n=150, W=1180, H=600, show='daily'):
    data = daily[-n:] if show == 'daily' else weekly[-n:]
    cs = closes[-n:] if show == 'daily' else [w['c'] for w in weekly][-n:]
    s20 = sma20[-n:] if show == 'daily' else None
    s50 = sma50[-n:] if show == 'daily' else None
    s200 = sma200[-n:] if show == 'daily' else None
    e200 = ema200[-n:] if show == 'daily' else None
    bu = bb_up[-n:] if show == 'daily' else None
    bd = bb_dn[-n:] if show == 'daily' else None

    ML, MR, MT, MB = 66, 190, 26, 118          # поля
    PW = W - ML - MR                            # ширина цены
    VH = 96                                     # высота объёма
    PH = H - MT - MB - VH - 16                  # высота цены

    hi = max(r['h'] for r in data); lo = min(r['l'] for r in data)
    # включаем в масштаб ключевые уровни
    hi = max(hi, 2570)
    if show == 'daily': lo = min(lo, 2190)
    pad = (hi-lo)*0.06
    hi += pad; lo -= pad
    y = lambda p: MT + PH - (p-lo)/(hi-lo)*PH
    bw = PW/len(data)
    cw = max(2.0, bw*0.62)
    x = lambda i: ML + bw*i + bw/2

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" font-family="ui-sans-serif,system-ui,Segoe UI,Roboto,Arial,sans-serif">']
    o.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#0d1117"/>')

    # сетка + подписи цены
    step = 100 if (hi-lo) > 400 else 50
    p = int(lo//step)*step
    while p <= hi:
        yy = y(p)
        if MT <= yy <= MT+PH:
            o.append(f'<line x1="{ML}" y1="{yy:.1f}" x2="{ML+PW}" y2="{yy:.1f}" stroke="#1f2733" stroke-width="1"/>')
            o.append(f'<text x="{ML-10}" y="{yy+4:.1f}" fill="#8b98a9" font-size="12" text-anchor="end">{p}</text>')
        p += step

    # зоны сопротивления / поддержки (только дневной)
    if show == 'daily':
        for a, b, _, kind in RES:
            if b < lo or a > hi: continue
            col = {'strong': '#f0616d', 'key': '#ff9f43', 'near': '#e0b341'}[kind]
            o.append(f'<rect x="{ML}" y="{y(b):.1f}" width="{PW}" height="{max(1.5,y(a)-y(b)):.1f}" fill="{col}" opacity="0.13"/>')
            o.append(f'<line x1="{ML}" y1="{y((a+b)/2):.1f}" x2="{ML+PW}" y2="{y((a+b)/2):.1f}" stroke="{col}" stroke-width="1" stroke-dasharray="5 4" opacity="0.65"/>')
        for a, b, _, kind in SUP:
            if b < lo or a > hi: continue
            col = {'strong': '#2ecc71', 'key': '#3ddc97', 'near': '#9be15d'}[kind]
            o.append(f'<rect x="{ML}" y="{y(b):.1f}" width="{PW}" height="{max(1.5,y(a)-y(b)):.1f}" fill="{col}" opacity="0.11"/>')
            o.append(f'<line x1="{ML}" y1="{y((a+b)/2):.1f}" x2="{ML+PW}" y2="{y((a+b)/2):.1f}" stroke="{col}" stroke-width="1" stroke-dasharray="5 4" opacity="0.6"/>')

    # лента Боллинджера
    if show == 'daily' and bu[-1]:
        pts_u = ' '.join(f'{x(i):.1f},{y(bu[i]):.1f}' for i in range(len(data)) if bu[i])
        pts_d = ' '.join(f'{x(i):.1f},{y(bd[i]):.1f}' for i in reversed(range(len(data))) if bd[i])
        o.append(f'<polygon points="{pts_u} {pts_d}" fill="#7aa2f7" opacity="0.07"/>')
        o.append(f'<polyline points="{pts_u}" fill="none" stroke="#7aa2f7" stroke-width="1" opacity="0.35" stroke-dasharray="3 3"/>')
        o.append(f'<polyline points="{pts_d}" fill="none" stroke="#7aa2f7" stroke-width="1" opacity="0.35" stroke-dasharray="3 3"/>')

    # свечи
    for i, r in enumerate(data):
        up = r['c'] >= r['o']
        col = '#26d07c' if up else '#ff5c6c'
        xx = x(i)
        o.append(f'<line x1="{xx:.1f}" y1="{y(r["h"]):.1f}" x2="{xx:.1f}" y2="{y(r["l"]):.1f}" stroke="{col}" stroke-width="1"/>')
        yo, yc = y(r['o']), y(r['c'])
        top, hgt = min(yo, yc), max(1.1, abs(yc-yo))
        o.append(f'<rect x="{xx-cw/2:.1f}" y="{top:.1f}" width="{cw:.1f}" height="{hgt:.1f}" fill="{col}" rx="0.6"/>')

    # скользящие
    def line(series, color, w=1.6, dash=''):
        pts = [(x(i), y(v)) for i, v in enumerate(series) if v is not None and lo <= v <= hi]
        if len(pts) < 2: return
        s = ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ''
        o.append(f'<polyline points="{s}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linejoin="round"{da}/>')
    if show == 'daily':
        line(s20, '#ffd166', 1.5)
        line(s50, '#c084fc', 1.5)
        line(s200, '#ff5c6c', 1.8, '6 4')
        line(e200, '#ff9f43', 1.5, '2 3')

    # подписи дат
    lbl_step = max(1, len(data)//10)
    for i in range(0, len(data), lbl_step):
        o.append(f'<text x="{x(i):.1f}" y="{MT+PH+VH+34:.1f}" fill="#8b98a9" font-size="11" text-anchor="middle">{esc(data[i]["date"][5:])}</text>')

    # объём
    vtop = MT+PH+16
    vmax = max(r['v'] for r in data)
    o.append(f'<line x1="{ML}" y1="{vtop}" x2="{ML+PW}" y2="{vtop}" stroke="#1f2733"/>')
    for i, r in enumerate(data):
        hgt = r['v']/vmax*VH
        col = '#26d07c' if r['c'] >= r['o'] else '#ff5c6c'
        o.append(f'<rect x="{x(i)-cw/2:.1f}" y="{vtop+VH-hgt:.1f}" width="{cw:.1f}" height="{hgt:.1f}" fill="{col}" opacity="0.45"/>')
    o.append(f'<text x="{ML-10}" y="{vtop+14}" fill="#6b7787" font-size="11" text-anchor="end">объём</text>')

    # текущая цена
    yc = y(CLOSE)
    o.append(f'<line x1="{ML}" y1="{yc:.1f}" x2="{ML+PW}" y2="{yc:.1f}" stroke="#e6edf3" stroke-width="1" stroke-dasharray="4 3" opacity="0.8"/>')
    o.append(f'<rect x="{ML+PW+6}" y="{yc-11:.1f}" width="76" height="22" rx="4" fill="#e6edf3"/>')
    o.append(f'<text x="{ML+PW+44}" y="{yc+4:.1f}" fill="#0d1117" font-size="13" font-weight="700" text-anchor="middle">{CLOSE:.2f}</text>')

    # метки уровней справа
    def tag(p, text, color, dy=0):
        yy = y(p)
        if not (MT-6 <= yy <= MT+PH+6): return
        o.append(f'<rect x="{ML+PW+90}" y="{yy-9+dy:.1f}" width="{MR-96}" height="18" rx="4" fill="{color}" opacity="0.16"/>')
        o.append(f'<text x="{ML+PW+95}" y="{yy+4+dy:.1f}" fill="{color}" font-size="11" font-weight="600">{esc(text)}</text>')
    if show == 'daily':
        tag(2558, 'R  2550–2566', '#ff8fa3')
        tag(2512, 'R  2500–2525  SMA200', '#ff9f43')
        tag(2457, 'R  2445–2470  EMA200', '#ffd166', 0)
        tag(2406, 'S  2400–2412  Fib 50%', '#9be15d')
        tag(2345, 'S  2335–2355  BB mid', '#3ddc97')
        tag(2290, 'S  2280–2300  объём', '#2ecc71')
        tag(2237, 'S  2225–2250', '#2ecc71')

    # легенда
    lx, ly = ML+8, MT+6
    items = ([('SMA20', '#ffd166'), ('SMA50', '#c084fc'), ('SMA200', '#ff5c6c'), ('EMA200', '#ff9f43'), ('BB(20,2)', '#7aa2f7')]
             if show == 'daily' else [('неделя', '#26d07c')])
    for i, (t, c) in enumerate(items):
        o.append(f'<line x1="{lx+i*104}" y1="{ly}" x2="{lx+i*104+22}" y2="{ly}" stroke="{c}" stroke-width="2.4"/>')
        o.append(f'<text x="{lx+i*104+28}" y="{ly+4}" fill="#9aa7b6" font-size="11.5">{esc(t)}</text>')
    o.append('</svg>')
    return '\n'.join(o)

# ---------- индикаторные панели ----------
def panel(W=1180, H=150, series=None, lo=None, hi=None, zones=None, title='', fmt='{:.0f}', color='#7aa2f7'):
    n = 150
    vals = series[-n:]
    idxs = [i for i, v in enumerate(vals) if v is not None]
    vals2 = [vals[i] for i in idxs]
    if lo is None: lo = min(vals2); hi = max(vals2)
    ML, MR, MT, MB = 66, 190, 22, 24
    PW = W-ML-MR; PH = H-MT-MB
    y = lambda p: MT + PH - (p-lo)/(hi-lo)*PH
    bw = PW/len(vals); x = lambda i: ML + bw*i + bw/2
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" font-family="ui-sans-serif,system-ui,Segoe UI,Roboto,Arial,sans-serif">']
    o.append(f'<rect width="{W}" height="{H}" fill="#0d1117"/>')
    for a, b, c, op in (zones or []):
        o.append(f'<rect x="{ML}" y="{y(b):.1f}" width="{PW}" height="{max(1,y(a)-y(b)):.1f}" fill="{c}" opacity="{op}"/>')
        o.append(f'<text x="{ML-10}" y="{y((a+b)/2)+4:.1f}" fill="#8b98a9" font-size="11" text-anchor="end">{fmt.format((a+b)/2)}</text>')
    pts = ' '.join(f'{x(i):.1f},{y(v):.1f}' for i, v in enumerate(vals) if v is not None)
    o.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.7"/>')
    o.append(f'<text x="{ML+6}" y="{MT+2}" fill="#9aa7b6" font-size="12" font-weight="600">{esc(title)}</text>')
    o.append(f'<text x="{ML+PW+90}" y="{y(vals2[-1])+4:.1f}" fill="{color}" font-size="13" font-weight="700">{fmt.format(vals2[-1])}</text>')
    o.append('</svg>')
    return '\n'.join(o)

rsi_svg = panel(series=rsi14, lo=10, hi=90, zones=[(70, 90, '#ff5c6c', .12), (30, 70, '#3ddc97', .05), (10, 30, '#26d07c', .12)],
                title='RSI(14), дневной  ·  >70 перекупленность, <30 перепроданность', fmt='{:.1f}', color='#ffd166')

# MACD
e12 = ema_series(closes, 12); e26 = ema_series(closes, 26)
macd_all = [e12[i]-e26[i] if (e12[i] is not None and e26[i] is not None) else None for i in range(len(closes))]
sig_all = [None]*len(closes)
mm = [m for m in macd_all if m is not None]
ss = ema_series(mm, 9)
off = len(closes)-len(ss)
for i, v in enumerate(ss): sig_all[off+i] = v
hist = [macd_all[i]-sig_all[i] if sig_all[i] is not None else None for i in range(len(closes))]

def macd_panel(W=1180, H=170):
    n = 150
    m = macd_all[-n:]; s = sig_all[-n:]; h = hist[-n:]
    lo = min(min(v for v in m if v is not None), min(v for v in h if v is not None))
    hi = max(max(v for v in m if v is not None), max(v for v in h if v is not None))
    pad = (hi-lo)*0.15; lo -= pad; hi += pad
    ML, MR, MT, MB = 66, 190, 24, 26
    PW = W-ML-MR; PH = H-MT-MB
    y = lambda p: MT+PH-(p-lo)/(hi-lo)*PH
    bw = PW/n; x = lambda i: ML+bw*i+bw/2
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" font-family="ui-sans-serif,system-ui,Segoe UI,Roboto,Arial,sans-serif">']
    o.append(f'<rect width="{W}" height="{H}" fill="#0d1117"/>')
    o.append(f'<line x1="{ML}" y1="{y(0):.1f}" x2="{ML+PW}" y2="{y(0):.1f}" stroke="#2b3441"/>')
    for i, v in enumerate(h):
        if v is None: continue
        c = '#26d07c' if v >= 0 else '#ff5c6c'
        yy = y(v); y0 = y(0)
        o.append(f'<rect x="{x(i)-bw*0.3:.1f}" y="{min(yy,y0):.1f}" width="{bw*0.6:.1f}" height="{max(0.8,abs(y0-yy)):.1f}" fill="{c}" opacity="0.65"/>')
    for series, col in ((m, '#7aa2f7'), (s, '#ff9f43')):
        pts = [(x(i), y(v)) for i, v in enumerate(series) if v is not None]
        o.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a,b in pts)}" fill="none" stroke="{col}" stroke-width="1.7"/>')
    o.append(f'<text x="{ML+6}" y="{MT}" fill="#9aa7b6" font-size="12" font-weight="600">MACD(12,26,9), дневной</text>')
    o.append(f'<line x1="{ML+150}" y1="{MT-4}" x2="{ML+172}" y2="{MT-4}" stroke="#7aa2f7" stroke-width="2.4"/><text x="{ML+178}" y="{MT}" fill="#9aa7b6" font-size="11.5">MACD</text>')
    o.append(f'<line x1="{ML+230}" y1="{MT-4}" x2="{ML+252}" y2="{MT-4}" stroke="#ff9f43" stroke-width="2.4"/><text x="{ML+258}" y="{MT}" fill="#9aa7b6" font-size="11.5">Signal</text>')
    o.append(f'<text x="{ML+PW+90}" y="{y(m[-1])+4:.1f}" fill="#7aa2f7" font-size="13" font-weight="700">{m[-1]:.1f}</text>')
    o.append('</svg>')
    return '\n'.join(o)

macd_svg = macd_panel()

# ---------- профиль объёма ----------
def volume_profile(W=1180, H=430, n=120):
    data = daily[-n:]
    ML, MR, MT, MB = 66, 30, 24, 30
    PW = W-ML-MR; PH = H-MT-MB
    lo, hi = 2050, 2620
    y = lambda p: MT+PH-(p-lo)/(hi-lo)*PH
    bins = {}
    step = 25
    for r in data:
        typ = (r['h']+r['l']+r['c'])/3
        b = int(typ//step)*step
        bins[b] = bins.get(b, 0)+r['v']
    vmax = max(bins.values())
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" font-family="ui-sans-serif,system-ui,Segoe UI,Roboto,Arial,sans-serif">']
    o.append(f'<rect width="{W}" height="{H}" fill="#0d1117"/>')
    p = lo
    while p <= hi:
        o.append(f'<line x1="{ML}" y1="{y(p):.1f}" x2="{ML+PW}" y2="{y(p):.1f}" stroke="#1a222d"/>')
        o.append(f'<text x="{ML-10}" y="{y(p)+4:.1f}" fill="#8b98a9" font-size="11" text-anchor="end">{p}</text>')
        p += 50
    for b, v in sorted(bins.items()):
        w = v/vmax*PW*0.82
        yy = y(b+step); hh = max(1.5, y(b)-y(b+step))
        hot = v >= vmax*0.55
        col = '#ff9f43' if hot else '#3b82f6'
        o.append(f'<rect x="{ML}" y="{yy:.1f}" width="{w:.1f}" height="{hh:.1f}" fill="{col}" opacity="{0.85 if hot else 0.5}" rx="1.5"/>')
        o.append(f'<text x="{ML+w+8:.1f}" y="{yy+hh/2+4:.1f}" fill="{"#ffb066" if hot else "#6f8fb8"}" font-size="11" font-weight="{"700" if hot else "400"}">{b}–{b+step}  ·  {v/1e9:.0f} млрд ₽</text>')
    o.append(f'<line x1="{ML}" y1="{y(CLOSE):.1f}" x2="{ML+PW}" y2="{y(CLOSE):.1f}" stroke="#e6edf3" stroke-dasharray="5 4"/>')
    o.append(f'<text x="{ML+PW}" y="{y(CLOSE)-8:.1f}" fill="#e6edf3" font-size="12" text-anchor="end" font-weight="700">текущая {CLOSE:.2f}</text>')
    o.append(f'<text x="{ML+6}" y="{MT}" fill="#9aa7b6" font-size="12.5" font-weight="600">Профиль объёма, 120 сессий (млрд ₽ в ценовом диапазоне 25 п.) — оранжевым узлы максимального объёма</text>')
    o.append('</svg>')
    return '\n'.join(o)

vp_svg = volume_profile()

chart_d = candle_chart(150, show='daily')
chart_w = candle_chart(94, show='weekly')

json.dump({'vals': VALS, 'chart_d': chart_d, 'chart_w': chart_w, 'rsi': rsi_svg,
           'macd': macd_svg, 'vp': vp_svg, 'atr': ATR, 'last_date': LAST['date'],
           'high': LAST['h'], 'low': LAST['l'], 'open': LAST['o'], 'vol': LAST['v']},
          open('chart_assets.json','w'))
print('OK', VALS)
print('ATR', round(ATR, 1))
