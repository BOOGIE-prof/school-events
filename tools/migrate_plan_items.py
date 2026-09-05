#!/usr/bin/env python3
"""Перенос старых строк айлық жоспар в новый формат «роль × неделя».

Раньше неделя хранила список мероприятий с ответственными. Новый вид плана —
таблица, где строки это роли. Скрипт складывает прежние мероприятия недели
в ячейку выбранной роли (по умолчанию — ТЖО), сохраняя имя ответственного в скобках.

    python3 tools/migrate_plan_items.py [--role "Мұғалімдер"] [--apply]

Без --apply только показывает, что будет сделано. Исходные записи не удаляются.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", default="ТЖО (Тәрбие орынбасары)", help="в какую строку плана положить мероприятия")
    ap.add_argument("--apply", action="store_true", help="выполнить перенос (без флага — только показать)")
    args = ap.parse_args()

    db.connect()
    with db.Tx() as conn:
        role = conn.execute("SELECT * FROM plan_roles WHERE name=?", (args.role,)).fetchone()
        if not role:
            names = [r["name"] for r in conn.execute("SELECT name FROM plan_roles ORDER BY position").fetchall()]
            raise SystemExit(f"Роль «{args.role}» не найдена. Доступны: {', '.join(names) or '—'}")

        weeks = conn.execute("SELECT * FROM plan_weeks ORDER BY month, week_no").fetchall()
        moved = 0
        for week in weeks:
            items = conn.execute(
                "SELECT i.title, i.responsible_name, u.name AS user_name FROM plan_items i"
                " LEFT JOIN users u ON u.id = i.responsible_id WHERE i.week_id=? ORDER BY i.position",
                (week["id"],),
            ).fetchall()
            if not items:
                continue

            lines = []
            for it in items:
                who = it["user_name"] or it["responsible_name"] or ""
                lines.append(f"{it['title']} ({who})" if who else it["title"])
            text = "\n".join(lines)

            existing = conn.execute(
                "SELECT text FROM plan_cells WHERE week_id=? AND role_id=?", (week["id"], role["id"])
            ).fetchone()
            if existing and existing["text"].strip():
                print(f"  {week['month']} {week['week_no']}-апта: ячейка уже заполнена, пропускаю")
                continue

            print(f"  {week['month']} {week['week_no']}-апта → «{args.role}»:")
            for line in lines:
                print(f"      {line}")
            if args.apply:
                conn.execute(
                    "INSERT INTO plan_cells (week_id, role_id, text) VALUES (?,?,?)"
                    " ON CONFLICT(week_id, role_id) DO UPDATE SET text=excluded.text",
                    (week["id"], role["id"], text),
                )
            moved += len(items)

        print()
        if args.apply:
            print(f"Перенесено мероприятий: {moved}. Исходные записи остались в базе.")
        else:
            print(f"Готово к переносу: {moved}. Запустите с --apply, чтобы применить.")


if __name__ == "__main__":
    main()
