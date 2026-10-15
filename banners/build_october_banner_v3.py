#!/usr/bin/env python3
"""Вариант 3 X-баннера «Құрмет айы»: тёмный, плакатный, мероприятия — цветными карточками.

Данные берутся из build_october_banner.py, поэтому даты во всех вариантах совпадают.

    python3 banners/build_october_banner_v3.py   →  banners/kurmet-ayi-2026-10-v3.html
"""

import pathlib

from build_october_banner import CELL_W, EMBLEM, EVENTS, GAP, calendar_html, icon

OUT = pathlib.Path(__file__).with_name("kurmet-ayi-2026-10-v3.html")

GOLD = "#FFC94A"
CELL_H = 76

# Переносы строк в карточках (карточка узкая, текст сам не переносится в макете Figma).
CARD_TEXT = {
    "card": ("Рақмет карточкасы", "Карточка благодарности"),
    "tracker": ("Құрмет трекері", "Трекер уважения"),
    "vote": ("Президент сайлауы", "Выборы президентов"),
    "ball": ("Ата-аналар арасындағы<br>волейбол турнирі", "Турнир по волейболу для родителей"),
    "quiz": ("Dostyq Quiz —<br>оқушылар арасында", "Dostyq Quiz среди учеников"),
    "uni": ("Астанаға сапар:<br>ЖОО-ларға экскурсия", "Астана: экскурсия по вузам"),
}


def cards_html():
    out = []
    for ev in EVENTS:
        kz, ru = CARD_TEXT[ev["icon"]]
        out.append(
            f'<div class="card" style="background:{ev["color"]}">'
            f'<div class="row"><div class="ic">{icon(ev["icon"], 28, ev["color"], 2.4)}</div>'
            f'<div class="date"><b>{ev["tile"]}</b><span>ҚАЗАН · ОКТЯБРЬ</span></div></div>'
            f'<div class="kz">{kz}</div><div class="ru">{ru}</div></div>')
    return "".join(out)


CSS = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ background: #fff; }}
body {{ font-family: 'Montserrat', sans-serif; color: #fff; }}
.banner {{ width: 800px; height: 1800px; position: relative; overflow: hidden;
  background: linear-gradient(180deg, #24062a 0%, #3d0742 45%, #6a0a6a 100%);
  display: flex; flex-direction: column; }}

.glow {{ position: absolute; border-radius: 50%; }}
.g1 {{ width: 640px; height: 640px; right: -300px; top: -260px; background: rgba(255,201,74,.07); }}
.g2 {{ width: 420px; height: 420px; left: -260px; top: 330px; background: rgba(255,255,255,.04); }}

.head {{ position: relative; padding: 44px 56px 0; display: flex; align-items: center; justify-content: space-between; flex: none; }}
.logo {{ display: flex; align-items: center; gap: 14px; }}
.logo .wm b {{ display: block; font-size: 40px; font-weight: 900; line-height: 1; letter-spacing: 1px; }}
.logo .wm span {{ display: block; font-size: 15px; font-weight: 600; letter-spacing: 11.8px; margin-top: 4px; }}
.pill {{ border: 2px solid {GOLD}; color: {GOLD}; border-radius: 40px; padding: 9px 20px; font-size: 18px;
  font-weight: 800; letter-spacing: 2px; }}

.hero {{ position: relative; padding: 40px 56px 0; flex: none; }}
.eyebrow {{ font-size: 19px; font-weight: 700; letter-spacing: 4px; color: {GOLD}; }}
.t1 {{ font-size: 140px; font-weight: 900; line-height: 126px; letter-spacing: -3px; margin-top: 16px; }}
.t2 {{ font-size: 140px; font-weight: 900; line-height: 126px; letter-spacing: -3px; color: {GOLD}; }}
.strip {{ margin-top: 22px; display: flex; align-items: center; gap: 18px; }}
.strip i {{ flex: 1; height: 3px; background: rgba(255,255,255,.25); display: block; }}
.strip b {{ font-size: 30px; font-weight: 700; letter-spacing: 6px; }}

.cal {{ position: relative; padding: 32px 54px 0; flex: none; }}
.sec {{ display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 14px; }}
.sec b {{ font-size: 28px; font-weight: 900; letter-spacing: 1px; color: #fff; }}
.sec span {{ font-size: 19px; font-weight: 600; color: {GOLD}; }}
.wds {{ display: grid; grid-template-columns: repeat(7, {CELL_W}px); gap: {GAP}px; margin-bottom: {GAP}px; }}
.wd {{ text-align: center; border-top: 3px solid {GOLD}; padding-top: 6px; }}
.wd.we {{ border-top-color: rgba(255,255,255,.3); }}
.wd b {{ display: block; font-size: 20px; font-weight: 800; line-height: 1.1; }}
.wd span {{ display: block; font-size: 14px; font-weight: 500; opacity: .65; }}
.weeks {{ display: flex; flex-direction: column; gap: {GAP}px; }}
.week {{ position: relative; display: grid; grid-template-columns: repeat(7, {CELL_W}px); gap: {GAP}px; }}
.cell {{ height: {CELL_H}px; border-radius: 14px; background: rgba(255,255,255,.09); position: relative; }}
.cell.we {{ background: rgba(255,255,255,.04); }}
.cell.empty {{ background: transparent; }}
.cell .num {{ position: absolute; left: 11px; top: 2px; font-size: 28px; font-weight: 800; color: #fff; }}
.cell.we .num {{ color: rgba(255,255,255,.45); }}
.cell.hit .num {{ color: #fff; }}
.cell .ic {{ position: absolute; right: 8px; bottom: 6px; display: flex; }}
.bar {{ position: absolute; bottom: 6px; height: 34px; border-radius: 10px; color: #fff;
  display: flex; align-items: center; gap: 9px; padding: 0 12px; font-size: 19px; font-weight: 800;
  margin-left: 6px; margin-right: 6px; }}
.bar svg {{ flex: none; }}

.ev {{ position: relative; padding: 32px 54px 0; flex: none; }}
.cards {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
.card {{ height: 168px; border-radius: 24px; padding: 18px 20px; position: relative; }}
.card .row {{ display: flex; align-items: center; gap: 14px; }}
.card .ic {{ width: 48px; height: 48px; border-radius: 50%; background: #fff; flex: none;
  display: flex; align-items: center; justify-content: center; }}
.card .date b {{ display: block; font-size: 30px; font-weight: 900; line-height: 1; }}
.card .date span {{ display: block; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; opacity: .85; margin-top: 4px; }}
.card .kz {{ margin-top: 14px; font-size: 20px; font-weight: 800; line-height: 24px; }}
.card .ru {{ margin-top: 6px; font-size: 15px; font-weight: 500; line-height: 19px; opacity: .88; }}

.foot {{ position: relative; margin-top: auto; flex: none; padding: 0 56px 34px; text-align: center; }}
.foot .ln {{ height: 3px; background: {GOLD}; margin: 0 auto 18px; width: 120px; border-radius: 2px; }}
.foot b {{ display: block; font-size: 24px; font-weight: 700; font-style: italic; }}
.foot b i {{ color: {GOLD}; font-style: italic; }}
.foot span {{ display: block; font-size: 17px; font-weight: 500; font-style: italic; opacity: .75; margin-top: 4px; }}
"""


def build():
    html = f"""<!doctype html>
<html lang="kk"><head><meta charset="utf-8">
<meta name="viewport" content="width=800">
<title>Құрмет айы — X-баннер, вариант 3</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,500;0,600;0,700;0,800;0,900;1,500;1,700&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body>
<div class="banner" id="banner">
  <div class="glow g1"></div><div class="glow g2"></div>
  <header class="head">
    <div class="logo">{EMBLEM.format(s=66, c="#fff")}<div class="wm"><b>DOSTYQ</b><span>SCHOOL</span></div></div>
    <div class="pill">ҚАЗАН · ОКТЯБРЬ 2026</div>
  </header>
  <section class="hero">
    <div class="eyebrow">АЙ ҚҰНДЫЛЫҒЫ · ЦЕННОСТЬ МЕСЯЦА</div>
    <div class="t1">ҚҰРМЕТ</div>
    <div class="t2">АЙЫ</div>
    <div class="strip"><b>МЕСЯЦ УВАЖЕНИЯ</b><i></i></div>
  </section>
  <section class="cal">
    <div class="sec"><b>ҚАЗАН КҮНТІЗБЕСІ</b><span>Календарь на октябрь</span></div>
    {calendar_html()}
  </section>
  <section class="ev">
    <div class="sec"><b>АЙ ІС-ШАРАЛАРЫ</b><span>Мероприятия месяца</span></div>
    <div class="cards">{cards_html()}</div>
  </section>
  <footer class="foot"><div class="ln"></div>
    <b>«Үлкенге — <i>құрмет</i>, кішіге — ізет»</b><span>Старшим — уважение, младшим — забота</span>
  </footer>
</div>
</body></html>
"""
    OUT.write_text(html, encoding="utf-8")
    return OUT


if __name__ == "__main__":
    print(build())
