#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Общая часть: стили, форматирование, SVG-графики по бумагам."""
import json, os, html, statistics, math
os.chdir(os.path.dirname(os.path.abspath(__file__)))

TA = json.load(open('ta_all.json'))
RAW = json.load(open('stock_data.json'))

# ---------------- портфель ----------------
PORT = [
 dict(t='SBER',   name='Сбербанк',                    qty=160,    uprice=286.10, val=45776, rec='Покупать', target=379.4,  div='≈38–42 ₽', cut='июль 2027',               dy=13.2, sector='Финансы'),
 dict(t='YDEX',   name='Яндекс',                      qty=12,     uprice=3499.50,val=41994, rec='Покупать', target=5816.5, div='≈110+ ₽',  cut='апрель 2027',             dy=6.3,  sector='IT'),
 dict(t='T',      name='Т-Технологии',                qty=160,    uprice=271.14, val=43382, rec='Покупать', target=411.93, div='4,7 ₽ выплачен 12.10.2026', cut='выплачен', dy=6.4, sector='Финансы'),
 dict(t='X5',     name='Корпоративный центр Икс 5',   qty=20,     uprice=2123.00,val=42460, rec='Покупать', target=2861.3, div='не объявлен', cut='январь 2027 (ожид.)',  dy=28.9, sector='Ритейл'),
 dict(t='GAZP',   name='Газпром',                     qty=270,    uprice=105.65, val=28526, rec='Держать',  target=140.49, div='не платит с 2022', cut='—',             dy=0.0,  sector='Нефть и газ'),
 dict(t='LKOH',   name='ЛУКОЙЛ',                      qty=4,      uprice=6110.00,val=24440, rec='Покупать', target=6221.5, div='535 ₽ рекомендован', cut='дек. 2026 — янв. 2027', dy=11.0, sector='Нефть и газ'),
 dict(t='MOEX',   name='Московская Биржа',            qty=140,    uprice=157.59, val=22063, rec='Держать',  target=197.57, div='≈20 ₽',   cut='июль 2027',               dy=12.4, sector='Финансы'),
 dict(t='TRNFP',  name='Транснефть-п',                qty=24,     uprice=1085.40,val=26050, rec='Покупать', target=1500.0, div='≈200+ ₽', cut='июль 2027',               dy=18.8, sector='Нефть и газ'),
 dict(t='OZON',   name='Озон',                        qty=6,      uprice=3539.50,val=21237, rec='Покупать', target=5458.75,div='≈70 ₽ (2026)', cut='2027',              dy=6.0,  sector='IT'),
 dict(t='GMKN',   name='Норникель',                   qty=180,    uprice=117.18, val=21092, rec='Покупать', target=156.0,  div='1,85 ₽ выплачен 12.10.2026', cut='выплачен', dy=1.6, sector='Металлы'),
 dict(t='MSRS',   name='Россети Московский регион',   qty=12000,  uprice=1.722,  val=20658, rec='Покупать', target=2.06,   div='≈0,19–0,23 ₽', cut='июль 2027',          dy=10.8, sector='Энергетика'),
 dict(t='SIBN',   name='Газпром нефть',               qty=28,     uprice=592.80, val=16598, rec='Держать',  target=563.15, div='42,51 ₽ (отсечка 13.10.2026)', cut='выплата в конце октября', dy=11.9, sector='Нефть и газ'),
 dict(t='PHOR',   name='ФосАгро',                     qty=3,      uprice=5532.00,val=16596, rec='Держать',  target=6186.37,div='292 ₽ за 3кв2026 (рек.)', cut='ожидается',      dy=0.0,  sector='Химия и удобрения'),
 dict(t='BANEP',  name='Башнефть-п',                  qty=26,     uprice=796.50, val=20709, rec='Держать',  target=933.0,  div='≈70 ₽',   cut='июль 2027',               dy=8.7,  sector='Нефть и газ'),
 dict(t='MTSS',   name='МТС',                         qty=120,    uprice=175.30, val=21036, rec='Покупать', target=242.55, div='≈35 ₽',   cut='июль 2027',               dy=20.0, sector='Телеком'),
 dict(t='FESH',   name='ДВМП (FESCO)',                qty=314,    uprice=63.20,  val=19845, rec='Покупать', target=80.0,   div='не платит', cut='—',                     dy=0.0,  sector='Транспорт'),
 dict(t='MRKU',   name='Россети Урал',                qty=20000,  uprice=0.680,  val=13600, rec='Покупать', target=0.70,   div='≈0,06 ₽', cut='июнь–июль 2027',          dy=9.0,  sector='Энергетика'),
 dict(t='NLMK',   name='НЛМК',                        qty=160,    uprice=77.36,  val=12378, rec='Держать',  target=88.28,  div='не платит с 2024', cut='—',                dy=0.0,  sector='Металлы'),
 dict(t='FEES',   name='ФСК Россети',                 qty=370000, uprice=0.05766,val=21334, rec='—',        target=None,   div='не платит с 2021', cut='—',                dy=0.0,  sector='Энергетика'),
 dict(t='PLZL',   name='Полюс',                       qty=11,     uprice=1122.00,val=12342, rec='Держать',  target=1341.8, div='≈30–40 ₽', cut='декабрь 2026',           dy=10.9, sector='Металлы'),
 dict(t='AFLT',   name='Аэрофлот',                    qty=340,    uprice=35.95,  val=12223, rec='Держать',  target=42.92,  div='≈5 ₽',    cut='июль 2027',               dy=14.7, sector='Транспорт'),
 dict(t='VTBR',   name='Банк ВТБ',                    qty=363,    uprice=56.00,  val=20326, rec='Покупать', target=89.55,  div='не объявлен', cut='июль 2027 (ожид.)',  dy=17.3, sector='Финансы'),
 dict(t='PMSB',   name='Пермэнергосбыт',              qty=20,     uprice=434.20, val=8684,  rec='—',        target=None,   div='≈20–30 ₽', cut='декабрь 2026',           dy=13.4, sector='Энергетика'),
 dict(t='MVID',   name='М.Видео',                     qty=170,    uprice=43.60,  val=7412,  rec='Держать',  target=42.5,   div='не платит с 2021', cut='—',                dy=0.0,  sector='Ритейл'),
 dict(t='MTLRP',  name='Мечел-п',                     qty=160,    uprice=41.20,  val=6592,  rec='Держать',  target=50.0,   div='не платит с 2021', cut='—',                dy=0.0,  sector='Металлы и уголь'),
]
FUNDS = [
 dict(t='Флагманский', name='ОПИФ «Флагманский» (УК «ГЕРОИ»)', val=310211, kind='Смешанный: акции + облигации, хедж', y1='+6,2%'),
 dict(t='РубПерсп',    name='ОПИФ «Рублёвые перспективы» (УК «ГЕРОИ»)', val=251146, kind='ОФЗ, цель «ключевая ставка +1–2%»', y1='+16,6%'),
 dict(t='BCSD',        name='БПИФ «БКС Денежный рынок» (BCSD)', val=123856, kind='Денежный рынок (репо под ставку ЦБ)', y1='+15,4%'),
 dict(t='TMON',        name='БПИФ «Т-Капитал Денежный рынок» (TMON)', val=26388, kind='Денежный рынок, ставка ON', y1='+14,7%'),
]
CASH = 180000
TOTAL_STOCKS = sum(p['val'] for p in PORT)
TOTAL_FUNDS = sum(f['val'] for f in FUNDS)
# итог сверен со страницей портфеля (1 438 953 ₽); расхождение в 19 ₽ — округление в исходной таблице
TOTAL = 1438953
for p in PORT:
    p['w_stocks'] = p['val']/TOTAL_STOCKS*100
    p['w_total'] = p['val']/TOTAL*100

LOTS = {'SBER':10,'YDEX':1,'T':1,'X5':1,'GAZP':10,'LKOH':1,'MOEX':10,'TRNFP':1,'OZON':1,'GMKN':10,
        'MSRS':100,'SIBN':1,'PHOR':1,'BANEP':1,'MTSS':10,'FESH':10,'MRKU':1000,'NLMK':10,'FEES':10000,
        'PLZL':1,'AFLT':10,'VTBR':100,'PMSB':10,'MVID':10,'MTLRP':1}
for p in PORT:
    p['lot'] = LOTS.get(p['t'], 1)
BY_T = {p['t']: p for p in PORT}

# ---------------- формат ----------------
def nf(x, d=2):
    if x is None: return '—'
    t = f'{x:.{d}f}'
    neg = t.startswith('-')
    if neg: t = t[1:]
    a, _, b = t.partition('.')
    a = ' '.join(reversed([a[max(0, len(a)-3*(k+1)):len(a)-3*k] for k in range((len(a)+2)//3)]))
    return ('−' if neg else '') + a + (',' + b if b else '')

def pf(x, d=2, sign=True):
    if x is None: return '—'
    return ('+' if (x >= 0 and sign) else '') + nf(x, d) + '%'

def pdec(t):
    return TA[t]['dec']

def P(t, x, sign=False):
    """цена бумаги с нужным числом знаков"""
    d = TA[t]['dec']
    return pf(x, d, sign) if sign else nf(x, d)

def esc(s):
    return html.escape(str(s), quote=True)

# ---------------- данные со сплит-коррекцией ----------------
def series(t):
    from ta_engine import adj_split, clean
    recs, _ = adj_split(clean(RAW[t]))
    return recs

# ---------------- SVG: свечи + уровни ----------------
def nice_step(span, target=7):
    if span <= 0: return 1
    raw = span/target
    mag = 10.0 ** int(math.floor(math.log10(raw)))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m*mag:
            return m*mag
    return 10*mag

def axis_dec(step):
    if step >= 100: return 0
    if step >= 10: return 0
    if step >= 1: return 1
    if step >= 0.1: return 2
    if step >= 0.01: return 3
    if step >= 0.001: return 4
    return 6

def stock_chart(t, n=130, W=1160, H=520):
    a = TA[t]
    recs = series(t)[-n:]
    dec = a['dec']
    cl = [r['c'] for r in recs]
    hi = max(r['h'] for r in recs); lo = min(r['l'] for r in recs)
    for lv in a['res'][:2]: hi = max(hi, lv['hi'])
    for lv in a['sup'][:2]: lo = min(lo, lv['lo'])
    if a['sma200']: hi = max(hi, a['sma200']); lo = min(lo, a['sma200'])
    pad = (hi-lo)*0.07 or hi*0.02
    hi += pad; lo -= pad
    ML, MR, MT, MB = 78, 176, 26, 96
    PW = W-ML-MR; VH = 78; PH = H-MT-MB-VH-14
    y = lambda p: MT+PH-(p-lo)/(hi-lo)*PH
    bw = PW/len(recs); cw = max(1.6, bw*0.64)
    x = lambda i: ML+bw*i+bw/2
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" font-family="ui-sans-serif,system-ui,Segoe UI,Roboto,Arial,sans-serif">']
    o.append(f'<rect width="{W}" height="{H}" fill="#0d1117"/>')
    step = nice_step(hi-lo)
    p = int(lo/step)*step
    while p <= hi:
        yy = y(p)
        if MT <= yy <= MT+PH:
            o.append(f'<line x1="{ML}" y1="{yy:.1f}" x2="{ML+PW}" y2="{yy:.1f}" stroke="#1f2733"/>')
            o.append(f'<text x="{ML-9}" y="{yy+4:.1f}" fill="#8b98a9" font-size="11.5" text-anchor="end">{nf(p, axis_dec(step))}</text>')
        p += step
    # зоны
    for lv in a['res'][:4]:
        col = '#ff5c6c' if lv is a['res'][0] else '#ff9f43'
        o.append(f'<rect x="{ML}" y="{y(max(lv["hi"],hi-1e-9)):.1f}" width="{PW}" height="{max(1.6,y(min(lv["lo"],lo))-y(max(lv["hi"],hi-1e-9))):.1f}" fill="{col}" opacity="0.14"/>')
    for lv in a['sup'][:4]:
        col = '#26d07c' if lv is a['sup'][0] else '#3ddc97'
        o.append(f'<rect x="{ML}" y="{y(max(lv["hi"],hi-1e-9)):.1f}" width="{PW}" height="{max(1.6,y(min(lv["lo"],lo))-y(max(lv["hi"],hi-1e-9))):.1f}" fill="{col}" opacity="0.13"/>')
    # SMA
    from ta_engine import sma
    all_c = [r['c'] for r in series(t)]
    for k, col, dash in ((20, '#ffd166', ''), (50, '#c084fc', ''), (200, '#ff5c6c', '6 4')):
        s = sma(all_c, k)[-n:]
        pts = [(x(i), y(v)) for i, v in enumerate(s) if v is not None and lo <= v <= hi]
        if len(pts) > 1:
            da = f' stroke-dasharray="{dash}"' if dash else ''
            o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5"%s/>' %
                     (' '.join(f'{u:.1f},{v:.1f}' for u, v in pts), col, da))
    # свечи
    for i, r in enumerate(recs):
        up = r['c'] >= r['o']
        col = '#26d07c' if up else '#ff5c6c'
        xx = x(i)
        o.append(f'<line x1="{xx:.1f}" y1="{y(r["h"]):.1f}" x2="{xx:.1f}" y2="{y(r["l"]):.1f}" stroke="{col}"/>')
        yo, yc = y(r['o']), y(r['c'])
        o.append(f'<rect x="{xx-cw/2:.1f}" y="{min(yo,yc):.1f}" width="{cw:.1f}" height="{max(1.1,abs(yc-yo)):.1f}" fill="{col}" rx="0.5"/>')
    # объём
    vtop = MT+PH+14; vmax = max(r['v'] for r in recs) or 1
    o.append(f'<line x1="{ML}" y1="{vtop}" x2="{ML+PW}" y2="{vtop}" stroke="#1f2733"/>')
    for i, r in enumerate(recs):
        hgt = r['v']/vmax*VH
        col = '#26d07c' if r['c'] >= r['o'] else '#ff5c6c'
        o.append(f'<rect x="{x(i)-cw/2:.1f}" y="{vtop+VH-hgt:.1f}" width="{cw:.1f}" height="{hgt:.1f}" fill="{col}" opacity="0.45"/>')
    lbl = max(1, len(recs)//9)
    for i in range(0, len(recs), lbl):
        o.append(f'<text x="{x(i):.1f}" y="{vtop+VH+20:.1f}" fill="#8b98a9" font-size="11" text-anchor="middle">{recs[i]["date"][5:]}</text>')
    # текущая цена
    yc = y(cl[-1])
    o.append(f'<line x1="{ML}" y1="{yc:.1f}" x2="{ML+PW}" y2="{yc:.1f}" stroke="#e6edf3" stroke-dasharray="4 3" opacity="0.85"/>')
    o.append(f'<rect x="{ML+PW+5}" y="{yc-10:.1f}" width="70" height="20" rx="4" fill="#e6edf3"/>')
    o.append(f'<text x="{ML+PW+40}" y="{yc+4:.1f}" fill="#0d1117" font-size="12" font-weight="700" text-anchor="middle">{nf(cl[-1], dec)}</text>')
    # метки уровней
    used = []
    def tag(price, text, col):
        yy = y(price)
        if not (MT <= yy <= MT+PH): return
        if any(abs(yy-u) < 15 for u in used): yy = (used[-1]+15) if used else yy
        used.append(yy)
        o.append(f'<rect x="{ML+PW+80}" y="{yy-9:.1f}" width="{MR-84}" height="18" rx="4" fill="{col}" opacity="0.16"/>')
        o.append(f'<text x="{ML+PW+85}" y="{yy+4:.1f}" fill="{col}" font-size="10.5" font-weight="600">{esc(text)}</text>')
    for j, lv in enumerate(a['res'][:3]):
        tag(lv['p'], f'R{j+1} {nf(lv["p"], dec)}', '#ff9f43' if j else '#ff8fa3')
    for j, lv in enumerate(a['sup'][:3]):
        tag(lv['p'], f'S{j+1} {nf(lv["p"], dec)}', '#3ddc97' if j else '#26d07c')
    # легенда
    lx = ML+8
    for k, (nm, col) in enumerate((('SMA20', '#ffd166'), ('SMA50', '#c084fc'), ('SMA200', '#ff5c6c'))):
        o.append(f'<line x1="{lx+k*98}" y1="{MT+4}" x2="{lx+k*98+20}" y2="{MT+4}" stroke="{col}" stroke-width="2.4"/>')
        o.append(f'<text x="{lx+k*98+26}" y="{MT+8}" fill="#9aa7b6" font-size="11.5">{nm}</text>')
    o.append('</svg>')
    return '\n'.join(o)

def rsi_chart(t, n=130, W=1160, H=132):
    from ta_engine import rsi
    a = TA[t]
    vals = rsi([r['c'] for r in series(t)])[-n:]
    ML, MR, MT, MB = 78, 176, 20, 18
    PW = W-ML-MR; PH = H-MT-MB
    lo, hi = 5, 95
    y = lambda p: MT+PH-(p-lo)/(hi-lo)*PH
    bw = PW/len(vals); x = lambda i: ML+bw*i+bw/2
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" font-family="ui-sans-serif,system-ui,Segoe UI,Roboto,Arial,sans-serif">']
    o.append(f'<rect width="{W}" height="{H}" fill="#0d1117"/>')
    for a_, b_, c_, op in ((70, 95, '#ff5c6c', .12), (30, 70, '#3ddc97', .05), (5, 30, '#26d07c', .12)):
        o.append(f'<rect x="{ML}" y="{y(b_):.1f}" width="{PW}" height="{y(a_)-y(b_):.1f}" fill="{c_}" opacity="{op}"/>')
        o.append(f'<text x="{ML-9}" y="{y(b_)+4:.1f}" fill="#8b98a9" font-size="11" text-anchor="end">{b_}</text>')
    pts = ' '.join(f'{x(i):.1f},{y(v):.1f}' for i, v in enumerate(vals) if v is not None)
    o.append(f'<polyline points="{pts}" fill="none" stroke="#ffd166" stroke-width="1.6"/>')
    o.append(f'<text x="{ML+6}" y="{MT+4}" fill="#9aa7b6" font-size="12" font-weight="600">RSI(14), дневной</text>')
    o.append(f'<text x="{ML+PW+85}" y="{y(vals[-1])+4:.1f}" fill="#ffd166" font-size="13" font-weight="700">{vals[-1]:.1f}</text>')
    o.append('</svg>')
    return '\n'.join(o)
