<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useShopStore } from '@/stores/shopStore'
import { useAuthStore } from '@/stores/authStore'
import { getApiErrorMessage } from '@/services/apiClient'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { AppBadge, AppButton, AppIcon, EmptyState, LoadingState, PageHeader, StatusBadge } from '@/components/ui'
import type { IconName } from '@/components/ui'
import SupplierOrderCard from '@/components/orders/SupplierOrderCard.vue'
import { formatDate, formatNumber, formatPrice } from '@/utils/format'

import NotificationBell from '@/components/NotificationBell.vue'

const router = useRouter()
const store = useShopStore()
const authStore = useAuthStore()
const toast = useToast()
const { confirm } = useConfirm()

const orders = computed(() => store.state.supplierOrders)
const isLoading = computed(() => store.state.ordersLoading)

const unreadCount = computed(() =>
  orders.value.filter(o => o.id > store.state.lastSeenOrderId).length
)

const updatingOrderId = ref<number | null>(null)
/* какое действие сейчас выполняется — чтобы показать загрузку на нужной кнопке */
const updatingAction = ref<'confirm' | 'reject' | null>(null)

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }
  if (authStore.user?.role !== 'SUPPLIER') {
    router.push('/')
    return
  }
  await store.fetchSupplierOrders()
  // Mark as seen once loaded
  store.markOrdersSeen('SUPPLIER')
})

const pendingOrders = computed(() =>
  orders.value.filter(o => o.status === 'CREATED')
)
const activeOrders = computed(() =>
  orders.value.filter(o => o.status === 'CONFIRMED' || o.status === 'IN_PROGRESS')
)
const historyOrders = computed(() =>
  orders.value.filter(o => o.status === 'COMPLETED' || o.status === 'CANCELLED')
)

const stats = computed<{ label: string; value: number; icon: IconName; highlight: boolean }[]>(() => [
  { label: 'Новые запросы', value: pendingOrders.value.length, icon: 'inbox', highlight: pendingOrders.value.length > 0 },
  { label: 'В работе', value: activeOrders.value.length, icon: 'truck', highlight: false },
  { label: 'Завершённые и отклонённые', value: historyOrders.value.length, icon: 'check-circle', highlight: false },
])

const confirmOrder = async (orderId: number) => {
  if (updatingOrderId.value) return
  updatingOrderId.value = orderId
  updatingAction.value = 'confirm'
  try {
    const updated = await store.updateOrderStatus(orderId, 'CONFIRMED')
    if (updated) {
      const idx = store.state.supplierOrders.findIndex(o => o.id === orderId)
      if (idx !== -1) store.state.supplierOrders[idx] = updated
      toast.success(`Заказ №${orderId} принят в работу`, 'Остатки на складе обновлены.')
    }
  } catch (err) {
    toast.error('Не удалось принять заказ', getApiErrorMessage(err, 'Ошибка при подтверждении'))
  } finally {
    updatingOrderId.value = null
    updatingAction.value = null
  }
}

const rejectOrder = async (orderId: number) => {
  const accepted = await confirm({
    title: `Отклонить заказ №${orderId}?`,
    message: 'Заказ перейдёт в раздел «Завершённые» со статусом «Отклонён».',
    confirmLabel: 'Отклонить',
    tone: 'danger',
  })
  if (!accepted) return
  if (updatingOrderId.value) return
  updatingOrderId.value = orderId
  updatingAction.value = 'reject'
  try {
    const updated = await store.updateOrderStatus(orderId, 'CANCELLED')
    if (updated) {
      const idx = store.state.supplierOrders.findIndex(o => o.id === orderId)
      if (idx !== -1) store.state.supplierOrders[idx] = updated
      toast.success(`Заказ №${orderId} отклонён`)
    }
  } catch (err) {
    toast.error('Не удалось отклонить заказ', getApiErrorMessage(err, 'Ошибка при отклонении'))
  } finally {
    updatingOrderId.value = null
    updatingAction.value = null
  }
}
</script>

<template>
  <div class="orders-page">
    <PageHeader
      eyebrow="Кабинет · Заказы"
      title="Управление заказами"
      description="Контролируйте свои продажи и остатки в реальном времени"
    >
      <template #actions>
        <div class="orders-page__bell">
          <NotificationBell :count="unreadCount" />
        </div>
      </template>
    </PageHeader>

    <LoadingState v-if="isLoading" variant="cards" :rows="3" label="Синхронизация заказов…" />

    <div v-else-if="orders.length === 0" class="ui-card">
      <EmptyState
        icon="clipboard-list"
        title="Заказов пока нет"
        description="Ваши товары ждут своих покупателей. Как только кто-то оформит заказ, он появится здесь."
      >
        <AppButton variant="secondary" icon="package" to="/cabinet/my-products">Мои товары</AppButton>
      </EmptyState>
    </div>

    <template v-else>
      <!-- СВОДКА -->
      <ul class="stats" aria-label="Сводка по заказам">
        <li
          v-for="stat in stats"
          :key="stat.label"
          class="stat ui-card"
          :class="{ 'stat--highlight': stat.highlight }"
        >
          <span class="stat__icon"><AppIcon :name="stat.icon" :size="20" /></span>
          <span class="stat__text">
            <span class="stat__value ui-num">{{ formatNumber(stat.value) }}</span>
            <span class="stat__label">{{ stat.label }}</span>
          </span>
        </li>
      </ul>

      <!-- НОВЫЕ ЗАПРОСЫ -->
      <section v-if="pendingOrders.length > 0" class="block" aria-labelledby="pending-title">
        <div class="block__head">
          <h2 id="pending-title" class="block__title">
            <span class="block__pulse" aria-hidden="true"></span>
            Новые запросы
          </h2>
          <AppBadge tone="warning" size="sm">{{ pendingOrders.length }}</AppBadge>
        </div>
        <div class="cards">
          <SupplierOrderCard v-for="order in pendingOrders" :key="order.id" :order="order" variant="new">
            <template #actions>
              <AppButton
                icon="check"
                :loading="updatingOrderId === order.id && updatingAction === 'confirm'"
                :disabled="updatingOrderId === order.id"
                @click="confirmOrder(order.id)"
              >
                Принять и списать со склада
              </AppButton>
              <AppButton
                variant="danger-ghost"
                icon="x"
                :loading="updatingOrderId === order.id && updatingAction === 'reject'"
                :disabled="updatingOrderId === order.id"
                @click="rejectOrder(order.id)"
              >
                Отклонить
              </AppButton>
            </template>
          </SupplierOrderCard>
        </div>
      </section>

      <!-- АКТИВНЫЕ -->
      <section v-if="activeOrders.length > 0" class="block" aria-labelledby="active-title">
        <div class="block__head">
          <h2 id="active-title" class="block__title">Активные сделки</h2>
          <AppBadge tone="info" size="sm">{{ activeOrders.length }}</AppBadge>
        </div>
        <div class="cards">
          <SupplierOrderCard v-for="order in activeOrders" :key="order.id" :order="order" variant="active" />
        </div>
      </section>

      <!-- ИСТОРИЯ -->
      <section v-if="historyOrders.length > 0" class="block" aria-labelledby="history-title">
        <div class="block__head">
          <h2 id="history-title" class="block__title">Завершённые</h2>
          <AppBadge tone="neutral" size="sm">{{ historyOrders.length }}</AppBadge>
        </div>
        <div class="ui-table-wrap">
          <table class="ui-table history">
            <thead>
              <tr>
                <th scope="col">Заказ</th>
                <th scope="col">Дата</th>
                <th scope="col">Покупатель</th>
                <th scope="col">Состав</th>
                <th scope="col" class="history__num">Сумма</th>
                <th scope="col">Статус</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in historyOrders" :key="order.id">
                <td class="history__id ui-num">№{{ order.id }}</td>
                <td class="history__date">{{ formatDate(order.created_at, 'datetime') }}</td>
                <td>
                  <div class="history__client">
                    <strong>{{ order.buyer_enterprise?.short_name || 'Покупатель' }}</strong>
                    <small>{{ order.buyer_enterprise?.region || 'Регион не указан' }}</small>
                  </div>
                </td>
                <td>
                  <ul class="history__items">
                    <li v-for="item in order.items" :key="item.id">
                      {{ item.product?.name || 'Товар' }}
                      <span class="ui-num">· {{ formatNumber(item.quantity) }} кг</span>
                    </li>
                  </ul>
                </td>
                <td class="history__num history__amount ui-num">{{ formatPrice(order.total_amount) }}</td>
                <td><StatusBadge :status="order.status" perspective="supplier" size="sm" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.orders-page {
  display: grid;
  gap: 1.5rem;
  min-width: 0;
}

.orders-page__bell {
  display: flex;
  justify-content: flex-end;
}

/* ===== СВОДКА ===== */
.stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  min-width: 0;
  padding: 1rem 1.15rem;
}

.stat__icon {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: var(--r-md);
  background: var(--c-surface-sunken);
  color: var(--c-text-2);
}

.stat--highlight {
  border-color: var(--c-accent-200);
}

.stat--highlight .stat__icon {
  background: var(--c-accent-50);
  color: var(--c-accent-700);
}

.stat__text {
  display: grid;
  gap: 0.15rem;
  min-width: 0;
}

.stat__value {
  font-size: var(--fs-2xl);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: var(--c-text);
}

.stat__label {
  color: var(--c-muted);
  font-size: var(--fs-sm);
  font-weight: 600;
  line-height: 1.3;
}

/* ===== БЛОКИ ===== */
.block {
  display: grid;
  gap: 1rem;
  min-width: 0;
}

.block__head {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.block__title {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  font-size: var(--fs-lg);
}

.block__pulse {
  width: 8px;
  height: 8px;
  flex: 0 0 auto;
  border-radius: var(--r-full);
  background: var(--c-accent);
  box-shadow: 0 0 0 4px var(--c-accent-100);
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 320px), 1fr));
  gap: 1rem;
}

/* ===== ТАБЛИЦА ИСТОРИИ ===== */
.history {
  min-width: 760px;
}

.history td {
  vertical-align: top;
}

.history__num {
  text-align: right;
}

.ui-table th.history__num {
  text-align: right;
}

.history__id {
  font-weight: 800;
  white-space: nowrap;
}

.history__date {
  color: var(--c-muted);
  white-space: nowrap;
}

.history__client {
  display: grid;
  gap: 0.15rem;
}

.history__client strong {
  font-weight: 700;
}

.history__client small {
  color: var(--c-muted);
  font-size: var(--fs-xs);
}

.history__items {
  display: grid;
  gap: 0.2rem;
  margin: 0;
  padding: 0;
  list-style: none;
  color: var(--c-text-2);
}

.history__items span {
  color: var(--c-muted);
  white-space: nowrap;
}

.history__amount {
  font-weight: 800;
  white-space: nowrap;
}

/* ===== АДАПТИВ ===== */
@media (max-width: 640px) {
  .stats {
    gap: 0.5rem;
  }

  .stat {
    align-items: flex-start;
    padding: 0.75rem;
  }

  .stat__icon {
    display: none;
  }

  .stat__value {
    font-size: var(--fs-xl);
  }

  .stat__label {
    font-size: var(--fs-xs);
  }
}
</style>
