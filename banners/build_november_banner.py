#!/usr/bin/env python3
"""X-баннер «Кемелдену және әділдік айы» на ноябрь 2026 — 80 × 180 см.

Стиль — как у октябрьского варианта 1 (фиолетовая шапка). В календаре дни недель
плана подкрашены цветом недели, мероприятия с датой — сплошной заливкой; ниже —
4 карточки «апта»: тема недели и что в ней проходит.

    python3 banners/build_november_banner.py   →  banners/kemeldenu-adildik-2026-11.html
"""

import calendar
import pathlib

from build_october_banner import BRAND, BRAND_DARK, EMBLEM

OUT = pathlib.Path(__file__).with_name("kemeldenu-adildik-2026-11.html")
YEAR, MONTH = 2026, 11

# Иконки — Lucide (ISC), контуры 24×24.
ICONS = {
    "landmark": '<line x1="3" x2="21" y1="22" y2="22"/><line x1="6" x2="6" y1="18" y2="11"/>'
                '<line x1="10" x2="10" y1="18" y2="11"/><line x1="14" x2="14" y1="18" y2="11"/>'
                '<line x1="18" x2="18" y1="18" y2="11"/><polygon points="12 2 20 7 4 7"/>',
    "debate": '<path d="M14 9a2 2 0 0 1-2 2H6l-4 4V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2z"/>'
              '<path d="M18 9h2a2 2 0 0 1 2 2v11l-4-4h-6a2 2 0 0 1-2-2v-1"/>',
    "crown": '<path d="M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519'
             'l-2.834 10.246a1 1 0 0 1-.956.734H5.81a1 1 0 0 1-.957-.734L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664'
             'a1 1 0 0 0 1.516-.294z"/><path d="M5 21h14"/>',
    "trophy": '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/>'
              '<path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/>'
              '<path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/>'
              '<path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>',
    "shelf": '<path d="m16 6 4 14"/><path d="M12 6v14"/><path d="M8 8v12"/><path d="M4 4v16"/>',
    "no-ai": '<path d="M13.67 8H18a2 2 0 0 1 2 2v4.33"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M22 22 2 2"/>'
             '<path d="M8 8H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h12a2 2 0 0 0 1.414-.586"/><path d="M9 13v2"/>'
             '<path d="M9.67 4H12v2.33"/>',
    "box": '<path d="M22 17a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9.5C2 7 4 5 6.5 5H18c2.2 0 4 1.8 4 4v8Z"/>'
           '<polyline points="15,9 18,9 18,11"/><path d="M6.5 5C9 5 11 7 11 9.5V17a2 2 0 0 1-2 2"/>'
           '<line x1="6" x2="7" y1="10" y2="10"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "up": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "route": '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/>'
             '<circle cx="18" cy="5" r="3"/>',
}


def icon(name, size, color="#fff", stroke=2.2):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" '
            f'xmlns="http://www.w3.org/2000/svg">{ICONS[name]}</svg>')


# Недели плана: даты, цвет, тема (KZ / RU, <br> — перенос строки) и что проходит.
# Пункт с датой — (дни, иконка, KZ, RU); без даты — идёт всю неделю.
WEEKS = [
    dict(n=1, days=range(2, 7), dates="2–6", color="#E0457B", tint="#fbe4ec",
         kz="Әділдік — адалдықтан<br>басталады", ru="Справедливость начинается<br>с честности",
         items=[(None, "shelf", "Адалдық сөресі", "Полка честности"),
                (None, "no-ai", "ЖИ-сіз апта", "Неделя без ИИ"),
                ([5], "landmark", "Парламент инаугурациясы", "Инаугурация парламента")]),
    dict(n=2, days=range(9, 14), dates="9–13", color="#8E2DA8", tint="#f1e1f6",
         kz="Әділ сөз,<br>әділ іс", ru="Справедливое слово,<br>справедливое дело",
         items=[(None, "shelf", "Адалдық сөресі", "Полка честности"),
                (None, "no-ai", "ЖИ-сіз апта", "Неделя без ИИ"),
                (None, "box", "Әділдік жәшігі", "Ящик справедливости"),
                ([12], "debate", "Дебат", "Дебаты")]),
    dict(n=3, days=range(16, 21), dates="16–20", color="#11A38C", tint="#ddf3ef",
         kz="Өзін-өзі жетілдіру —<br>кемелдікке жол", ru="Самосовершенствование —<br>путь к совершенству",
         items=[(None, "target", "Мақсаттар қабырғасы", "Стена целей"),
                (None, "up", "Марафон 1%", "Каждый день лучше на 1%"),
                (None, "route", "Жеке жол картасы", "Личная карта успеха")]),
    dict(n=4, days=range(23, 28), dates="23–27", color="#1E88D2", tint="#ddebf8",
         kz="Кемел адам — әділ<br>қоғамның негізі", ru="Совершенный человек —<br>основа справедливого общества",
         items=[(None, "target", "Мақсаттар қабырғасы", "Стена целей"),
                (None, "up", "Марафон 1%", "Каждый день лучше на 1%"),
                ([23, 24, 25, 26], "crown", "Шахмат турнирі", "Турнир по шахматам"),
                ([23, 24, 25, 26], "trophy", "Теннис турнирі", "Турнир по теннису")]),
]

WEEKDAYS = [("Дс", "Пн"), ("Сс", "Вт"), ("Ср", "Ср"), ("Бс", "Чт"), ("Жм", "Пт"), ("Сб", "Сб"), ("Жс", "Вс")]
CELL_W, CELL_H, GAP = 92, 50, 8


def calendar_html():
    week_of, event_of = {}, {}
    for w in WEEKS:
        for d in w["days"]:
            week_of[d] = w
        for days, ic, *_ in w["items"]:
            for d in days or []:
                # 23–26: два турнира в одни дни — в ячейке хватает одной иконки
                event_of.setdefault(d, (w, "trophy" if len(days) > 1 else ic))
    head = "".join(f'<div class="wd{" we" if i >= 5 else ""}"><b>{kz}</b><span>{ru}</span></div>'
                   for i, (kz, ru) in enumerate(WEEKDAYS))
    rows = []
    for week in calendar.Calendar(firstweekday=0).monthdayscalendar(YEAR, MONTH):
        cells = []
        for i, d in enumerate(week):
            if d == 0:
                cells.append('<div class="cell empty"></div>')
            elif d in event_of:
                w, ic = event_of[d]
                cells.append(f'<div class="cell hit" style="background:{w["color"]}"><span class="num">{d}</span>'
                             f'<span class="ic">{icon(ic, 22)}</span></div>')
            elif d in week_of:
                w = week_of[d]
                cells.append(f'<div class="cell wk" style="background:{w["tint"]}"><span class="num" '
                             f'style="color:{w["color"]}">{d}</span></div>')
            else:
                cells.append(f'<div class="cell{" we" if i >= 5 else ""}"><span class="num">{d}</span></div>')
        rows.append(f'<div class="week">{"".join(cells)}</div>')
    return f'<div class="wds">{head}</div><div class="weeks">{"".join(rows)}</div>'


def cards_html():
    out = []
    for w in WEEKS:
        items = []
        for days, ic, kz, ru in w["items"]:
            if days:
                label = str(days[0]) if len(days) == 1 else f"{days[0]}–{days[-1]}"
                mark = (f'<div class="mk date" style="background:{w["color"]}"><b>{label}</b>'
                        f'<span>ҚАРАША</span></div>')
            else:
                mark = f'<div class="mk" style="background:{w["tint"]}">{icon(ic, 22, w["color"])}</div>'
            items.append(f'<div class="it">{mark}<div class="tx"><b>{kz}</b><span>{ru}</span></div></div>')
        out.append(
            f'<div class="card">'
            f'<div class="ch" style="background:{w["color"]}"><b>{w["n"]}-АПТА</b>'
            f'<span>{w["dates"]} қараша · ноября</span></div>'
            f'<div class="topic" style="color:{w["color"]}">{w["kz"]}</div>'
            f'<div class="topic-ru">{w["ru"]}</div>'
            f'<div class="its">{"".join(items)}</div></div>')
    return "".join(out)


CSS = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ background: #fff; }}
body {{ font-family: 'Montserrat', sans-serif; color: #241a26; }}
.banner {{ width: 800px; height: 1800px; position: relative; overflow: hidden; background: #fbf7fb;
  display: flex; flex-direction: column; }}

.hero {{ position: relative; height: 460px; flex: none; overflow: hidden; color: #fff;
  background: linear-gradient(160deg, #9a1a9a 0%, {BRAND} 45%, {BRAND_DARK} 100%);
  border-radius: 0 0 64px 64px; padding: 44px 56px 0; }}
.ring {{ position: absolute; border-radius: 50%; border: 34px solid rgba(255,255,255,.07); }}
.r1 {{ width: 520px; height: 520px; right: -210px; top: -190px; }}
.r2 {{ width: 280px; height: 280px; left: -170px; top: 290px; border-width: 24px; }}
.logo {{ display: flex; align-items: center; gap: 16px; position: relative; }}
.logo .wm b {{ display: block; font-size: 46px; font-weight: 900; line-height: 1; letter-spacing: 1px; }}
.logo .wm span {{ display: block; font-size: 17px; font-weight: 600; letter-spacing: 13.4px; margin-top: 4px; }}
.month {{ position: absolute; right: 56px; top: 54px; text-align: right; }}
.month b {{ display: block; font-size: 30px; font-weight: 800; letter-spacing: 3px; }}
.month span {{ display: block; font-size: 20px; font-weight: 500; opacity: .8; letter-spacing: 2px; margin-top: 2px; }}
.eyebrow {{ position: relative; margin-top: 32px; display: inline-flex; gap: 12px; align-items: center;
  background: rgba(255,255,255,.14); border-radius: 40px; padding: 10px 22px;
  font-size: 18px; font-weight: 700; letter-spacing: 2.4px; }}
.eyebrow i {{ width: 8px; height: 8px; border-radius: 50%; background: #FFC94A; display: block; }}
.title {{ position: relative; margin-top: 20px; font-weight: 900; letter-spacing: -1.5px; }}
.title .l1 {{ font-size: 88px; line-height: 86px; }}
.title .l2 {{ display: flex; align-items: baseline; gap: 14px; font-size: 88px; line-height: 86px; color: #FFC94A; }}
.title .and {{ font-size: 34px; font-weight: 800; letter-spacing: 0; color: #fff; }}
.title .ay {{ font-size: 48px; color: #fff; letter-spacing: 1px; }}
.sub {{ position: relative; margin-top: 16px; font-size: 25px; font-weight: 700; opacity: .95;
  border-left: 5px solid rgba(255,255,255,.35); padding-left: 18px; line-height: 32px; }}

.cal {{ padding: 24px 54px 0; flex: none; }}
.sec {{ display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 14px; }}
.sec b {{ font-size: 32px; font-weight: 900; color: {BRAND}; letter-spacing: 1px; }}
.sec span {{ font-size: 21px; font-weight: 600; color: #8a7a8c; }}
.wds {{ display: grid; grid-template-columns: repeat(7, {CELL_W}px); gap: {GAP}px; margin-bottom: {GAP}px; }}
.wd {{ text-align: center; background: {BRAND}; color: #fff; border-radius: 14px; padding: 6px 0 5px; }}
.wd.we {{ background: #b783b7; }}
.wd b {{ display: block; font-size: 21px; font-weight: 800; line-height: 1.1; }}
.wd span {{ display: block; font-size: 15px; font-weight: 500; opacity: .85; }}
.weeks {{ display: flex; flex-direction: column; gap: {GAP}px; }}
.week {{ display: grid; grid-template-columns: repeat(7, {CELL_W}px); gap: {GAP}px; }}
.cell {{ height: {CELL_H}px; border-radius: 14px; background: #fff; border: 2px solid #eadcea; position: relative; }}
.cell.we {{ background: #f3eaf3; border-color: #f3eaf3; }}
.cell.empty {{ background: transparent; border: 2px dashed #eadcea; }}
.cell.wk, .cell.hit {{ border: none; }}
.cell .num {{ position: absolute; left: 11px; top: 3px; font-size: 26px; font-weight: 800; color: #3a2a3c; }}
.cell.we .num {{ color: #9b7d9d; }}
.cell.hit .num {{ color: #fff; }}
.cell .ic {{ position: absolute; right: 8px; bottom: 7px; display: flex; }}

.list {{ padding: 24px 54px 0; flex: none; }}
.cards {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
.card {{ background: #fff; border: 2px solid #eadcea; border-radius: 22px; overflow: hidden; height: 328px; }}
.ch {{ display: flex; align-items: center; justify-content: space-between; padding: 9px 16px; color: #fff; }}
.ch b {{ font-size: 19px; font-weight: 900; letter-spacing: 1.5px; }}
.ch span {{ font-size: 14px; font-weight: 700; opacity: .92; }}
.topic {{ padding: 10px 16px 0; font-size: 18px; font-weight: 800; line-height: 22px; }}
.topic-ru {{ padding: 4px 16px 0; font-size: 13.5px; font-weight: 500; font-style: italic; line-height: 17px; color: #7a6a7d; }}
.its {{ padding: 10px 14px 0; display: flex; flex-direction: column; gap: 6px; }}
.it {{ display: flex; align-items: center; gap: 12px; }}
.mk {{ width: 40px; height: 40px; border-radius: 11px; flex: none; display: flex; align-items: center; justify-content: center; }}
.mk.date {{ width: 60px; flex-direction: column; color: #fff; text-align: center; }}
.mk.date b {{ display: block; font-size: 15px; font-weight: 900; line-height: 1; }}
.mk.date span {{ display: block; font-size: 7.5px; font-weight: 700; letter-spacing: .8px; margin-top: 3px; }}
.tx b {{ display: block; font-size: 15.5px; font-weight: 800; line-height: 1.15; color: #241a26; }}
.tx span {{ display: block; font-size: 12.5px; font-weight: 500; color: #6c5d6e; margin-top: 2px; }}

.foot {{ margin-top: auto; height: 90px; flex: none; background: {BRAND_DARK}; color: #fff;
  display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;
  border-radius: 46px 46px 0 0; }}
.foot b {{ display: block; font-size: 21px; font-weight: 700; font-style: italic; }}
.foot b i {{ color: #FFC94A; font-style: italic; }}
.foot span {{ display: block; font-size: 14px; font-weight: 500; font-style: italic; opacity: .8; margin-top: 4px; }}
"""


def build():
    html = f"""<!doctype html>
<html lang="kk"><head><meta charset="utf-8">
<meta name="viewport" content="width=800">
<title>Кемелдену және әділдік айы — X-баннер</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,500;0,600;0,700;0,800;0,900;1,500;1,700&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body>
<div class="banner" id="banner">
  <section class="hero">
    <div class="ring r1"></div><div class="ring r2"></div>
    <div class="logo">{EMBLEM.format(s=78, c="#fff")}<div class="wm"><b>DOSTYQ</b><span>SCHOOL</span></div></div>
    <div class="month"><b>ҚАРАША 2026</b><span>НОЯБРЬ</span></div>
    <div class="eyebrow"><i></i>АЙ ҚҰНДЫЛЫҒЫ · ЦЕННОСТЬ МЕСЯЦА</div>
    <div class="title">
      <div class="l1">КЕМЕЛДЕНУ</div>
      <div class="l2"><span class="and">және</span><span>ӘДІЛДІК</span><span class="ay">АЙЫ</span></div>
    </div>
    <div class="sub">Месяц совершенствования и справедливости</div>
  </section>
  <section class="cal">
    <div class="sec"><b>ҚАРАША КҮНТІЗБЕСІ</b><span>Календарь на ноябрь</span></div>
    {calendar_html()}
  </section>
  <section class="list">
    <div class="sec"><b>4 АПТА — 4 ТАҚЫРЫП</b><span>4 недели — 4 темы</span></div>
    <div class="cards">{cards_html()}</div>
  </section>
  <footer class="foot">
    <b>«Талап, еңбек, терең ой, қанағат, рақым — <i>бес асыл іс</i>» · Абай</b>
    <span>Стремление, труд, глубокая мысль, умеренность, милосердие — пять благородных дел</span>
  </footer>
</div>
</body></html>
"""
    OUT.write_text(html, encoding="utf-8")
    return OUT


if __name__ == "__main__":
    print(build())
