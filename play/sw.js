// Offline support: cache the app shell, serve it when there is no connection.
const CACHE = "quest520-v54";
const FILES = ["./", "index.html", "manifest.webmanifest", "icon.svg", "icon-192.png", "icon-180.png", "gen.js", "music.js", "exam.js", "account.js", "checklist.html"];
self.addEventListener("install", e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES.map(f => new Request(f, { cache: "reload" })))).then(() => self.skipWaiting())));
self.addEventListener("activate", e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || /\.supabase\.co$/.test(new URL(e.request.url).hostname)) return; // account data is never cached
  // Same-origin files skip the browser's HTTP cache (revalidate), so a new release shows up right away.
  const req = new URL(e.request.url).origin === location.origin ? new Request(e.request.url, { cache: "no-cache", credentials: "same-origin" }) : e.request;
  e.respondWith(fetch(req).then(r => { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return r; }).catch(() => caches.match(e.request).then(r => r || caches.match("index.html"))));
});
