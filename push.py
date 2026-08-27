"""Push-уведомления на телефон (Web Push + VAPID).

Отправка включается только когда заданы ключи VAPID_PUBLIC_KEY и VAPID_PRIVATE_KEY;
без них приложение работает как раньше, просто без уведомлений.

Два повода написать учителю:
  • сразу — когда на него назначили задачу или мероприятие одобрили;
  • раз в день — напоминание о задачах, у которых подходит или прошёл срок
    (эндпоинт /api/cron/notify, его дёргает внешний планировщик).
"""

import json
import os
import sys

import db

VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY", "").strip()
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "").strip()
VAPID_SUBJECT = os.environ.get("VAPID_SUBJECT", "mailto:admin@dostyq.school").strip()
CRON_KEY = os.environ.get("PUSH_CRON_KEY", "").strip()

ENABLED = bool(VAPID_PUBLIC_KEY and VAPID_PRIVATE_KEY)


def _webpush():
    """pywebpush импортируется лениво: без ключей зависимость не нужна."""
    from pywebpush import webpush, WebPushException
    return webpush, WebPushException


def save_subscription(conn, user_id, subscription):
    keys = subscription.get("keys") or {}
    endpoint = str(subscription.get("endpoint") or "")[:1000]
    p256dh, auth = str(keys.get("p256dh") or ""), str(keys.get("auth") or "")
    if not (endpoint and p256dh and auth):
        return False
    conn.execute(
        "INSERT INTO push_subscriptions (endpoint, user_id, p256dh, auth, created_at) VALUES (?,?,?,?,?)"
        " ON CONFLICT(endpoint) DO UPDATE SET user_id=excluded.user_id, p256dh=excluded.p256dh, auth=excluded.auth",
        (endpoint, user_id, p256dh, auth, db.now_iso()),
    )
    return True


def delete_subscription(conn, endpoint):
    conn.execute("DELETE FROM push_subscriptions WHERE endpoint=?", (endpoint,))


def _send_one(row, payload):
    """Возвращает True, если доставлено; False — если подписка больше не годится."""
    webpush, WebPushException = _webpush()
    try:
        webpush(
            subscription_info={
                "endpoint": row["endpoint"],
                "keys": {"p256dh": row["p256dh"], "auth": row["auth"]},
            },
            data=json.dumps(payload, ensure_ascii=False),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_SUBJECT},
            timeout=10,
        )
        return True
    except WebPushException as err:
        status = getattr(err.response, "status_code", None)
        # 404/410 — подписка отозвана: браузер удалён, приложение снесено
        if status in (404, 410):
            return False
        print(f"push: не отправлено ({status}): {err}", file=sys.stderr, flush=True)
        return True
    except Exception as err:  # сеть, таймаут — подписку не трогаем
        print(f"push: ошибка отправки: {err}", file=sys.stderr, flush=True)
        return True


def notify_users(user_ids, title, body, url="/"):
    """Шлёт уведомление всем устройствам перечисленных пользователей."""
    if not ENABLED or not user_ids:
        return 0
    payload = {"title": title, "body": body, "url": url}
    sent, dead = 0, []
    with db.Tx() as conn:
        placeholders = ",".join("?" for _ in user_ids)
        rows = conn.execute(
            f"SELECT * FROM push_subscriptions WHERE user_id IN ({placeholders})", tuple(user_ids)
        ).fetchall()
        for row in rows:
            if _send_one(row, payload):
                sent += 1
            else:
                dead.append(row["endpoint"])
        for endpoint in dead:
            conn.execute("DELETE FROM push_subscriptions WHERE endpoint=?", (endpoint,))
    return sent


def notify_task_assigned(conn, task_title, event_title, deadline, user_ids):
    """Мгновенное уведомление тем, кого только что назначили ответственными."""
    if not ENABLED or not user_ids:
        return
    tail = f" · срок {_human_date(deadline)}" if deadline else ""
    notify_users(
        user_ids,
        "Вам назначена задача",
        f"{task_title} — {event_title}{tail}",
        "/",
    )


def _human_date(value):
    if not value:
        return ""
    try:
        year, month, day = value.split("-")
        months = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
        return f"{int(day)} {months[int(month) - 1]}"
    except Exception:
        return value


REMINDER_HOUR = int(os.environ.get("REMINDER_HOUR", "8"))        # час местного времени
TZ_OFFSET_HOURS = int(os.environ.get("TZ_OFFSET_HOURS", "5"))    # Казахстан — UTC+5


def _local_now():
    from datetime import datetime, timedelta, timezone
    return datetime.now(timezone.utc) + timedelta(hours=TZ_OFFSET_HOURS)


def _reminder_sent_today(conn, day):
    row = conn.execute("SELECT value FROM settings WHERE key='last_reminder_day'").fetchone()
    return bool(row) and row["value"] == day


def _mark_reminder_sent(conn, day):
    conn.execute(
        "INSERT INTO settings (key, value) VALUES ('last_reminder_day', ?)"
        " ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (day,),
    )


def maybe_send_daily(force=False):
    """Рассылает напоминания раз в сутки после REMINDER_HOUR.

    Вызывается фоновым потоком и внешним планировщиком: повторную отправку
    в тот же день отсекает отметка в базе, поэтому лишних уведомлений не будет.
    """
    if not ENABLED:
        return {"enabled": False, "sent": 0}
    now = _local_now()
    day = now.date().isoformat()
    with db.Tx() as conn:
        if _reminder_sent_today(conn, day):
            return {"skipped": "уже отправляли сегодня", "sent": 0}
        if not force and now.hour < REMINDER_HOUR:
            return {"skipped": f"ещё рано, рассылка после {REMINDER_HOUR}:00", "sent": 0}
        _mark_reminder_sent(conn, day)
    result = run_deadline_reminders(now.date())
    result["day"] = day
    return result


def start_scheduler():
    """Фоновый поток: проверяет раз в 10 минут, не пора ли рассылать напоминания.

    На бесплатном хостинге сервис засыпает при простое, поэтому поток —
    не гарантия: он сработает, когда приложение проснётся. Для точного времени
    есть эндпоинт /api/cron/notify, который может дёргать внешний планировщик.
    """
    if not ENABLED:
        return
    import threading

    def loop():
        import time
        while True:
            try:
                result = maybe_send_daily()
                if result.get("sent"):
                    print(f"push: напоминания отправлены — {result}", flush=True)
            except Exception as err:
                print(f"push: планировщик: {err}", file=sys.stderr, flush=True)
            time.sleep(600)

    threading.Thread(target=loop, daemon=True, name="reminders").start()


def run_deadline_reminders(today=None):
    """Ежедневная рассылка: просроченные задачи и те, у которых срок в ближайшие 3 дня."""
    if not ENABLED:
        return {"enabled": False, "sent": 0}

    from datetime import date, datetime, timedelta
    today = today or date.today()
    horizon = (today + timedelta(days=3)).isoformat()

    per_user = {}
    with db.Tx() as conn:
        rows = conn.execute(
            "SELECT t.title, t.deadline, e.title AS event_title, r.user_id"
            " FROM tasks t"
            " JOIN events e ON e.id = t.event_id"
            " JOIN task_responsible r ON r.task_id = t.id"
            " WHERE t.status <> 'done' AND e.status IN ('draft','pending','approved')"
            "   AND t.deadline <> '' AND t.deadline <= ?",
            (horizon,),
        ).fetchall()

    for row in rows:
        per_user.setdefault(row["user_id"], []).append(row)

    total = 0
    for user_id, tasks in per_user.items():
        overdue = [t for t in tasks if t["deadline"] < today.isoformat()]
        soon = [t for t in tasks if t["deadline"] >= today.isoformat()]
        if overdue and soon:
            title = f"Просрочено: {len(overdue)}, скоро срок: {len(soon)}"
        elif overdue:
            title = f"Просроченных задач: {len(overdue)}" if len(overdue) > 1 else "Задача просрочена"
        else:
            title = f"Скоро срок у задач: {len(soon)}" if len(soon) > 1 else "Приближается срок задачи"

        first = (overdue or soon)[0]
        body = f"{first['title']} — {first['event_title']} · {_human_date(first['deadline'])}"
        if len(tasks) > 1:
            body += f" и ещё {len(tasks) - 1}"
        total += notify_users([user_id], title, body, "/")

    return {"enabled": True, "users": len(per_user), "sent": total}
