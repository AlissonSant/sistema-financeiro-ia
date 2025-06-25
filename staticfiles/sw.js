// sw.js - Service Worker para PWA IA Financeiro
const CACHE_NAME = 'ia-financeiro-v1.0.0';
const OFFLINE_URL = '/offline/';

// URLs essenciais para cache
const ESSENTIAL_URLS = [
  '/',
  '/dashboard/',
  '/metas/',
  '/login/',
  '/static/css/base.css',
  '/static/js/app.js',
  '/offline/',
  // Adicione outras URLs críticas
];

// URLs de API para cache dinâmico
const API_URLS = [
  '/dashboard/',
  '/metas/',
  '/metas/criar/',
];

// Instalação do Service Worker
self.addEventListener('install', event => {
  console.log('🚀 IA Financeiro PWA: Service Worker instalando...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('💾 Cache criado:', CACHE_NAME);
        return cache.addAll(ESSENTIAL_URLS);
      })
      .catch(error => {
        console.error('❌ Erro no cache inicial:', error);
      })
  );
  
  // Força ativação imediata
  self.skipWaiting();
});

// Ativação do Service Worker
self.addEventListener('activate', event => {
  console.log('✅ IA Financeiro PWA: Service Worker ativado!');
  
  event.waitUntil(
    // Remove caches antigos
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('🗑️ Removendo cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // Toma controle de todas as páginas
      return self.clients.claim();
    })
  );
});

// Interceptação de requisições
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Estratégia: Cache First para recursos estáticos
  if (request.destination === 'style' || 
      request.destination === 'script' || 
      request.destination === 'image') {
    
    event.respondWith(
      caches.match(request)
        .then(response => {
          if (response) {
            console.log('📦 Servindo do cache:', request.url);
            return response;
          }
          
          // Se não está no cache, busca da rede e adiciona ao cache
          return fetch(request)
            .then(response => {
              if (response.status === 200) {
                const responseClone = response.clone();
                caches.open(CACHE_NAME)
                  .then(cache => cache.put(request, responseClone));
              }
              return response;
            });
        })
        .catch(() => {
          console.log('🔌 Offline: recurso não disponível');
        })
    );
    return;
  }
  
  // Estratégia: Network First para páginas HTML
  if (request.destination === 'document') {
    event.respondWith(
      fetch(request)
        .then(response => {
          // Salva páginas importantes no cache
          if (response.status === 200 && ESSENTIAL_URLS.includes(url.pathname)) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME)
              .then(cache => cache.put(request, responseClone));
          }
          return response;
        })
        .catch(() => {
          // Se offline, tenta servir do cache
          return caches.match(request)
            .then(response => {
              if (response) {
                console.log('📱 Modo offline: servindo página do cache');
                return response;
              }
              
              // Se não tem no cache, mostra página offline
              return caches.match(OFFLINE_URL);
            });
        })
    );
    return;
  }
  
  // Estratégia: Stale While Revalidate para APIs
  if (API_URLS.some(apiUrl => url.pathname.startsWith(apiUrl))) {
    event.respondWith(
      caches.open(CACHE_NAME)
        .then(cache => {
          return cache.match(request)
            .then(response => {
              // Busca atualização em background
              const fetchPromise = fetch(request)
                .then(networkResponse => {
                  if (networkResponse.status === 200) {
                    cache.put(request, networkResponse.clone());
                  }
                  return networkResponse;
                })
                .catch(() => {
                  console.log('🔌 API offline, usando cache');
                });
              
              // Retorna cache imediatamente se disponível, senão espera rede
              return response || fetchPromise;
            });
        })
    );
    return;
  }
});

// Notificações Push
self.addEventListener('push', event => {
  console.log('🔔 Notificação push recebida');
  
  if (!event.data) return;
  
  const data = event.data.json();
  const options = {
    body: data.body || 'Nova atualização no IA Financeiro!',
    icon: '/static/images/icon-192x192.png',
    badge: '/static/images/badge-72x72.png',
    vibrate: [200, 100, 200],
    tag: data.tag || 'ia-financeiro',
    renotify: true,
    requireInteraction: true,
    actions: [
      {
        action: 'view',
        title: '👁️ Visualizar',
        icon: '/static/images/action-view.png'
      },
      {
        action: 'dismiss',
        title: '✖️ Dispensar',
        icon: '/static/images/action-close.png'
      }
    ],
    data: {
      url: data.url || '/dashboard/',
      timestamp: Date.now()
    }
  };
  
  event.waitUntil(
    self.registration.showNotification(
      data.title || '🏦 IA Financeiro', 
      options
    )
  );
});

// Clique em notificação
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  const action = event.action;
  const data = event.notification.data;
  
  if (action === 'dismiss') {
    return;
  }
  
  // Abre ou foca na janela do app
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(clients => {
        // Se já tem uma janela aberta, foca nela
        for (const client of clients) {
          if (client.url.includes(self.location.origin)) {
            if (action === 'view' && data.url) {
              client.navigate(data.url);
            }
            return client.focus();
          }
        }
        
        // Se não tem janela aberta, abre nova
        const targetUrl = (action === 'view' && data.url) ? data.url : '/dashboard/';
        return clients.openWindow(targetUrl);
      })
  );
});

// Sincronização em background
self.addEventListener('sync', event => {
  console.log('🔄 Sincronização em background:', event.tag);
  
  if (event.tag === 'sync-transactions') {
    event.waitUntil(syncTransactions());
  }
  
  if (event.tag === 'sync-goals') {
    event.waitUntil(syncGoals());
  }
});

// Funções de sincronização
async function syncTransactions() {
  try {
    // Busca transações pendentes no IndexedDB local
    const pendingTransactions = await getPendingTransactions();
    
    for (const transaction of pendingTransactions) {
      try {
        await fetch('/api/transactions/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(transaction)
        });
        
        // Remove da lista de pendentes
        await removePendingTransaction(transaction.id);
        console.log('✅ Transação sincronizada:', transaction.id);
        
      } catch (error) {
        console.log('❌ Erro ao sincronizar transação:', error);
      }
    }
  } catch (error) {
    console.log('❌ Erro na sincronização:', error);
  }
}

async function syncGoals() {
  try {
    // Implementar sincronização de metas
    console.log('🎯 Sincronizando metas...');
  } catch (error) {
    console.log('❌ Erro ao sincronizar metas:', error);
  }
}

// Funções auxiliares para IndexedDB (implementar conforme necessário)
async function getPendingTransactions() {
  // Implementar busca no IndexedDB
  return [];
}

async function removePendingTransaction(id) {
  // Implementar remoção do IndexedDB
}

// Log de inicialização
console.log('🚀 IA Financeiro PWA Service Worker carregado!');
console.log('📱 Versão:', CACHE_NAME);
console.log('🇧🇷 Desenvolvido no Brasil com tecnologia nacional!');