// ═══════════════════════════════════════════════════════════════════════
//  KardPad — Service Worker (PWA)
//  Estrategia: Network-first con cache fallback.
//  - Siempre intenta el servidor (los archivos cambian con frecuencia).
//  - Si no hay red (offline), sirve la última versión cacheada.
//  - Esto permite que la pantalla de IP se muestre incluso sin conexión.
// ═══════════════════════════════════════════════════════════════════════

const CACHE_NAME = 'kardpad-v2';
const ASSETS = [
  './',
  './index.html',
  './main.css',
  './app.js',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
];

// ── Install: pre-cache los archivos esenciales ─────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
  // Activar inmediatamente sin esperar a que se cierren las pestañas
  self.skipWaiting();
});

// ── Activate: limpiar caches viejos ────────────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      )
    )
  );
  // Tomar control de todas las pestañas abiertas
  self.clients.claim();
});

// ── Fetch: network-first, cache fallback ───────────────────────────
self.addEventListener('fetch', (event) => {
  // Solo cachear requests GET del mismo origen
  if (event.request.method !== 'GET') return;

  // No cachear requests a CDN externos (jsQR, Google Fonts)
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Clonar y guardar en cache
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        return response;
      })
      .catch(() => {
        // Sin red → servir desde cache
        return caches.match(event.request);
      })
  );
});
