<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { getApiErrorMessage } from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'
import {
  AppBadge,
  AppButton,
  AppIcon,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
  StatusBadge,
} from '@/components/ui'
import type { IconName } from '@/components/ui'
import { formatDate, formatPrice, pluralize } from '@/utils/format'

type NotificationItem = {
  id: string
  title: string
  text: string
  kind: 'order' | 'message' | 'system'
  date: string
  /** код статуса заказа — для бейджа */
  status?: string
}

const router = useRouter()
const authStore = useAuthStore()
const store = useShopStore()
const notifications = ref<NotificationItem[]>([])
const loading = ref(false)
const error = ref('')

const perspective = authStore.user?.role === 'SUPPLIER' ? 'supplier' : 'buyer'

const buildOrderNotifications = () => {
  const source = authStore.user?.role === 'SUPPLIER' ? store.state.supplierOrders : store.state.myOrders

  return source.slice(0, 8).map((order) => ({
    id: `order-${order.id}`,
    title: `Заказ #${order.id}`,
    text: `Сумма заказа: ${formatPrice(order.total_amount ?? 0)}`,
    kind: 'order' as const,
    date: order.created_at,
    status: order.status,
  }))
}

const loadNotifications = async () => {
  loading.value = true
  error.value = ''
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
        kind: 'system' as const,
        date: new Date().toISOString(),
      },
      ...buildOrderNotifications(),
      ...chatNotifications,
    ].sort((a, b) => +new Date(b.date) - +new Date(a.date))
  } catch (e) {
    error.value = getApiErrorMessage(e, 'Не удалось загрузить уведомления')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }
  loadNotifications()
})

const KIND_META: Record<
  NotificationItem['kind'],
  { label: string; icon: IconName; tone: 'info' | 'accent' | 'neutral'; to?: string; action?: string }
> = {
  order: { label: 'Заказ', icon: 'package', tone: 'info', to: '/cabinet/orders', action: 'К заказам' },
  message: { label: 'Чат', icon: 'message', tone: 'accent', to: '/cabinet/chat', action: 'Открыть чат' },
  system: { label: 'Система', icon: 'bell', tone: 'neutral' },
}
</script>

<template>
  <div class="notifications">
    <PageHeader
      eyebrow="Уведомления"
      title="Лента событий"
      description="Здесь собраны заказы, новые сообщения и системные подсказки."
    >
      <template #actions>
        <AppButton to="/cabinet/chat" icon="message">Перейти в чат</AppButton>
      </template>
    </PageHeader>

    <LoadingState v-if="loading && notifications.length === 0" variant="skeleton" :rows="5" label="Загрузка уведомлений…" />

    <ErrorState v-else-if="error" :message="error" :retrying="loading" @retry="loadNotifications" />

    <div v-else-if="notifications.length === 0" class="ui-card ui-card--pad">
      <EmptyState icon="bell" title="У вас пока нет уведомлений" description="Новые заказы и сообщения появятся здесь." />
    </div>

    <section v-else class="feed ui-card" aria-labelledby="feed-title">
      <header class="feed__head">
        <h2 id="feed-title" class="feed__title">Последние события</h2>
        <span class="ui-muted feed__count">
          <span class="ui-num">{{ notifications.length }}</span>
          {{ pluralize(notifications.length, ['событие', 'события', 'событий']) }}
        </span>
      </header>

      <ul class="feed__list">
        <li v-for="item in notifications" :key="item.id" class="note" :class="`note--${item.kind}`">
          <span class="note__icon" aria-hidden="true">
            <AppIcon :name="KIND_META[item.kind].icon" :size="20" />
          </span>

          <div class="note__body">
            <div class="note__top">
              <h3 class="note__title">{{ item.title }}</h3>
              <AppBadge :tone="KIND_META[item.kind].tone" size="sm">{{ KIND_META[item.kind].label }}</AppBadge>
              <StatusBadge v-if="item.status" :status="item.status" :perspective="perspective" />
            </div>
            <p class="note__text">{{ item.text }}</p>
          </div>

          <div class="note__side">
            <time class="note__time ui-num" :datetime="item.date">{{ formatDate(item.date, 'datetime') }}</time>
            <AppButton
              v-if="KIND_META[item.kind].to"
              :to="KIND_META[item.kind].to"
              variant="ghost"
              size="sm"
              icon-right="chevron-right"
            >
              {{ KIND_META[item.kind].action }}
            </AppButton>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>

<style scoped>
.notifications {
  display: grid;
  gap: 1.5rem;
  min-width: 0;
}

.feed {
  overflow: hidden;
}

.feed__head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem 1rem;
  padding: 1.1rem clamp(1.1rem, 2.5vw, 1.5rem);
  border-bottom: 1px solid var(--c-border);
}

.feed__title {
  font-size: var(--fs-lg);
}

.feed__count {
  font-size: var(--fs-sm);
}

.feed__list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.note {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: start;
  gap: 0.9rem;
  padding: 1rem clamp(1.1rem, 2.5vw, 1.5rem);
  border-bottom: 1px solid var(--c-border);
  transition: background var(--dur) var(--ease);
}

.note:last-child {
  border-bottom: none;
}

.note:hover {
  background: var(--c-surface-2);
}

.note__icon {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: var(--r-md);
  background: var(--c-surface-sunken);
  color: var(--c-text-2);
}

.note--order .note__icon {
  background: var(--c-info-bg);
  color: var(--c-info);
}

.note--message .note__icon {
  background: var(--c-accent-50);
  color: var(--c-accent-700);
}

.note__body {
  display: grid;
  gap: 0.25rem;
  min-width: 0;
}

.note__top {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem 0.5rem;
}

.note__title {
  font-size: var(--fs-md);
  letter-spacing: -0.01em;
}

.note__text {
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  overflow-wrap: anywhere;
}

.note__side {
  display: grid;
  justify-items: end;
  gap: 0.25rem;
}

.note__time {
  color: var(--c-muted);
  font-size: var(--fs-xs);
  white-space: nowrap;
  padding-top: 0.2rem;
}

@media (max-width: 640px) {
  .note {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .note__side {
    grid-column: 2;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
  }

  .note__time {
    padding-top: 0;
  }
}
</style>
