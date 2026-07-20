/* CEASA PWA Service Worker
 * Estratégia:
 *  - App shell (index.html, ícones, manifest, CDNs estáticos) -> cache-first para instalabilidade e offline.
 *  - Firebase (googleapis / firestore / firebaseio / identitytoolkit) -> SEMPRE network,
 *    NUNCA cacheado. Isso é essencial para evitar leituras/escritas obsoletas quando
 *    vários compradores estão fazendo pedidos simultaneamente (evita "race" com dados
 *    desatualizados servidos do cache).
 *  - Demais requisições GET -> stale-while-revalidate (rápido e sempre atualiza em background).
 */

const VERSION = 'ceasa-v1.0.1';
const SHELL_CACHE = `ceasa-shell-${VERSION}`;
const RUNTIME_CACHE = `ceasa-runtime-${VERSION}`;

// Recursos essenciais do app shell (funciona offline após primeira visita)
const SHELL_ASSETS = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/offline.html',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/icons/maskable-512.png',
  '/icons/apple-touch-icon.png',
  '/icons/favicon-32.png',
  '/icons/favicon.ico'
];

// Domínios do Firebase que NUNCA devem ser cacheados (dados em tempo real)
const REALTIME_HOSTS = [
  'firestore.googleapis.com',
  'firebase.googleapis.com',
  'firebaseio.com',
  'identitytoolkit.googleapis.com',
  'securetoken.googleapis.com',
  'firebaseinstallations.googleapis.com',
  'firebaseremoteconfig.googleapis.com'
];

function isRealtimeRequest(url) {
  return REALTIME_HOSTS.some(h => url.hostname === h || url.hostname.endsWith('.' + h));
}

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then(cache =>
      cache.addAll(SHELL_ASSETS).catch(err => {
        // Não falhar a instalação se algum asset externo estiver indisponível
        console.warn('[SW] shell precache warning:', err);
      })
    ).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => k !== SHELL_CACHE && k !== RUNTIME_CACHE)
          .map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return; // POST/PUT/PATCH sempre direto pra rede

  let url;
  try { url = new URL(req.url); } catch { return; }

  // 1) Firebase / dados em tempo real: SEMPRE rede, sem cache. Evita race.
  if (isRealtimeRequest(url)) {
    event.respondWith(fetch(req));
    return;
  }

  // 2) Navegação (HTML): network-first com fallback pra shell/offline
  if (req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html')) {
    event.respondWith(
      fetch(req)
        .then(res => {
          const copy = res.clone();
          caches.open(SHELL_CACHE).then(c => c.put('/index.html', copy)).catch(() => {});
          return res;
        })
        .catch(() =>
          caches.match(req).then(r => r || caches.match('/index.html')).then(r => r || caches.match('/offline.html'))
        )
    );
    return;
  }

  // 3) Assets do próprio site: cache-first
  if (url.origin === self.location.origin) {
    event.respondWith(
      caches.match(req).then(cached => {
        const network = fetch(req).then(res => {
          if (res && res.status === 200) {
            const copy = res.clone();
            caches.open(RUNTIME_CACHE).then(c => c.put(req, copy));
          }
          return res;
        }).catch(() => cached);
        return cached || network;
      })
    );
    return;
  }

  // 4) CDNs de terceiros (Tailwind, Lucide, gstatic Firebase JS): stale-while-revalidate
  event.respondWith(
    caches.match(req).then(cached => {
      const network = fetch(req).then(res => {
        if (res && res.status === 200 && res.type !== 'opaque') {
          const copy = res.clone();
          caches.open(RUNTIME_CACHE).then(c => c.put(req, copy));
        }
        return res;
      }).catch(() => cached);
      return cached || network;
    })
  );
});
