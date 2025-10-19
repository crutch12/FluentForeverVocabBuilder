const CACHE_NAME = 'ffh-v1';
const urlsToCache = [
  '/',
  '/static/css/bootstrap-dark.css',
  '/static/css/style.css',
  'https://code.jquery.com/jquery-3.4.1.min.js',
  '/static/js/paste.js',
  '/static/js/index.js',
  '/static/manifest.json'
];

// Install event - cache resources
self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function (cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', function (event) {
  event.respondWith(
    caches.match(event.request)
      .then(function (response) {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      }
      )
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys().then(function (cacheNames) {
      return Promise.all(
        cacheNames.map(function (cacheName) {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

