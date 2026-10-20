<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'

type NotificationItem = {
  id: string
  title: string
  text: string
  kind: 'order' | 'message' | 'system'
  date: string
}

const router = useRouter()
const authStore = useAuthStore()
const store = useShopStore()
const notifications = ref<NotificationItem[]>([])
const loading = ref(false)

const formatDate = (value: string) =>
  new Date(value).toLocaleString('ru-RU', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })

const buildOrderNotifications = () => {
  const source = authStore.user?.role === 'SUPPLIER' ? store.state.supplierOrders : store.state.myOrders

  return source.slice(0, 8).map((order) => ({
    id: `order-${order.id}`,
    title: `Заказ #${order.id}`,
    text: `Статус: ${order.status}. Сумма: ${order.total_amount ?? 0} ₽.`,
    kind: 'order' as const,
    date: order.created_at,
  }))
}

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }

  loading.value = true
  try {
    if (authStore.user?.role === 'SUPPLIER') {
      await store.fetchSupplierOrders()
    } else {
      await store.fetchMyOrders()
    }

    const chatsResponse = await api.get('/chats')
    const chatNotifications = (chatsResponse.data || []).slice(0, 4).map((chat: any) => ({
      id: `chat-${chat.id}`,
      title: `Чат #${chat.id}`,
      text: chat.last_message?.content ? `Последнее сообщение: ${chat.last_message.content}` : 'В чате пока нет сообщений.',
      kind: 'message' as const,
      date: chat.last_message?.created_at || chat.created_at,
    }))

    notifications.value = [
      {
        id: 'system-1',
        title: 'Система',
        text: 'Все основные уведомления теперь собираются в одном месте.',
        kind: 'system',
        date: new Date().toISOString(),
      },
      ...buildOrderNotifications(),
      ...chatNotifications,
    ].sort((a, b) => +new Date(b.date) - +new Date(a.date))
  } finally {
    loading.value = false
  }
})

const badgeLabel = {
  order: 'Заказ',
  message: 'Чат',
  system: 'Система',
}
</script>

<template>
  <main class="notifications-page">
    <section class="hero">
      <div>
        <p class="eyebrow">Уведомления</p>
        <h1>Лента событий</h1>
        <p class="hero-lead">Здесь собраны заказы, новые сообщения и системные подсказки.</p>
      </div>
      <router-link to="/chat" class="primary-btn">Перейти в чат</router-link>
    </section>

    <div class="feed">
      <div v-if="loading" class="state-box">Загрузка уведомлений...</div>

      <div v-else-if="notifications.length === 0" class="state-box">
        У вас пока нет уведомлений.
      </div>

      <div v-else class="list">
        <article v-for="item in notifications" :key="item.id" class="notify-card">
          <div class="notify-head">
            <span class="badge" :class="item.kind">{{ badgeLabel[item.kind] }}</span>
            <time>{{ formatDate(item.date) }}</time>
          </div>
          <div class="notify-body">
            <h2>{{ item.title }}</h2>
            <p>{{ item.text }}</p>
          </div>
        </article>
      </div>
    </div>
  </main>
</template>

<style scoped>
.notifications-page {
  display: grid;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
  color: var(--sl-ink);
}

/* ===== ШАПКА ===== */
.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem 2rem;
  padding: clamp(1.25rem, 3vw, 2rem);
  border-bottom: 1px solid var(--sl-line);
}

.eyebrow {
  margin: 0 0 0.6rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

.hero h1 {
  margin: 0;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  color: var(--sl-ink);
}

.hero-lead {
  margin: 0.75rem 0 0;
  max-width: 60ch;
  color: var(--sl-muted);
}

.primary-btn {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.7rem 1.2rem;
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
  border-radius: 0;
  font-weight: 700;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.primary-btn:hover {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.primary-btn:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

/* ===== ЛЕНТА ===== */
.feed {
  padding: clamp(1.25rem, 3vw, 2rem);
}

.state-box {
  padding: 1.25rem;
  background: #fff;
  border: 1px solid var(--sl-line);
  color: var(--sl-muted);
}

.list {
  display: grid;
  gap: 1px;
  background: var(--sl-line);
  border: 1px solid var(--sl-line);
}

.notify-card {
  display: grid;
  grid-template-columns: 170px minmax(0, 1fr);
  gap: 0.5rem 1.5rem;
  padding: 1.1rem 1.25rem;
  background: #fff;
  transition: background 0.2s ease;
}

.notify-card:hover {
  background: var(--sl-paper);
}

.notify-head {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--sl-muted);
}

.badge {
  padding: 0.2rem 0.5rem;
  border-radius: 0;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  border: 1px solid transparent;
}

.badge.order {
  background: var(--sl-ink);
  color: var(--sl-lime);
}

.badge.message {
  background: var(--sl-lime);
  color: var(--sl-ink);
}

.badge.system {
  background: var(--sl-paper);
  border-color: var(--sl-line);
  color: var(--sl-ink);
}

.notify-body {
  min-width: 0;
}

.notify-card h2 {
  margin: 0 0 0.3rem;
  font-family: inherit;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0;
  color: var(--sl-ink);
}

.notify-card p {
  margin: 0;
  color: var(--sl-muted);
  overflow-wrap: anywhere;
}

@media (max-width: 900px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 600px) {
  .notify-card {
    grid-template-columns: minmax(0, 1fr);
  }

  .notify-head {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
