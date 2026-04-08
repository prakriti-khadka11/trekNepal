const CACHE_NAME = 'treknepal-v1';

// Pages to cache for offline access
const STATIC_ASSETS = [
  '/',
  '/trekking/',
  '/packages/',
  '/static/css/style.css',
  '/static/img/logo.png',
];

// Install — cache static assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS).catch(() => {});
    })
  );
  self.skipWaiting();
});

// Activate — clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch — network first, fall back to cache
self.addEventListener('fetch', event => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;
  // Skip admin and API requests
  if (event.request.url.includes('/admin/') ||
      event.request.url.includes('/weather/data/') ||
      event.request.url.includes('/currency-converter/rates/')) return;

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Cache a copy of the response
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        return response;
      })
      .catch(() => {
        // Network failed — try cache
        return caches.match(event.request).then(cached => {
          if (cached) return cached;
          // Offline fallback for navigation
          if (event.request.mode === 'navigate') {
            return caches.match('/');
          }
        });
      })
  );
});
