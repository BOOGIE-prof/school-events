"""Слой хранения данных.

Работает с двумя базами и сам выбирает нужную:
  * задана переменная DATABASE_URL (postgres://…) — используется PostgreSQL;
  * иначе — файл SQLite (по умолчанию data/school.db), удобно для локальной работы.

SQL в коде пишется в стиле SQLite (плейсхолдер «?»), для PostgreSQL он
переписывается автоматически.
"""

import os
import re
import base64
import hashlib
import secrets
import sqlite3
import threading
from datetime import datetime, timezone

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
USE_PG = DATABASE_URL.startswith(("postgres://", "postgresql://"))
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "school.db"))

_lock = threading.RLock()
_conn = None

# различия диалектов
_TYPES = {
    "SERIAL": "SERIAL PRIMARY KEY" if USE_PG else "INTEGER PRIMARY KEY AUTOINCREMENT",
    "BLOB": "BYTEA" if USE_PG else "BLOB",
}

SCHEMA = """

CREATE TABLE IF NOT EXISTS users (
  id            {SERIAL},
  email         TEXT NOT NULL UNIQUE,
  name          TEXT NOT NULL,
  role          TEXT NOT NULL DEFAULT 'teacher',
  password_hash TEXT NOT NULL,
  created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
  token      TEXT PRIMARY KEY,
  user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ideas (
  id                 TEXT PRIMARY KEY,
  title              TEXT NOT NULL,
  description        TEXT NOT NULL DEFAULT '',
  author_id          INTEGER REFERENCES users(id) ON DELETE SET NULL,
  created_at         TEXT NOT NULL,
  status             TEXT NOT NULL DEFAULT 'open',
  converted_event_id TEXT
);

CREATE TABLE IF NOT EXISTS idea_reactions (
  idea_id TEXT NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
  emoji   TEXT NOT NULL,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  PRIMARY KEY (idea_id, emoji, user_id)
);

CREATE TABLE IF NOT EXISTS idea_comments (
  id         TEXT PRIMARY KEY,
  idea_id    TEXT NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
  user_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,
  text       TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
  id              TEXT PRIMARY KEY,
  title           TEXT NOT NULL,
  description     TEXT NOT NULL DEFAULT '',
  date            TEXT NOT NULL DEFAULT '',
  location        TEXT NOT NULL DEFAULT '',
  budget          TEXT NOT NULL DEFAULT '',
  status          TEXT NOT NULL DEFAULT 'draft',
  created_by      INTEGER REFERENCES users(id) ON DELETE SET NULL,
  created_at      TEXT NOT NULL,
  source_idea_id  TEXT,
  template_id     TEXT,
  archive_summary TEXT,
  archived_at     TEXT
);

CREATE TABLE IF NOT EXISTS tasks (
  id       TEXT PRIMARY KEY,
  event_id TEXT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  title    TEXT NOT NULL,
  comment  TEXT NOT NULL DEFAULT '',
  deadline TEXT NOT NULL DEFAULT '',
  status   TEXT NOT NULL DEFAULT 'todo',
  position INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS task_responsible (
  task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  PRIMARY KEY (task_id, user_id)
);

CREATE TABLE IF NOT EXISTS templates (
  id       TEXT PRIMARY KEY,
  name     TEXT NOT NULL,
  position INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS template_tasks (
  id          {SERIAL},
  template_id TEXT NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
  title       TEXT NOT NULL,
  comment     TEXT NOT NULL DEFAULT '',
  position    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS files (
  id         TEXT PRIMARY KEY,
  event_id   TEXT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  name       TEXT NOT NULL,
  mime       TEXT NOT NULL DEFAULT 'application/octet-stream',
  size       INTEGER NOT NULL DEFAULT 0,
  data       {BLOB} NOT NULL,
  created_at TEXT NOT NULL
);

-- Айлық жоспар: месячный план по неделям (заменяет Excel-таблицу)
CREATE TABLE IF NOT EXISTS plan_weeks (
  id      TEXT PRIMARY KEY,
  month   TEXT NOT NULL,                 -- '2026-09'
  week_no INTEGER NOT NULL,              -- 1..6
  topic   TEXT NOT NULL DEFAULT '',      -- тақырып недели
  UNIQUE (month, week_no)
);

CREATE TABLE IF NOT EXISTS plan_items (
  id               TEXT PRIMARY KEY,
  week_id          TEXT NOT NULL REFERENCES plan_weeks(id) ON DELETE CASCADE,
  title            TEXT NOT NULL,        -- іс шара
  responsible_id   INTEGER REFERENCES users(id) ON DELETE SET NULL,
  responsible_name TEXT NOT NULL DEFAULT '',  -- жауапты, если это не пользователь системы
  position         INTEGER NOT NULL DEFAULT 0
);

-- Ручные корректировки очков: завуч может прибавить или снять любое количество
CREATE TABLE IF NOT EXISTS point_adjustments (
  id         TEXT PRIMARY KEY,
  user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  points     INTEGER NOT NULL,          -- со знаком: плюс начисляет, минус снимает
  reason     TEXT NOT NULL DEFAULT '',
  created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
  created_at TEXT NOT NULL
);

-- Служебные настройки приложения (например, дата последней рассылки напоминаний)
CREATE TABLE IF NOT EXISTS settings (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

-- Подписки браузеров на push-уведомления: у одного человека их несколько
-- (телефон, рабочий компьютер), поэтому ключ — endpoint, а не пользователь
CREATE TABLE IF NOT EXISTS push_subscriptions (
  endpoint   TEXT PRIMARY KEY,
  user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  p256dh     TEXT NOT NULL,
  auth       TEXT NOT NULL,
  created_at TEXT NOT NULL,
  last_sent  TEXT
);

CREATE TABLE IF NOT EXISTS activity (
  id         TEXT PRIMARY KEY,
  actor_id   INTEGER REFERENCES users(id) ON DELETE SET NULL,
  actor_name TEXT NOT NULL,
  type       TEXT NOT NULL,
  message    TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_push_user ON push_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_plan_weeks_month ON plan_weeks(month);
CREATE INDEX IF NOT EXISTS idx_plan_items_week ON plan_items(week_id);
CREATE INDEX IF NOT EXISTS idx_tasks_event ON tasks(event_id);
CREATE INDEX IF NOT EXISTS idx_comments_idea ON idea_comments(idea_id);
CREATE INDEX IF NOT EXISTS idx_activity_created ON activity(created_at DESC);
"""

DEFAULT_TEMPLATES = [
    ("Линейка 1 сентября", [
        ("Украсить актовый зал / школьный двор", "Шары, баннер, цветы у сцены"),
        ("Подготовить сценарий линейки", "Согласовать текст ведущих с администрацией"),
        ("Организовать музыкальное сопровождение", "Звук, микрофоны, плейлист"),
        ("Встреча первоклассников", "Назначить сопровождающих по классам"),
        ("Фото- и видеосъёмка", ""),
    ]),
    ("День учителя", [
        ("Организовать концертную программу", "Номера от классов, распределить очередность"),
        ("Подготовить поздравления и подарки", "Собрать список от родительских комитетов"),
        ("Оформить зал", ""),
        ("Пригласить ветеранов педагогического труда", ""),
    ]),
    ("Новый год / Ёлка", [
        ("Украсить школу и ёлку", ""),
        ("Организовать новогодние утренники по параллелям", "Составить график по классам"),
        ("Заказать / подготовить подарки", ""),
        ("Костюмы Деда Мороза и Снегурочки", ""),
        ("Техника безопасности (гирлянды, пиротехника)", "Проверить перед мероприятием"),
    ]),
    ("Выпускной", [
        ("Забронировать площадку", ""),
        ("Согласовать бюджет с родительским комитетом", ""),
        ("Организовать фото- и видеосъёмку", ""),
        ("Подготовить праздничную программу", ""),
        ("Вручение аттестатов — торжественная часть", "Порядок вызова выпускников"),
        ("Организация фуршета / банкета", ""),
    ]),
    ("День открытых дверей", [
        ("Подготовить презентацию школы", ""),
        ("Организовать экскурсии по кабинетам", "Назначить ответственных учителей по этажам"),
        ("Оформить информационные стенды", ""),
        ("Встреча и регистрация гостей", ""),
    ]),
    ("День здоровья / спортивный праздник", [
        ("Составить программу эстафет и соревнований", ""),
        ("Подготовить спортивный инвентарь", ""),
        ("Медицинское сопровождение", "Дежурство школьного медработника"),
        ("Награждение победителей", "Грамоты, медали"),
    ]),
]


def now_iso():
    # миллисекунды нужны, чтобы события одной секунды сохраняли порядок
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def uid(prefix):
    return f"{prefix}-{secrets.token_hex(8)}"


class Connection:
    """Единый интерфейс к SQLite и PostgreSQL.

    SQL пишется в стиле SQLite; для PostgreSQL «?» превращается в «%s».
    Если соединение с PostgreSQL оборвалось (например, бесплатная база уснула),
    запрос повторяется один раз на свежем соединении.
    """

    def __init__(self):
        self.raw = None
        self._open()

    def _open(self):
        if USE_PG:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            self.raw = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor, connect_timeout=10)
        else:
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            self.raw = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.raw.row_factory = sqlite3.Row
            self.raw.execute("PRAGMA journal_mode=WAL")
            self.raw.execute("PRAGMA foreign_keys=ON")

    def execute(self, sql, params=()):
        if not USE_PG:
            return self.raw.execute(sql, params)
        try:
            return self._pg_execute(sql, params)
        except Exception as err:
            if not _is_connection_error(err):
                raise
            try:
                self.raw.close()
            except Exception:
                pass
            self._open()
            return self._pg_execute(sql, params)

    def _pg_execute(self, sql, params):
        cur = self.raw.cursor()
        cur.execute(sql.replace("?", "%s"), params)
        return cur

    def commit(self):
        self.raw.commit()

    def rollback(self):
        try:
            self.raw.rollback()
        except Exception:
            pass

    def init_schema(self):
        ddl = SCHEMA.format(**_TYPES)
        if USE_PG:
            cur = self.raw.cursor()
            cur.execute(ddl)
        else:
            self.raw.executescript(ddl)
        self.commit()


def _is_connection_error(err):
    name = type(err).__name__
    return name in ("OperationalError", "InterfaceError", "AdminShutdown") or "server closed" in str(err).lower()


def connect():
    global _conn
    with _lock:
        if _conn is None:
            _conn = Connection()
            _conn.init_schema()
            _seed_templates(_conn)
            _conn.commit()
        return _conn


def _seed_templates(conn):
    if conn.execute("SELECT COUNT(*) c FROM templates").fetchone()["c"]:
        return
    for pos, (name, tasks) in enumerate(DEFAULT_TEMPLATES):
        tid = uid("tpl")
        conn.execute("INSERT INTO templates (id, name, position) VALUES (?,?,?)", (tid, name, pos))
        for tpos, (title, comment) in enumerate(tasks):
            conn.execute(
                "INSERT INTO template_tasks (template_id, title, comment, position) VALUES (?,?,?,?)",
                (tid, title, comment, tpos),
            )


class Tx:
    """Context manager giving a cursor inside a serialized transaction."""

    def __enter__(self):
        _lock.acquire()
        self.conn = connect()
        return self.conn

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        finally:
            _lock.release()
        return False


# ---------------------------------------------------------------- passwords

def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"pbkdf2_sha256$200000${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_password(password, stored):
    try:
        algo, rounds, salt_b64, digest_b64 = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), base64.b64decode(salt_b64), int(rounds))
        return secrets.compare_digest(digest, base64.b64decode(digest_b64))
    except Exception:
        return False


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------------------------------------------------------------- auth

def create_user(email, password, name):
    """Роль при регистрации не выбирается: первый пользователь становится завучом,
    остальные — учителями, и повысить их может только завуч."""
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        raise ValueError("Укажите корректный email.")
    if len(password) < 6:
        raise ValueError("Пароль должен быть не короче 6 символов.")
    if not name.strip():
        raise ValueError("Укажите имя и фамилию.")
    with Tx() as conn:
        if conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            raise ValueError("Пользователь с таким email уже существует.")
        role = "zavuch" if conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"] == 0 else "teacher"
        conn.execute(
            "INSERT INTO users (email, name, role, password_hash, created_at) VALUES (?,?,?,?,?)",
            (email, name.strip(), role, hash_password(password), now_iso()),
        )
        return conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()


def authenticate(email, password):
    email = (email or "").strip().lower()
    with Tx() as conn:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not row or not verify_password(password or "", row["password_hash"]):
        return None
    return row


def create_session(user_id):
    token = secrets.token_urlsafe(32)
    with Tx() as conn:
        conn.execute("INSERT INTO sessions (token, user_id, created_at) VALUES (?,?,?)", (token, user_id, now_iso()))
    return token


def delete_session(token):
    with Tx() as conn:
        conn.execute("DELETE FROM sessions WHERE token=?", (token,))


def user_for_token(token):
    if not token:
        return None
    with Tx() as conn:
        return conn.execute(
            "SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.token=?", (token,)
        ).fetchone()


# ---------------------------------------------------------------- activity

def log_activity(conn, actor, type_, message):
    conn.execute(
        "INSERT INTO activity (id, actor_id, actor_name, type, message, created_at) VALUES (?,?,?,?,?,?)",
        (uid("act"), actor["id"], actor["name"], type_, message, now_iso()),
    )
    conn.execute(
        "DELETE FROM activity WHERE id NOT IN (SELECT id FROM activity ORDER BY created_at DESC LIMIT 200)"
    )


# ---------------------------------------------------------------- state

def full_state(conn, me):
    users = conn.execute("SELECT id, email, name, role FROM users ORDER BY name").fetchall()
    email_by_id = {u["id"]: u["email"] for u in users}

    reactions = {}
    for r in conn.execute("SELECT * FROM idea_reactions").fetchall():
        reactions.setdefault(r["idea_id"], {}).setdefault(r["emoji"], []).append(email_by_id.get(r["user_id"], ""))

    comments = {}
    for c in conn.execute(
        "SELECT c.*, u.name AS author_name FROM idea_comments c LEFT JOIN users u ON u.id=c.user_id ORDER BY c.created_at"
    ).fetchall():
        comments.setdefault(c["idea_id"], []).append(
            {"author": c["author_name"] or "—", "text": c["text"], "createdAt": c["created_at"]}
        )

    ideas = []
    for i in conn.execute(
        "SELECT i.*, u.name AS author_name, u.email AS author_email FROM ideas i "
        "LEFT JOIN users u ON u.id=i.author_id ORDER BY i.created_at DESC"
    ).fetchall():
        ideas.append({
            "id": i["id"],
            "title": i["title"],
            "description": i["description"],
            "author": i["author_email"] or "",
            "authorName": i["author_name"] or "—",
            "createdAt": i["created_at"],
            "status": i["status"],
            "convertedEventId": i["converted_event_id"],
            "reactions": reactions.get(i["id"], {}),
            "comments": comments.get(i["id"], []),
        })

    resp = {}
    for r in conn.execute("SELECT * FROM task_responsible").fetchall():
        resp.setdefault(r["task_id"], []).append(email_by_id.get(r["user_id"], ""))

    tasks_by_event = {}
    for t in conn.execute("SELECT * FROM tasks ORDER BY position, id").fetchall():
        tasks_by_event.setdefault(t["event_id"], []).append({
            "id": t["id"],
            "title": t["title"],
            "comment": t["comment"],
            "deadline": t["deadline"],
            "status": t["status"],
            "responsible": resp.get(t["id"], []),
        })

    files_by_event = {}
    for f in conn.execute("SELECT id, event_id, name, size FROM files ORDER BY created_at").fetchall():
        files_by_event.setdefault(f["event_id"], []).append(
            {"id": f["id"], "name": f["name"], "size": f["size"], "url": f"/api/files/{f['id']}"}
        )

    events = []
    for e in conn.execute(
        "SELECT e.*, u.email AS creator_email FROM events e LEFT JOIN users u ON u.id=e.created_by "
        "ORDER BY e.created_at DESC"
    ).fetchall():
        ev = {
            "id": e["id"],
            "title": e["title"],
            "description": e["description"],
            "date": e["date"],
            "location": e["location"],
            "budget": e["budget"],
            "status": e["status"],
            "createdBy": e["creator_email"] or "",
            "createdAt": e["created_at"],
            "sourceIdeaId": e["source_idea_id"],
            "templateId": e["template_id"],
            "tasks": tasks_by_event.get(e["id"], []),
        }
        if e["status"] == "done" or e["archive_summary"] or files_by_event.get(e["id"]):
            ev["archive"] = {
                "summary": e["archive_summary"] or "",
                "archivedAt": e["archived_at"],
                "files": files_by_event.get(e["id"], []),
            }
        events.append(ev)

    tpl_tasks = {}
    for t in conn.execute("SELECT * FROM template_tasks ORDER BY position, id").fetchall():
        tpl_tasks.setdefault(t["template_id"], []).append({"title": t["title"], "comment": t["comment"]})
    templates = [
        {"id": t["id"], "name": t["name"], "tasks": tpl_tasks.get(t["id"], [])}
        for t in conn.execute("SELECT * FROM templates ORDER BY position, id").fetchall()
    ]

    name_by_id = {u["id"]: u["name"] for u in users}
    adjustments = [
        {
            "id": a["id"],
            "email": email_by_id.get(a["user_id"], ""),
            "points": a["points"],
            "reason": a["reason"],
            "byName": name_by_id.get(a["created_by"], "—"),
            "createdAt": a["created_at"],
        }
        for a in conn.execute("SELECT * FROM point_adjustments ORDER BY created_at DESC").fetchall()
    ]

    # айлық жоспар: {'2026-09': [{weekNo, topic, items: [...]}, ...]}
    items_by_week = {}
    for i in conn.execute("SELECT * FROM plan_items ORDER BY position, id").fetchall():
        items_by_week.setdefault(i["week_id"], []).append({
            "id": i["id"],
            "title": i["title"],
            "responsible": email_by_id.get(i["responsible_id"], ""),
            "responsibleName": i["responsible_name"],
        })

    plan = {}
    for w in conn.execute("SELECT * FROM plan_weeks ORDER BY month, week_no").fetchall():
        plan.setdefault(w["month"], []).append({
            "id": w["id"],
            "weekNo": w["week_no"],
            "topic": w["topic"],
            "items": items_by_week.get(w["id"], []),
        })

    activity = [
        {
            "id": a["id"],
            "actorName": a["actor_name"],
            "type": a["type"],
            "message": a["message"],
            "timestamp": a["created_at"],
        }
        for a in conn.execute("SELECT * FROM activity ORDER BY created_at DESC LIMIT 60").fetchall()
    ]

    return {
        "me": {"email": me["email"], "name": me["name"], "role": me["role"]} if me else None,
        "users": [{"email": u["email"], "name": u["name"], "role": u["role"]} for u in users],
        "ideas": ideas,
        "events": events,
        "templates": templates,
        "adjustments": adjustments,
        "activity": activity,
        "plan": plan,
    }


def user_id_by_email(conn, email):
    row = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
    return row["id"] if row else None
