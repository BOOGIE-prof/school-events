#!/usr/bin/env python3
"""Вариант 2 X-баннера «Құрмет айы»: светлый, с казахским орнаментом (қошқар мүйіз).

Данные (мероприятия, календарь, иконки) берутся из build_october_banner.py,
поэтому даты во всех вариантах совпадают.

    python3 banners/build_october_banner_v2.py   →  banners/kurmet-ayi-2026-10-v2.html
"""

import pathlib

from build_october_banner import BRAND, CELL_H, CELL_W, EMBLEM, EVENTS, GAP, calendar_html, icon

OUT = pathlib.Path(__file__).with_name("kurmet-ayi-2026-10-v2.html")

CREAM = "#fff8ef"
GOLD = "#d9981a"
INK = "#2a1630"


def ornament(width, color, unit=60, height=30, stroke=2.6):
    """Полоса из повторяющихся «бараньих рогов» — 60 × 30 на мотив."""
    paths = []
    for i in range(width // unit):
        x = i * unit
        paths.append(
            f'<path d="M{x+30} 30V22C{x+30} 10 {x+18} 4 {x+11} 9C{x+5} 13 {x+7} 22 {x+14} 21'
            f'C{x+18} 20 {x+18} 15 {x+15} 14M{x+30} 22C{x+30} 10 {x+42} 4 {x+49} 9'
            f'C{x+55} 13 {x+53} 22 {x+46} 21C{x+42} 20 {x+42} 15 {x+45} 14"/>')
    w = (width // unit) * unit
    return (f'<svg width="{w}" height="{height}" viewBox="0 0 {w} {height}" fill="none" stroke="{color}" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" '
            f'xmlns="http://www.w3.org/2000/svg">{"".join(paths)}</svg>')


def timeline_html():
    items = []
    for ev in EVENTS:
        day, _, last = ev["tile"].partition("–")
        num = f'{day}<i>–{last}</i>' if last else day
        items.append(
            f'<div class="tl">'
            f'<div class="d" style="color:{ev["color"]}"><b>{num}</b><span>ҚАЗАН · ОКТ</span></div>'
            f'<div class="pin" style="background:{ev["color"]}">{icon(ev["icon"], 24)}</div>'
            f'<div class="t"><b>{ev["kz"]}</b><span>{ev["ru"]}</span></div>'
            f'</div>')
    return "".join(items)


CSS = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ background: #fff; }}
body {{ font-family: 'Montserrat', sans-serif; color: {INK}; }}
.banner {{ width: 800px; height: 1800px; position: relative; overflow: hidden; background: {CREAM};
  display: flex; flex-direction: column; }}

.top {{ height: 18px; flex: none; background: {BRAND}; }}
.head {{ padding: 34px 56px 0; display: flex; align-items: center; justify-content: space-between; flex: none; }}
.logo {{ display: flex; align-items: center; gap: 14px; }}
.logo .wm b {{ display: block; font-size: 38px; font-weight: 900; line-height: 1; letter-spacing: 1px; color: {BRAND}; }}
.logo .wm span {{ display: block; font-size: 14px; font-weight: 600; letter-spacing: 11.2px; margin-top: 4px; color: {BRAND}; }}
.year {{ text-align: right; }}
.year b {{ display: block; font-size: 26px; font-weight: 800; color: {BRAND}; letter-spacing: 2px; }}
.year span {{ display: block; font-size: 16px; font-weight: 600; color: {GOLD}; letter-spacing: 2px; margin-top: 2px; }}

.orn {{ display: flex; justify-content: center; flex: none; padding-top: 26px; }}
.hero {{ text-align: center; padding-top: 18px; flex: none; }}
.kicker {{ display: inline-flex; align-items: center; gap: 14px; font-size: 18px; font-weight: 700;
  letter-spacing: 3px; color: {GOLD}; }}
.kicker i {{ width: 40px; height: 3px; background: {GOLD}; display: block; border-radius: 2px; }}
.big {{ font-size: 150px; font-weight: 900; line-height: 140px; letter-spacing: -3px; color: {BRAND}; margin-top: 6px; }}
.big2 {{ font-size: 64px; font-weight: 900; line-height: 64px; letter-spacing: 14px; color: {INK}; }}
.ru {{ margin-top: 14px; display: inline-block; background: {BRAND}; color: #fff; border-radius: 40px;
  padding: 10px 30px; font-size: 26px; font-weight: 700; }}

.cal {{ margin: 34px 34px 0; padding: 26px 20px 24px; background: {BRAND}; border-radius: 36px; flex: none; }}
.sec {{ display: flex; align-items: baseline; justify-content: space-between; padding: 0 4px; margin-bottom: 16px; }}
.sec b {{ font-size: 28px; font-weight: 900; letter-spacing: 1px; }}
.sec span {{ font-size: 19px; font-weight: 600; }}
.cal .sec b {{ color: #fff; }}
.cal .sec span {{ color: #fff; opacity: .75; }}
.wds {{ display: grid; grid-template-columns: repeat(7, {CELL_W}px); gap: {GAP}px; margin-bottom: {GAP}px; }}
.wd {{ text-align: center; padding: 2px 0 4px; }}
.wd b {{ display: block; font-size: 20px; font-weight: 800; line-height: 1.1; color: #fff; }}
.wd span {{ display: block; font-size: 14px; font-weight: 500; color: #fff; opacity: .7; }}
.wd.we b {{ color: #FFC94A; }}
.weeks {{ display: flex; flex-direction: column; gap: {GAP}px; }}
.week {{ position: relative; display: grid; grid-template-columns: repeat(7, {CELL_W}px); gap: {GAP}px; }}
.cell {{ height: {CELL_H}px; border-radius: 14px; background: rgba(255,255,255,.12); position: relative; }}
.cell.we {{ background: rgba(255,255,255,.06); }}
.cell.empty {{ background: transparent; border: 2px dashed rgba(255,255,255,.18); }}
.cell .num {{ position: absolute; left: 11px; top: 3px; font-size: 30px; font-weight: 800; color: #fff; }}
.cell.we .num {{ color: rgba(255,255,255,.55); }}
.cell.hit {{ border: 3px solid #fff; }}
.cell.hit .num {{ color: #fff; left: 8px; top: 0; }}
.cell .ic {{ position: absolute; right: 6px; bottom: 5px; display: flex; }}
.bar {{ position: absolute; bottom: 7px; height: 36px; border-radius: 11px; color: #fff;
  display: flex; align-items: center; gap: 9px; padding: 0 13px; font-size: 20px; font-weight: 800;
  margin-left: 6px; margin-right: 6px; border: 2px solid #fff; }}
.bar svg {{ flex: none; }}

.events {{ padding: 34px 56px 0; flex: none; }}
.events .sec b {{ color: {BRAND}; }}
.events .sec span {{ color: {GOLD}; }}
.tls {{ position: relative; display: flex; flex-direction: column; gap: 12px; padding-top: 4px; }}
.line {{ position: absolute; left: 156px; top: 20px; bottom: 20px; width: 4px; background: #ecd9ec; border-radius: 2px; }}
.tl {{ position: relative; display: flex; align-items: center; height: 60px; }}
.d {{ width: 120px; flex: none; text-align: right; margin-right: 16px; }}
.d b {{ display: block; font-size: 34px; font-weight: 900; line-height: 1; }}
.d b i {{ font-style: normal; font-size: 24px; }}
.d span {{ display: block; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; margin-top: 4px; color: #a08aa3; }}
.pin {{ width: 44px; height: 44px; border-radius: 50%; flex: none;
  display: flex; align-items: center; justify-content: center; border: 4px solid {CREAM}; }}
.t {{ padding-left: 18px; }}
.t b {{ display: block; font-size: 20px; font-weight: 800; line-height: 1.15; color: {INK}; }}
.t span {{ display: block; font-size: 16.5px; font-weight: 500; color: #7a6a7d; margin-top: 3px; }}

.foot {{ margin-top: auto; flex: none; text-align: center; padding-bottom: 0; }}
.foot .orn {{ padding-top: 0; }}
.foot .q {{ background: {BRAND}; color: #fff; padding: 18px 0 20px; margin-top: 14px; }}
.foot b {{ display: block; font-size: 23px; font-weight: 700; font-style: italic; }}
.foot b i {{ color: #FFC94A; font-style: italic; }}
.foot span {{ display: block; font-size: 17px; font-weight: 500; font-style: italic; opacity: .8; margin-top: 3px; }}
"""


def build():
    html = f"""<!doctype html>
<html lang="kk"><head><meta charset="utf-8">
<meta name="viewport" content="width=800">
<title>Құрмет айы — X-баннер, вариант 2</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,500;0,600;0,700;0,800;0,900;1,500;1,700&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body>
<div class="banner" id="banner">
  <div class="top"></div>
  <header class="head">
    <div class="logo">{EMBLEM.format(s=64, c=BRAND)}<div class="wm"><b>DOSTYQ</b><span>SCHOOL</span></div></div>
    <div class="year"><b>ҚАЗАН 2026</b><span>ОКТЯБРЬ</span></div>
  </header>
  <div class="orn">{ornament(720, GOLD)}</div>
  <section class="hero">
    <div class="kicker"><i></i>АЙ ҚҰНДЫЛЫҒЫ · ЦЕННОСТЬ МЕСЯЦА<i></i></div>
    <div class="big">ҚҰРМЕТ</div>
    <div class="big2">АЙЫ</div>
    <div class="ru">Месяц уважения</div>
  </section>
  <section class="cal">
    <div class="sec"><b>ҚАЗАН КҮНТІЗБЕСІ</b><span>Календарь на октябрь</span></div>
    {calendar_html()}
  </section>
  <section class="events">
    <div class="sec"><b>АЙ ІС-ШАРАЛАРЫ</b><span>Мероприятия месяца</span></div>
    <div class="tls"><div class="line"></div>{timeline_html()}</div>
  </section>
  <footer class="foot">
    <div class="orn">{ornament(720, BRAND, stroke=2.2)}</div>
    <div class="q"><b>«Үлкенге — <i>құрмет</i>, кішіге — ізет»</b><span>Старшим — уважение, младшим — забота</span></div>
  </footer>
</div>
</body></html>
"""
    OUT.write_text(html, encoding="utf-8")
    return OUT


if __name__ == "__main__":
    print(build())
