#!/usr/bin/env python3
"""Перенос данных из локальной базы SQLite в PostgreSQL.

    DATABASE_URL='postgresql://…' python3 tools/migrate_to_postgres.py [путь/к/school.db]

По умолчанию берётся data/school.db. Скрипт создаёт схему в PostgreSQL,
переносит все таблицы в порядке зависимостей и поправляет счётчики id.
Если в целевой базе уже есть пользователи, перенос не выполняется —
чтобы случайно не задвоить данные.
"""

import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# порядок важен: сначала таблицы, на которые ссылаются остальные
TABLES = [
    "users", "sessions", "ideas", "idea_reactions", "idea_comments",
    "events", "tasks", "task_responsible", "templates", "template_tasks",
    "files", "plan_weeks", "plan_items", "annulled", "activity",
]
# таблицы с автоинкрементным id — для них нужно сдвинуть счётчик
SEQUENCES = {"users": "users_id_seq", "template_tasks": "template_tasks_id_seq"}
BLOB_COLUMNS = {("files", "data")}


def main():
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url.startswith(("postgres://", "postgresql://")):
        raise SystemExit("Укажите переменную DATABASE_URL со строкой подключения к PostgreSQL.")

    src_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "school.db")
    if not os.path.isfile(src_path):
        raise SystemExit(f"Файл базы не найден: {src_path}")

    import psycopg2
    import db as dbmod

    src = sqlite3.connect(src_path)
    src.row_factory = sqlite3.Row

    dst = psycopg2.connect(url)
    cur = dst.cursor()
    cur.execute(dbmod.SCHEMA.format(SERIAL="SERIAL PRIMARY KEY", BLOB="BYTEA"))
    dst.commit()

    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0]:
        raise SystemExit("В целевой базе уже есть пользователи — перенос отменён, чтобы не задвоить данные.")

    # шаблоны создаются автоматически при первом запуске — очищаем, перенесём свои
    cur.execute("DELETE FROM templates")
    dst.commit()

    total = 0
    for table in TABLES:
        try:
            rows = src.execute(f"SELECT * FROM {table}").fetchall()
        except sqlite3.OperationalError:
            print(f"  {table}: таблицы нет в исходной базе, пропускаю")
            continue
        if not rows:
            print(f"  {table}: пусто")
            continue

        columns = rows[0].keys()
        placeholders = ",".join(["%s"] * len(columns))
        sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
        for row in rows:
            values = []
            for col in columns:
                value = row[col]
                if (table, col) in BLOB_COLUMNS and value is not None:
                    value = psycopg2.Binary(value)
                values.append(value)
            cur.execute(sql, values)
        dst.commit()
        total += len(rows)
        print(f"  {table}: перенесено {len(rows)}")

    for table, seq in SEQUENCES.items():
        cur.execute(f"SELECT setval('{seq}', COALESCE((SELECT MAX(id) FROM {table}), 1), true)")
    dst.commit()

    print(f"\nГотово. Всего перенесено записей: {total}")
    src.close()
    dst.close()


if __name__ == "__main__":
    main()
