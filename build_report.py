#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка HTML-отчёта по IMOEX из подготовленных SVG-активов."""
import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

A = json.load(open('chart_assets.json'))
V = A['vals']
ATR = V['atr']

def fmt(x, d=2):
    t = f'{x:.{d}f}'
    a, _, b = t.partition('.')
    a = ' '.join(reversed([a[max(0, i-3):i] for i in range(len(a), 0, -3)][::-1]))
    return a + (',' + b if b else '')

def n1(x):
    return f'{x:.1f}'.replace('.', ',')

def n2(x):
    return f'{x:.2f}'.replace('.', ',')

CSS = """
:root{--bg:#080b10;--card:#111721;--card2:#0d131c;--line:#1e2733;--tx:#e6edf3;--mut:#8b98a9;
--grn:#26d07c;--red:#ff5c6c;--amb:#ff9f43;--yel:#ffd166;--blu:#7aa2f7;--pur:#c084fc;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif;
line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:1240px;margin:0 auto;padding:28px 20px 70px}
h1{font-size:clamp(24px,3.4vw,38px);margin:0 0 6px;letter-spacing:-.5px}
h2{font-size:clamp(19px,2.2vw,24px);margin:44px 0 14px;padding-bottom:10px;border-bottom:1px solid var(--line);letter-spacing:-.2px}
h2 .n{display:inline-block;width:28px;height:28px;line-height:28px;text-align:center;border-radius:8px;
background:#1b2432;color:var(--blu);font-size:14px;margin-right:10px;vertical-align:2px}
h3{font-size:16px;margin:22px 0 8px;color:#cfd8e3}
p{margin:9px 0;color:#c7d1dc}
a{color:var(--blu)}
.sub{color:var(--mut);font-size:14px}
.card{background:linear-gradient(180deg,#121a25,#0d131c);border:1px solid var(--line);border-radius:16px;padding:20px;margin:14px 0}
.grid{display:grid;gap:14px}
.g4{grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.g2{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.kpi{background:var(--card2);border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.kpi .l{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.6px}
.kpi .v{font-size:24px;font-weight:700;margin-top:3px;font-variant-numeric:tabular-nums}
.kpi .d{font-size:12.5px;color:var(--mut);margin-top:2px}
.up{color:var(--grn)}.dn{color:var(--red)}.am{color:var(--amb)}.ye{color:var(--yel)}.bl{color:var(--blu)}
table{width:100%;border-collapse:collapse;font-size:14px;margin:8px 0}
th,td{text-align:left;padding:10px 11px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11.5px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut);font-weight:600;background:#0e141d}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tr:hover td{background:#131b26}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11.5px;font-weight:700;letter-spacing:.3px}
.b-r{background:rgba(255,92,108,.14);color:#ff8b96;border:1px solid rgba(255,92,108,.35)}
.b-s{background:rgba(38,208,124,.13);color:#4ce0a0;border:1px solid rgba(38,208,124,.33)}
.b-n{background:rgba(255,159,67,.14);color:#ffb877;border:1px solid rgba(255,159,67,.33)}
.b-i{background:rgba(122,162,247,.14);color:#9db8fb;border:1px solid rgba(122,162,247,.33)}
.b-g{background:rgba(139,152,169,.13);color:#a8b4c2;border:1px solid rgba(139,152,169,.3)}
.verdict{border-left:4px solid var(--amb);background:linear-gradient(90deg,rgba(255,159,67,.09),rgba(13,19,28,0) 60%)}
.note{border-left:3px solid var(--blu);background:rgba(122,162,247,.07);padding:12px 15px;border-radius:0 10px 10px 0;margin:12px 0;font-size:14px}
.warn{border-left:3px solid var(--red);background:rgba(255,92,108,.07);padding:12px 15px;border-radius:0 10px 10px 0;margin:12px 0;font-size:14px}
.chart{background:#0d1117;border:1px solid var(--line);border-radius:14px;overflow:hidden;margin:12px 0}
.chart svg{display:block;width:100%;height:auto}
.cap{font-size:12.5px;color:var(--mut);padding:9px 14px;border-top:1px solid var(--line);background:#0b1017}
.setup{border:1px solid var(--line);border-radius:14px;overflow:hidden;background:var(--card2)}
.setup .hd{padding:13px 16px;font-weight:700;font-size:15px;display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
.hd-long{background:linear-gradient(90deg,rgba(38,208,124,.18),rgba(38,208,124,.02));border-bottom:1px solid rgba(38,208,124,.25)}
.hd-short{background:linear-gradient(90deg,rgba(255,92,108,.18),rgba(255,92,108,.02));border-bottom:1px solid rgba(255,92,108,.25)}
.hd-wait{background:linear-gradient(90deg,rgba(255,159,67,.18),rgba(255,159,67,.02));border-bottom:1px solid rgba(255,159,67,.25)}
.setup .bd{padding:6px 16px 16px}
.row{display:flex;gap:10px;padding:8px 0;border-bottom:1px dashed #1c2531;font-size:14px}
.row:last-child{border-bottom:0}
.row .k{min-width:132px;color:var(--mut);font-size:12.5px;text-transform:uppercase;letter-spacing:.4px;padding-top:2px}
.row .val{flex:1}
.pill{display:inline-block;background:#182130;border:1px solid #26313f;border-radius:7px;padding:1px 8px;margin:1px 3px 1px 0;font-variant-numeric:tabular-nums;font-size:13.5px}
.ladder{display:flex;flex-direction:column;gap:5px;margin:10px 0}
.rung{display:grid;grid-template-columns:120px 1fr;gap:12px;align-items:center;background:#0e141d;border:1px solid var(--line);border-radius:10px;padding:8px 12px}
.rung .p{font-weight:700;font-variant-numeric:tabular-nums;font-size:15px}
.rung .t{font-size:13px;color:#b9c4d1}
.rung.res{border-left:3px solid var(--red)}
.rung.sup{border-left:3px solid var(--grn)}
.rung.now{border-left:3px solid var(--yel);background:#151d16}
ul{margin:8px 0 8px 2px;padding-left:20px}
li{margin:5px 0;color:#c7d1dc}
.scen{border:1px solid var(--line);border-radius:14px;padding:16px;background:var(--card2)}
.scen .t{font-weight:700;font-size:15px;margin-bottom:6px}
.prob{float:right;font-size:12.5px;padding:2px 10px;border-radius:999px;background:#182130;border:1px solid #26313f;color:#a8b4c2}
.foot{margin-top:40px;padding-top:18px;border-top:1px solid var(--line);color:var(--mut);font-size:12.5px}
.tag{font-size:11px;color:var(--mut);letter-spacing:.5px;text-transform:uppercase}
.big{font-size:clamp(30px,5vw,46px);font-weight:800;letter-spacing:-1px;font-variant-numeric:tabular-nums}
.toc{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}
.toc a{text-decoration:none;font-size:13px;padding:6px 12px;border-radius:999px;background:#131b26;border:1px solid var(--line);color:#b9c4d1}
.toc a:hover{border-color:#2f3d4f;color:#fff}
.disc{font-size:12.5px;color:#7d8998;background:#0c1119;border:1px solid var(--line);border-radius:12px;padding:14px 16px}
@media(max-width:640px){.rung{grid-template-columns:88px 1fr}.row .k{min-width:104px}}
"""

HEAD = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>IMOEX — технический анализ на 18.10.2026</title>
<style>{CSS}</style></head><body><div class="wrap">"""

HEADER = f"""
<div class="tag">Технический анализ · Московская биржа · индекс IMOEX</div>
<h1>Индекс МосБиржи (IMOEX): уровни и план заявок</h1>
<div class="sub">Данные на закрытие основной сессии <b>пятницы, 16 октября 2026</b> · отчёт сформирован 18.10.2026 ·
источник котировок — ISS Московской биржи. Сегодня суббота: основная сессия откроется в понедельник 20.10,
выходная сессия Мосбиржи работает сб/вс 10:00–19:00 — котировки могут уйти от пятничных ещё до понедельника.</div>

<div class="grid g4" style="margin-top:18px">
  <div class="kpi"><div class="l">IMOEX2 (все сессии)</div><div class="v">{fmt(V['close'])}</div>
    <div class="d up">▲ +{n2(V['chg_day'])}% за пятницу · +{n2(V['chg_week'])}% за неделю</div></div>
  <div class="kpi"><div class="l">IMOEX (основная сессия)</div><div class="v">2 426,09</div>
    <div class="d up">максимум закрытия за 4 месяца (с 18.06)</div></div>
  <div class="kpi"><div class="l">RTSI · RGBI · CNY/RUB</div><div class="v" style="font-size:19px">915,88 · 111,66 · 12,46</div>
    <div class="d up">неделя: +2,8% · +0,7% · рубль укрепился</div></div>
  <div class="kpi"><div class="l">С начала 2026</div><div class="v dn">{n2(V['ytd'])}%</div>
    <div class="d">от минимума 20.07 (1 898,5) — <span class="up">+28,1%</span></div></div>
</div>

<div class="card verdict">
  <div class="tag">Резюме</div>
  <div class="big am" style="font-size:22px;line-height:1.35;margin-top:4px">
  Восходящий импульс не сломан, но цена упёрлась в «стену» 2 445–2 525 — здесь покупать уже поздно, лучше ждать откат</div>
  <p style="margin-top:10px">9 октября индекс пробил вверх трёхмесячный боковик 2 225–2 383 (+3,8% за сессию) и удержался выше 2 400; пятница прошла на повышенном объёме (86 млрд ₽ в пятницу против
  среднедневных 74,6 млрд), закрепился выше SMA20/SMA50 и закрыл неделю на максимуме с середины июня. Но прямо над ценой
  стоит плотный кластер сопротивления: верхняя полоса Боллинджера (2 445), EMA200 (2 452), 50% коррекции падения
  2 912 → 1 899 (2 461), круглые 2 500, SMA200 (2 515) и цель аналитиков 2 510. Стохастик на дневке уже 93 (перекуплен),
  RSI 64,9 — есть запас, но не бесконечный. До опорного заседания ЦБ 23 октября рынок, вероятнее всего, останется в
  диапазоне <b>2 340–2 470</b>.</p>
  <p><b>Практический вывод:</b> рыночными заявками «в лоб» на текущих 2 431 позицию лучше не набирать. Оптимально —
  лимитные покупки в зоне <b>2 365–2 400</b> (первая очередь) и <b>2 335–2 355</b> (вторая), либо вход по факту
  дневного закрытия выше <b>2 470</b>. Подробности — в разделе «Где ставить заявку».</p>
</div>

<div class="toc">
  <a href="#snap">Срез рынка</a><a href="#chart">Графики</a><a href="#ind">Индикаторы</a>
  <a href="#levels">Уровни</a><a href="#ladder">Карта уровней</a><a href="#scen">Сценарии</a>
  <a href="#orders">Где ставить заявку</a><a href="#cal">Календарь</a><a href="#risk">Риски</a>
</div>
"""

SNAP = f"""
<h2 id="snap"><span class="n">1</span>Срез рынка: что произошло</h2>
<div class="grid g2">
<div class="card" style="margin:0">
  <h3 style="margin-top:0">Факты недели (13–16.10)</h3>
  <ul>
    <li>Пятница: <b>+1,65%</b>, закрытие 2 431,07 (IMOEX2) / 2 426,09 (основная сессия) — лучший результат с 18 июня.</li>
    <li>Максимум недели <b>2 445,64</b> (14.10), минимум <b>2 374,48</b> (12.10). Объём пятницы — 86,0 млрд ₽, 1,15× к среднему за 20 дней.</li>
    <li>Лидеры пятницы: Полюс +6%, ВК +4,1%, НОВАТЭК +4%, Интер РАО +3,7%, ФосАгро +3,5%, Позитив +3,4%.</li>
    <li>Неделя для IMOEX2: <b>+1,2%</b>, для RTS — <b>+2,8%</b> (валюта помогла), RGBI +0,7%.</li>
  </ul>
</div>
<div class="card" style="margin:0">
  <h3 style="margin-top:0">Драйверы</h3>
  <ul>
    <li><b>Геополитика:</b> «дизельная сделка» РФ–США, обсуждение смягчения санкций против «теневого флота», заявления Д. Трампа об урегулировании — рынок закладывает снижение санкционного давления.</li>
    <li><b>Нефть:</b> Brent выше <b>$107</b> (пик с середины сентября $107,3), сопротивление $107,5 и сентябрьский пик $109,97.</li>
    <li><b>Рубль:</b> CNY/RUB 12,46 (−1,8% за неделю), доллар ЦБ 83,62. Сильный рубль — плюс для RTS, минус для рублёвой выручки экспортёров.</li>
    <li><b>Ставка:</b> ключевая 14%, длинные ОФЗ ~16,7%. Опорное заседание ЦБ — <b>пятница, 23 октября</b>: консенсус «сохранить 14%», альтернатива — символические −25 б.п.</li>
  </ul>
</div>
</div>
"""

CHARTS = f"""
<h2 id="chart"><span class="n">2</span>Графики с уровнями</h2>
<div class="chart">{A['chart_d']}
<div class="cap">Дневной график IMOEX, 150 сессий (19.03.2026 — 16.10.2026). Красные/оранжевые/жёлтые полосы — зоны сопротивления,
зелёные — зоны поддержки. Жёлтая линия — SMA20, фиолетовая — SMA50, красная пунктирная — SMA200 (2 515),
оранжевая пунктирная — EMA200 (2 452), голубая лента — Боллинджер (20, 2σ).</div></div>

<div class="grid g2">
  <div class="chart" style="margin:0">{A['rsi']}<div class="cap">RSI(14) = {n1(V['rsi'])} — зона уверенного роста, до перекупленности (>70) ещё есть запас, но осциллятор выше 60 уже пятую сессию подряд.</div></div>
  <div class="chart" style="margin:0">{A['macd']}<div class="cap">MACD {n1(V['macd'])} выше сигнальной {n1(V['macd_sig'])} (гистограмма +{n1(V['macd_hist'])}) — бычий импульс сохраняется, но столбики почти перестали расти: импульс выдыхается.</div></div>
</div>

<div class="chart">{A['chart_w']}
<div class="cap">Недельный график, 94 недели. Видна вся картина: пик 3 371 (февраль 2025) → обвал к 1 898,5 (20.07.2026) → отскок на 28%.
Цена вернулась выше недельных SMA10 (2 259) и SMA20 (2 269), недельная SMA30 (2 407) пройдена вверх на этой неделе —
закрепление над ней открывает дорогу к 2 500–2 550.</div></div>

<div class="chart">{A['vp']}
<div class="cap">Профиль объёма за 120 сессий. Главный «магнит» и опора — узел <b>2 250–2 300</b> (там проторговано больше всего),
второй — <b>2 400–2 425</b>. Выше 2 450 объёмов почти нет: это «воздушный карман», поэтому пробой 2 470 может дать быстрое
движение к 2 500–2 525. Ниже 2 200 — тоже разреженное пространство.</div></div>
"""

IND = f"""
<h2 id="ind"><span class="n">3</span>Индикаторы: сводная таблица</h2>
<table>
<thead><tr><th>Индикатор</th><th class="n">Значение</th><th>Интерпретация</th><th>Сигнал</th></tr></thead>
<tbody>
<tr><td>Цена vs SMA20 (2 326,9)</td><td class="n">+4,5%</td><td>Цена далеко выше средней — краткосрочно перегрета</td><td><span class="badge b-r">осторожно</span></td></tr>
<tr><td>Цена vs SMA50 (2 257,7)</td><td class="n">+7,7%</td><td>Средний тренд восходящий, SMA50 развернулась вверх</td><td><span class="badge b-s">покупка</span></td></tr>
<tr><td>Цена vs SMA100 (2 282,0)</td><td class="n">+6,5%</td><td>Пройдена вверх 13.10 — структурный плюс</td><td><span class="badge b-s">покупка</span></td></tr>
<tr><td>Цена vs EMA200 (2 452,4)</td><td class="n">−0,9%</td><td><b>Первое серьёзное сопротивление</b>, тестируется прямо сейчас</td><td><span class="badge b-r">сопротивление</span></td></tr>
<tr><td>Цена vs SMA200 (2 515,3)</td><td class="n">−3,4%</td><td>Долгосрочный тренд нисходящий: цена ниже SMA200 с 23.04.2026</td><td><span class="badge b-r">медвежий фон</span></td></tr>
<tr><td>SMA20 vs SMA50</td><td class="n">2 326,9 / 2 257,7</td><td>SMA20 выше SMA50 с 29 сентября — бычья конфигурация малых средних</td><td><span class="badge b-s">покупка</span></td></tr>
<tr><td>RSI(14) дневной</td><td class="n">{n1(V['rsi'])}</td><td>Бычья зона 55–70, дивергенций с ценой нет</td><td><span class="badge b-s">покупка</span></td></tr>
<tr><td>Stochastic (14,3,3)</td><td class="n">93,4 / 84,8</td><td>%K глубоко в перекупленности — высока вероятность 2–4 дневной паузы/отката</td><td><span class="badge b-r">перекуплен</span></td></tr>
<tr><td>MACD (12,26,9)</td><td class="n">{n1(V['macd'])} / {n1(V['macd_sig'])}</td><td>Выше нуля и выше сигнала; гистограмма +9,6, но растёт медленнее, чем 13–14.10</td><td><span class="badge b-s">покупка</span></td></tr>
<tr><td>Боллинджер (20, 2σ)</td><td class="n">2 445,4 / 2 326,9 / 2 208,3</td><td>Закрытие в 14 п. от верхней границы, ширина ленты 10,2% — волатильность расширяется после сжатия</td><td><span class="badge b-n">нейтрально</span></td></tr>
<tr><td>ATR(14)</td><td class="n">{n1(V['atr'])} п. ({n2(V['atrp'])}%)</td><td>Средний дневной ход — ориентиры для стопов: 1×ATR ≈ 43 п., 1,5×ATR ≈ 65 п.</td><td><span class="badge b-i">риск-менеджмент</span></td></tr>
<tr><td>Ишимоку (9/26/52)</td><td class="n">2 372,8 / 2 335,2 / 2 354,0 / 2 248,6</td><td>Цена выше облака, Тенкан > Киджун — тренд вверх; облако 2 249–2 354 = зона поддержки</td><td><span class="badge b-s">покупка</span></td></tr>
<tr><td>Объём</td><td class="n">86,0 млрд ₽</td><td>1,15× к среднему за 20 дней — пробой подтверждён, но не «кульминационно»</td><td><span class="badge b-s">покупка</span></td></tr>
<tr><td>Недельные SMA10/20/30</td><td class="n">2 258,5 / 2 269,4 / 2 406,7</td><td>Цена выше всех трёх — недельный тренд развернулся вверх</td><td><span class="badge b-s">покупка</span></td></tr>
</tbody></table>
<div class="note">Итог по индикаторам: <b>7 сигналов «покупка», 4 «осторожно/сопротивление», 1 нейтральный</b>.
Тренд вверх подтверждён, но точка входа «здесь и сейчас» плохая: перекупленный стохастик + цена в 4,5% от SMA20 +
сопротивление EMA200 в 20 пунктах выше. Классическая ситуация «тренд бычий, момент — нет».</div>
"""

LEVELS = f"""
<h2 id="levels"><span class="n">4</span>Уровни: сопротивления и поддержки</h2>
<h3>Сопротивления (сверху вниз)</h3>
<table>
<thead><tr><th class="n">Зона</th><th>Из чего состоит</th><th>Сила</th><th>Что означает пробой</th></tr></thead>
<tbody>
<tr><td class="n"><b>2 690–2 700</b></td><td>Fib 78,6% от падения 2 912 → 1 898,5 (2 695); закрытие сентября 2 695</td><td><span class="badge b-r">цель 2027</span></td><td>смена годового тренда</td></tr>
<tr><td class="n"><b>2 630–2 660</b></td><td>Закрытие апреля (2 658), зона апрельского предложения и закрытия апреля 2 658</td><td><span class="badge b-r">сильное</span></td><td>выход к 2 700</td></tr>
<tr><td class="n"><b>2 550–2 566</b></td><td>Максимум 16.06 (2 550,1) + закрытие мая (2 565,6)</td><td><span class="badge b-r">сильное</span></td><td>подтверждение разворота года</td></tr>
<tr><td class="n"><b>2 500–2 525</b></td><td>Круглый уровень 2 500 · <b>SMA200 = 2 515,3</b> · Fib 61,8% = 2 524,9 · цель аналитиков 2 510 · закрытие октября 2025 = 2 525</td><td><span class="badge b-r">ключевое</span></td><td>переход индекса в бычий долгосрочный режим</td></tr>
<tr><td class="n"><b>2 445–2 470</b></td><td>Максимум недели 2 445,6 · <b>EMA200 = 2 452,4</b> · верхняя BB = 2 445,4 · Fib 50% = 2 405–2 461 · пивот R2 = 2 469,3</td><td><span class="badge b-n">ближайшее ключевое</span></td><td>открывает «воздушный карман» до 2 500</td></tr>
<tr><td class="n"><b>2 439–2 445</b></td><td>Хай пятницы 2 439,2 + верхняя полоса Боллинджера</td><td><span class="badge b-n">локальное</span></td><td>продолжение импульса к 2 470</td></tr>
</tbody></table>

<h3>Поддержки (сверху вниз)</h3>
<table>
<thead><tr><th class="n">Зона</th><th>Из чего состоит</th><th>Сила</th><th>Что означает пробой вниз</th></tr></thead>
<tbody>
<tr><td class="n"><b>2 400–2 412</b></td><td>Круглые 2 400 · пивот пятницы 2 420,1 · S1 2 401 · Fib 50% отскока 2 405 · основание консолидации 9–16.10</td><td><span class="badge b-s">первая</span></td><td>откат к 2 370, сценарий «боковик»</td></tr>
<tr><td class="n"><b>2 370–2 385</b></td><td>S2 пивота 2 370,9 · Тенкан-сен 2 372,8 · SMA10 2 375 · минимум 15.10 (2 383,7) · нижняя граница гэпа недели</td><td><span class="badge b-s">средняя</span></td><td>тест середины Боллинджера</td></tr>
<tr><td class="n"><b>2 335–2 355</b></td><td><b>Середина BB 2 326,9</b> · Киджун-сен 2 335,2 · Сенкоу A 2 354,0 · уровень, который аналитики называют главной краткосрочной поддержкой · верхняя граница сентябрьского боковика</td><td><span class="badge b-s">ключевая</span></td><td>слом восходящей структуры, цель 2 280</td></tr>
<tr><td class="n"><b>2 280–2 300</b></td><td>EMA50 2 299,1 · <b>максимальный узел объёма 2 250–2 300</b> · Fib 38,2% = 2 285,7 · недельная SMA20 (2 269) рядом · Сенкоу B 2 248,6</td><td><span class="badge b-s">очень сильная</span></td><td>возврат в трёхмесячный боковик</td></tr>
<tr><td class="n"><b>2 225–2 250</b></td><td>Минимумы 22.09 (2 245,9) и 29.09 (2 224,8) · нижняя BB 2 208,3 · психологические 2 200</td><td><span class="badge b-s">сильная</span></td><td>риск ухода к 2 140–2 100</td></tr>
<tr><td class="n"><b>2 117–2 140</b></td><td>Минимум 07.07 (2 117,5) · Fib 23,6% = 2 137,7</td><td><span class="badge b-g">глубокая</span></td><td>отмена бычьего сценария</td></tr>
<tr><td class="n"><b>1 898–1 958</b></td><td>Дно 20.07.2026 (1 898,5) и 17.07 (1 958,4)</td><td><span class="badge b-g">экстремум года</span></td><td>—</td></tr>
</tbody></table>

<h3>Коррекции Фибоначчи падения 2 912,0 (09.03.2026) → 1 898,5 (20.07.2026)</h3>
<table>
<thead><tr><th>Уровень</th><th class="n">Значение</th><th>Статус</th></tr></thead>
<tbody>
<tr><td>23,6%</td><td class="n">2 137,7</td><td>пройден 24.08</td></tr>
<tr><td>38,2%</td><td class="n">2 285,7</td><td>пройден 05.10, теперь поддержка</td></tr>
<tr><td><b>50,0%</b></td><td class="n"><b>2 405,3</b></td><td><b>здесь и сейчас — цена выше с 13.10</b></td></tr>
<tr><td>61,8%</td><td class="n">2 524,9</td><td>главная цель роста, совпадает с SMA200</td></tr>
<tr><td>78,6%</td><td class="n">2 695,1</td><td>цель при закреплении выше 2 525</td></tr>
</tbody></table>
"""

LADDER = """
<h2 id="ladder"><span class="n">5</span>Карта уровней одним взглядом</h2>
<div class="ladder">
  <div class="rung res"><div class="p dn">2 695</div><div class="t">Fib 78,6% — цель «большого» разворота</div></div>
  <div class="rung res"><div class="p dn">2 550–2 566</div><div class="t">максимум июня + закрытие мая</div></div>
  <div class="rung res"><div class="p dn">2 500–2 525</div><div class="t"><b>SMA200 (2 515) · Fib 61,8% · круглый 2 500 · цель аналитиков 2 510</b></div></div>
  <div class="rung res"><div class="p dn">2 445–2 470</div><div class="t"><b>EMA200 (2 452) · верхняя Боллинджер (2 445) · Fib 50% (2 461) · хай недели (2 445,6)</b> — главная преграда</div></div>
  <div class="rung res"><div class="p am">2 439</div><div class="t">хай пятницы 16.10 — ближайший триггер</div></div>
  <div class="rung now"><div class="p ye">2 431,07</div><div class="t">ТЕКУЩАЯ ЦЕНА (IMOEX2, закрытие 16.10.2026)</div></div>
  <div class="rung sup"><div class="p up">2 400–2 412</div><div class="t">пивот 2 420 · S1 2 401 · Fib 50% отскока — <b>зона заявки №1</b></div></div>
  <div class="rung sup"><div class="p up">2 370–2 385</div><div class="t">Тенкан 2 373 · SMA10 2 375 · S2 2 371 — <b>зона заявки №2</b></div></div>
  <div class="rung sup"><div class="p up">2 335–2 355</div><div class="t">середина BB 2 327 · Киджун 2 335 · Сенкоу A 2 354 — <b>зона заявки №3, последняя для лонга</b></div></div>
  <div class="rung sup"><div class="p up">2 280–2 300</div><div class="t">EMA50 2 299 · самый плотный узел объёма · Fib 38,2% — «тяжёлая» поддержка</div></div>
  <div class="rung sup"><div class="p up">2 225–2 250</div><div class="t">минимумы сентября · нижняя BB 2 208 — здесь стоп для среднесрочного лонга</div></div>
  <div class="rung sup"><div class="p up">2 117–2 138</div><div class="t">минимум июля · Fib 23,6% — отмена бычьей картины</div></div>
  <div class="rung sup"><div class="p up">1 898</div><div class="t">дно 2026 года</div></div>
</div>
"""

SCEN = f"""
<h2 id="scen"><span class="n">6</span>Сценарии на 1–4 недели</h2>
<div class="grid g3">
  <div class="scen"><span class="prob">вероятность ~35%</span>
    <div class="t up">A. Пробой и уход к 2 500+</div>
    <p style="font-size:14px">Триггер: дневное закрытие выше <b>2 470</b> на объёме &gt;90 млрд ₽ и/или позитив по санкциям
    (снятие ограничений с «теневого флота», сдвиг в переговорах) + мягкий ЦБ 23 октября.</p>
    <p style="font-size:14px">Цели: <span class="pill">2 500</span><span class="pill">2 525 (SMA200/Fib 61,8%)</span>
    <span class="pill">2 550–2 566</span> далее <span class="pill">2 630</span><span class="pill">2 695</span></p>
    <p style="font-size:14px">Между 2 470 и 2 500 объёмов почти нет — движение может быть быстрым (2–4 сессии).</p>
  </div>
  <div class="scen"><span class="prob">вероятность ~40% (база)</span>
    <div class="t am">B. Консолидация 2 340–2 470</div>
    <p style="font-size:14px">Рынок «переваривает» рост +28% от дна и ждёт ЦБ 23 октября. Геополитика даёт новости
    порциями, Brent держится $105–108, рубль стабилен.</p>
    <p style="font-size:14px">Тактика: торговля от границ диапазона — покупка у 2 350–2 380, фиксация у 2 440–2 460.
    Ориентир аналитика Freedom Global на понедельник: <b>2 350–2 450</b>.</p>
    <p style="font-size:14px">Длительность: 1–3 недели; сжатие волатильности (ширина BB уже 10,2%) обычно заканчивается
    импульсом — следим за направлением выхода.</p>
  </div>
  <div class="scen"><span class="prob">вероятность ~25%</span>
    <div class="t dn">C. Откат к 2 280–2 250</div>
    <p style="font-size:14px">Триггер: жёсткая риторика ЦБ 23 октября (или отказ от снижения при росте инфляционных
    ожиданий), срыв санкционных договорённостей, Brent ниже $104,9, закрытие дня ниже <b>2 335</b>.</p>
    <p style="font-size:14px">Цели: <span class="pill">2 335</span><span class="pill">2 300</span>
    <span class="pill">2 280 (EMA50 + объём)</span><span class="pill">2 250</span> экстремум — <span class="pill">2 200</span></p>
    <p style="font-size:14px">Сильный рубль (CNY/RUB &lt; 12,3) дополнительно давит на рублёвую выручку экспортёров —
    негатив для индекса при прочих равных.</p>
  </div>
</div>
"""

ORDERS = f"""
<h2 id="orders"><span class="n">7</span>Где ставить заявку</h2>
<div class="warn"><b>Главное правило текущей точки.</b> Цена 2 431 — это 4,5% выше SMA20, стохастик 93, в 21 пункте выше
стоит EMA200, а в 84 пунктах — SMA200. Покупать рыночной заявкой в такой позиции — значит заведомо брать худший R/R.
Заявки ставим <b>ниже рынка</b> (на откат) либо <b>выше рынка</b> (на подтверждённый пробой), но не «в лоб».</div>

<div class="grid g2">
<div class="setup">
  <div class="hd hd-long"><span>🟢 Сетап №1 — основной: лимитная покупка на откате</span><span class="badge b-s">тренд + уровень</span></div>
  <div class="bd">
    <div class="row"><div class="k">Инструмент</div><div class="val">IMOEX через фьючерс Mix (MX-12.26), биржевой ETF/БПИФ на индекс, либо корзина ликвидных бумаг индекса (Сбер, Лукойл, Газпром нефть, НОВАТЭК, Полюс)</div></div>
    <div class="row"><div class="k">Очередь 1 (40%)</div><div class="val"><span class="pill">лимит 2 395–2 405</span> — пивот 2 420/S1 2 401/Fib 50% отскока; сработает уже на обычном дневном откате (ATR = 43 п.)</div></div>
    <div class="row"><div class="k">Очередь 2 (35%)</div><div class="val"><span class="pill">лимит 2 365–2 375</span> — Тенкан 2 373 + SMA10 2 375 + S2 2 371</div></div>
    <div class="row"><div class="k">Очередь 3 (25%)</div><div class="val"><span class="pill">лимит 2 340–2 352</span> — середина Боллинджера 2 327 + Киджун 2 335 + Сенкоу A 2 354. Это последняя ступень: ниже — уже сценарий C</div></div>
    <div class="row"><div class="k">Средняя входа</div><div class="val">≈ <b>2 375</b> при исполнении всех трёх очередей</div></div>
    <div class="row"><div class="k">Стоп</div><div class="val"><span class="pill">2 278</span> — дневное закрытие ниже 2 280 (EMA50 + узел объёма + Fib 38,2%). Для фьючерса — жёсткий стоп-лосс 2 275. Риск ≈ 100 п. ≈ 4,2% ≈ 2,3×ATR</div></div>
    <div class="row"><div class="k">Цели</div><div class="val">T1 <span class="pill">2 445</span> (фиксировать 40%) · T2 <span class="pill">2 510–2 525</span> (SMA200/Fib 61,8%, фиксировать 40%) · T3 <span class="pill">2 560</span> и <span class="pill">2 690</span> (остаток, трейлинг по SMA20)</div></div>
    <div class="row"><div class="k">R/R</div><div class="val"><b>1 : 1,4</b> до T1 · <b>1 : 2,4</b> до T2 · <b>1 : 3,2</b> до T3 — считается от средней 2 375</div></div>
    <div class="row"><div class="k">Срок</div><div class="val">2–8 недель</div></div>
    <div class="row"><div class="k">Отмена</div><div class="val">если дневное закрытие ниже <b>2 335</b> — заявку 3-й очереди снимаем и ждём 2 280–2 300</div></div>
  </div>
</div>

<div class="setup">
  <div class="hd hd-wait"><span>🟠 Сетап №2 — покупка на пробое (если отката не дали)</span><span class="badge b-n">подтверждение</span></div>
  <div class="bd">
    <div class="row"><div class="k">Триггер</div><div class="val">дневное закрытие <b>выше 2 470</b> (EMA200 + верхняя BB + Fib 50% позади) при объёме ≥ 90 млрд ₽ и без «падающей звезды»/доджи на следующей свече</div></div>
    <div class="row"><div class="k">Вход</div><div class="val"><span class="pill">стоп-лимит 2 472–2 480</span> или лимитка на ретесте <span class="pill">2 455–2 465</span> (бывшее сопротивление = поддержка)</div></div>
    <div class="row"><div class="k">Стоп</div><div class="val"><span class="pill">2 388</span> — под основание пробойной консолидации и под S1 2 401 (риск ≈ 85 п. ≈ 3,5%)</div></div>
    <div class="row"><div class="k">Цели</div><div class="val">T1 <span class="pill">2 500</span> · T2 <span class="pill">2 525</span> (SMA200 + Fib 61,8% — здесь обязательна частичная фиксация) · T3 <span class="pill">2 560</span> · T4 <span class="pill">2 630</span></div></div>
    <div class="row"><div class="k">R/R</div><div class="val">1 : 0,4 до T1 · <b>1 : 0,7</b> до T2 · <b>1 : 1,5</b> до T3 — вход хуже, чем в сетапе №1, зато вероятность выше</div></div>
    <div class="row"><div class="k">Важно</div><div class="val">SMA200 (2 515) — выше неё индекс не закрывался с 23 апреля 2026 (около 120 сессий подряд ниже). Первый подход к годовой средней редко заканчивается пробоем: фиксируйте часть и переводите стоп в безубыток на 2 500</div></div>
  </div>
</div>

<div class="setup">
  <div class="hd hd-short"><span>🔴 Сетап №3 — шорт (только контртрендовый, спекулятивный)</span><span class="badge b-r">высокий риск</span></div>
  <div class="bd">
    <div class="row"><div class="k">Условие</div><div class="val">не шортить «против тренда по факту уровня» — нужен сигнал: разворотная свеча (пин-бар/поглощение) в зоне <b>2 500–2 525</b> на объёме + RSI &gt; 70 + медвежья дивергенция по RSI/MACD</div></div>
    <div class="row"><div class="k">Вход</div><div class="val"><span class="pill">2 505–2 520</span> после подтверждения, не раньше</div></div>
    <div class="row"><div class="k">Стоп</div><div class="val"><span class="pill">2 562</span> — выше максимума 16.06 (2 550) с буфером 0,5×ATR</div></div>
    <div class="row"><div class="k">Цели</div><div class="val">T1 <span class="pill">2 445</span> · T2 <span class="pill">2 400</span> · T3 <span class="pill">2 350</span></div></div>
    <div class="row"><div class="k">R/R</div><div class="val">1 : 1,3 до T1 · 1 : 2,2 до T2 · 1 : 3,5 до T3</div></div>
    <div class="row"><div class="k">Альтернатива</div><div class="val">если не хотите шортить индекс — просто <b>зафиксируйте часть longs у 2 500–2 525</b> и переведите стоп в безубыток. Это тот же эффект без риска контртрендовой позиции</div></div>
  </div>
</div>

<div class="setup">
  <div class="hd hd-wait"><span>⚪ Сетап №4 — покупка на слабости (если придёт сценарий C)</span><span class="badge b-i">терпение</span></div>
  <div class="bd">
    <div class="row"><div class="k">Зона</div><div class="val"><span class="pill">2 280–2 300</span> (EMA50 + главный узел объёма + Fib 38,2%) и <span class="pill">2 225–2 250</span> (нижняя BB + минимумы сентября)</div></div>
    <div class="row"><div class="k">Фильтр</div><div class="val">входить только после разворотной дневной свечи и возврата цены выше 2 300; «ловить ножи» на новостях о ставке не нужно</div></div>
    <div class="row"><div class="k">Стоп</div><div class="val"><span class="pill">2 195</span> (под нижнюю BB и 2 200) — риск ≈ 4%</div></div>
    <div class="row"><div class="k">Цели</div><div class="val"><span class="pill">2 350</span> · <span class="pill">2 440</span> · <span class="pill">2 510</span></div></div>
    <div class="row"><div class="k">R/R</div><div class="val">1 : 1,1 · 1 : 2,1 · 1 : 2,9 — математически лучшая точка всего отчёта, но она может и не прийти</div></div>
  </div>
</div>
</div>

<h3>Размер позиции и риск</h3>
<table>
<thead><tr><th>Параметр</th><th>Рекомендация</th><th>Пояснение</th></tr></thead>
<tbody>
<tr><td>Риск на сделку</td><td class="n"><b>≤ 1% депозита</b></td><td>при стопе 100 п. (сетап №1) на 1 млн ₽ портфеля = 10 тыс ₽ риска → объём позиции ≈ 237 тыс ₽ (плечо не используется)</td></tr>
<tr><td>Объём позиции</td><td class="n">10–25% портфеля</td><td>индексный инструмент (фьючерс MX/ETF), набираемый тремя очередями, а не одним ордером</td></tr>
<tr><td>Ширина стопа</td><td class="n">≥ 1,5 × ATR = 65 п.</td><td>стоп ближе 65 пунктов на текущей волатильности выбивается шумом</td></tr>
<tr><td>Тип заявки</td><td class="n">лимитная / стоп-лимит</td><td>рыночные — только на пробое с подтверждением; на вечерней и выходной сессии спреды шире</td></tr>
<tr><td>Перенос через выходные</td><td class="n">уменьшить позицию</td><td>главный риск — геополитические новости сб–вс; Мосбиржа торгует в выходные 10:00–19:00, гэп возможен в обе стороны</td></tr>
<tr><td>Фиксация</td><td class="n">частями: 40/40/20</td><td>у 2 445, у 2 510–2 525, остаток с трейлингом по SMA20 (сейчас 2 327 и быстро растёт)</td></tr>
</tbody></table>
<div class="note"><b>Коротко, если нужен один ответ:</b> ставьте лимитную заявку на покупку
<span class="pill">2 395–2 405</span> первой очередью и <span class="pill">2 340–2 355</span> второй,
стоп на закрытии дня ниже <span class="pill">2 280</span>, цели <span class="pill">2 445</span> →
<span class="pill">2 510–2 525</span> → <span class="pill">2 560+</span>.
Если цена уйдёт вверх без вас — входите только после дневного закрытия выше <span class="pill">2 470</span>.</div>
"""

CAL = f"""
<h2 id="cal"><span class="n">8</span>Календарь: что двигает индекс на следующей неделе</h2>
<table>
<thead><tr><th>Дата</th><th>Событие</th><th>Почему важно для IMOEX</th></tr></thead>
<tbody>
<tr><td class="n">Пн 20.10</td><td>Старт недели, ориентир аналитиков 2 350–2 450</td><td>проверка на удержание 2 400 после пятничного рывка; выходная сессия Мосбиржи уже может дать гэп</td></tr>
<tr><td class="n">Вт 21.10</td><td>МСФО ФосАгро за 9 мес.; отчётность Северстали на неделе; операционные результаты Европлана и Глоракса</td><td>ФосАгро и Северсталь — кандидаты на промежуточные дивиденды; дивидендный фактор сейчас поддерживает рынок</td></tr>
<tr><td class="n">Ср–Чт</td><td>Совет директоров Газпрома (поправки в бюджет и инвестпрограмму-2026), акционеры Акрона (дивиденды), ТГК-1 (допэмиссия); индекс цен производителей за сентябрь</td><td>Газпром — ~13% веса индекса, любые сигналы по инвестпрограмме двигают IMOEX</td></tr>
<tr><td class="n"><b>Пт 23.10</b></td><td><b>Опорное заседание ЦБ РФ по ключевой ставке (сейчас 14%) + пресс-конференция + резюме</b></td><td><b>Главное событие недели.</b> Консенсус — сохранение 14%, альтернатива −25 б.п. Мягкий тон = плюс для акций и минус для рубля; жёсткий тон = откат к 2 335 и ниже. Длинные ОФЗ сейчас ~16,7% — альтернативная доходность высока</td></tr>
<tr><td class="n">22.10 / 24.10</td><td>Истекает лицензия Минфина США на переговоры с ЛУКОЙЛом (22.10); лицензии по зарубежным АЗС продлены до 24.04.2027</td><td>ЛУКОЙЛ — крупный вес в индексе и дивидендная история (~9% доходности); новостной фон по санкциям</td></tr>
<tr><td class="n">Фон</td><td>Геополитика: реализация «дизельной сделки» (2–3 недели на процедуры), возможное смягчение санкций против «теневого флота», заявления Трампа/Дмитриева по сотрудничеству (СПГ, Арктик СПГ 2)</td><td>основной драйвер последних трёх недель; любая эскалация — быстрый откат на 3–5%</td></tr>
<tr><td class="n">Фон</td><td>Brent: сопротивление $107,5, сентябрьский пик $109,97; поддержка $104,9</td><td>выше $107 — поддержка для экспортёров и бюджета; слом $104,9 — медвежий сигнал</td></tr>
<tr><td class="n">Фон</td><td>Дивиденды за 9 мес. 2026: ЛУКОЙЛ ~9%, ВИ.РУ 8,5%, Циан 4,9%; делистинг ПИК (торги будут остановлены)</td><td>дивидендный спрос удерживает рынок от глубоких откатов</td></tr>
</tbody></table>
"""

RISK = """
<h2 id="risk"><span class="n">9</span>Риски и что сломает картину</h2>
<div class="grid g2">
<div class="card" style="margin:0">
<h3 style="margin-top:0">Против роста</h3>
<ul>
<li><b>SMA200 (2 515) сверху.</b> Долгосрочный тренд всё ещё нисходящий: индекс на 3,4% ниже годовой средней. Пробой с первой попытки исторически удаётся редко.</li>
<li><b>Жёсткий ЦБ 23.10.</b> Инфляция ускорилась (0,96% за неделю в начале октября из-за индексации тарифов ЖКУ), длинные ОФЗ дают ~16,7% — у акций слабый аргумент «дешевизны».</li>
<li><b>Сильный рубль.</b> CNY/RUB 12,46 и движение к 12,32 — минус для рублёвой выручки и дивидендов экспортёров, которые формируют основу индекса.</li>
<li><b>Геополитический разворот.</b> Весь рост с 20.07 (+28%) построен на ожиданиях деэскалации. Одна негативная новость = откат на 3–5% за сессию (в 2026 году такое уже случалось: −4,2% за день 22.06, −7,5% 16.07).</li>
<li><b>Перегрев короткого момента.</b> Стохастик 93, цена у верхней BB, +4,5% от SMA20 — технический откат на 2–4% статистически вероятен.</li>
<li><b>Brent ниже $104,9</b> — слом структуры в нефти утянет индекс вниз.</li>
</ul>
</div>
<div class="card" style="margin:0">
<h3 style="margin-top:0">За рост</h3>
<ul>
<li><b>Тренд развернулся:</b> цена выше SMA20/50/100, выше недельных SMA10/20/30, выше облака Ишимоку, SMA20 &gt; SMA50.</li>
<li><b>Объём подтверждает:</b> пятничный пробой прошёл на 1,15× среднего объёма, рост недели сопровождался спросом.</li>
<li><b>Профиль объёма:</b> над 2 470 почти нет проторговки — «воздушный карман» до 2 500–2 525.</li>
<li><b>Дивиденды:</b> ЛУКОЙЛ ~9%, ВИ.РУ 8,5%, Циан 4,9% + ожидания по X5, Татнефти, ФосАгро — локальный спрос.</li>
<li><b>Нефть и металлы:</b> Brent &gt; $107, золото ~$4 200 — поддержали Полюс (+6% в пятницу) и нефтегаз.</li>
<li><b>Смягчение санкций:</b> «дизельная сделка», возможные послабления по «теневому флоту», продление лицензий ЛУКОЙЛа до 04.2027.</li>
</ul>
</div>
</div>
<div class="warn" style="margin-top:14px"><b>Триггеры отмены бычьего сценария</b> (фиксируем/переворачиваем позицию):
① дневное закрытие ниже <b>2 335</b> → цель 2 280–2 300; ② дневное закрытие ниже <b>2 280</b> → цель 2 250, затем 2 200;
③ дневное закрытие ниже <b>2 200</b> → восходящая структура с июля сломана, пересматриваем картину полностью.</div>
"""

FOOT = """
<h2><span class="n">10</span>Методика и источники</h2>
<div class="disc">
<p style="margin-top:0"><b>Откуда данные.</b> Котировки и объёмы — ISS Московской биржи
(<code>iss.moex.com</code>), история дневных значений IMOEX с 03.01.2025 по 16.10.2026 (455 сессий).
Расчёт индикаторов — собственный: SMA/EMA, RSI(14) по Уайлдеру, MACD(12,26,9), Боллинджер(20, 2σ), ATR(14),
Stochastic(14,3,3), Ишимоку(9/26/52), классические пивот-уровни, профиль объёма по 120 сессиям, недельная агрегация.</p>
<p><b>Контекст и мнения:</b> Интерфакс (итоги торгов 16.10.2026), Велес Капитал / ФОМАГ (Е. Кожухова, прогноз на неделю —
сопротивление 2 510, поддержка 2 335), Freedom Global (Н. Мильчакова — диапазон понедельника 2 350–2 450),
БКС Мир инвестиций (А. Мамонтов — по нефти), Альфа-Инвестиции (итоги недели 16.10.2026), Банк России (календарь заседаний:
23.10.2026, ставка 14%).</p>
<p><b>Важные оговорки.</b> ① Расчёты ведутся по IMOEX2 (все сессии, закрытие 2 431,07); значение основной сессии 16.10 —
2 426,09, разница ~5 п. несущественна для уровней. ② Мосбиржа торгует в выходные (сб/вс 10:00–19:00) — котировки
могут уйти от пятничных ещё до открытия понедельника. ③ Индекс сам по себе не торгуется: заявки ставятся во фьючерсе Mix (MX),
биржевых фондах на индекс либо в корзине бумаг — учитывайте базис фьючерса, спреды и комиссии.
④ Уровни — это вероятностные зоны, а не гарантии: рынок регулярно проходит их на 1–2% «шумом», поэтому стопы
привязаны к закрытию дня, а не к внутридневному минимуму.</p>
<p style="margin-bottom:0"><b>Дисклеймер.</b> Материал носит исключительно информационно-аналитический характер и не является
индивидуальной инвестиционной рекомендацией. Операции с фьючерсами и инструментами с плечом могут привести к потере всего
капитала. Решения и риск — на инвесторе.</p>
</div>
<div class="foot">Отчёт сформирован 18.10.2026 · данные торгов на 16.10.2026 · все значения индекса в пунктах IMOEX</div>
</div></body></html>
"""

html = HEAD + HEADER + SNAP + CHARTS + IND + LEVELS + LADDER + SCEN + ORDERS + CAL + RISK + FOOT
open('IMOEX_technical_analysis_2026-10-18.html', 'w', encoding='utf-8').write(html)
print('written', len(html), 'bytes')
