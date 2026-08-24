/* School Events — фронтенд. React загружается из CDN, JSX компилируется Babel Standalone.
   Все данные приходят с сервера (Python + SQLite) через /api. */

const { useState, useEffect, useMemo, useCallback, useRef } = React;

/* ----------------------------------------------------------------------
   ИКОНКИ
---------------------------------------------------------------------- */
function makeIcon(paths) {
  return function IconComponent({ size = 16, color = "currentColor", fill = "none", style }) {
    return (
      <svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill={fill}
        stroke={color}
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{ flexShrink: 0, ...style }}
        aria-hidden="true"
      >
        {paths}
      </svg>
    );
  };
}

const Home = makeIcon(<><path d="M3 10.5 12 3l9 7.5" /><path d="M5.5 9.6V20h13V9.6" /><path d="M10 20v-5h4v5" /></>);
const Lightbulb = makeIcon(<><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z" /><path d="M9.5 19h5" /><path d="M10.5 21.5h3" /></>);
const LayoutGrid = makeIcon(<><rect x="3" y="3" width="7.5" height="7.5" rx="1.6" /><rect x="13.5" y="3" width="7.5" height="7.5" rx="1.6" /><rect x="3" y="13.5" width="7.5" height="7.5" rx="1.6" /><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.6" /></>);
const CalendarIcon = makeIcon(<><rect x="3" y="5" width="18" height="16" rx="2.2" /><path d="M8 3v4M16 3v4M3 10h18" /></>);
const FileText = makeIcon(<><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" /><path d="M14 3v5h5" /><path d="M9 13h6M9 17h5" /></>);
const ArchiveIcon = makeIcon(<><rect x="3" y="4" width="18" height="4.5" rx="1.4" /><path d="M5 8.5V19a1.5 1.5 0 0 0 1.5 1.5h11A1.5 1.5 0 0 0 19 19V8.5" /><path d="M10 12.5h4" /></>);
const Bell = makeIcon(<><path d="M18 16.5V11a6 6 0 1 0-12 0v5.5L4 19.5h16z" /><path d="M10 21.5a2.2 2.2 0 0 0 4 0" /></>);
const Trophy = makeIcon(<><path d="M8 3.5h8V9a4 4 0 0 1-8 0z" /><path d="M8 5H5.2a3 3 0 0 0 2.9 3.4" /><path d="M16 5h2.8a3 3 0 0 1-2.9 3.4" /><path d="M12 13v4" /><path d="M9.5 21h5l-.8-4h-3.4z" /></>);
const UsersIcon = makeIcon(<><circle cx="9.5" cy="8" r="3.4" /><path d="M3.5 20c0-3.3 2.7-5.4 6-5.4s6 2.1 6 5.4" /><path d="M16.5 5.3a3.4 3.4 0 0 1 0 5.4" /><path d="M18 14.9c1.9.8 3 2.4 3 5.1" /></>);
const UserCircle2 = makeIcon(<><circle cx="12" cy="12" r="9" /><circle cx="12" cy="10" r="3" /><path d="M6.4 19.2a6.2 6.2 0 0 1 11.2 0" /></>);
const LogOut = makeIcon(<><path d="M10 4H6.5A2.5 2.5 0 0 0 4 6.5v11A2.5 2.5 0 0 0 6.5 20H10" /><path d="M16.5 15.5 20 12l-3.5-3.5" /><path d="M20 12H10" /></>);
const Plus = makeIcon(<><path d="M12 5.5v13M5.5 12h13" /></>);
const X = makeIcon(<><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" /></>);
const Check = makeIcon(<><path d="M5 12.5 10 17.5 19 7" /></>);
const Trash2 = makeIcon(<><path d="M4 7h16" /><path d="M10 4.2h4" /><path d="M6.5 7l.9 12.2A1.5 1.5 0 0 0 8.9 20.5h6.2a1.5 1.5 0 0 0 1.5-1.3L17.5 7" /><path d="M10.5 11v6M13.5 11v6" /></>);
const Pencil = makeIcon(<><path d="M4 20.2h4L20 8.2l-4-4L4 16.2z" /><path d="M14.5 5.7l3.8 3.8" /></>);
const Search = makeIcon(<><circle cx="11" cy="11" r="6.2" /><path d="M20 20l-4.6-4.6" /></>);
const MapPin = makeIcon(<><path d="M12 21.2s7-6.1 7-11.2a7 7 0 1 0-14 0c0 5.1 7 11.2 7 11.2z" /><circle cx="12" cy="10" r="2.6" /></>);
const Wallet = makeIcon(<><path d="M4 7.5V6.4A1.9 1.9 0 0 1 5.9 4.5H16v3" /><rect x="3" y="7.5" width="18" height="12" rx="2.2" /><path d="M17 13.5h.01" /></>);
const ChevronLeft = makeIcon(<><path d="M14.5 5.5 8 12l6.5 6.5" /></>);
const ChevronRight = makeIcon(<><path d="M9.5 5.5 16 12l-6.5 6.5" /></>);
const Paperclip = makeIcon(<><path d="M19.5 11.5 11 20a4.6 4.6 0 0 1-6.5-6.5l8.7-8.7a3.1 3.1 0 0 1 4.4 4.4l-8.7 8.7a1.6 1.6 0 0 1-2.2-2.2l8-8" /></>);
const Star = makeIcon(<><path d="M12 3.6l2.6 5.4 5.9.8-4.3 4.2 1 5.9-5.2-2.8-5.2 2.8 1-5.9L3.5 9.8l5.9-.8z" /></>);
const ArrowRight = makeIcon(<><path d="M4.5 12h15" /><path d="M13.5 6l6 6-6 6" /></>);
const Activity = makeIcon(<><path d="M3 12.5h4l3 7.5 4-16 3 8.5h4" /></>);
const Clock = makeIcon(<><circle cx="12" cy="12" r="9" /><path d="M12 6.8V12l3.4 2" /></>);
const TableIcon = makeIcon(<><rect x="3" y="4.5" width="18" height="15" rx="2" /><path d="M3 9.5h18M9 9.5V19.5M3 14.5h18" /></>);
const Download = makeIcon(<><path d="M12 4v11" /><path d="M8 11.5l4 4 4-4" /><path d="M4.5 19.5h15" /></>);
const Printer = makeIcon(<><path d="M7 9V4h10v5" /><rect x="3.5" y="9" width="17" height="7" rx="1.8" /><path d="M7 14h10v6H7z" /></>);

/* ----------------------------------------------------------------------
   КОНСТАНТЫ
---------------------------------------------------------------------- */
const REACTIONS = ["👍", "❤️", "🔥", "🎉"];

const KZ_MONTHS = ["Қаңтар", "Ақпан", "Наурыз", "Сәуір", "Мамыр", "Маусым", "Шілде", "Тамыз", "Қыркүйек", "Қазан", "Қараша", "Желтоқсан"];
const VALUES_BY_MONTH = {
  9: "Еңбекқорлық және кәсіби біліктілік айы",
  10: "Тәуелсіздік және отаншылдық айы",
  11: "Әділдік және жауапкершілік айы",
  12: "Бірлік және ынтымақ айы",
  1: "Заң және тәртіп айы",
  2: "Жасампаздық және жаңашылдық айы",
  3: "Тәуелсіздік және отаншылдық айы",
  4: "Еңбекқорлық және кәсіби біліктілік айы",
  5: "Бірлік және ынтымақ айы",
};
const getMonthValue = (m) => VALUES_BY_MONTH[m] || null;

const STATUS_LABELS = {
  draft: { label: "Черновик", color: "var(--text-soft)", bg: "var(--surface-2)" },
  pending: { label: "На рассмотрении", color: "var(--warning)", bg: "var(--warning-soft)" },
  approved: { label: "Одобрено", color: "var(--success)", bg: "var(--success-soft)" },
  rejected: { label: "Отклонено", color: "var(--danger)", bg: "var(--danger-soft)" },
  done: { label: "Проведено", color: "var(--accent)", bg: "var(--accent-soft)" },
};
const TASK_STATUS_LABELS = {
  todo: { label: "Не начато", color: "var(--text-soft)", bg: "var(--surface-2)" },
  in_progress: { label: "В работе", color: "var(--warning)", bg: "var(--warning-soft)" },
  done: { label: "Готово", color: "var(--success)", bg: "var(--success-soft)" },
};

const POINTS_PER_TASK = 100;
const POINTS_PER_IDEA = 10;
const POINTS_PER_APPROVED_IDEA = 50;
// Задача считается проваленной, только когда мероприятие отмечено проведённым,
// а её статус остался не «Готово». Пока мероприятие идёт, минусов нет.
const POINTS_PER_FAILED_TASK = 100;

/* Призовой фонд: победителя рейтинга объявляют перед Новым годом.
   Чтобы изменить приз или дату — правьте только этот объект. */
const PRIZE = {
  title: "Сертификат на 100 000 ₸",
  subtitle: "победителю рейтинга учителей",
  announceDay: 25,
  announceMonth: 12,
};

function prizeAnnounceDate() {
  const now = new Date();
  const thisYear = new Date(now.getFullYear(), PRIZE.announceMonth - 1, PRIZE.announceDay);
  thisYear.setHours(23, 59, 59, 0);
  return now > thisYear
    ? new Date(now.getFullYear() + 1, PRIZE.announceMonth - 1, PRIZE.announceDay)
    : thisYear;
}

function daysWord(n) {
  const last = n % 10, two = n % 100;
  if (two >= 11 && two <= 14) return "дней";
  if (last === 1) return "день";
  if (last >= 2 && last <= 4) return "дня";
  return "дней";
}

function pointsWord(n) {
  const last = n % 10, two = n % 100;
  if (two >= 11 && two <= 14) return "очков";
  if (last === 1) return "очко";
  if (last >= 2 && last <= 4) return "очка";
  return "очков";
}

const LEVEL_STYLES = {
  1: { bg: "#ffffff", border: "var(--border)", chip: "var(--surface-2)", chipText: "var(--text-soft)" },
  2: { bg: "#f6e3d0", border: "#b8703a", chip: "#e7c4a0", chipText: "#7a4419" },
  3: { bg: "#eef0f3", border: "#9aa7b5", chip: "#d9dee4", chipText: "#4a5560" },
  4: { bg: "#fdf1cf", border: "#d1a520", chip: "#f3dd94", chipText: "#8a6a08" },
};
const getLevelStyle = (level) => LEVEL_STYLES[Math.min(level, 4)] || LEVEL_STYLES[1];

/* ----------------------------------------------------------------------
   УТИЛИТЫ
---------------------------------------------------------------------- */
function fmtDate(d) {
  if (!d) return "—";
  const dt = new Date(d + "T00:00:00");
  if (isNaN(dt)) return d;
  return dt.toLocaleDateString("ru-RU", { day: "2-digit", month: "short", year: "numeric" });
}
function daysUntil(dateStr) {
  if (!dateStr) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Math.round((new Date(dateStr + "T00:00:00") - today) / 86400000);
}
function timeAgo(iso) {
  const min = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
  if (min < 1) return "только что";
  if (min < 60) return `${min} мин назад`;
  const hrs = Math.floor(min / 60);
  if (hrs < 24) return `${hrs} ч назад`;
  const days = Math.floor(hrs / 24);
  if (days === 1) return "вчера";
  if (days < 7) return `${days} дн назад`;
  return new Date(iso).toLocaleDateString("ru-RU", { day: "2-digit", month: "short" });
}
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(",")[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

function computeRanking(events, ideas, users, adjustments) {
  const points = {}, doneTasks = {}, failedTasks = {}, ideasProposed = {}, ideasApproved = {};

  events.forEach((ev) => {
    (ev.tasks || []).forEach((t) => {
      if (t.status === "done") {
        (t.responsible || []).forEach((email) => {
          points[email] = (points[email] || 0) + POINTS_PER_TASK;
          doneTasks[email] = (doneTasks[email] || 0) + 1;
        });
      } else if (ev.status === "done") {
        (t.responsible || []).forEach((email) => {
          points[email] = (points[email] || 0) - POINTS_PER_FAILED_TASK;
          failedTasks[email] = (failedTasks[email] || 0) + 1;
        });
      }
    });
  });

  // Удалённая идея очки не отнимает: автор уже вложил труд, а удаление — нейтральное действие
  ideas.forEach((idea) => {
    if (!idea.author) return;
    points[idea.author] = (points[idea.author] || 0) + POINTS_PER_IDEA;
    ideasProposed[idea.author] = (ideasProposed[idea.author] || 0) + 1;
    if (idea.status === "converted") {
      points[idea.author] = (points[idea.author] || 0) + POINTS_PER_APPROVED_IDEA;
      ideasApproved[idea.author] = (ideasApproved[idea.author] || 0) + 1;
    }
  });

  const manual = {};
  (adjustments || []).forEach((a) => {
    manual[a.email] = (manual[a.email] || 0) + a.points;
  });

  return users
    .map((u) => {
      const rawPoints = points[u.email] || 0;
      const adjusted = manual[u.email] || 0;
      const finalPoints = rawPoints + adjusted;
      return {
        ...u,
        rawPoints,
        adjusted,
        points: finalPoints,
        tasksDone: doneTasks[u.email] || 0,
        tasksFailed: failedTasks[u.email] || 0,
        ideasProposed: ideasProposed[u.email] || 0,
        ideasApproved: ideasApproved[u.email] || 0,
        // уровень считается только по набранным очкам: минус не опускает ниже первого
        level: 1 + Math.floor(Math.max(0, finalPoints) / 500),
      };
    })
    .sort((a, b) => b.points - a.points || b.tasksDone - a.tasksDone);
}

/* ----------------------------------------------------------------------
   API
---------------------------------------------------------------------- */
async function apiCall(method, path, body) {
  const res = await fetch(path, {
    method,
    credentials: "same-origin",
    headers: body === undefined ? {} : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  let data = {};
  try {
    data = await res.json();
  } catch (e) {
    /* пустой ответ */
  }
  if (!res.ok) {
    const err = new Error(data.error || `Ошибка ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return data;
}

/* ----------------------------------------------------------------------
   ГЛАВНЫЙ КОМПОНЕНТ
---------------------------------------------------------------------- */
function App() {
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState(null);
  const [tab, setTab] = useState("home");
  const [profileOpen, setProfileOpen] = useState(false);
  const busyRef = useRef(false);

  const showToast = useCallback((text, ok = false) => {
    setToast({ text, ok });
    setTimeout(() => setToast(null), 3600);
  }, []);

  const run = useCallback(async (method, path, body) => {
    busyRef.current = true;
    setBusy(true);
    try {
      const next = await apiCall(method, path, body);
      setState(next);
      return next;
    } catch (err) {
      if (err.status === 401) setState(null);
      showToast(err.message);
      throw err;
    } finally {
      busyRef.current = false;
      setBusy(false);
    }
  }, [showToast]);

  useEffect(() => {
    (async () => {
      try {
        setState(await apiCall("GET", "/api/state"));
      } catch (e) {
        setState(null);
      }
      setLoading(false);
    })();
  }, []);

  // фоновое обновление — данные общие для всей школы
  useEffect(() => {
    if (!state?.me) return;
    const id = setInterval(async () => {
      if (busyRef.current || document.hidden) return;
      try {
        setState(await apiCall("GET", "/api/state"));
      } catch (e) {
        /* сеть отвалилась — покажем актуальные данные при следующем тике */
      }
    }, 15000);
    return () => clearInterval(id);
  }, [state?.me]);

  const currentUser = state?.me || null;
  const users = state?.users || [];
  const ideas = state?.ideas || [];
  const events = state?.events || [];
  const templates = state?.templates || [];
  const adjustments = state?.adjustments || [];
  const activity = state?.activity || [];
  const plan = state?.plan || {};
  const isZavuch = currentUser?.role === "zavuch";

  const myTaskNotifications = useMemo(() => {
    if (!currentUser) return [];
    const list = [];
    events.forEach((ev) => {
      (ev.tasks || []).forEach((t) => {
        if (!t.responsible?.includes(currentUser.email) || t.status === "done") return;
        const dleft = daysUntil(t.deadline);
        if (dleft === null) return;
        if (dleft < 0) list.push({ type: "overdue", event: ev, task: t, days: dleft });
        else if (dleft <= 3) list.push({ type: "soon", event: ev, task: t, days: dleft });
      });
    });
    return list.sort((a, b) => a.days - b.days);
  }, [events, currentUser]);

  const pendingApprovalCount = useMemo(() => events.filter((e) => e.status === "pending").length, [events]);

  const myRankInfo = useMemo(() => {
    if (!currentUser) return null;
    return computeRanking(events, ideas, users, adjustments).find((r) => r.email === currentUser.email) || null;
  }, [events, ideas, users, adjustments, currentUser]);

  const handleLogout = async () => {
    try {
      await apiCall("POST", "/api/auth/logout");
    } catch (e) {
      /* сессия и так недействительна */
    }
    setState(null);
    setTab("home");
  };

  if (loading) {
    return <div className="sea-root"><div className="sea-boot">Загрузка…</div></div>;
  }

  if (!currentUser) {
    return (
      <div className="sea-root">
        <AuthScreen
          onLogin={(email, password) => run("POST", "/api/auth/login", { email, password })}
          onRegister={(data) => run("POST", "/api/auth/register", data)}
        />
        {toast && <Toast toast={toast} />}
      </div>
    );
  }

  const NAV_ITEMS = [
    { key: "home", label: "Главная", icon: Home },
    { key: "ideas", label: "Доска идей", icon: Lightbulb },
    { key: "events", label: "Мероприятия", icon: LayoutGrid, badge: isZavuch ? pendingApprovalCount : 0 },
    { key: "calendar", label: "Календарь", icon: CalendarIcon },
    { key: "plan", label: "Айлық жоспар", icon: TableIcon },
    { key: "templates", label: "Шаблоны", icon: FileText },
    { key: "archive", label: "Архив", icon: ArchiveIcon },
    { key: "notifications", label: "Уведомления", icon: Bell, badge: myTaskNotifications.length },
    { key: "leaderboard", label: "Рейтинг", icon: Trophy },
    { key: "users", label: "Пользователи", icon: UsersIcon },
  ];

  const now = new Date();
  const monthValue = getMonthValue(now.getMonth() + 1);

  return (
    <div className="sea-root">
      <header className="sea-header">
        <div style={{ maxWidth: 1180, margin: "0 auto", padding: "12px 20px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, marginBottom: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <img src="/logo.png?v=1" alt="Dostyq School" style={{ height: 32, width: "auto", display: "block" }} />
              <div style={{ width: 1, height: 26, background: "var(--border)" }} />
              <div>
                <div style={{ fontWeight: 700, fontSize: 15, letterSpacing: "-0.01em" }}>Events</div>
                <div style={{ fontSize: 11.5, color: "var(--text-faint)" }}>{busy ? "Сохранение…" : "Планирование и задачи"}</div>
              </div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div className="sea-hide-mobile" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <button
                  onClick={() => setProfileOpen(true)}
                  className="sea-btn sea-btn-ghost"
                  style={{ padding: "4px 8px", gap: 8 }}
                  title="Изменить имя"
                >
                  <UserCircle2 size={18} color="var(--text-faint)" />
                  <span style={{ textAlign: "left" }}>
                    <span style={{ fontSize: 13, fontWeight: 600, display: "block" }}>{currentUser.name}</span>
                    <span style={{ fontSize: 11, color: "var(--text-faint)" }}>{isZavuch ? "Завуч" : "Учитель"}</span>
                  </span>
                </button>
                {myRankInfo && (() => {
                  const earned = Math.max(0, myRankInfo.points);
                  return (
                    <div style={{ width: 74, marginLeft: 4 }} title={`${earned % 500}/500 очков до уровня ${myRankInfo.level + 1}`}>
                      <div style={{ fontSize: 9.5, color: myRankInfo.points < 0 ? "var(--danger)" : "var(--text-faint)", marginBottom: 2, whiteSpace: "nowrap" }}>
                        {myRankInfo.points < 0 ? `${myRankInfo.points} очков` : `Ур. ${myRankInfo.level} · ${500 - (earned % 500)} до след.`}
                      </div>
                      <div style={{ height: 5, background: "var(--surface-2)", borderRadius: 999, overflow: "hidden" }}>
                        <div style={{ height: "100%", width: `${((earned % 500) / 500) * 100}%`, background: "var(--accent)", borderRadius: 999 }} />
                      </div>
                    </div>
                  );
                })()}
              </div>
              <button className="sea-btn sea-btn-ghost" onClick={handleLogout} title="Выйти">
                <LogOut size={15} /> <span className="sea-hide-mobile">Выйти</span>
              </button>
            </div>
          </div>
          <nav className="sea-scrollbar" style={{ display: "flex", gap: 4, overflowX: "auto", paddingBottom: 2 }}>
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              return (
                <button key={item.key} className={`sea-nav-tab ${tab === item.key ? "active" : ""}`} onClick={() => setTab(item.key)}>
                  <Icon size={15} />
                  {item.label}
                  {!!item.badge && (
                    <span style={{ background: "var(--danger)", color: "#fff", fontSize: 10, fontWeight: 700, borderRadius: 999, minWidth: 16, height: 16, display: "flex", alignItems: "center", justifyContent: "center", padding: "0 4px", marginLeft: 2 }}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
        {monthValue && (
          <div style={{ background: "var(--accent)", color: "#fff", fontSize: 12.5, fontWeight: 600, padding: "6px 20px", display: "flex", alignItems: "center", justifyContent: "center", gap: 6, flexWrap: "wrap" }}>
            <span style={{ opacity: 0.85 }}>Құндылық — {KZ_MONTHS[now.getMonth()]}:</span>
            <span>{monthValue}</span>
          </div>
        )}
      </header>

      <main style={{ maxWidth: 1180, margin: "0 auto", padding: "22px 20px 60px" }}>
        {tab === "home" && (
          <DashboardView
            currentUser={currentUser} isZavuch={isZavuch} events={events} ideas={ideas} users={users}
            adjustments={adjustments} activity={activity} pendingApprovalCount={pendingApprovalCount}
            myTaskNotifications={myTaskNotifications} onNavigate={setTab}
          />
        )}
        {tab === "ideas" && (
          <IdeasBoard
            ideas={ideas} currentUser={currentUser} isZavuch={isZavuch} templates={templates}
            run={run} onJumpToEvent={() => setTab("events")}
          />
        )}
        {tab === "events" && (
          <EventsBoard events={events} currentUser={currentUser} isZavuch={isZavuch} users={users} templates={templates} run={run} />
        )}
        {tab === "calendar" && <CalendarView events={events} />}
        {tab === "plan" && <MonthlyPlanView plan={plan} users={users} isZavuch={isZavuch} run={run} />}
        {tab === "templates" && <TemplatesView templates={templates} run={run} />}
        {tab === "archive" && <ArchiveView events={events} users={users} run={run} />}
        {tab === "notifications" && <NotificationsView notifications={myTaskNotifications} onOpenEvents={() => setTab("events")} />}
        {tab === "leaderboard" && (
          <LeaderboardView events={events} users={users} ideas={ideas} adjustments={adjustments} isZavuch={isZavuch} run={run} currentUser={currentUser} />
        )}
        {tab === "users" && <UsersAdminView users={users} currentUser={currentUser} isZavuch={isZavuch} run={run} />}
      </main>

      {profileOpen && (
        <ProfileModal currentUser={currentUser} onClose={() => setProfileOpen(false)} run={run} />
      )}

      {toast && <Toast toast={toast} />}
    </div>
  );
}

function ProfileModal({ currentUser, onClose, run }) {
  const [name, setName] = useState(currentUser.name);
  const [busy, setBusy] = useState(false);

  const save = async () => {
    setBusy(true);
    try {
      await run("PATCH", "/api/me", { name: name.trim() });
      onClose();
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title="Мой профиль" onClose={onClose}>
      <div className="sea-field">
        <label className="sea-label">Имя и фамилия</label>
        <input
          autoFocus
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && name.trim()) save(); }}
        />
        <div style={{ fontSize: 11.5, color: "var(--text-faint)", marginTop: 5 }}>
          Так вас видят коллеги — в рейтинге, в задачах и в плане месяца.
        </div>
      </div>
      <div className="sea-field">
        <label className="sea-label">Email</label>
        <input value={currentUser.email} disabled style={{ background: "var(--surface)", color: "var(--text-faint)" }} />
        <div style={{ fontSize: 11.5, color: "var(--text-faint)", marginTop: 5 }}>
          Email — это логин, он не меняется. Роль назначает завуч.
        </div>
      </div>
      <ModalFooter>
        <button className="sea-btn sea-btn-ghost" onClick={onClose}>Отмена</button>
        <button className="sea-btn sea-btn-primary" disabled={!name.trim() || name.trim() === currentUser.name || busy} onClick={save}>
          Сохранить
        </button>
      </ModalFooter>
    </Modal>
  );
}

function Toast({ toast }) {
  return <div className={`sea-toast ${toast.ok ? "sea-toast-ok" : ""}`}>{toast.text}</div>;
}

/* ----------------------------------------------------------------------
   ВХОД / РЕГИСТРАЦИЯ
---------------------------------------------------------------------- */
function AuthScreen({ onLogin, onRegister }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    setError("");
    const cleanEmail = email.trim().toLowerCase();
    if (!cleanEmail.includes("@")) return setError("Укажите корректный email.");
    if (password.length < 6) return setError("Пароль должен быть не короче 6 символов.");
    if (mode === "register" && !name.trim()) return setError("Укажите имя и фамилию.");

    setBusy(true);
    try {
      if (mode === "login") await onLogin(cleanEmail, password);
      else await onRegister({ email: cleanEmail, password, name: name.trim() });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: 20, background: "var(--surface)" }}>
      <div style={{ width: "100%", maxWidth: 380 }}>
        <div style={{ textAlign: "center", marginBottom: 22 }}>
          <img src="/logo.png?v=1" alt="Dostyq School" style={{ height: 54, width: "auto", margin: "0 auto 14px", display: "block" }} />
          <div style={{ fontWeight: 700, fontSize: 18 }}>Events</div>
          <div style={{ fontSize: 13, color: "var(--text-faint)", marginTop: 3 }}>Планирование, идеи и задачи для коллектива</div>
        </div>

        <div className="sea-card">
          <div style={{ display: "flex", gap: 4, marginBottom: 16, background: "var(--surface-2)", padding: 3, borderRadius: 9 }}>
            {["login", "register"].map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => { setMode(m); setError(""); }}
                className="sea-btn"
                style={{ flex: 1, justifyContent: "center", border: "none", background: mode === m ? "#fff" : "transparent", boxShadow: mode === m ? "var(--shadow-sm)" : "none" }}
              >
                {m === "login" ? "Вход" : "Регистрация"}
              </button>
            ))}
          </div>

          <div onKeyDown={(e) => { if (e.key === "Enter") submit(); }}>
            {mode === "register" && (
              <div className="sea-field">
                <label className="sea-label">Имя и фамилия</label>
                <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Мария Иванова" />
              </div>
            )}
            <div className="sea-field">
              <label className="sea-label">Email</label>
              <input type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@school.kz" />
            </div>
            <div className="sea-field">
              <label className="sea-label">Пароль</label>
              <input type="password" autoComplete={mode === "login" ? "current-password" : "new-password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
            </div>
            {mode === "register" && (
              <div style={{ fontSize: 11.5, color: "var(--text-faint)", marginBottom: 12 }}>
                Все новые аккаунты создаются с ролью «Учитель». Права завуча выдаёт действующий завуч
                на вкладке «Пользователи» (первый зарегистрированный сотрудник получает их автоматически).
              </div>
            )}
            {error && (
              <div style={{ color: "var(--danger)", fontSize: 13, marginBottom: 12, background: "var(--danger-soft)", padding: "8px 10px", borderRadius: 8 }}>
                {error}
              </div>
            )}
            <button type="button" onClick={submit} className="sea-btn sea-btn-primary" style={{ width: "100%", justifyContent: "center", padding: 10 }} disabled={busy}>
              {busy ? "Подождите…" : mode === "login" ? "Войти" : "Создать аккаунт"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ----------------------------------------------------------------------
   ГЛАВНАЯ / ДАШБОРД
---------------------------------------------------------------------- */
function DashboardView({ currentUser, isZavuch, events, ideas, users, adjustments, activity, pendingApprovalCount, myTaskNotifications, onNavigate }) {
  const ranking = useMemo(() => computeRanking(events, ideas, users, adjustments), [events, ideas, users, adjustments]);
  const myRank = ranking.findIndex((r) => r.email === currentUser.email);
  const myPoints = myRank >= 0 ? ranking[myRank].points : 0;
  const openIdeasCount = ideas.filter((i) => i.status !== "converted" && i.status !== "deleted").length;

  const upcoming = useMemo(() => {
    const todayStr = new Date().toISOString().slice(0, 10);
    return events
      .filter((e) => e.status !== "rejected" && e.status !== "done" && e.date && e.date >= todayStr)
      .sort((a, b) => new Date(a.date) - new Date(b.date))
      .slice(0, 4);
  }, [events]);

  const stats = [
    ...(isZavuch ? [{ key: "events", label: "Ожидают одобрения", value: pendingApprovalCount, icon: LayoutGrid, color: "var(--warning)", bg: "var(--warning-soft)" }] : []),
    { key: "notifications", label: "Мои напоминания", value: myTaskNotifications.length, icon: Bell, color: "var(--danger)", bg: "var(--danger-soft)" },
    { key: "ideas", label: "Идей на доске", value: openIdeasCount, icon: Lightbulb, color: "var(--accent)", bg: "var(--accent-soft)" },
    { key: "leaderboard", label: "Мои очки", value: myPoints, icon: Star, color: "var(--success)", bg: "var(--success-soft)" },
  ];

  const monthValue = getMonthValue(new Date().getMonth() + 1);

  return (
    <div>
      <SectionHeader title={`Здравствуйте, ${currentUser.name.split(" ")[0]}!`} subtitle="Краткий обзор того, что происходит в школе прямо сейчас." />

      <div style={{ marginBottom: 16 }}>
        <PrizeBanner ranking={ranking} currentUser={currentUser} onOpenLeaderboard={() => onNavigate("leaderboard")} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 10, marginBottom: 20 }}>
        {stats.map((s) => {
          const Icon = s.icon;
          return (
            <button key={s.key} onClick={() => onNavigate(s.key)} className="sea-card" style={{ textAlign: "left", display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{ width: 38, height: 38, borderRadius: 10, background: s.bg, color: s.color, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                <Icon size={18} />
              </div>
              <div style={{ minWidth: 0 }}>
                <div style={{ fontSize: 20, fontWeight: 800, lineHeight: 1.1 }}>{s.value}</div>
                <div style={{ fontSize: 11.5, color: "var(--text-faint)" }}>{s.label}</div>
              </div>
            </button>
          );
        })}
      </div>

      <div className="sea-dashboard-grid" style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 16 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
            <div style={{ fontWeight: 700, fontSize: 14.5 }}>Ближайшие мероприятия</div>
            <button className="sea-btn sea-btn-ghost" style={{ padding: "4px 8px", fontSize: 12.5 }} onClick={() => onNavigate("events")}>
              Все мероприятия <ArrowRight size={13} />
            </button>
          </div>
          {upcoming.length === 0 ? (
            <EmptyState icon={CalendarIcon} text="Ближайших мероприятий нет" hint="Загляните на доску идей или создайте новое мероприятие" />
          ) : (
            <div style={{ display: "grid", gap: 8 }}>
              {upcoming.map((ev) => {
                const doneCount = (ev.tasks || []).filter((t) => t.status === "done").length;
                const totalCount = (ev.tasks || []).length;
                return (
                  <button key={ev.id} onClick={() => onNavigate("events")} className="sea-card" style={{ textAlign: "left", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, width: "100%" }}>
                    <div style={{ minWidth: 0 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3, flexWrap: "wrap" }}>
                        <span style={{ fontWeight: 700, fontSize: 13.5 }}>{ev.title}</span>
                        <StatusBadge status={ev.status} />
                      </div>
                      <div style={{ fontSize: 12, color: "var(--text-faint)", display: "flex", alignItems: "center", gap: 4 }}>
                        <CalendarIcon size={12} /> {fmtDate(ev.date)} {ev.location ? `· ${ev.location}` : ""}
                      </div>
                    </div>
                    {totalCount > 0 && <ProgressRing value={(doneCount / totalCount) * 100} size={32} strokeWidth={3.5} label={`${doneCount}/${totalCount}`} />}
                  </button>
                );
              })}
            </div>
          )}

          {monthValue && (
            <div className="sea-card" style={{ marginTop: 16, background: "var(--accent-soft)", border: "none", color: "var(--accent)" }}>
              <div style={{ fontSize: 11.5, fontWeight: 700, opacity: 0.85 }}>Құндылық — {KZ_MONTHS[new Date().getMonth()]}</div>
              <div style={{ fontSize: 14, fontWeight: 700, marginTop: 2 }}>{monthValue}</div>
            </div>
          )}
        </div>

        <div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
            <div style={{ fontWeight: 700, fontSize: 14.5 }}>Топ рейтинга</div>
            <button className="sea-btn sea-btn-ghost" style={{ padding: "4px 8px", fontSize: 12.5 }} onClick={() => onNavigate("leaderboard")}>
              Весь рейтинг <ArrowRight size={13} />
            </button>
          </div>
          {ranking.every((r) => r.points === 0) ? (
            <EmptyState icon={Trophy} text="Рейтинг пока пуст" />
          ) : (
            <div style={{ display: "grid", gap: 8 }}>
              {ranking.slice(0, 5).map((u, idx) => {
                const medals = ["🥇", "🥈", "🥉"];
                const lvlStyle = getLevelStyle(u.level);
                return (
                  <div key={u.email} className="sea-card" style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 14px", background: lvlStyle.bg, borderColor: lvlStyle.border }}>
                    <div style={{ width: 20, textAlign: "center", fontSize: idx < 3 ? 15 : 12, fontWeight: 700, color: "var(--text-faint)" }}>
                      {idx < 3 ? medals[idx] : idx + 1}
                    </div>
                    <div style={{ flex: 1, minWidth: 0, fontSize: 13, fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{u.name}</div>
                    <div style={{ fontSize: 13, fontWeight: 800, color: "var(--accent)", whiteSpace: "nowrap" }}>{u.points}</div>
                  </div>
                );
              })}
            </div>
          )}

          <div style={{ marginTop: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 10 }}>
              <Activity size={15} color="var(--text-faint)" />
              <div style={{ fontWeight: 700, fontSize: 14.5 }}>Лента активности</div>
            </div>
            {activity.length === 0 ? (
              <EmptyState icon={Activity} text="Активности пока нет" hint="Здесь появятся идеи, задачи и мероприятия коллег" />
            ) : (
              <div className="sea-card" style={{ padding: 6 }}>
                <div style={{ display: "grid" }}>
                  {activity.slice(0, 10).map((a, idx) => (
                    <div key={a.id} style={{ display: "flex", gap: 9, padding: "9px 8px", borderBottom: idx < Math.min(activity.length, 10) - 1 ? "1px solid var(--border)" : "none" }}>
                      <div style={{ width: 6, height: 6, borderRadius: 999, background: "var(--accent)", marginTop: 6, flexShrink: 0 }} />
                      <div style={{ minWidth: 0 }}>
                        <div style={{ fontSize: 12.5, lineHeight: 1.4 }}>
                          <span style={{ fontWeight: 700 }}>{a.actorName}</span> <span style={{ color: "var(--text-soft)" }}>{a.message}</span>
                        </div>
                        <div style={{ fontSize: 10.5, color: "var(--text-faint)", marginTop: 1 }}>{timeAgo(a.timestamp)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ----------------------------------------------------------------------
   ДОСКА ИДЕЙ
---------------------------------------------------------------------- */
function IdeasBoard({ ideas, currentUser, isZavuch, templates, run, onJumpToEvent }) {
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const [convertingIdea, setConvertingIdea] = useState(null);
  const [commentDrafts, setCommentDrafts] = useState({});
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);

  const addIdea = async () => {
    if (!title.trim()) return;
    await run("POST", "/api/ideas", { title: title.trim(), description: desc.trim() });
    setTitle("");
    setDesc("");
    setShowForm(false);
  };

  const addComment = async (ideaId) => {
    const text = (commentDrafts[ideaId] || "").trim();
    if (!text) return;
    await run("POST", `/api/ideas/${ideaId}/comments`, { text });
    setCommentDrafts((d) => ({ ...d, [ideaId]: "" }));
  };

  const finishConvert = async (data) => {
    await run("POST", `/api/ideas/${convertingIdea.id}/convert`, data);
    setConvertingIdea(null);
    onJumpToEvent();
  };

  const sorted = useMemo(
    () =>
      [...ideas]
        .filter((i) => i.status !== "converted" && i.status !== "deleted")
        .sort((a, b) => {
          const ra = Object.values(a.reactions || {}).flat().length;
          const rb = Object.values(b.reactions || {}).flat().length;
          return rb - ra || new Date(b.createdAt) - new Date(a.createdAt);
        }),
    [ideas]
  );

  return (
    <div>
      <SectionHeader
        title="Доска идей"
        subtitle="Предлагайте идеи мероприятий, реагируйте и обсуждайте — завуч превращает лучшие идеи в мероприятия."
        action={<button className="sea-btn sea-btn-primary" onClick={() => setShowForm(true)}><Plus size={15} /> Добавить идею</button>}
      />

      {showForm && (
        <div className="sea-card" style={{ marginBottom: 16 }}>
          <div className="sea-field">
            <label className="sea-label">Название идеи</label>
            <input autoFocus value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Например: Ярмарка талантов" />
          </div>
          <div className="sea-field">
            <label className="sea-label">Описание</label>
            <textarea rows={3} value={desc} onChange={(e) => setDesc(e.target.value)} placeholder="Кратко опишите суть идеи" />
          </div>
          <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
            <button className="sea-btn sea-btn-ghost" onClick={() => setShowForm(false)}>Отмена</button>
            <button className="sea-btn sea-btn-primary" onClick={addIdea} disabled={!title.trim()}>Опубликовать</button>
          </div>
        </div>
      )}

      {sorted.length === 0 ? (
        <EmptyState icon={Lightbulb} text="Пока нет ни одной идеи. Добавьте первую!" />
      ) : (
        <div style={{ display: "grid", gap: 12 }}>
          {sorted.map((idea) => {
            const totalReactions = Object.values(idea.reactions || {}).flat().length;
            const canDelete = idea.author === currentUser.email || isZavuch;
            return (
              <div key={idea.id} className="sea-card">
                <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 3 }}>{idea.title}</div>
                    <div style={{ fontSize: 12, color: "var(--text-faint)" }}>
                      {idea.authorName} · {new Date(idea.createdAt).toLocaleDateString("ru-RU")}
                    </div>
                  </div>
                  {canDelete && (
                    <div style={{ display: "flex", gap: 6, alignItems: "flex-start" }}>
                      {confirmDeleteId === idea.id ? (
                        <>
                          <button className="sea-btn sea-btn-danger" style={{ padding: "4px 8px", fontSize: 11.5 }} onClick={() => { setConfirmDeleteId(null); run("DELETE", `/api/ideas/${idea.id}`); }}>Точно?</button>
                          <button className="sea-btn sea-btn-ghost" style={{ padding: "4px 8px", fontSize: 11.5 }} onClick={() => setConfirmDeleteId(null)}>Отмена</button>
                        </>
                      ) : (
                        <button className="sea-btn sea-btn-ghost sea-btn-danger" onClick={() => setConfirmDeleteId(idea.id)} title="Удалить идею"><Trash2 size={14} /></button>
                      )}
                    </div>
                  )}
                </div>
                {idea.description && <p style={{ margin: "10px 0 0", color: "var(--text-soft)" }}>{idea.description}</p>}

                <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 12 }}>
                  {REACTIONS.map((emoji) => {
                    const count = (idea.reactions?.[emoji] || []).length;
                    const active = idea.reactions?.[emoji]?.includes(currentUser.email);
                    return (
                      <button
                        key={emoji}
                        onClick={() => run("POST", `/api/ideas/${idea.id}/reactions`, { emoji })}
                        className="sea-btn"
                        style={{ padding: "5px 10px", fontSize: 13, background: active ? "var(--accent-soft)" : "#fff", borderColor: active ? "var(--accent)" : "var(--border)" }}
                      >
                        {emoji} {count > 0 && <span style={{ fontSize: 12 }}>{count}</span>}
                      </button>
                    );
                  })}
                  {totalReactions > 0 && (
                    <span style={{ fontSize: 12, color: "var(--text-faint)", alignSelf: "center", marginLeft: 4 }}>всего реакций: {totalReactions}</span>
                  )}
                  {isZavuch && (
                    <button className="sea-btn sea-btn-primary" style={{ marginLeft: "auto" }} onClick={() => setConvertingIdea(idea)}>
                      <Check size={14} /> Одобрить → создать мероприятие
                    </button>
                  )}
                </div>

                {idea.comments?.length > 0 && (
                  <div style={{ marginTop: 12, borderTop: "1px solid var(--border)", paddingTop: 10, display: "grid", gap: 6 }}>
                    {idea.comments.map((c, idx) => (
                      <div key={idx} style={{ fontSize: 12.5 }}>
                        <span style={{ fontWeight: 600 }}>{c.author}: </span>
                        <span style={{ color: "var(--text-soft)" }}>{c.text}</span>
                      </div>
                    ))}
                  </div>
                )}
                <div style={{ display: "flex", gap: 6, marginTop: 10 }}>
                  <input
                    placeholder="Написать комментарий…"
                    value={commentDrafts[idea.id] || ""}
                    onChange={(e) => setCommentDrafts((d) => ({ ...d, [idea.id]: e.target.value }))}
                    onKeyDown={(e) => { if (e.key === "Enter") addComment(idea.id); }}
                  />
                  <button className="sea-btn" onClick={() => addComment(idea.id)}>Отправить</button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {convertingIdea && (
        <ConvertIdeaModal idea={convertingIdea} templates={templates} onClose={() => setConvertingIdea(null)} onSubmit={finishConvert} />
      )}
    </div>
  );
}

function ConvertIdeaModal({ idea, templates, onClose, onSubmit }) {
  const [form, setForm] = useState({
    title: idea.title,
    description: idea.description || "",
    date: "",
    location: "",
    budget: "",
    templateId: "",
  });
  const set = (patch) => setForm((f) => ({ ...f, ...patch }));

  return (
    <Modal title="Создать мероприятие из идеи" onClose={onClose}>
      <div className="sea-field">
        <label className="sea-label">Название мероприятия</label>
        <input value={form.title} onChange={(e) => set({ title: e.target.value })} />
      </div>
      <div className="sea-field">
        <label className="sea-label">Описание</label>
        <textarea rows={3} value={form.description} onChange={(e) => set({ description: e.target.value })} />
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <div className="sea-field">
          <label className="sea-label">Дата</label>
          <input type="date" value={form.date} onChange={(e) => set({ date: e.target.value })} />
        </div>
        <div className="sea-field">
          <label className="sea-label">Бюджет</label>
          <input value={form.budget} onChange={(e) => set({ budget: e.target.value })} placeholder="напр. 50 000 ₸" />
        </div>
      </div>
      <div className="sea-field">
        <label className="sea-label">Место проведения</label>
        <input value={form.location} onChange={(e) => set({ location: e.target.value })} placeholder="Актовый зал, спортзал…" />
      </div>
      <div className="sea-field">
        <label className="sea-label">Шаблон задач (необязательно)</label>
        <select value={form.templateId} onChange={(e) => set({ templateId: e.target.value })}>
          <option value="">Без шаблона — задачи добавим позже</option>
          {templates.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
      </div>
      <ModalFooter>
        <button className="sea-btn sea-btn-ghost" onClick={onClose}>Отмена</button>
        <button className="sea-btn sea-btn-primary" onClick={() => onSubmit(form)} disabled={!form.title.trim()}>
          <Check size={14} /> Создать мероприятие
        </button>
      </ModalFooter>
    </Modal>
  );
}

/* ----------------------------------------------------------------------
   МЕРОПРИЯТИЯ
---------------------------------------------------------------------- */
function EventsBoard({ events, currentUser, isZavuch, users, templates, run }) {
  const [showForm, setShowForm] = useState(false);
  const [openEventId, setOpenEventId] = useState(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [respFilter, setRespFilter] = useState("all");
  const [locationFilter, setLocationFilter] = useState("");

  const createEvent = async (data) => {
    const next = await run("POST", "/api/events", data);
    setShowForm(false);
    const created = next.events.find((e) => e.title === data.title && e.createdBy === currentUser.email);
    if (created) setOpenEventId(created.id);
  };

  const conflictsFor = (ev) => {
    if (!ev.date || !ev.location) return [];
    return events.filter(
      (o) => o.id !== ev.id && o.date === ev.date && o.location &&
        o.location.trim().toLowerCase() === ev.location.trim().toLowerCase() && o.status !== "rejected"
    );
  };

  const filtered = useMemo(
    () =>
      events
        .filter((e) => e.status !== "done")
        .filter((e) => (statusFilter === "all" ? true : e.status === statusFilter))
        .filter((e) => (respFilter === "all" ? true : (e.tasks || []).some((t) => t.responsible?.includes(respFilter))))
        .filter((e) => (locationFilter ? (e.location || "").toLowerCase().includes(locationFilter.toLowerCase()) : true))
        .filter((e) => (search ? e.title.toLowerCase().includes(search.toLowerCase()) : true))
        .sort((a, b) => new Date(a.date || "9999-12-31") - new Date(b.date || "9999-12-31")),
    [events, statusFilter, respFilter, locationFilter, search]
  );

  const openEvent = events.find((e) => e.id === openEventId);

  return (
    <div>
      <SectionHeader
        title="Мероприятия"
        subtitle="Распределение задач и ответственных по мероприятиям."
        action={<button className="sea-btn sea-btn-primary" onClick={() => setShowForm(true)}><Plus size={15} /> Новое мероприятие</button>}
      />

      <div className="sea-card" style={{ marginBottom: 16, display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}>
        <div style={{ position: "relative", flex: "1 1 200px", minWidth: 180 }}>
          <Search size={14} style={{ position: "absolute", left: 10, top: 10, color: "var(--text-faint)" }} />
          <input style={{ paddingLeft: 30 }} placeholder="Поиск по названию…" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <select style={{ width: "auto", minWidth: 150 }} value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">Все статусы</option>
          {Object.entries(STATUS_LABELS).filter(([k]) => k !== "done").map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
        </select>
        <select style={{ width: "auto", minWidth: 160 }} value={respFilter} onChange={(e) => setRespFilter(e.target.value)}>
          <option value="all">Все ответственные</option>
          {users.map((u) => <option key={u.email} value={u.email}>{u.name}</option>)}
        </select>
        <input style={{ width: "auto", minWidth: 150 }} placeholder="Место проведения…" value={locationFilter} onChange={(e) => setLocationFilter(e.target.value)} />
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon={LayoutGrid} text="Мероприятий не найдено." />
      ) : (
        <div style={{ display: "grid", gap: 10 }}>
          {filtered.map((ev) => {
            const conflicts = conflictsFor(ev);
            const doneCount = (ev.tasks || []).filter((t) => t.status === "done").length;
            const totalCount = (ev.tasks || []).length;
            return (
              <button key={ev.id} onClick={() => setOpenEventId(ev.id)} className="sea-card" style={{ textAlign: "left", display: "block", width: "100%" }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 10, flexWrap: "wrap" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4, flexWrap: "wrap" }}>
                      <span style={{ fontWeight: 700, fontSize: 15 }}>{ev.title}</span>
                      <StatusBadge status={ev.status} />
                      {conflicts.length > 0 && <span className="sea-badge" style={{ color: "var(--danger)", background: "var(--danger-soft)" }}>Конфликт даты/места</span>}
                    </div>
                    <div style={{ display: "flex", gap: 14, flexWrap: "wrap", fontSize: 12.5, color: "var(--text-soft)" }}>
                      <span style={{ display: "flex", alignItems: "center", gap: 4 }}><CalendarIcon size={13} /> {fmtDate(ev.date)}</span>
                      {ev.location && <span style={{ display: "flex", alignItems: "center", gap: 4 }}><MapPin size={13} /> {ev.location}</span>}
                      {ev.budget && <span style={{ display: "flex", alignItems: "center", gap: 4 }}><Wallet size={13} /> {ev.budget}</span>}
                    </div>
                  </div>
                  {totalCount > 0 && <ProgressRing value={(doneCount / totalCount) * 100} size={36} strokeWidth={4} label={`${doneCount}/${totalCount}`} />}
                </div>
              </button>
            );
          })}
        </div>
      )}

      {showForm && <EventFormModal templates={templates} onClose={() => setShowForm(false)} onSubmit={createEvent} />}

      {openEvent && (
        <EventDetailModal
          event={openEvent}
          users={users}
          isZavuch={isZavuch}
          conflicts={conflictsFor(openEvent)}
          run={run}
          onClose={() => setOpenEventId(null)}
        />
      )}
    </div>
  );
}

function EventFormModal({ templates, onClose, onSubmit }) {
  const [form, setForm] = useState({ title: "", description: "", date: "", location: "", budget: "", templateId: "" });
  const [busy, setBusy] = useState(false);
  const set = (patch) => setForm((f) => ({ ...f, ...patch }));

  const submit = async () => {
    setBusy(true);
    try {
      await onSubmit({ ...form, title: form.title.trim() });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title="Новое мероприятие" onClose={onClose}>
      <div className="sea-field">
        <label className="sea-label">Название</label>
        <input autoFocus value={form.title} onChange={(e) => set({ title: e.target.value })} placeholder="Например: Ярмарка талантов" />
      </div>
      <div className="sea-field">
        <label className="sea-label">Описание</label>
        <textarea rows={3} value={form.description} onChange={(e) => set({ description: e.target.value })} />
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <div className="sea-field">
          <label className="sea-label">Дата</label>
          <input type="date" value={form.date} onChange={(e) => set({ date: e.target.value })} />
        </div>
        <div className="sea-field">
          <label className="sea-label">Бюджет</label>
          <input value={form.budget} onChange={(e) => set({ budget: e.target.value })} placeholder="напр. 50 000 ₸" />
        </div>
      </div>
      <div className="sea-field">
        <label className="sea-label">Место проведения</label>
        <input value={form.location} onChange={(e) => set({ location: e.target.value })} placeholder="Актовый зал, спортзал…" />
      </div>
      <div className="sea-field">
        <label className="sea-label">Начать с шаблона (необязательно)</label>
        <select value={form.templateId} onChange={(e) => set({ templateId: e.target.value })}>
          <option value="">Без шаблона</option>
          {templates.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
      </div>
      <ModalFooter>
        <button className="sea-btn sea-btn-ghost" onClick={onClose}>Отмена</button>
        <button className="sea-btn sea-btn-primary" disabled={!form.title.trim() || busy} onClick={submit}>Создать</button>
      </ModalFooter>
    </Modal>
  );
}

function StatusBadge({ status }) {
  const s = STATUS_LABELS[status] || STATUS_LABELS.draft;
  return <span className="sea-badge" style={{ color: s.color, background: s.bg }}>{s.label}</span>;
}

function EventDetailModal({ event, users, isZavuch, conflicts, run, onClose }) {
  const [editingMeta, setEditingMeta] = useState(false);
  const [meta, setMeta] = useState({
    title: event.title, description: event.description || "", date: event.date || "",
    location: event.location || "", budget: event.budget || "",
  });
  const [addingTask, setAddingTask] = useState(false);
  const [taskDraft, setTaskDraft] = useState({ title: "", comment: "", responsible: [], deadline: "" });
  const [archiveMode, setArchiveMode] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const patchEvent = (patch) => run("PATCH", `/api/events/${event.id}`, patch);

  const saveMeta = async () => {
    await patchEvent(meta);
    setEditingMeta(false);
  };

  const addTask = async () => {
    if (!taskDraft.title.trim()) return;
    await run("POST", `/api/events/${event.id}/tasks`, { ...taskDraft, title: taskDraft.title.trim() });
    setTaskDraft({ title: "", comment: "", responsible: [], deadline: "" });
    setAddingTask(false);
  };

  const toggleDraftResponsible = (email) => {
    setTaskDraft((d) => {
      const set = new Set(d.responsible);
      set.has(email) ? set.delete(email) : set.add(email);
      return { ...d, responsible: Array.from(set) };
    });
  };

  const doneCount = (event.tasks || []).filter((t) => t.status === "done").length;
  const totalCount = (event.tasks || []).length;

  return (
    <Modal
      title={<div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}><span>{event.title}</span><StatusBadge status={event.status} /></div>}
      onClose={onClose}
      wide
    >
      {conflicts.length > 0 && (
        <div style={{ background: "var(--danger-soft)", color: "var(--danger)", padding: "10px 12px", borderRadius: 8, fontSize: 13, marginBottom: 14 }}>
          ⚠️ Конфликт: в это же время в «{event.location}» запланировано ещё {conflicts.length} мероприятие(й): {conflicts.map((c) => c.title).join(", ")}.
        </div>
      )}

      {editingMeta ? (
        <div className="sea-card" style={{ marginBottom: 16 }}>
          <div className="sea-field"><label className="sea-label">Название</label><input value={meta.title} onChange={(e) => setMeta({ ...meta, title: e.target.value })} /></div>
          <div className="sea-field"><label className="sea-label">Описание</label><textarea rows={3} value={meta.description} onChange={(e) => setMeta({ ...meta, description: e.target.value })} /></div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div className="sea-field"><label className="sea-label">Дата</label><input type="date" value={meta.date} onChange={(e) => setMeta({ ...meta, date: e.target.value })} /></div>
            <div className="sea-field"><label className="sea-label">Бюджет</label><input value={meta.budget} onChange={(e) => setMeta({ ...meta, budget: e.target.value })} /></div>
          </div>
          <div className="sea-field"><label className="sea-label">Место проведения</label><input value={meta.location} onChange={(e) => setMeta({ ...meta, location: e.target.value })} /></div>
          <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
            <button className="sea-btn sea-btn-ghost" onClick={() => setEditingMeta(false)}>Отмена</button>
            <button className="sea-btn sea-btn-primary" onClick={saveMeta} disabled={!meta.title.trim()}>Сохранить</button>
          </div>
        </div>
      ) : (
        <div style={{ marginBottom: 18 }}>
          {event.description && <p style={{ color: "var(--text-soft)", marginTop: 0 }}>{event.description}</p>}
          <div style={{ display: "flex", gap: 16, flexWrap: "wrap", alignItems: "center", fontSize: 13, color: "var(--text-soft)", marginBottom: 10 }}>
            <span style={{ display: "flex", alignItems: "center", gap: 5 }}><CalendarIcon size={14} /> {fmtDate(event.date)}</span>
            {event.location && <span style={{ display: "flex", alignItems: "center", gap: 5 }}><MapPin size={14} /> {event.location}</span>}
            {event.budget && <span style={{ display: "flex", alignItems: "center", gap: 5 }}><Wallet size={14} /> {event.budget}</span>}
            {totalCount > 0 && (
              <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <ProgressRing value={(doneCount / totalCount) * 100} size={26} strokeWidth={3} label="" /> {doneCount}/{totalCount} задач
              </span>
            )}
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button className="sea-btn" onClick={() => { setMeta({ title: event.title, description: event.description || "", date: event.date || "", location: event.location || "", budget: event.budget || "" }); setEditingMeta(true); }}>
              <Pencil size={13} /> Изменить
            </button>
            {event.status === "draft" && (
              <button className="sea-btn sea-btn-primary" onClick={() => patchEvent({ status: "pending" })}>Отправить на рассмотрение</button>
            )}
            {event.status === "pending" && isZavuch && (
              <>
                <button className="sea-btn" style={{ color: "var(--success)" }} onClick={() => patchEvent({ status: "approved" })}><Check size={14} /> Одобрить</button>
                <button className="sea-btn sea-btn-danger" onClick={() => patchEvent({ status: "rejected" })}><X size={14} /> Отклонить</button>
              </>
            )}
            {event.status === "rejected" && <button className="sea-btn" onClick={() => patchEvent({ status: "draft" })}>Вернуть в черновик</button>}
            {event.status === "approved" && (
              <button className="sea-btn sea-btn-primary" onClick={() => setArchiveMode(true)}><ArchiveIcon size={14} /> Отметить как проведено</button>
            )}
            {confirmDelete ? (
              <>
                <span style={{ fontSize: 12.5, color: "var(--danger)", alignSelf: "center", marginLeft: "auto" }}>Удалить безвозвратно?</span>
                <button className="sea-btn sea-btn-danger" onClick={async () => { await run("DELETE", `/api/events/${event.id}`); onClose(); }}>Да, удалить</button>
                <button className="sea-btn sea-btn-ghost" onClick={() => setConfirmDelete(false)}>Отмена</button>
              </>
            ) : (
              <button className="sea-btn sea-btn-danger" style={{ marginLeft: "auto" }} onClick={() => setConfirmDelete(true)}><Trash2 size={13} /> Удалить</button>
            )}
          </div>
        </div>
      )}

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
        <div style={{ fontWeight: 700, fontSize: 14 }}>Задачи</div>
        <button className="sea-btn" onClick={() => setAddingTask((v) => !v)}><Plus size={13} /> Добавить задачу</button>
      </div>

      {addingTask && (
        <div className="sea-card" style={{ marginBottom: 12, background: "var(--surface)" }}>
          <div className="sea-field"><label className="sea-label">Название задачи</label><input autoFocus value={taskDraft.title} onChange={(e) => setTaskDraft({ ...taskDraft, title: e.target.value })} /></div>
          <div className="sea-field"><label className="sea-label">Комментарий — что конкретно нужно сделать</label><textarea rows={2} value={taskDraft.comment} onChange={(e) => setTaskDraft({ ...taskDraft, comment: e.target.value })} /></div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div className="sea-field">
              <label className="sea-label">Дедлайн</label>
              <input type="date" value={taskDraft.deadline} onChange={(e) => setTaskDraft({ ...taskDraft, deadline: e.target.value })} />
            </div>
            <div className="sea-field">
              <label className="sea-label">Ответственные</label>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 5, maxHeight: 90, overflowY: "auto", border: "1px solid var(--border)", borderRadius: 8, padding: 6 }}>
                {users.map((u) => {
                  const active = taskDraft.responsible.includes(u.email);
                  return (
                    <button
                      key={u.email}
                      className="sea-chip"
                      style={{ border: "none", cursor: "pointer", background: active ? "var(--accent-soft)" : "var(--surface-2)", color: active ? "var(--accent)" : "var(--text-soft)" }}
                      onClick={() => toggleDraftResponsible(u.email)}
                    >
                      {u.name}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
          <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
            <button className="sea-btn sea-btn-ghost" onClick={() => setAddingTask(false)}>Отмена</button>
            <button className="sea-btn sea-btn-primary" onClick={addTask} disabled={!taskDraft.title.trim()}>Добавить</button>
          </div>
        </div>
      )}

      {totalCount === 0 ? (
        <div style={{ color: "var(--text-faint)", fontSize: 13, padding: "16px 0" }}>Задач пока нет.</div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table className="sea-table sea-table-responsive">
            <thead>
              <tr><th>Задача</th><th>Комментарий</th><th>Ответственные</th><th>Дедлайн</th><th>Статус</th><th></th></tr>
            </thead>
            <tbody>
              {event.tasks.map((t) => (
                <TaskRow
                  key={t.id}
                  task={t}
                  users={users}
                  onChange={(patch) => run("PATCH", `/api/tasks/${t.id}`, patch)}
                  onRemove={() => run("DELETE", `/api/tasks/${t.id}`)}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {archiveMode && (
        <ArchiveModal
          event={event}
          users={users}
          onClose={() => setArchiveMode(false)}
          onSave={async (payload) => {
            await run("POST", `/api/events/${event.id}/archive`, payload);
            setArchiveMode(false);
            onClose();
          }}
        />
      )}
    </Modal>
  );
}

function TaskRow({ task, users, onChange, onRemove }) {
  const [editingResp, setEditingResp] = useState(false);
  const [flash, setFlash] = useState(false);
  const respNames = users.filter((u) => task.responsible?.includes(u.email)).map((u) => u.name);
  const dleft = daysUntil(task.deadline);
  const overdue = dleft !== null && dleft < 0 && task.status !== "done";

  const handleStatusChange = (val) => {
    if (val === "done" && task.status !== "done" && (task.responsible || []).length > 0) {
      setFlash(true);
      setTimeout(() => setFlash(false), 1300);
    }
    onChange({ status: val });
  };

  return (
    <tr>
      <td data-label="Задача" style={{ minWidth: 140, fontWeight: 600 }}>{task.title}</td>
      <td data-label="Комментарий" style={{ minWidth: 180, color: "var(--text-soft)" }}>{task.comment || "—"}</td>
      <td data-label="Ответственные" style={{ minWidth: 150 }}>
        {editingResp ? (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 4, maxWidth: 220 }}>
            {users.map((u) => {
              const active = task.responsible?.includes(u.email);
              return (
                <button
                  key={u.email}
                  className="sea-chip"
                  style={{ cursor: "pointer", border: "none", background: active ? "var(--accent-soft)" : "var(--surface-2)", color: active ? "var(--accent)" : "var(--text-soft)" }}
                  onClick={() => {
                    const set = new Set(task.responsible || []);
                    set.has(u.email) ? set.delete(u.email) : set.add(u.email);
                    onChange({ responsible: Array.from(set) });
                  }}
                >
                  {u.name}
                </button>
              );
            })}
            <button className="sea-btn sea-btn-ghost" style={{ padding: "2px 6px" }} onClick={() => setEditingResp(false)}>Готово</button>
          </div>
        ) : (
          <button className="sea-btn sea-btn-ghost" style={{ padding: "4px 6px", fontWeight: 400 }} onClick={() => setEditingResp(true)}>
            {respNames.length ? respNames.join(", ") : <span style={{ color: "var(--text-faint)" }}>Назначить…</span>}
          </button>
        )}
      </td>
      <td data-label="Дедлайн" style={{ minWidth: 130 }}>
        <input type="date" value={task.deadline || ""} onChange={(e) => onChange({ deadline: e.target.value })} style={{ padding: "5px 8px", borderColor: overdue ? "var(--danger)" : "var(--border)" }} />
        {overdue && <div style={{ fontSize: 11, color: "var(--danger)", marginTop: 2 }}>Просрочено</div>}
      </td>
      <td data-label="Статус" style={{ minWidth: 130, position: "relative" }}>
        <select value={task.status} onChange={(e) => handleStatusChange(e.target.value)} style={{ padding: "5px 8px" }}>
          {Object.entries(TASK_STATUS_LABELS).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
        </select>
        {flash && <span className="sea-points-flash">+{POINTS_PER_TASK}</span>}
      </td>
      <td data-label="">
        <button className="sea-btn sea-btn-ghost sea-btn-danger" style={{ padding: 6 }} onClick={onRemove}><Trash2 size={13} /></button>
      </td>
    </tr>
  );
}

function ArchiveModal({ event, users, onClose, onSave }) {
  const [summary, setSummary] = useState("");
  const [files, setFiles] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  // После архивации незакрытые задачи считаются проваленными — покажем это заранее
  const unfinished = (event.tasks || []).filter((t) => t.status !== "done");
  const penalties = useMemo(() => {
    const byEmail = {};
    unfinished.forEach((t) => (t.responsible || []).forEach((email) => {
      byEmail[email] = (byEmail[email] || 0) + 1;
    }));
    return Object.entries(byEmail)
      .map(([email, count]) => ({
        name: users.find((u) => u.email === email)?.name || email,
        count,
      }))
      .sort((a, b) => b.count - a.count);
  }, [event.tasks, users]);
  const orphanTasks = unfinished.filter((t) => !(t.responsible || []).length).length;

  const handleFiles = async (fileList) => {
    setError("");
    const arr = Array.from(fileList).slice(0, 20);
    for (const f of arr) {
      if (f.size > 4 * 1024 * 1024) {
        setError(`Файл «${f.name}» больше 4 МБ — он не будет загружен.`);
        continue;
      }
      const data = await fileToBase64(f);
      setFiles((prev) => [...prev, { name: f.name, size: f.size, data }]);
    }
  };

  const save = async () => {
    setBusy(true);
    try {
      await onSave({ summary, files });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title="Отметить мероприятие как проведённое" onClose={onClose}>
      {unfinished.length > 0 && (
        <div style={{ background: "var(--danger-soft)", color: "var(--danger)", padding: "11px 13px", borderRadius: 8, fontSize: 13, marginBottom: 16 }}>
          <div style={{ fontWeight: 700, marginBottom: penalties.length ? 6 : 0 }}>
            Незакрытых задач: {unfinished.length}. После архивации они считаются невыполненными.
          </div>
          {penalties.length > 0 && (
            <div style={{ display: "grid", gap: 3 }}>
              {penalties.map((p) => (
                <div key={p.name}>
                  {p.name} — минус {p.count * POINTS_PER_FAILED_TASK} очков
                  {p.count > 1 ? ` (${p.count} задачи)` : ""}
                </div>
              ))}
            </div>
          )}
          {orphanTasks > 0 && (
            <div style={{ marginTop: 6, opacity: 0.85 }}>
              Ещё {orphanTasks} задач(и) без ответственных — за них очки не снимаются.
            </div>
          )}
          <div style={{ marginTop: 8, color: "var(--text-soft)", fontSize: 12.5 }}>
            Если задачи на самом деле выполнены, закройте окно и отметьте их «Готово» — или сделайте это позже в архиве, тогда минус пересчитается в плюс.
          </div>
        </div>
      )}
      <div className="sea-field">
        <label className="sea-label">Итоги мероприятия (что было сделано, как прошло)</label>
        <textarea rows={4} value={summary} onChange={(e) => setSummary(e.target.value)} placeholder="Краткий итог для архива" />
      </div>
      <div className="sea-field">
        <label className="sea-label">Файлы (фото, документы) — по желанию, до 4 МБ каждый</label>
        <input type="file" multiple onChange={(e) => handleFiles(e.target.files)} />
        {error && <div style={{ color: "var(--danger)", fontSize: 12, marginTop: 6 }}>{error}</div>}
        {files.length > 0 && (
          <div style={{ display: "grid", gap: 4, marginTop: 8 }}>
            {files.map((f, idx) => (
              <div key={idx} className="sea-chip" style={{ justifyContent: "space-between" }}>
                <span style={{ display: "flex", alignItems: "center", gap: 5 }}><Paperclip size={12} /> {f.name}</span>
                <button onClick={() => setFiles(files.filter((_, i) => i !== idx))} style={{ border: "none", background: "none", cursor: "pointer" }}><X size={12} /></button>
              </div>
            ))}
          </div>
        )}
      </div>
      <ModalFooter>
        <button className="sea-btn sea-btn-ghost" onClick={onClose}>Отмена</button>
        <button className="sea-btn sea-btn-primary" disabled={busy} onClick={save}>
          <ArchiveIcon size={14} /> {busy ? "Отправка…" : "Отправить в архив"}
        </button>
      </ModalFooter>
    </Modal>
  );
}

/* ----------------------------------------------------------------------
   КАЛЕНДАРЬ
---------------------------------------------------------------------- */
function CalendarView({ events }) {
  const [cursor, setCursor] = useState(() => {
    const d = new Date();
    return new Date(d.getFullYear(), d.getMonth(), 1);
  });
  const [selectedDay, setSelectedDay] = useState(null);

  const year = cursor.getFullYear();
  const month = cursor.getMonth();
  const monthLabel = cursor.toLocaleDateString("ru-RU", { month: "long", year: "numeric" });

  const eventsByDate = useMemo(() => {
    const map = {};
    events.forEach((e) => {
      if (!e.date) return;
      (map[e.date] = map[e.date] || []).push(e);
    });
    return map;
  }, [events]);

  const conflictDates = useMemo(() => {
    const set = new Set();
    Object.entries(eventsByDate).forEach(([date, list]) => {
      const byLoc = {};
      list.forEach((e) => {
        if (!e.location) return;
        const key = e.location.trim().toLowerCase();
        byLoc[key] = (byLoc[key] || 0) + 1;
      });
      if (Object.values(byLoc).some((c) => c > 1)) set.add(date);
    });
    return set;
  }, [eventsByDate]);

  const startWeekday = (new Date(year, month, 1).getDay() + 6) % 7;
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells = [];
  for (let i = 0; i < startWeekday; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);

  const pad = (n) => String(n).padStart(2, "0");
  const dateStr = (d) => `${year}-${pad(month + 1)}-${pad(d)}`;
  const todayStr = new Date().toISOString().slice(0, 10);
  const selectedEvents = selectedDay ? eventsByDate[selectedDay] || [] : [];
  const monthValue = getMonthValue(month + 1);

  return (
    <div>
      <SectionHeader title="Календарь" subtitle="Все запланированные мероприятия. Даты с конфликтом места отмечены красным." />
      <div className="sea-card">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
          <button className="sea-btn sea-btn-ghost" onClick={() => setCursor(new Date(year, month - 1, 1))}><ChevronLeft size={16} /></button>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontWeight: 700, fontSize: 15, textTransform: "capitalize" }}>{monthLabel}</div>
            <div style={{ fontSize: 11.5, color: "var(--text-faint)" }}>{KZ_MONTHS[month]}</div>
          </div>
          <button className="sea-btn sea-btn-ghost" onClick={() => setCursor(new Date(year, month + 1, 1))}><ChevronRight size={16} /></button>
        </div>
        {monthValue ? (
          <div style={{ background: "var(--accent-soft)", color: "var(--accent)", borderRadius: 8, padding: "8px 12px", fontSize: 12.5, fontWeight: 600, textAlign: "center", margin: "8px 0 14px" }}>
            Құндылық: {monthValue}
          </div>
        ) : (
          <div style={{ marginBottom: 14 }} />
        )}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 4, fontSize: 11.5, color: "var(--text-faint)", marginBottom: 6, textAlign: "center", fontWeight: 600 }}>
          {["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"].map((d) => <div key={d}>{d}</div>)}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 4 }}>
          {cells.map((d, idx) => {
            if (!d) return <div key={idx} />;
            const ds = dateStr(d);
            const dayEvents = eventsByDate[ds] || [];
            const isToday = ds === todayStr;
            const hasConflict = conflictDates.has(ds);
            return (
              <button
                key={idx}
                onClick={() => setSelectedDay(ds)}
                style={{
                  minHeight: 60, textAlign: "left", padding: 6, borderRadius: 8, border: "1px solid",
                  borderColor: selectedDay === ds ? "var(--accent)" : "var(--border)",
                  background: isToday ? "var(--accent-soft)" : "#fff", position: "relative",
                }}
              >
                <div style={{ fontSize: 12.5, fontWeight: isToday ? 700 : 500, color: isToday ? "var(--accent)" : "var(--text)" }}>{d}</div>
                <div style={{ display: "flex", flexDirection: "column", gap: 2, marginTop: 4 }}>
                  {dayEvents.slice(0, 2).map((e) => {
                    const st = STATUS_LABELS[e.status] || STATUS_LABELS.draft;
                    return (
                      <div key={e.id} style={{ fontSize: 10.5, padding: "1px 5px", borderRadius: 4, background: hasConflict ? "var(--danger-soft)" : st.bg, color: hasConflict ? "var(--danger)" : st.color, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {e.title}
                      </div>
                    );
                  })}
                  {dayEvents.length > 2 && <div style={{ fontSize: 10, color: "var(--text-faint)" }}>+{dayEvents.length - 2} ещё</div>}
                </div>
              </button>
            );
          })}
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 14, paddingTop: 12, borderTop: "1px solid var(--border)" }}>
          {Object.entries(STATUS_LABELS).map(([k, v]) => (
            <span key={k} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11.5, color: "var(--text-faint)" }}>
              <span style={{ width: 9, height: 9, borderRadius: 3, background: v.bg, border: `1px solid ${v.color}` }} />
              {v.label}
            </span>
          ))}
        </div>
      </div>

      {selectedDay && (
        <div className="sea-card" style={{ marginTop: 14 }}>
          <div style={{ fontWeight: 700, marginBottom: 8 }}>{fmtDate(selectedDay)}</div>
          {selectedEvents.length === 0 ? (
            <div style={{ color: "var(--text-faint)", fontSize: 13 }}>Мероприятий нет.</div>
          ) : (
            <div style={{ display: "grid", gap: 8 }}>
              {selectedEvents.map((e) => (
                <div key={e.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 10px", background: "var(--surface)", borderRadius: 8 }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 13.5 }}>{e.title}</div>
                    <div style={{ fontSize: 12, color: "var(--text-faint)" }}>{e.location || "место не указано"}</div>
                  </div>
                  <StatusBadge status={e.status} />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ----------------------------------------------------------------------
   АЙЛЫҚ ЖОСПАР — месячный план по неделям
---------------------------------------------------------------------- */
function monthKey(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
}

function resolveResponsible(input, users) {
  const value = (input || "").trim();
  const match = users.find((u) => u.name.toLowerCase() === value.toLowerCase());
  return match ? { responsible: match.email, responsibleName: "" } : { responsible: "", responsibleName: value };
}

function MonthlyPlanView({ plan, users, isZavuch, run }) {
  const [cursor, setCursor] = useState(() => {
    const now = new Date();
    const current = new Date(now.getFullYear(), now.getMonth(), 1);
    if (plan[monthKey(current)]) return current;
    // на текущий месяц плана нет — открываем ближайший месяц, для которого он составлен
    const upcoming = Object.keys(plan).filter((m) => m >= monthKey(current)).sort()[0];
    if (!upcoming) return current;
    const [y, m] = upcoming.split("-").map(Number);
    return new Date(y, m - 1, 1);
  });
  const [drafts, setDrafts] = useState({});

  const month = monthKey(cursor);
  const weeks = plan[month] || [];
  const monthValue = getMonthValue(cursor.getMonth() + 1);
  const monthLabel = `${KZ_MONTHS[cursor.getMonth()]} ${cursor.getFullYear()}`;

  const nameOf = (item) =>
    item.responsible ? users.find((u) => u.email === item.responsible)?.name || item.responsible : item.responsibleName;

  const addWeek = () => {
    const next = weeks.length ? Math.max(...weeks.map((w) => w.weekNo)) + 1 : 1;
    if (next > 6) return;
    run("POST", "/api/plan/weeks", { month, weekNo: next, topic: "" });
  };

  const addItem = (weekId) => {
    const draft = drafts[weekId] || {};
    const title = (draft.title || "").trim();
    if (!title) return;
    run("POST", `/api/plan/weeks/${weekId}/items`, { title, ...resolveResponsible(draft.who, users) })
      .then(() => setDrafts((d) => ({ ...d, [weekId]: { title: "", who: "" } })));
  };

  const exportCsv = () => {
    const rows = [["Апта", "Тақырып", "Іс шара", "Жауапты"]];
    weeks.forEach((w) => {
      if (!w.items.length) rows.push([`${w.weekNo} апта`, w.topic, "", ""]);
      w.items.forEach((i, idx) => rows.push([idx === 0 ? `${w.weekNo} апта` : "", idx === 0 ? w.topic : "", i.title, nameOf(i)]));
    });
    const csv = "﻿" + rows
      .map((r) => r.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(";"))
      .join("\r\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `жоспар-${month}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <SectionHeader
        title="Айлық жоспар"
        subtitle="Общий план месяца по неделям: тема недели, мероприятия и ответственные. Заменяет таблицу в Excel."
        action={
          weeks.length > 0 && (
            <div style={{ display: "flex", gap: 8 }} className="sea-no-print">
              <button className="sea-btn" onClick={exportCsv}><Download size={14} /> CSV для Excel</button>
              <button className="sea-btn" onClick={() => window.print()}><Printer size={14} /> Печать</button>
            </div>
          )
        }
      />

      <div className="sea-card sea-print-area">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, marginBottom: 12 }}>
          <button className="sea-btn sea-btn-ghost sea-no-print" onClick={() => setCursor(new Date(cursor.getFullYear(), cursor.getMonth() - 1, 1))}>
            <ChevronLeft size={16} />
          </button>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontWeight: 700, fontSize: 16 }}>{monthLabel}</div>
            <div style={{ fontSize: 12, color: "var(--text-faint)" }}>
              {cursor.toLocaleDateString("ru-RU", { month: "long", year: "numeric" })}
            </div>
          </div>
          <button className="sea-btn sea-btn-ghost sea-no-print" onClick={() => setCursor(new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1))}>
            <ChevronRight size={16} />
          </button>
        </div>

        {monthValue && (
          <div style={{ background: "var(--accent-soft)", color: "var(--accent)", borderRadius: 8, padding: "9px 12px", fontSize: 13.5, fontWeight: 700, textAlign: "center", marginBottom: 14 }}>
            {monthValue}
          </div>
        )}

        {weeks.length === 0 ? (
          <EmptyState
            icon={TableIcon}
            text="На этот месяц плана ещё нет"
            hint={isZavuch ? "Добавьте первую неделю — и заполните тему, мероприятия и ответственных." : "План составляет завуч."}
          />
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table className="sea-table sea-plan-table" style={{ minWidth: 620 }}>
              <thead>
                <tr>
                  <th style={{ width: 90 }}>Апта</th>
                  <th style={{ width: "26%" }}>Тақырып</th>
                  <th>Іс шаралар</th>
                  <th style={{ width: "22%" }}>Жауапты</th>
                  {isZavuch && <th style={{ width: 40 }} className="sea-no-print"></th>}
                </tr>
              </thead>
              <tbody>
                {weeks.map((w) => {
                  const rowCount = Math.max(1, w.items.length) + (isZavuch ? 1 : 0);
                  const firstCells = (
                    <>
                      <td rowSpan={rowCount} style={{ fontWeight: 700, verticalAlign: "middle", background: "var(--surface)" }}>
                        {w.weekNo} апта
                      </td>
                      <td rowSpan={rowCount} style={{ verticalAlign: "middle" }}>
                        {isZavuch ? (
                          <input
                            defaultValue={w.topic}
                            placeholder="апта тақырыбы"
                            style={{ padding: "6px 8px" }}
                            onBlur={(e) => {
                              if (e.target.value !== w.topic) run("PATCH", `/api/plan/weeks/${w.id}`, { topic: e.target.value });
                            }}
                          />
                        ) : (
                          w.topic || <span style={{ color: "var(--text-faint)" }}>—</span>
                        )}
                      </td>
                    </>
                  );

                  const rows = [];
                  if (w.items.length === 0) {
                    rows.push(
                      <tr key={`${w.id}-empty`}>
                        {firstCells}
                        <td colSpan={isZavuch ? 3 : 2} style={{ color: "var(--text-faint)" }}>Іс шаралар әлі қосылмаған</td>
                      </tr>
                    );
                  } else {
                    w.items.forEach((item, idx) => {
                      rows.push(
                        <tr key={item.id}>
                          {idx === 0 && firstCells}
                          <td>
                            {isZavuch ? (
                              <input
                                defaultValue={item.title}
                                style={{ padding: "6px 8px" }}
                                onBlur={(e) => {
                                  const v = e.target.value.trim();
                                  if (v && v !== item.title) run("PATCH", `/api/plan/items/${item.id}`, { title: v });
                                }}
                              />
                            ) : item.title}
                          </td>
                          <td>
                            {isZavuch ? (
                              <input
                                list="sea-plan-users"
                                defaultValue={nameOf(item)}
                                placeholder="жауапты"
                                style={{ padding: "6px 8px" }}
                                onBlur={(e) => {
                                  if (e.target.value.trim() !== nameOf(item)) {
                                    run("PATCH", `/api/plan/items/${item.id}`, resolveResponsible(e.target.value, users));
                                  }
                                }}
                              />
                            ) : (nameOf(item) || <span style={{ color: "var(--text-faint)" }}>—</span>)}
                          </td>
                          {isZavuch && (
                            <td className="sea-no-print">
                              <button className="sea-btn sea-btn-ghost sea-btn-danger" style={{ padding: 5 }} onClick={() => run("DELETE", `/api/plan/items/${item.id}`)}>
                                <X size={13} />
                              </button>
                            </td>
                          )}
                        </tr>
                      );
                    });
                  }

                  if (isZavuch) {
                    const draft = drafts[w.id] || { title: "", who: "" };
                    rows.push(
                      <tr key={`${w.id}-add`} className="sea-no-print">
                        {w.items.length === 0 ? null : null}
                        <td>
                          <input
                            value={draft.title}
                            placeholder="+ жаңа іс шара"
                            style={{ padding: "6px 8px" }}
                            onChange={(e) => setDrafts((d) => ({ ...d, [w.id]: { ...draft, title: e.target.value } }))}
                            onKeyDown={(e) => { if (e.key === "Enter") addItem(w.id); }}
                          />
                        </td>
                        <td>
                          <input
                            list="sea-plan-users"
                            value={draft.who}
                            placeholder="жауапты"
                            style={{ padding: "6px 8px" }}
                            onChange={(e) => setDrafts((d) => ({ ...d, [w.id]: { ...draft, who: e.target.value } }))}
                            onKeyDown={(e) => { if (e.key === "Enter") addItem(w.id); }}
                          />
                        </td>
                        <td>
                          <button className="sea-btn" style={{ padding: 5 }} onClick={() => addItem(w.id)} disabled={!draft.title.trim()}>
                            <Plus size={13} />
                          </button>
                        </td>
                      </tr>
                    );
                  }
                  return rows;
                })}
              </tbody>
            </table>
            <datalist id="sea-plan-users">
              {users.map((u) => <option key={u.email} value={u.name} />)}
            </datalist>
          </div>
        )}

        {isZavuch && (
          <div style={{ display: "flex", gap: 8, marginTop: 14, flexWrap: "wrap" }} className="sea-no-print">
            <button className="sea-btn sea-btn-primary" onClick={addWeek} disabled={weeks.length >= 6}>
              <Plus size={14} /> Апта қосу
            </button>
            {weeks.length > 0 && (
              <button
                className="sea-btn sea-btn-danger"
                onClick={() => run("DELETE", `/api/plan/weeks/${weeks[weeks.length - 1].id}`)}
              >
                <Trash2 size={13} /> Соңғы аптаны өшіру
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* ----------------------------------------------------------------------
   ШАБЛОНЫ
---------------------------------------------------------------------- */
function TemplatesView({ templates, run }) {
  const [editing, setEditing] = useState(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);

  return (
    <div>
      <SectionHeader
        title="Шаблоны мероприятий"
        subtitle="Типовые наборы задач для повторяющихся мероприятий. Можно редактировать и добавлять новые."
        action={<button className="sea-btn sea-btn-primary" onClick={() => setEditing({ id: "", name: "", tasks: [] })}><Plus size={15} /> Новый шаблон</button>}
      />
      <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))" }}>
        {templates.map((t) => (
          <div key={t.id} className="sea-card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div style={{ fontWeight: 700, fontSize: 14.5 }}>{t.name}</div>
              {confirmDeleteId === t.id ? (
                <div style={{ display: "flex", gap: 4 }}>
                  <button className="sea-btn sea-btn-danger" style={{ padding: "4px 8px", fontSize: 11.5 }} onClick={() => { setConfirmDeleteId(null); run("DELETE", `/api/templates/${t.id}`); }}>Точно?</button>
                  <button className="sea-btn sea-btn-ghost" style={{ padding: "4px 8px", fontSize: 11.5 }} onClick={() => setConfirmDeleteId(null)}>Отмена</button>
                </div>
              ) : (
                <div style={{ display: "flex", gap: 4 }}>
                  <button className="sea-btn sea-btn-ghost" style={{ padding: 6 }} onClick={() => setEditing(t)}><Pencil size={13} /></button>
                  <button className="sea-btn sea-btn-ghost sea-btn-danger" style={{ padding: 6 }} onClick={() => setConfirmDeleteId(t.id)}><Trash2 size={13} /></button>
                </div>
              )}
            </div>
            <div style={{ fontSize: 12.5, color: "var(--text-faint)", marginTop: 6 }}>{t.tasks.length} задач(и)</div>
            <ul style={{ margin: "8px 0 0", paddingLeft: 18, fontSize: 12.5, color: "var(--text-soft)" }}>
              {t.tasks.slice(0, 4).map((task, idx) => <li key={idx}>{task.title}</li>)}
              {t.tasks.length > 4 && <li style={{ color: "var(--text-faint)" }}>и ещё {t.tasks.length - 4}…</li>}
            </ul>
          </div>
        ))}
      </div>

      {editing && (
        <TemplateEditModal
          template={editing}
          onClose={() => setEditing(null)}
          onSave={async (tpl) => { await run("POST", "/api/templates", tpl); setEditing(null); }}
        />
      )}
    </div>
  );
}

function TemplateEditModal({ template, onClose, onSave }) {
  const [name, setName] = useState(template.name);
  const [tasks, setTasks] = useState(template.tasks || []);
  const [draft, setDraft] = useState({ title: "", comment: "" });

  const addTask = () => {
    if (!draft.title.trim()) return;
    setTasks([...tasks, { title: draft.title.trim(), comment: draft.comment.trim() }]);
    setDraft({ title: "", comment: "" });
  };

  return (
    <Modal title={template.name ? "Редактировать шаблон" : "Новый шаблон"} onClose={onClose}>
      <div className="sea-field">
        <label className="sea-label">Название шаблона</label>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Например: Конкурс чтецов" />
      </div>
      <div className="sea-field">
        <label className="sea-label">Задачи в шаблоне</label>
        {tasks.length > 0 && (
          <div style={{ display: "grid", gap: 6, marginBottom: 10 }}>
            {tasks.map((t, idx) => (
              <div key={idx} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "var(--surface)", padding: "7px 10px", borderRadius: 8 }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 13 }}>{t.title}</div>
                  {t.comment && <div style={{ fontSize: 12, color: "var(--text-faint)" }}>{t.comment}</div>}
                </div>
                <button onClick={() => setTasks(tasks.filter((_, i) => i !== idx))} style={{ border: "none", background: "none", cursor: "pointer" }}><X size={14} /></button>
              </div>
            ))}
          </div>
        )}
        <div style={{ display: "flex", gap: 6 }}>
          <input placeholder="Название задачи" value={draft.title} onChange={(e) => setDraft({ ...draft, title: e.target.value })} onKeyDown={(e) => { if (e.key === "Enter") addTask(); }} />
          <input placeholder="Комментарий" value={draft.comment} onChange={(e) => setDraft({ ...draft, comment: e.target.value })} onKeyDown={(e) => { if (e.key === "Enter") addTask(); }} />
          <button className="sea-btn" onClick={addTask}><Plus size={14} /></button>
        </div>
      </div>
      <ModalFooter>
        <button className="sea-btn sea-btn-ghost" onClick={onClose}>Отмена</button>
        <button className="sea-btn sea-btn-primary" disabled={!name.trim()} onClick={() => onSave({ id: template.id, name: name.trim(), tasks })}>Сохранить шаблон</button>
      </ModalFooter>
    </Modal>
  );
}

/* ----------------------------------------------------------------------
   АРХИВ
---------------------------------------------------------------------- */
function ArchiveView({ events, users, run }) {
  const [openId, setOpenId] = useState(null);
  const archived = events.filter((e) => e.status === "done").sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0));
  const open = archived.find((e) => e.id === openId);

  return (
    <div>
      <SectionHeader title="Архив мероприятий" subtitle="Прошедшие мероприятия с итогами и материалами." />
      {archived.length === 0 ? (
        <EmptyState icon={ArchiveIcon} text="Архив пока пуст. Проведённые мероприятия появятся здесь." />
      ) : (
        <div style={{ display: "grid", gap: 10 }}>
          {archived.map((e) => (
            <button key={e.id} className="sea-card" style={{ textAlign: "left", width: "100%" }} onClick={() => setOpenId(e.id)}>
              <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 8 }}>
                <div>
                  <div style={{ fontWeight: 700 }}>{e.title}</div>
                  <div style={{ fontSize: 12.5, color: "var(--text-faint)", marginTop: 2 }}>{fmtDate(e.date)} {e.location && `· ${e.location}`}</div>
                </div>
                {e.archive?.files?.length > 0 && <span className="sea-chip"><Paperclip size={12} /> {e.archive.files.length} файл(ов)</span>}
              </div>
              {e.archive?.summary && <p style={{ margin: "8px 0 0", fontSize: 13, color: "var(--text-soft)" }}>{e.archive.summary}</p>}
            </button>
          ))}
        </div>
      )}

      {open && (
        <Modal title={open.title} onClose={() => setOpenId(null)}>
          <div style={{ fontSize: 13, color: "var(--text-faint)", marginBottom: 12 }}>
            {fmtDate(open.date)} {open.location && `· ${open.location}`} {open.budget && `· бюджет: ${open.budget}`}
          </div>
          <div className="sea-field">
            <label className="sea-label">Итоги</label>
            <p style={{ margin: 0, color: "var(--text-soft)" }}>{open.archive?.summary || "Без описания."}</p>
          </div>
          {open.archive?.files?.length > 0 && (
            <div className="sea-field">
              <label className="sea-label">Файлы</label>
              <div style={{ display: "grid", gap: 6 }}>
                {open.archive.files.map((f) => (
                  <a key={f.id} href={f.url} className="sea-chip" style={{ textDecoration: "none", width: "fit-content" }}>
                    <Paperclip size={12} /> {f.name}
                  </a>
                ))}
              </div>
            </div>
          )}
          <div className="sea-field">
            <label className="sea-label">Список задач</label>
            <div style={{ display: "grid", gap: 6 }}>
              {(open.tasks || []).length === 0 && <div style={{ fontSize: 13, color: "var(--text-faint)" }}>Задач не было.</div>}
              {(open.tasks || []).map((t) => {
                const failed = t.status !== "done" && (t.responsible || []).length > 0;
                return (
                <div key={t.id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, background: failed ? "var(--danger-soft)" : "var(--surface)", padding: "8px 10px", borderRadius: 8 }}>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                      <span style={{ fontWeight: 600, fontSize: 13 }}>{t.title}</span>
                      {failed && (
                        <span className="sea-badge" style={{ color: "var(--danger)", background: "#fff" }}>
                          не выполнена · −{POINTS_PER_FAILED_TASK}
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: 11.5, color: "var(--text-faint)" }}>
                      {users.filter((u) => t.responsible?.includes(u.email)).map((u) => u.name).join(", ") || "без ответственного"}
                    </div>
                  </div>
                  <select value={t.status} onChange={(e) => run("PATCH", `/api/tasks/${t.id}`, { status: e.target.value })} style={{ width: "auto", padding: "5px 8px", flexShrink: 0 }}>
                    {Object.entries(TASK_STATUS_LABELS).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
                  </select>
                </div>
                );
              })}
            </div>
            <div style={{ fontSize: 11.5, color: "var(--text-faint)", marginTop: 6 }}>
              Задачи, оставшиеся невыполненными к моменту архивации, отнимают у ответственных
              по {POINTS_PER_FAILED_TASK} очков. Если задача на самом деле была выполнена, а статус забыли поменять —
              отметьте её «Готово» прямо здесь: минус пересчитается в плюс.
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

/* ----------------------------------------------------------------------
   УВЕДОМЛЕНИЯ
---------------------------------------------------------------------- */
function NotificationsView({ notifications, onOpenEvents }) {
  return (
    <div>
      <SectionHeader title="Уведомления" subtitle="Напоминания о ваших задачах с приближающимся или просроченным дедлайном." />
      {notifications.length === 0 ? (
        <EmptyState icon={Bell} text="Нет актуальных напоминаний. Все ваши задачи в порядке." />
      ) : (
        <div style={{ display: "grid", gap: 8 }}>
          {notifications.map((n, idx) => (
            <div key={idx} className="sea-card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 10, borderColor: n.type === "overdue" ? "var(--danger)" : "var(--border)" }}>
              <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                <div style={{ color: n.type === "overdue" ? "var(--danger)" : "var(--warning)", marginTop: 2 }}>
                  {n.type === "overdue" ? <Clock size={16} /> : <Bell size={16} />}
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 13.5 }}>{n.task.title}</div>
                  <div style={{ fontSize: 12.5, color: "var(--text-faint)" }}>Мероприятие: {n.event.title}</div>
                  <div style={{ fontSize: 12, marginTop: 2, color: n.type === "overdue" ? "var(--danger)" : "var(--warning)" }}>
                    {n.type === "overdue" ? `Просрочено на ${Math.abs(n.days)} дн.` : n.days === 0 ? "Срок — сегодня" : `Срок через ${n.days} дн.`}
                  </div>
                </div>
              </div>
              <button className="sea-btn" onClick={onOpenEvents}>Открыть</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ----------------------------------------------------------------------
   РЕЙТИНГ
---------------------------------------------------------------------- */
function LeaderboardView({ events, users, ideas, adjustments, isZavuch, run, currentUser }) {
  const ranking = useMemo(() => computeRanking(events, ideas, users, adjustments), [events, users, ideas, adjustments]);
  const [adjusting, setAdjusting] = useState(null);
  const maxPoints = Math.max(1, ...ranking.map((r) => r.points));
  const medals = ["🥇", "🥈", "🥉"];

  // карточка в списке могла обновиться после начисления — берём свежие данные
  const adjustingUser = adjusting ? ranking.find((r) => r.email === adjusting.email) : null;

  return (
    <div>
      <SectionHeader
        title="Рейтинг"
        subtitle={`Игровой зачёт вклада в мероприятия — ${POINTS_PER_TASK} очков за выполненную задачу, ${POINTS_PER_IDEA} за предложенную идею, ${POINTS_PER_APPROVED_IDEA} — если идея одобрена и стала мероприятием. Если мероприятие отмечено проведённым, а задача осталась невыполненной, ответственные теряют ${POINTS_PER_FAILED_TASK} очков.`}
      />

      <div style={{ marginBottom: 18 }}>
        <PrizeBanner ranking={ranking} currentUser={currentUser} />
      </div>

      {ranking.every((r) => r.rawPoints === 0) ? (
        <EmptyState icon={Trophy} text="Пока никто не набрал очков — предложите идею или выполните задачу в мероприятии!" />
      ) : (
        <div style={{ display: "grid", gap: 10 }}>
          {ranking.map((u, idx) => {
            const lvlStyle = getLevelStyle(u.level);
            return (
              <div
                key={u.email}
                className="sea-card"
                style={{
                  display: "flex", alignItems: "center", gap: 14,
                  borderColor: idx === 0 && u.points > 0 ? "var(--accent)" : lvlStyle.border,
                  background: idx === 0 && u.points > 0 ? "var(--accent-soft)" : lvlStyle.bg,
                }}
              >
                <div style={{ width: 30, textAlign: "center", fontSize: idx < 3 ? 20 : 14, fontWeight: 700, color: "var(--text-faint)" }}>
                  {idx < 3 ? medals[idx] : idx + 1}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                    <span style={{ fontWeight: 700, fontSize: 14.5 }}>{u.name}</span>
                    <span className="sea-chip" style={{ background: lvlStyle.chip, color: lvlStyle.chipText, fontWeight: 700 }}>Уровень {u.level}</span>
                    <span className="sea-chip">{u.role === "zavuch" ? "Завуч" : "Учитель"}</span>
                  </div>
                  <div style={{ marginTop: 6, height: 6, background: "var(--surface-2)", borderRadius: 999, overflow: "hidden" }}>
                    <div style={{ height: "100%", width: `${Math.max(4, (Math.max(0, u.points) / maxPoints) * 100)}%`, background: "var(--accent)", borderRadius: 999 }} />
                  </div>
                  <div style={{ fontSize: 11.5, color: "var(--text-faint)", marginTop: 4 }}>
                    {u.tasksDone} выполненных задач · {u.ideasProposed} идей предложено{u.ideasApproved > 0 ? ` · ${u.ideasApproved} одобрено` : ""}
                    {u.tasksFailed > 0 && (
                      <span style={{ color: "var(--danger)", fontWeight: 600 }}>
                        {" · "}{u.tasksFailed} не выполнено (−{u.tasksFailed * POINTS_PER_FAILED_TASK})
                      </span>
                    )}
                    {u.adjusted !== 0 && (
                      <span style={{ color: u.adjusted > 0 ? "var(--success)" : "var(--danger)", fontWeight: 600 }}>
                        {" · "}от завуча {u.adjusted > 0 ? "+" : "−"}{Math.abs(u.adjusted)}
                      </span>
                    )}
                  </div>
                </div>
                <div style={{ textAlign: "right", whiteSpace: "nowrap", display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 4, fontWeight: 800, fontSize: 17, color: u.points < 0 ? "var(--danger)" : "var(--accent)" }}>
                      <Star size={16} fill={u.points < 0 ? "var(--danger)" : "var(--accent)"} color={u.points < 0 ? "var(--danger)" : "var(--accent)"} /> {u.points}
                    </div>
                    <div style={{ fontSize: 10.5, color: "var(--text-faint)" }}>очков</div>
                  </div>
                  {isZavuch && (
                    <button className="sea-btn" style={{ padding: "4px 9px", fontSize: 11.5 }} onClick={() => setAdjusting(u)}>
                      <Star size={12} /> Изменить очки
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {adjustingUser && (
        <AdjustPointsModal
          user={adjustingUser}
          adjustments={adjustments.filter((a) => a.email === adjustingUser.email)}
          onClose={() => setAdjusting(null)}
          run={run}
        />
      )}
    </div>
  );
}

function AdjustPointsModal({ user, adjustments, onClose, run }) {
  const [amount, setAmount] = useState("");
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);

  const value = parseInt(amount, 10);
  const valid = Number.isFinite(value) && value !== 0;

  const submit = async (points) => {
    setBusy(true);
    try {
      await run("POST", "/api/points/adjust", { email: user.email, points, reason: reason.trim() });
      setAmount("");
      setReason("");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title={`Очки — ${user.name}`} onClose={onClose}>
      <div style={{ display: "flex", alignItems: "center", gap: 14, background: "var(--surface)", padding: "12px 14px", borderRadius: 10, marginBottom: 16 }}>
        <div>
          <div style={{ fontSize: 22, fontWeight: 800, color: user.points < 0 ? "var(--danger)" : "var(--accent)", lineHeight: 1.1 }}>{user.points}</div>
          <div style={{ fontSize: 11, color: "var(--text-faint)" }}>очков сейчас</div>
        </div>
        <div style={{ fontSize: 12, color: "var(--text-soft)" }}>
          Заработано за задачи и идеи: {user.rawPoints}
          {user.adjusted !== 0 && (
            <>
              <br />Ручные начисления: {user.adjusted > 0 ? "+" : "−"}{Math.abs(user.adjusted)}
            </>
          )}
        </div>
      </div>

      <div className="sea-field">
        <label className="sea-label">Сколько очков</label>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 8 }}>
          {[100, 50, -50, -100].map((n) => (
            <button
              key={n}
              className="sea-btn"
              style={{ padding: "5px 11px", color: n > 0 ? "var(--success)" : "var(--danger)" }}
              disabled={busy}
              onClick={() => submit(n)}
            >
              {n > 0 ? `+${n}` : n}
            </button>
          ))}
        </div>
        <input
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="или своё число: 250 либо -250"
          onKeyDown={(e) => { if (e.key === "Enter" && valid) submit(value); }}
        />
      </div>

      <div className="sea-field">
        <label className="sea-label">Причина — увидят все в ленте активности</label>
        <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="напр. помощь на городском конкурсе" />
      </div>

      <button
        className="sea-btn sea-btn-primary"
        style={{ width: "100%", justifyContent: "center" }}
        disabled={!valid || busy}
        onClick={() => submit(value)}
      >
        {valid && value > 0 ? `Начислить ${value}` : valid ? `Снять ${Math.abs(value)}` : "Укажите количество"}
      </button>

      {adjustments.length > 0 && (
        <div style={{ marginTop: 18 }}>
          <div className="sea-label">История начислений</div>
          <div style={{ display: "grid", gap: 6 }}>
            {adjustments.map((a) => (
              <div key={a.id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, background: "var(--surface)", padding: "8px 10px", borderRadius: 8 }}>
                <div style={{ minWidth: 0 }}>
                  <span style={{ fontWeight: 700, color: a.points > 0 ? "var(--success)" : "var(--danger)" }}>
                    {a.points > 0 ? `+${a.points}` : a.points}
                  </span>
                  {a.reason && <span style={{ color: "var(--text-soft)" }}> — {a.reason}</span>}
                  <div style={{ fontSize: 11, color: "var(--text-faint)" }}>{a.byName} · {timeAgo(a.createdAt)}</div>
                </div>
                <button
                  className="sea-btn sea-btn-ghost sea-btn-danger"
                  style={{ padding: 5 }}
                  title="Отменить это начисление"
                  onClick={() => run("DELETE", `/api/points/adjust/${a.id}`)}
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </Modal>
  );
}

/* ----------------------------------------------------------------------
   ПОЛЬЗОВАТЕЛИ
---------------------------------------------------------------------- */
function UsersAdminView({ users, currentUser, isZavuch, run }) {
  return (
    <div>
      <SectionHeader
        title="Пользователи и роли"
        subtitle={isZavuch ? "Управление ролями сотрудников школы." : "Список сотрудников. Менять роли может только завуч."}
      />
      <div className="sea-card">
        <table className="sea-table">
          <thead><tr><th>Имя</th><th>Email</th><th>Роль</th></tr></thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.email}>
                <td style={{ fontWeight: 600 }}>
                  {u.name} {u.email === currentUser.email && <span style={{ color: "var(--text-faint)", fontWeight: 400 }}>(вы)</span>}
                </td>
                <td style={{ color: "var(--text-soft)" }}>{u.email}</td>
                <td>
                  {isZavuch ? (
                    <select value={u.role} onChange={(e) => run("PATCH", `/api/users/${encodeURIComponent(u.email)}`, { role: e.target.value })} style={{ width: "auto" }}>
                      <option value="teacher">Учитель</option>
                      <option value="zavuch">Завуч</option>
                    </select>
                  ) : (
                    <span className="sea-chip">{u.role === "zavuch" ? "Завуч" : "Учитель"}</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ----------------------------------------------------------------------
   ОБЩИЕ КОМПОНЕНТЫ
---------------------------------------------------------------------- */
function PrizeBanner({ ranking, currentUser, onOpenLeaderboard }) {
  const announce = prizeAnnounceDate();
  const daysLeft = Math.max(0, Math.ceil((announce - new Date()) / 86400000));
  const leader = ranking[0];
  const started = leader && leader.points > 0;
  const myIndex = ranking.findIndex((r) => r.email === currentUser.email);
  const me = myIndex >= 0 ? ranking[myIndex] : null;

  let standing = "Рейтинг ещё не начался — выполните первую задачу и займите первое место.";
  if (started && me) {
    const gap = leader.points - me.points;
    if (myIndex === 0) {
      const second = ranking[1];
      const lead = second ? me.points - second.points : me.points;
      standing = lead > 0
        ? `Вы первый — отрыв ${lead} ${pointsWord(lead)}.`
        : "Вы делите первое место — любая выполненная задача решит спор.";
    } else {
      standing = `Вы на ${myIndex + 1} месте. До первого — ${gap} ${pointsWord(gap)}.`;
    }
  }

  return (
    <div
      style={{
        background: "linear-gradient(135deg, var(--accent) 0%, #5c0b5c 100%)",
        color: "#fff", borderRadius: "var(--radius-lg)", padding: "16px 18px",
        display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap",
        boxShadow: "var(--shadow-sm)",
      }}
    >
      <div style={{ width: 44, height: 44, borderRadius: 12, background: "rgba(255,255,255,0.16)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
        <Trophy size={24} color="#fff" />
      </div>

      <div style={{ flex: "1 1 240px", minWidth: 0 }}>
        <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase", opacity: 0.75 }}>
          Приз года
        </div>
        <div style={{ fontSize: 17, fontWeight: 800, letterSpacing: "-0.01em", marginTop: 1 }}>
          {PRIZE.title}
        </div>
        <div style={{ fontSize: 12.5, opacity: 0.9, marginTop: 2 }}>
          {PRIZE.subtitle} · итоги {announce.toLocaleDateString("ru-RU", { day: "numeric", month: "long" })}, перед Новым годом
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", flexShrink: 0 }}>
        <div style={{ textAlign: "center", background: "rgba(255,255,255,0.13)", borderRadius: 10, padding: "8px 14px", minWidth: 82 }}>
          <div style={{ fontSize: 21, fontWeight: 800, lineHeight: 1.1, fontVariantNumeric: "tabular-nums" }}>{daysLeft}</div>
          <div style={{ fontSize: 10.5, opacity: 0.85 }}>{daysWord(daysLeft)} до итогов</div>
        </div>
        <div style={{ fontSize: 12.5, maxWidth: 250, display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 2 }}>
          {started && (
            <div style={{ fontWeight: 700 }}>
              Лидер: {leader.name} — {leader.points}
            </div>
          )}
          <div style={{ opacity: 0.9 }}>{standing}</div>
          {onOpenLeaderboard && (
            <button
              onClick={onOpenLeaderboard}
              className="sea-btn"
              style={{ marginTop: 6, padding: "5px 10px", fontSize: 12, background: "rgba(255,255,255,0.16)", borderColor: "transparent", color: "#fff" }}
            >
              Смотреть рейтинг <ArrowRight size={12} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function SectionHeader({ title, subtitle, action }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, marginBottom: 18, flexWrap: "wrap" }}>
      <div>
        <h1 style={{ fontSize: 20, fontWeight: 700, margin: 0, letterSpacing: "-0.01em" }}>{title}</h1>
        {subtitle && <p style={{ margin: "4px 0 0", color: "var(--text-faint)", fontSize: 13 }}>{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

function EmptyState({ icon: Icon, text, hint }) {
  return (
    <div className="sea-empty sea-card">
      <div className="sea-empty-icon-wrap"><Icon size={26} /></div>
      <div style={{ fontWeight: 600, color: "var(--text)" }}>{text}</div>
      {hint && <div style={{ fontSize: 12.5, marginTop: 4, color: "var(--text-faint)" }}>{hint}</div>}
    </div>
  );
}

function ProgressRing({ value, size = 40, strokeWidth = 4, label }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (Math.max(0, Math.min(100, value)) / 100) * circumference;
  return (
    <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="var(--surface-2)" strokeWidth={strokeWidth} />
        <circle
          cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="var(--accent)" strokeWidth={strokeWidth}
          strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
          style={{ transition: "stroke-dashoffset .3s ease" }}
        />
      </svg>
      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: size < 36 ? 9 : 10.5, fontWeight: 700, color: "var(--text)" }}>
        {label !== undefined ? label : `${Math.round(value)}%`}
      </div>
    </div>
  );
}

function Modal({ title, children, onClose, wide }) {
  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="sea-modal-backdrop" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="sea-modal sea-scrollbar" style={wide ? { maxWidth: 760 } : {}}>
        <div className="sea-modal-header">
          <div style={{ fontWeight: 700, fontSize: 16 }}>{title}</div>
          <button className="sea-btn sea-btn-ghost" style={{ padding: 6 }} onClick={onClose}><X size={16} /></button>
        </div>
        <div className="sea-modal-body sea-scrollbar">{children}</div>
      </div>
    </div>
  );
}

function ModalFooter({ children }) {
  return <div className="sea-modal-footer">{children}</div>;
}

/* ---------------------------------------------------------------- монтирование */
const rootEl = document.getElementById("root");
rootEl.dataset.mounted = "1";
ReactDOM.createRoot(rootEl).render(<App />);
