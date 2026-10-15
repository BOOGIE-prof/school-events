#!/usr/bin/env python3
"""X-баннер «Құрмет айы» на октябрь 2026 — 80 × 180 см.

Собирает самодостаточный HTML (1 px = 1 мм), из которого делается макет в Figma
и PNG-превью. Шрифт — Montserrat (есть все казахские буквы).

    python3 banners/build_october_banner.py   →  banners/kurmet-ayi-2026-10.html
"""

import calendar
import pathlib

OUT = pathlib.Path(__file__).with_name("kurmet-ayi-2026-10.html")

YEAR, MONTH = 2026, 10
BRAND = "#800080"
BRAND_DARK = "#4d004d"

# Иконки — Lucide (ISC), только контуры 24×24.
ICONS = {
    "card": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>'
            '<path d="M14.8 7.5a1.84 1.84 0 0 0-2.6 0l-.2.3-.3-.3a1.84 1.84 0 1 0-2.4 2.8L12 13l2.7-2.7c.9-.9.8-2.1.1-2.8"/>',
    "tracker": '<path d="m3 17 2 2 4-4"/><path d="m3 7 2 2 4-4"/><path d="M13 6h8"/><path d="M13 12h8"/><path d="M13 18h8"/>',
    "vote": '<path d="m9 12 2 2 4-4"/><path d="M5 7c0-1.1.9-2 2-2h10a2 2 0 0 1 2 2v12H5V7Z"/><path d="M22 19H2"/>',
    "ball": '<path d="M11.1 7.1a16.55 16.55 0 0 1 10.9 4"/><path d="M12 12a12.6 12.6 0 0 1-8.7 5"/>'
            '<path d="M16.8 13.6a16.55 16.55 0 0 1-9 7.5"/><path d="M20.7 17a12.8 12.8 0 0 0-8.7-5 13.3 13.3 0 0 1 0-10"/>'
            '<path d="M6.3 3.8a16.55 16.55 0 0 0 1.9 11.5"/><circle cx="12" cy="12" r="10"/>',
    "quiz": '<path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/>'
            '<path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/>'
            '<path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/>'
            '<path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/>'
            '<path d="M19.938 10.5a4 4 0 0 1 .585.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/>'
            '<path d="M19.967 17.484A4 4 0 0 1 18 18"/>',
    "uni": '<circle cx="12" cy="10" r="1"/><path d="M22 20V8h-4l-6-4-6 4H2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2"/>'
           '<path d="M6 17v.01"/><path d="M6 13v.01"/><path d="M18 17v.01"/><path d="M18 13v.01"/>'
           '<path d="M14 22v-5a2 2 0 0 0-2-2a2 2 0 0 0-2 2v5"/>',
}

# Эмблема Dostyq School (книга), перерисована в вектор по static/emblem.png.
EMBLEM = (
    '<svg width="{s}" height="{s}" viewBox="40 40 418 418" xmlns="http://www.w3.org/2000/svg">'
    '<path fill="{c}" d="M52 112A60 60 0 0 1 112 52L375 52A8 8 0 0 1 383 60L383 312A8 8 0 0 1 375 320'
    'L130 320A48 48 0 0 0 82 368A48 48 0 0 0 130 416L417 416L417 93A8 8 0 0 1 425 85L437 85'
    'A8 8 0 0 1 445 93L445 437A8 8 0 0 1 437 445L107 445A55 55 0 0 1 52 390Z"/>'
    '<path fill="{c}" d="M130 348L375 348A20 20 0 0 1 375 388L130 388A20 20 0 0 1 130 348Z"/>'
    '</svg>'
)


def icon(name, size, color="#fff", stroke=2.2):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" '
            f'xmlns="http://www.w3.org/2000/svg">{ICONS[name]}</svg>')


# Мероприятия: дни, цвет, иконка, дата на плашке, название KZ / RU.
EVENTS = [
    dict(days=range(5, 10), color="#E0457B", icon="card",
         tile="5–9", kz="Рақмет карточкасы", ru="Карточка благодарности"),
    dict(days=range(12, 17), color="#8E2DA8", icon="tracker",
         tile="12–16", kz="Құрмет трекері", ru="Трекер уважения"),
    dict(days=[16], color="#1E88D2", icon="vote",
         tile="16", kz="Президент сайлауы", ru="Выборы президентов"),
    dict(days=[17], color="#F08A1C", icon="ball",
         tile="17", kz="Ата-аналар арасындағы волейбол турнирі", ru="Турнир по волейболу для родителей"),
    dict(days=[21], color="#11A38C", icon="quiz",
         tile="21", kz="Dostyq Quiz — оқушылар арасында", ru="Dostyq Quiz среди учеников"),
    dict(days=[27, 28], color="#4153C4", icon="uni",
         tile="27–28", kz="Астана: университеттерге экскурсия", ru="Поездка в Астану: экскурсия по университетам"),
]

WEEKDAYS = [("Дс", "Пн"), ("Сс", "Вт"), ("Ср", "Ср"), ("Бс", "Чт"), ("Жм", "Пт"), ("Сб", "Сб"), ("Жс", "Вс")]

CELL_W, CELL_H, GAP = 92, 84, 8


def calendar_html():
    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(YEAR, MONTH)
    single = {}
    for ev in EVENTS:
        if len(ev["days"]) <= 2:
            for d in ev["days"]:
                single.setdefault(d, ev)
    ranges = [ev for ev in EVENTS if len(ev["days"]) > 2]

    head = "".join(
        f'<div class="wd{" we" if i >= 5 else ""}"><b>{kz}</b><span>{ru}</span></div>'
        for i, (kz, ru) in enumerate(WEEKDAYS))

    rows = []
    for week in weeks:
        cells = []
        for i, d in enumerate(week):
            if d == 0:
                cells.append('<div class="cell empty"></div>')
                continue
            cls = "cell" + (" we" if i >= 5 else "")
            ev = single.get(d)
            if ev:
                cells.append(
                    f'<div class="{cls} hit" style="background:{ev["color"]}">'
                    f'<span class="num">{d}</span><span class="ic">{icon(ev["icon"], 34)}</span></div>')
            else:
                cells.append(f'<div class="{cls}"><span class="num">{d}</span></div>')
        bars = []
        for ev in ranges:
            idx = [i for i, d in enumerate(week) if d in ev["days"]]
            if idx:
                left = idx[0] * (CELL_W + GAP)
                width = len(idx) * CELL_W + (len(idx) - 1) * GAP
                # Последний день недели-мероприятия может быть занят одиночным событием (16-е) —
                # полоса тогда заканчивается перед ним.
                if week[idx[-1]] in single:
                    width -= CELL_W + GAP
                bars.append(
                    f'<div class="bar" style="left:{left}px;width:{width}px;background:{ev["color"]}">'
                    f'{icon(ev["icon"], 22, stroke=2.4)}<span>{ev["kz"]}</span></div>')
        rows.append(f'<div class="week">{"".join(cells)}{"".join(bars)}</div>')
    return f'<div class="wds">{head}</div><div class="weeks">{"".join(rows)}</div>'


def events_html():
    items = []
    for ev in EVENTS:
        items.append(
            f'<div class="ev">'
            f'<div class="tile" style="background:{ev["color"]}">{icon(ev["icon"], 26)}'
            f'<div><b>{ev["tile"]}</b><span>ҚАЗ · ОКТ</span></div></div>'
            f'<div class="what"><b>{ev["kz"]}</b><span>{ev["ru"]}</span></div>'
            f'</div>')
    return "".join(items)


CSS = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ background: #fff; }}
body {{ font-family: 'Montserrat', sans-serif; color: #241a26; }}
.banner {{ width: 800px; height: 1800px; position: relative; overflow: hidden; background: #fbf7fb;
  display: flex; flex-direction: column; }}

.hero {{ position: relative; height: 520px; flex: none; overflow: hidden; color: #fff;
  background: linear-gradient(160deg, #9a1a9a 0%, {BRAND} 45%, {BRAND_DARK} 100%);
  border-radius: 0 0 64px 64px; padding: 52px 56px 0; }}
.ring {{ position: absolute; border-radius: 50%; border: 34px solid rgba(255,255,255,.07); }}
.r1 {{ width: 520px; height: 520px; right: -210px; top: -190px; }}
.r2 {{ width: 280px; height: 280px; left: -170px; top: 300px; border-width: 24px; }}
.logo {{ display: flex; align-items: center; gap: 16px; position: relative; }}
.logo .wm b {{ display: block; font-size: 46px; font-weight: 900; line-height: 1; letter-spacing: 1px; }}
.logo .wm span {{ display: block; font-size: 17px; font-weight: 600; letter-spacing: 13.4px; margin-top: 4px; }}
.month {{ position: absolute; right: 56px; top: 62px; text-align: right; }}
.month b {{ display: block; font-size: 30px; font-weight: 800; letter-spacing: 3px; }}
.month span {{ display: block; font-size: 20px; font-weight: 500; opacity: .8; letter-spacing: 2px; margin-top: 2px; }}
.eyebrow {{ position: relative; margin-top: 40px; display: inline-flex; gap: 12px; align-items: center;
  background: rgba(255,255,255,.14); border-radius: 40px; padding: 10px 22px;
  font-size: 18px; font-weight: 700; letter-spacing: 2.4px; }}
.eyebrow i {{ width: 8px; height: 8px; border-radius: 50%; background: #FFC94A; display: block; }}
.title {{ position: relative; margin-top: 22px; font-size: 140px; font-weight: 900; line-height: 126px;
  letter-spacing: -2px; }}
.title .l2 {{ display: flex; align-items: center; gap: 26px; }}
.title .y {{ color: #FFC94A; }}
.title .sub {{ font-size: 40px; line-height: 44px; font-weight: 700; letter-spacing: 0; padding-top: 14px;
  border-left: 5px solid rgba(255,255,255,.35); padding-left: 24px; }}

.cal {{ padding: 30px 54px 0; flex: none; }}
.sec {{ display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 14px; }}
.sec b {{ font-size: 32px; font-weight: 900; color: {BRAND}; letter-spacing: 1px; }}
.sec span {{ font-size: 21px; font-weight: 600; color: #8a7a8c; }}
.wds {{ display: grid; grid-template-columns: repeat(7, {CELL_W}px); gap: {GAP}px; margin-bottom: {GAP}px; }}
.wd {{ text-align: center; background: {BRAND}; color: #fff; border-radius: 14px; padding: 6px 0 5px; }}
.wd.we {{ background: #b783b7; }}
.wd b {{ display: block; font-size: 21px; font-weight: 800; line-height: 1.1; }}
.wd span {{ display: block; font-size: 15px; font-weight: 500; opacity: .85; }}
.weeks {{ display: flex; flex-direction: column; gap: {GAP}px; }}
.week {{ position: relative; display: grid; grid-template-columns: repeat(7, {CELL_W}px); gap: {GAP}px; }}
.cell {{ height: {CELL_H}px; border-radius: 16px; background: #fff; border: 2px solid #eadcea; position: relative; }}
.cell.we {{ background: #f3eaf3; border-color: #f3eaf3; }}
.cell.empty {{ background: transparent; border: 2px dashed #eadcea; }}
.cell .num {{ position: absolute; left: 11px; top: 3px; font-size: 30px; font-weight: 800; color: #3a2a3c; }}
.cell.we .num {{ color: #9b7d9d; }}
.cell.hit {{ border: none; }}
.cell.hit .num {{ color: #fff; }}
.cell .ic {{ position: absolute; right: 9px; bottom: 8px; display: flex; }}
.bar {{ position: absolute; bottom: 7px; height: 36px; border-radius: 11px; color: #fff;
  display: flex; align-items: center; gap: 9px; padding: 0 13px; font-size: 20px; font-weight: 800;
  margin-left: 6px; margin-right: 6px; }}
.bar svg {{ flex: none; }}

.list {{ padding: 30px 54px 0; flex: none; }}
.evs {{ display: flex; flex-direction: column; gap: 8px; }}
.ev {{ display: flex; align-items: center; gap: 18px; background: #fff; border-radius: 18px;
  padding: 8px 14px 8px 8px; border: 2px solid #eadcea; height: 77px; }}
.tile {{ width: 136px; height: 59px; border-radius: 13px; flex: none; color: #fff; text-align: center;
  display: flex; align-items: center; justify-content: center; gap: 10px; }}
.tile svg {{ flex: none; }}
.tile b {{ display: block; font-size: 25px; font-weight: 900; line-height: 1; }}
.tile span {{ display: block; font-size: 11px; font-weight: 700; letter-spacing: 1px; margin-top: 4px; opacity: .9; }}
.what {{ flex: 1; min-width: 0; }}
.what b {{ display: block; font-size: 20px; font-weight: 800; line-height: 1.15; color: #241a26; }}
.what span {{ display: block; font-size: 16.5px; font-weight: 500; color: #6c5d6e; margin-top: 3px; line-height: 1.2; }}

.foot {{ margin-top: auto; height: 92px; flex: none; background: {BRAND_DARK}; color: #fff;
  display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;
  border-radius: 46px 46px 0 0; }}
.foot b {{ display: block; font-size: 23px; font-weight: 700; font-style: italic; }}
.foot b i {{ color: #FFC94A; font-style: italic; }}
.foot span {{ display: block; font-size: 17px; font-weight: 500; font-style: italic; opacity: .8; margin-top: 3px; }}
"""


def build():
    html = f"""<!doctype html>
<html lang="kk"><head><meta charset="utf-8">
<meta name="viewport" content="width=800">
<title>Құрмет айы — X-баннер</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,500;0,600;0,700;0,800;0,900;1,500;1,700&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body>
<div class="banner" id="banner">
  <section class="hero">
    <div class="ring r1"></div><div class="ring r2"></div>
    <div class="logo">{EMBLEM.format(s=78, c="#fff")}<div class="wm"><b>DOSTYQ</b><span>SCHOOL</span></div></div>
    <div class="month"><b>ҚАЗАН 2026</b><span>ОКТЯБРЬ</span></div>
    <div class="eyebrow"><i></i>АЙ ҚҰНДЫЛЫҒЫ · ЦЕННОСТЬ МЕСЯЦА</div>
    <div class="title">ҚҰРМЕТ<div class="l2"><span class="y">АЙЫ</span><span class="sub">Месяц<br>уважения</span></div></div>
  </section>
  <section class="cal">
    <div class="sec"><b>ҚАЗАН КҮНТІЗБЕСІ</b><span>Календарь на октябрь</span></div>
    {calendar_html()}
  </section>
  <section class="list">
    <div class="sec"><b>АЙ ІС-ШАРАЛАРЫ</b><span>Мероприятия месяца</span></div>
    <div class="evs">{events_html()}</div>
  </section>
  <footer class="foot"><b>«Үлкенге — <i>құрмет</i>, кішіге — ізет»</b><span>Старшим — уважение, младшим — забота</span></footer>
</div>
</body></html>
"""
    OUT.write_text(html, encoding="utf-8")
    return OUT


if __name__ == "__main__":
    print(build())
