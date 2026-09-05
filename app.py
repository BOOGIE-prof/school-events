#!/usr/bin/env python3
"""School Events — веб-приложение для планирования школьных мероприятий.

Бэкенд без внешних зависимостей: стандартная библиотека Python + SQLite.
Запуск:  python3 app.py       (по умолчанию http://localhost:8000)
"""

import base64
import json
import mimetypes
import os
import re
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import SimpleCookie

import db
import push

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
COOKIE_NAME = "sea_session"
MAX_BODY = 24 * 1024 * 1024
MAX_FILE = 4 * 1024 * 1024
MAX_EVENT_FILES_BYTES = 20 * 1024 * 1024
SECURE_COOKIES = os.environ.get("SECURE_COOKIES", "").lower() in ("1", "true", "yes")

EVENT_STATUSES = ("draft", "pending", "approved", "rejected", "done")
TASK_STATUSES = ("todo", "in_progress", "done")


class HttpError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def clean(value, limit=2000):
    return str(value or "").strip()[:limit]


def clean_date(value):
    value = clean(value, 10)
    return value if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) else ""


# ---------------------------------------------------------------- API handlers

def api_register(ctx):
    body = ctx["body"]
    user = db.create_user(
        clean(body.get("email"), 200),
        str(body.get("password") or ""),
        clean(body.get("name"), 120),
    )
    ctx["set_session"] = db.create_session(user["id"])
    with db.Tx() as conn:
        return db.full_state(conn, user)


def api_login(ctx):
    user = db.authenticate(ctx["body"].get("email"), ctx["body"].get("password"))
    if not user:
        raise HttpError(401, "Неверный email или пароль.")
    ctx["set_session"] = db.create_session(user["id"])
    with db.Tx() as conn:
        return db.full_state(conn, user)


def api_logout(ctx):
    if ctx["token"]:
        db.delete_session(ctx["token"])
    ctx["clear_session"] = True
    return {"ok": True}


def api_state(ctx):
    me = require_user(ctx)
    with db.Tx() as conn:
        return db.full_state(conn, me)


def require_user(ctx):
    if not ctx["user"]:
        raise HttpError(401, "Требуется вход в систему.")
    return ctx["user"]


def require_zavuch(ctx):
    me = require_user(ctx)
    if me["role"] != "zavuch":
        raise HttpError(403, "Действие доступно только завучу.")
    return me


def state_after(conn, me):
    return db.full_state(conn, me)


# ---- ideas

def api_create_idea(ctx):
    me = require_user(ctx)
    title = clean(ctx["body"].get("title"), 200)
    if not title:
        raise HttpError(400, "Укажите название идеи.")
    with db.Tx() as conn:
        idea_id = db.uid("idea")
        conn.execute(
            "INSERT INTO ideas (id, title, description, author_id, created_at, status) VALUES (?,?,?,?,?, 'open')",
            (idea_id, title, clean(ctx["body"].get("description"), 4000), me["id"], db.now_iso()),
        )
        db.log_activity(conn, me, "idea_created", f"предложил(а) идею «{title}»")
        return state_after(conn, me)


def api_delete_idea(ctx, idea_id):
    """Идея убирается с доски, но остаётся в базе со статусом deleted:
    удаление — нейтральное действие и не должно отнимать у автора уже начисленные очки."""
    me = require_user(ctx)
    with db.Tx() as conn:
        row = conn.execute("SELECT * FROM ideas WHERE id=?", (idea_id,)).fetchone()
        if not row:
            raise HttpError(404, "Идея не найдена.")
        if row["author_id"] != me["id"] and me["role"] != "zavuch":
            raise HttpError(403, "Удалить идею может её автор или завуч.")
        if row["status"] == "converted":
            raise HttpError(400, "Идея уже стала мероприятием — её нельзя убрать с доски.")
        conn.execute("UPDATE ideas SET status='deleted' WHERE id=?", (idea_id,))
        return state_after(conn, me)


def api_toggle_reaction(ctx, idea_id):
    me = require_user(ctx)
    emoji = clean(ctx["body"].get("emoji"), 8)
    with db.Tx() as conn:
        if not conn.execute("SELECT 1 FROM ideas WHERE id=?", (idea_id,)).fetchone():
            raise HttpError(404, "Идея не найдена.")
        existing = conn.execute(
            "SELECT 1 FROM idea_reactions WHERE idea_id=? AND emoji=? AND user_id=?", (idea_id, emoji, me["id"])
        ).fetchone()
        if existing:
            conn.execute(
                "DELETE FROM idea_reactions WHERE idea_id=? AND emoji=? AND user_id=?", (idea_id, emoji, me["id"])
            )
        else:
            conn.execute(
                "INSERT INTO idea_reactions (idea_id, emoji, user_id) VALUES (?,?,?)", (idea_id, emoji, me["id"])
            )
        return state_after(conn, me)


def api_add_comment(ctx, idea_id):
    me = require_user(ctx)
    text = clean(ctx["body"].get("text"), 2000)
    if not text:
        raise HttpError(400, "Пустой комментарий.")
    with db.Tx() as conn:
        if not conn.execute("SELECT 1 FROM ideas WHERE id=?", (idea_id,)).fetchone():
            raise HttpError(404, "Идея не найдена.")
        conn.execute(
            "INSERT INTO idea_comments (id, idea_id, user_id, text, created_at) VALUES (?,?,?,?,?)",
            (db.uid("cmt"), idea_id, me["id"], text, db.now_iso()),
        )
        return state_after(conn, me)


def api_convert_idea(ctx, idea_id):
    me = require_zavuch(ctx)
    body = ctx["body"]
    with db.Tx() as conn:
        idea = conn.execute("SELECT * FROM ideas WHERE id=?", (idea_id,)).fetchone()
        if not idea:
            raise HttpError(404, "Идея не найдена.")
        title = clean(body.get("title"), 200) or idea["title"]
        event_id = _insert_event(conn, me, body, title, source_idea_id=idea_id)
        conn.execute("UPDATE ideas SET status='converted', converted_event_id=? WHERE id=?", (event_id, idea_id))
        db.log_activity(
            conn, me, "idea_approved", f"одобрил(а) идею «{idea['title']}» → мероприятие «{title}»"
        )
        return state_after(conn, me)


# ---- events

def _insert_event(conn, me, body, title, source_idea_id=None):
    event_id = db.uid("event")
    template_id = clean(body.get("templateId"), 64) or None
    conn.execute(
        "INSERT INTO events (id, title, description, date, location, budget, status, created_by, created_at,"
        " source_idea_id, template_id) VALUES (?,?,?,?,?,?, 'draft', ?,?,?,?)",
        (
            event_id,
            title,
            clean(body.get("description"), 4000),
            clean_date(body.get("date")),
            clean(body.get("location"), 200),
            clean(body.get("budget"), 100),
            me["id"],
            db.now_iso(),
            source_idea_id,
            template_id,
        ),
    )
    if template_id:
        tpl_tasks = conn.execute(
            "SELECT * FROM template_tasks WHERE template_id=? ORDER BY position, id", (template_id,)
        ).fetchall()
        for pos, t in enumerate(tpl_tasks):
            conn.execute(
                "INSERT INTO tasks (id, event_id, title, comment, deadline, status, position)"
                " VALUES (?,?,?,?,'', 'todo', ?)",
                (db.uid("task"), event_id, t["title"], t["comment"], pos),
            )
    return event_id


def api_create_event(ctx):
    me = require_user(ctx)
    title = clean(ctx["body"].get("title"), 200)
    if not title:
        raise HttpError(400, "Укажите название мероприятия.")
    with db.Tx() as conn:
        _insert_event(conn, me, ctx["body"], title)
        db.log_activity(conn, me, "event_created", f"создал(а) мероприятие «{title}»")
        return state_after(conn, me)


def api_update_event(ctx, event_id):
    me = require_user(ctx)
    body = ctx["body"]
    with db.Tx() as conn:
        ev = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        if not ev:
            raise HttpError(404, "Мероприятие не найдено.")

        fields, values = [], []
        for key, column, cleaner in (
            ("title", "title", lambda v: clean(v, 200)),
            ("description", "description", lambda v: clean(v, 4000)),
            ("date", "date", clean_date),
            ("location", "location", lambda v: clean(v, 200)),
            ("budget", "budget", lambda v: clean(v, 100)),
        ):
            if key in body:
                value = cleaner(body[key])
                if key == "title" and not value:
                    raise HttpError(400, "Название не может быть пустым.")
                fields.append(f"{column}=?")
                values.append(value)

        new_status = body.get("status")
        if new_status is not None:
            if new_status not in EVENT_STATUSES:
                raise HttpError(400, "Неизвестный статус.")
            if new_status in ("approved", "rejected") and me["role"] != "zavuch":
                raise HttpError(403, "Одобрять и отклонять мероприятия может только завуч.")
            if new_status == "done" and ev["status"] != "done":
                raise HttpError(400, "Для архивации используйте отдельное действие.")
            fields.append("status=?")
            values.append(new_status)

        if fields:
            conn.execute(f"UPDATE events SET {', '.join(fields)} WHERE id=?", (*values, event_id))

        if new_status and new_status != ev["status"]:
            labels = {
                "pending": f"отправил(а) мероприятие «{ev['title']}» на рассмотрение",
                "approved": f"одобрил(а) мероприятие «{ev['title']}»",
                "rejected": f"отклонил(а) мероприятие «{ev['title']}»",
                "draft": f"вернул(а) мероприятие «{ev['title']}» в черновик",
            }
            if new_status in labels:
                db.log_activity(conn, me, f"event_{new_status}", labels[new_status])
        return state_after(conn, me)


def api_delete_event(ctx, event_id):
    me = require_user(ctx)
    with db.Tx() as conn:
        ev = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        if not ev:
            raise HttpError(404, "Мероприятие не найдено.")
        if ev["created_by"] != me["id"] and me["role"] != "zavuch":
            raise HttpError(403, "Удалить мероприятие может его автор или завуч.")
        conn.execute("DELETE FROM events WHERE id=?", (event_id,))
        return state_after(conn, me)


def api_archive_event(ctx, event_id):
    me = require_user(ctx)
    body = ctx["body"]
    files = body.get("files") or []
    with db.Tx() as conn:
        ev = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        if not ev:
            raise HttpError(404, "Мероприятие не найдено.")
        total = conn.execute(
            "SELECT COALESCE(SUM(size),0) s FROM files WHERE event_id=?", (event_id,)
        ).fetchone()["s"]
        for f in files[:20]:
            try:
                raw = base64.b64decode((f.get("data") or "").split(",")[-1], validate=True)
            except Exception:
                raise HttpError(400, "Не удалось прочитать файл.")
            if len(raw) > MAX_FILE:
                raise HttpError(413, f"Файл «{clean(f.get('name'), 120)}» больше 4 МБ.")
            total += len(raw)
            if total > MAX_EVENT_FILES_BYTES:
                raise HttpError(413, "Суммарный размер файлов мероприятия больше 20 МБ.")
            name = clean(f.get("name"), 200) or "file"
            conn.execute(
                "INSERT INTO files (id, event_id, name, mime, size, data, created_at) VALUES (?,?,?,?,?,?,?)",
                (
                    db.uid("file"),
                    event_id,
                    name,
                    mimetypes.guess_type(name)[0] or "application/octet-stream",
                    len(raw),
                    raw,
                    db.now_iso(),
                ),
            )
        conn.execute(
            "UPDATE events SET status='done', archive_summary=?, archived_at=? WHERE id=?",
            (clean(body.get("summary"), 8000), db.now_iso(), event_id),
        )
        db.log_activity(conn, me, "event_done", f"отметил(а) мероприятие «{ev['title']}» как проведённое")
        return state_after(conn, me)


# ---- tasks

def api_create_task(ctx, event_id):
    me = require_user(ctx)
    body = ctx["body"]
    title = clean(body.get("title"), 200)
    if not title:
        raise HttpError(400, "Укажите название задачи.")
    with db.Tx() as conn:
        if not conn.execute("SELECT 1 FROM events WHERE id=?", (event_id,)).fetchone():
            raise HttpError(404, "Мероприятие не найдено.")
        pos = conn.execute("SELECT COALESCE(MAX(position),-1)+1 p FROM tasks WHERE event_id=?", (event_id,)).fetchone()["p"]
        task_id = db.uid("task")
        conn.execute(
            "INSERT INTO tasks (id, event_id, title, comment, deadline, status, position) VALUES (?,?,?,?,?, 'todo', ?)",
            (task_id, event_id, title, clean(body.get("comment"), 2000), clean_date(body.get("deadline")), pos),
        )
        newly_assigned = _set_responsible(conn, task_id, body.get("responsible") or [], notify_by=me["id"])
        event_title = conn.execute("SELECT title FROM events WHERE id=?", (event_id,)).fetchone()["title"]
        payload = state_after(conn, me)

    if newly_assigned:
        push.notify_task_assigned(None, title, event_title, clean_date(body.get("deadline")), newly_assigned)
    return payload


def _set_responsible(conn, task_id, emails, notify_by=None):
    """Переназначает ответственных. Возвращает id тех, кого назначили только что —
    им уходит push-уведомление (уже назначенных повторно не беспокоим)."""
    before = {
        row["user_id"]
        for row in conn.execute("SELECT user_id FROM task_responsible WHERE task_id=?", (task_id,)).fetchall()
    }
    conn.execute("DELETE FROM task_responsible WHERE task_id=?", (task_id,))
    after = []
    for email in list(dict.fromkeys(emails))[:50]:
        user_id = db.user_id_by_email(conn, clean(email, 200).lower())
        if user_id:
            conn.execute("INSERT INTO task_responsible (task_id, user_id) VALUES (?,?)", (task_id, user_id))
            after.append(user_id)
    # себе уведомление не шлём: человек и так знает, что взял задачу
    return [uid for uid in after if uid not in before and uid != notify_by]


def api_update_task(ctx, task_id):
    me = require_user(ctx)
    body = ctx["body"]
    with db.Tx() as conn:
        task = conn.execute(
            "SELECT t.*, e.title AS event_title FROM tasks t JOIN events e ON e.id=t.event_id WHERE t.id=?", (task_id,)
        ).fetchone()
        if not task:
            raise HttpError(404, "Задача не найдена.")

        fields, values = [], []
        if "title" in body:
            title = clean(body["title"], 200)
            if not title:
                raise HttpError(400, "Название задачи не может быть пустым.")
            fields.append("title=?"); values.append(title)
        if "comment" in body:
            fields.append("comment=?"); values.append(clean(body["comment"], 2000))
        if "deadline" in body:
            fields.append("deadline=?"); values.append(clean_date(body["deadline"]))
        if "status" in body:
            if body["status"] not in TASK_STATUSES:
                raise HttpError(400, "Неизвестный статус задачи.")
            fields.append("status=?"); values.append(body["status"])
        if fields:
            conn.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id=?", (*values, task_id))
        newly_assigned = []
        if "responsible" in body:
            newly_assigned = _set_responsible(conn, task_id, body["responsible"] or [], notify_by=me["id"])

        if body.get("status") == "done" and task["status"] != "done":
            db.log_activity(
                conn, me, "task_done",
                f"выполнил(а) задачу «{task['title']}» в мероприятии «{task['event_title']}»",
            )
        payload = state_after(conn, me)

    # уведомляем уже после закрытия транзакции: сеть не должна держать базу
    if newly_assigned:
        deadline = clean_date(body.get("deadline")) if "deadline" in body else task["deadline"]
        push.notify_task_assigned(
            None, clean(body.get("title"), 200) or task["title"], task["event_title"], deadline, newly_assigned
        )
    return payload


def api_delete_task(ctx, task_id):
    me = require_user(ctx)
    with db.Tx() as conn:
        conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        return state_after(conn, me)


# ---- templates

def api_save_template(ctx):
    me = require_user(ctx)
    body = ctx["body"]
    name = clean(body.get("name"), 200)
    if not name:
        raise HttpError(400, "Укажите название шаблона.")
    tasks = body.get("tasks") or []
    with db.Tx() as conn:
        template_id = clean(body.get("id"), 64)
        exists = conn.execute("SELECT 1 FROM templates WHERE id=?", (template_id,)).fetchone() if template_id else None
        if exists:
            conn.execute("UPDATE templates SET name=? WHERE id=?", (name, template_id))
            conn.execute("DELETE FROM template_tasks WHERE template_id=?", (template_id,))
        else:
            template_id = db.uid("tpl")
            pos = conn.execute("SELECT COALESCE(MAX(position),-1)+1 p FROM templates").fetchone()["p"]
            conn.execute("INSERT INTO templates (id, name, position) VALUES (?,?,?)", (template_id, name, pos))
        for pos, t in enumerate(tasks[:100]):
            title = clean(t.get("title"), 200)
            if title:
                conn.execute(
                    "INSERT INTO template_tasks (template_id, title, comment, position) VALUES (?,?,?,?)",
                    (template_id, title, clean(t.get("comment"), 2000), pos),
                )
        return state_after(conn, me)


def api_delete_template(ctx, template_id):
    me = require_user(ctx)
    with db.Tx() as conn:
        conn.execute("DELETE FROM templates WHERE id=?", (template_id,))
        return state_after(conn, me)


# ---- users / rating

def api_update_user(ctx, email):
    me = require_zavuch(ctx)
    role = clean(ctx["body"].get("role"), 20)
    if role not in ("teacher", "zavuch"):
        raise HttpError(400, "Неизвестная роль.")
    email = urllib.parse.unquote(email).lower()
    with db.Tx() as conn:
        target = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not target:
            raise HttpError(404, "Пользователь не найден.")
        if role == "teacher" and target["role"] == "zavuch":
            others = conn.execute(
                "SELECT COUNT(*) c FROM users WHERE role='zavuch' AND id<>?", (target["id"],)
            ).fetchone()["c"]
            if others == 0:
                raise HttpError(400, "В школе должен остаться хотя бы один завуч.")
        conn.execute("UPDATE users SET role=? WHERE id=?", (role, target["id"]))
        return state_after(conn, me)


# ---- айлық жоспар (месячный план)

MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def api_create_plan_week(ctx):
    me = require_zavuch(ctx)
    body = ctx["body"]
    month = clean(body.get("month"), 7)
    if not MONTH_RE.match(month):
        raise HttpError(400, "Неверный месяц.")
    try:
        week_no = int(body.get("weekNo") or 0)
    except (TypeError, ValueError):
        raise HttpError(400, "Неверный номер недели.")
    if not 1 <= week_no <= 6:
        raise HttpError(400, "Номер недели должен быть от 1 до 6.")
    with db.Tx() as conn:
        if conn.execute("SELECT 1 FROM plan_weeks WHERE month=? AND week_no=?", (month, week_no)).fetchone():
            raise HttpError(409, f"{week_no}-апта уже есть в плане этого месяца.")
        conn.execute(
            "INSERT INTO plan_weeks (id, month, week_no, topic) VALUES (?,?,?,?)",
            (db.uid("week"), month, week_no, clean(body.get("topic"), 300)),
        )
        return state_after(conn, me)


def api_update_plan_week(ctx, week_id):
    me = require_zavuch(ctx)
    body = ctx["body"]
    with db.Tx() as conn:
        if not conn.execute("SELECT 1 FROM plan_weeks WHERE id=?", (week_id,)).fetchone():
            raise HttpError(404, "Неделя не найдена.")
        for field, column in (("topic", "topic"), ("goal", "goal"), ("success", "success")):
            if field in body:
                conn.execute(f"UPDATE plan_weeks SET {column}=? WHERE id=?", (clean(body[field], 1000), week_id))
        return state_after(conn, me)


def api_update_plan_month(ctx, month):
    """Шапка месяца: ҚҰНДЫЛЫҚ и подзаголовок плана."""
    me = require_zavuch(ctx)
    if not MONTH_RE.match(month):
        raise HttpError(400, "Неверный месяц.")
    body = ctx["body"]
    with db.Tx() as conn:
        row = conn.execute("SELECT * FROM plan_months WHERE month=?", (month,)).fetchone()
        value_title = clean(body.get("valueTitle"), 300) if "valueTitle" in body else (row["value_title"] if row else "")
        subtitle = clean(body.get("subtitle"), 300) if "subtitle" in body else (row["subtitle"] if row else "")
        conn.execute(
            "INSERT INTO plan_months (month, value_title, subtitle) VALUES (?,?,?)"
            " ON CONFLICT(month) DO UPDATE SET value_title=excluded.value_title, subtitle=excluded.subtitle",
            (month, value_title, subtitle),
        )
        return state_after(conn, me)


def api_create_plan_role(ctx):
    me = require_zavuch(ctx)
    name = clean(ctx["body"].get("name"), 200)
    if not name:
        raise HttpError(400, "Укажите название роли.")
    with db.Tx() as conn:
        pos = conn.execute("SELECT COALESCE(MAX(position),-1)+1 p FROM plan_roles").fetchone()["p"]
        conn.execute("INSERT INTO plan_roles (id, name, position) VALUES (?,?,?)", (db.uid("role"), name, pos))
        return state_after(conn, me)


def api_update_plan_role(ctx, role_id):
    me = require_zavuch(ctx)
    name = clean(ctx["body"].get("name"), 200)
    if not name:
        raise HttpError(400, "Название роли не может быть пустым.")
    with db.Tx() as conn:
        if not conn.execute("SELECT 1 FROM plan_roles WHERE id=?", (role_id,)).fetchone():
            raise HttpError(404, "Роль не найдена.")
        conn.execute("UPDATE plan_roles SET name=? WHERE id=?", (name, role_id))
        return state_after(conn, me)


def api_delete_plan_role(ctx, role_id):
    me = require_zavuch(ctx)
    with db.Tx() as conn:
        conn.execute("DELETE FROM plan_roles WHERE id=?", (role_id,))
        return state_after(conn, me)


def api_set_plan_cell(ctx):
    """Одна ячейка таблицы: что делает роль на этой неделе."""
    me = require_zavuch(ctx)
    body = ctx["body"]
    week_id = clean(body.get("weekId"), 64)
    role_id = clean(body.get("roleId"), 64)
    text = clean(body.get("text"), 2000)
    with db.Tx() as conn:
        if not conn.execute("SELECT 1 FROM plan_weeks WHERE id=?", (week_id,)).fetchone():
            raise HttpError(404, "Неделя не найдена.")
        if not conn.execute("SELECT 1 FROM plan_roles WHERE id=?", (role_id,)).fetchone():
            raise HttpError(404, "Роль не найдена.")
        if text:
            conn.execute(
                "INSERT INTO plan_cells (week_id, role_id, text) VALUES (?,?,?)"
                " ON CONFLICT(week_id, role_id) DO UPDATE SET text=excluded.text",
                (week_id, role_id, text),
            )
        else:
            conn.execute("DELETE FROM plan_cells WHERE week_id=? AND role_id=?", (week_id, role_id))
        return state_after(conn, me)


def api_delete_plan_week(ctx, week_id):
    me = require_zavuch(ctx)
    with db.Tx() as conn:
        conn.execute("DELETE FROM plan_weeks WHERE id=?", (week_id,))
        return state_after(conn, me)


def _responsible_fields(conn, body):
    """Ответственный — либо пользователь системы, либо просто имя текстом."""
    email = clean(body.get("responsible"), 200).lower()
    user_id = db.user_id_by_email(conn, email) if email else None
    name = clean(body.get("responsibleName"), 200)
    if user_id:
        name = ""
    return user_id, name


def api_create_plan_item(ctx, week_id):
    me = require_zavuch(ctx)
    title = clean(ctx["body"].get("title"), 300)
    if not title:
        raise HttpError(400, "Укажите название мероприятия.")
    with db.Tx() as conn:
        if not conn.execute("SELECT 1 FROM plan_weeks WHERE id=?", (week_id,)).fetchone():
            raise HttpError(404, "Неделя не найдена.")
        pos = conn.execute(
            "SELECT COALESCE(MAX(position),-1)+1 p FROM plan_items WHERE week_id=?", (week_id,)
        ).fetchone()["p"]
        user_id, name = _responsible_fields(conn, ctx["body"])
        conn.execute(
            "INSERT INTO plan_items (id, week_id, title, responsible_id, responsible_name, position)"
            " VALUES (?,?,?,?,?,?)",
            (db.uid("plan"), week_id, title, user_id, name, pos),
        )
        return state_after(conn, me)


def api_update_plan_item(ctx, item_id):
    me = require_zavuch(ctx)
    body = ctx["body"]
    with db.Tx() as conn:
        if not conn.execute("SELECT 1 FROM plan_items WHERE id=?", (item_id,)).fetchone():
            raise HttpError(404, "Строка плана не найдена.")
        if "title" in body:
            title = clean(body["title"], 300)
            if not title:
                raise HttpError(400, "Название не может быть пустым.")
            conn.execute("UPDATE plan_items SET title=? WHERE id=?", (title, item_id))
        if "responsible" in body or "responsibleName" in body:
            user_id, name = _responsible_fields(conn, body)
            conn.execute(
                "UPDATE plan_items SET responsible_id=?, responsible_name=? WHERE id=?", (user_id, name, item_id)
            )
        return state_after(conn, me)


def api_delete_plan_item(ctx, item_id):
    me = require_zavuch(ctx)
    with db.Tx() as conn:
        conn.execute("DELETE FROM plan_items WHERE id=?", (item_id,))
        return state_after(conn, me)


def api_push_config(ctx):
    """Открытый ключ для подписки — клиент запрашивает его перед включением уведомлений."""
    require_user(ctx)
    return {"enabled": push.ENABLED, "publicKey": push.VAPID_PUBLIC_KEY}


def api_push_subscribe(ctx):
    me = require_user(ctx)
    with db.Tx() as conn:
        if not push.save_subscription(conn, me["id"], ctx["body"] or {}):
            raise HttpError(400, "Некорректные данные подписки.")
    return {"ok": True}


def api_push_unsubscribe(ctx):
    require_user(ctx)
    endpoint = clean(ctx["body"].get("endpoint"), 1000)
    with db.Tx() as conn:
        push.delete_subscription(conn, endpoint)
    return {"ok": True}


def api_push_test(ctx):
    """Проверочное уведомление самому себе — чтобы учитель убедился, что всё работает."""
    me = require_user(ctx)
    sent = push.notify_users([me["id"]], "Уведомления включены",
                             "Так будут выглядеть напоминания о задачах.", "/")
    if not sent:
        raise HttpError(400, "Не удалось отправить: подписка не найдена или недействительна.")
    return {"ok": True, "sent": sent}


def api_cron_notify(ctx):
    """Ежедневная рассылка напоминаний. Вызывается внешним планировщиком по ключу."""
    key = ctx["query"].get("key", [""])[0]
    if not push.CRON_KEY or key != push.CRON_KEY:
        raise HttpError(403, "Неверный ключ.")
    force = ctx["query"].get("force", ["0"])[0] == "1"
    return push.maybe_send_daily(force=force)


def api_update_profile(ctx):
    """Каждый может изменить своё отображаемое имя."""
    me = require_user(ctx)
    name = clean(ctx["body"].get("name"), 120)
    if not name:
        raise HttpError(400, "Имя не может быть пустым.")
    with db.Tx() as conn:
        conn.execute("UPDATE users SET name=? WHERE id=?", (name, me["id"]))
        fresh = conn.execute("SELECT * FROM users WHERE id=?", (me["id"],)).fetchone()
        return state_after(conn, fresh)


def api_adjust_points(ctx):
    """Завуч начисляет или снимает произвольное количество очков."""
    me = require_zavuch(ctx)
    email = clean(ctx["body"].get("email"), 200).lower()
    try:
        points = int(ctx["body"].get("points"))
    except (TypeError, ValueError):
        raise HttpError(400, "Укажите количество очков числом.")
    if points == 0:
        raise HttpError(400, "Количество очков не может быть нулём.")
    if abs(points) > 100000:
        raise HttpError(400, "Слишком большое количество очков.")
    with db.Tx() as conn:
        target = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not target:
            raise HttpError(404, "Пользователь не найден.")
        reason = clean(ctx["body"].get("reason"), 300)
        conn.execute(
            "INSERT INTO point_adjustments (id, user_id, points, reason, created_by, created_at)"
            " VALUES (?,?,?,?,?,?)",
            (db.uid("adj"), target["id"], points, reason, me["id"], db.now_iso()),
        )
        sign = "начислил(а)" if points > 0 else "снял(а)"
        tail = f" — {reason}" if reason else ""
        db.log_activity(
            conn, me, "points_adjusted",
            f"{sign} {abs(points)} очков участнику {target['name']}{tail}",
        )
        return state_after(conn, me)


def api_delete_adjustment(ctx, adj_id):
    me = require_zavuch(ctx)
    with db.Tx() as conn:
        conn.execute("DELETE FROM point_adjustments WHERE id=?", (adj_id,))
        return state_after(conn, me)


ROUTES = [
    ("POST", r"^/api/auth/register$", api_register),
    ("POST", r"^/api/auth/login$", api_login),
    ("POST", r"^/api/auth/logout$", api_logout),
    ("GET", r"^/api/state$", api_state),
    ("POST", r"^/api/ideas$", api_create_idea),
    ("DELETE", r"^/api/ideas/([\w-]+)$", api_delete_idea),
    ("POST", r"^/api/ideas/([\w-]+)/reactions$", api_toggle_reaction),
    ("POST", r"^/api/ideas/([\w-]+)/comments$", api_add_comment),
    ("POST", r"^/api/ideas/([\w-]+)/convert$", api_convert_idea),
    ("POST", r"^/api/events$", api_create_event),
    ("PATCH", r"^/api/events/([\w-]+)$", api_update_event),
    ("DELETE", r"^/api/events/([\w-]+)$", api_delete_event),
    ("POST", r"^/api/events/([\w-]+)/archive$", api_archive_event),
    ("POST", r"^/api/events/([\w-]+)/tasks$", api_create_task),
    ("PATCH", r"^/api/tasks/([\w-]+)$", api_update_task),
    ("DELETE", r"^/api/tasks/([\w-]+)$", api_delete_task),
    ("POST", r"^/api/templates$", api_save_template),
    ("DELETE", r"^/api/templates/([\w-]+)$", api_delete_template),
    ("PATCH", r"^/api/plan/months/(\d{4}-\d{2})$", api_update_plan_month),
    ("POST", r"^/api/plan/roles$", api_create_plan_role),
    ("PATCH", r"^/api/plan/roles/([\w-]+)$", api_update_plan_role),
    ("DELETE", r"^/api/plan/roles/([\w-]+)$", api_delete_plan_role),
    ("PUT", r"^/api/plan/cells$", api_set_plan_cell),
    ("POST", r"^/api/plan/weeks$", api_create_plan_week),
    ("PATCH", r"^/api/plan/weeks/([\w-]+)$", api_update_plan_week),
    ("DELETE", r"^/api/plan/weeks/([\w-]+)$", api_delete_plan_week),
    ("POST", r"^/api/plan/weeks/([\w-]+)/items$", api_create_plan_item),
    ("PATCH", r"^/api/plan/items/([\w-]+)$", api_update_plan_item),
    ("DELETE", r"^/api/plan/items/([\w-]+)$", api_delete_plan_item),
    ("GET", r"^/api/push/config$", api_push_config),
    ("POST", r"^/api/push/subscribe$", api_push_subscribe),
    ("POST", r"^/api/push/unsubscribe$", api_push_unsubscribe),
    ("POST", r"^/api/push/test$", api_push_test),
    ("GET", r"^/api/cron/notify$", api_cron_notify),
    ("PATCH", r"^/api/me$", api_update_profile),
    ("PATCH", r"^/api/users/(.+)$", api_update_user),
    ("POST", r"^/api/points/adjust$", api_adjust_points),
    ("DELETE", r"^/api/points/adjust/([\w-]+)$", api_delete_adjustment),
]


class Handler(BaseHTTPRequestHandler):
    server_version = "SchoolEvents"
    protocol_version = "HTTP/1.1"
    _head_only = False  # при HEAD-запросе отдаём только заголовки

    def _write_body(self, body):
        if not self._head_only:
            self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    # ------------------------------------------------------------ helpers

    def _session_token(self):
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        morsel = cookie.get(COOKIE_NAME)
        return morsel.value if morsel else None

    def _send_json(self, status, payload, extra_headers=()):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        for key, value in extra_headers:
            self.send_header(key, value)
        self.end_headers()
        self._write_body(raw)

    def _cookie_header(self, token, clear=False):
        parts = [
            f"{COOKIE_NAME}={'' if clear else token}",
            "Path=/",
            "HttpOnly",
            "SameSite=Lax",
            "Max-Age=0" if clear else "Max-Age=2592000",
        ]
        if SECURE_COOKIES:
            parts.append("Secure")
        return "; ".join(parts)

    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise HttpError(413, "Слишком большой запрос.")
        if not length:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            raise HttpError(400, "Некорректный JSON.")

    # ------------------------------------------------------------ routing

    def _handle(self, method):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/"):
            self._query = urllib.parse.parse_qs(parsed.query)
            self._handle_api(method, path)
        elif method == "GET":
            self._serve_static(path)
        else:
            self._send_json(405, {"error": "Метод не поддерживается."})

    def _handle_api(self, method, path):
        file_match = re.fullmatch(r"/api/files/([\w-]+)", path)
        if file_match and method == "GET":
            return self._serve_file(file_match.group(1))

        for route_method, pattern, handler in ROUTES:
            match = re.fullmatch(pattern, path)
            if not match:
                continue
            if route_method != method:
                continue
            ctx = {
                "token": self._session_token(), "body": {}, "set_session": None,
                "clear_session": False, "query": getattr(self, "_query", {}),
            }
            try:
                if method in ("POST", "PATCH", "PUT"):
                    ctx["body"] = self._read_body()
                ctx["user"] = db.user_for_token(ctx["token"])
                payload = handler(ctx, *match.groups())
            except HttpError as err:
                return self._send_json(err.status, {"error": err.message})
            except ValueError as err:
                return self._send_json(400, {"error": str(err)})
            except Exception as err:  # pragma: no cover
                self.log_message("server error: %r", err)
                return self._send_json(500, {"error": "Внутренняя ошибка сервера."})

            headers = []
            if ctx["set_session"]:
                headers.append(("Set-Cookie", self._cookie_header(ctx["set_session"])))
            if ctx["clear_session"]:
                headers.append(("Set-Cookie", self._cookie_header("", clear=True)))
            return self._send_json(200, payload, headers)

        self._send_json(404, {"error": "Неизвестный метод API."})

    def _serve_file(self, file_id):
        if not db.user_for_token(self._session_token()):
            return self._send_json(401, {"error": "Требуется вход в систему."})
        with db.Tx() as conn:
            row = conn.execute("SELECT * FROM files WHERE id=?", (file_id,)).fetchone()
        if not row:
            return self._send_json(404, {"error": "Файл не найден."})
        self.send_response(200)
        self.send_header("Content-Type", row["mime"])
        self.send_header("Content-Length", str(len(row["data"])))
        self.send_header("Content-Disposition", "attachment; filename*=UTF-8''" + urllib.parse.quote(row["name"]))
        self.end_headers()
        self._write_body(row["data"])

    def _serve_static(self, path):
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        target = os.path.normpath(os.path.join(STATIC_DIR, rel))
        if not target.startswith(STATIC_DIR) or not os.path.isfile(target):
            target = os.path.join(STATIC_DIR, "index.html")
        with open(target, "rb") as fh:
            body = fh.read()
        if target.endswith(".webmanifest"):
            ctype = "application/manifest+json"
        else:
            ctype = mimetypes.guess_type(target)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "application/json", "application/manifest+json"):
            ctype += "; charset=utf-8"

        # sw.js и оболочка не кэшируются браузером, иначе обновления не доедут;
        # библиотеки в /vendor/ неизменны и кэшируются надолго
        if target.endswith(("index.html", ".jsx", "sw.js", ".webmanifest")):
            cache = "no-cache"
        elif "/vendor/" in target.replace(os.sep, "/"):
            cache = "max-age=31536000, immutable"
        else:
            cache = "max-age=3600"

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", cache)
        if target.endswith("sw.js"):
            self.send_header("Service-Worker-Allowed", "/")
        self.end_headers()
        self._write_body(body)

    def do_GET(self):
        self._handle("GET")

    def do_HEAD(self):
        """Проверки живости у хостингов ходят через HEAD — отвечаем заголовками без тела."""
        self._head_only = True
        try:
            self._handle("GET")
        finally:
            self._head_only = False

    def do_POST(self):
        self._handle("POST")

    def do_PUT(self):
        self._handle("PUT")

    def do_PATCH(self):
        self._handle("PATCH")

    def do_DELETE(self):
        self._handle("DELETE")


def main():
    port = int(os.environ.get("PORT", 8000))
    if db.USE_PG:
        source = "PostgreSQL " + db.DATABASE_URL.split("@")[-1].split("?")[0]
    else:
        source = "SQLite " + db.DB_PATH
    print(f"База данных: {source}", flush=True)
    db.connect()
    push.start_scheduler()
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"School Events запущен: http://localhost:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nОстановлено.")


if __name__ == "__main__":
    main()
