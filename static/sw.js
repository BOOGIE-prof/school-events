/* Service worker: оболочка приложения работает офлайн, данные — только по сети.

   Стратегии:
   • оболочка (html, jsx, css, иконки) — сначала сеть, при неудаче кэш;
     так обновления приходят сразу, но при плохой связи приложение открывается;
   • /api/* — только сеть: показывать устаревшие мероприятия и очки нельзя.

   Чтобы выкатить новую версию оболочки, достаточно поднять CACHE_VERSION. */

const CACHE_VERSION = "sea-v3";
const SHELL = [
  "/",
  "/app.jsx",
  "/styles.css",
  "/logo.png",
  "/emblem.png",
  "/icon-192.png",
  "/icon-512.png",
  "/manifest.webmanifest",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then((cache) => cache.addAll(SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

/* Push-уведомления о задачах */
self.addEventListener("push", (event) => {
  let data = { title: "Events", body: "", url: "/" };
  try {
    if (event.data) data = Object.assign(data, event.data.json());
  } catch (e) {
    if (event.data) data.body = event.data.text();
  }
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: "/icon-192.png",
      badge: "/icon-192.png",
      data: { url: data.url || "/" },
      tag: data.tag || "sea-task",
    })
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const target = (event.notification.data && event.notification.data.url) || "/";
  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((list) => {
      // приложение уже открыто — просто выводим его вперёд
      for (const client of list) {
        if (client.url.indexOf(self.location.origin) === 0 && "focus" in client) return client.focus();
      }
      return self.clients.openWindow(target);
    })
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith("/api/")) return; // данные всегда живые

  event.respondWith(
    fetch(request)
      .then((response) => {
        if (response && response.ok) {
          const copy = response.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(request, copy));
        }
        return response;
      })
      .catch(() =>
        caches.match(request).then((cached) =>
          // на переходы внутри приложения отдаём стартовую страницу
          cached || (request.mode === "navigate" ? caches.match("/") : undefined)
        )
      )
  );
});
