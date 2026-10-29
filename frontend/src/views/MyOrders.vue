<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useShopStore } from '@/stores/shopStore'
import { useAuthStore } from '@/stores/authStore'
import { getApiErrorMessage } from '@/services/apiClient'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { ACTIVE_ORDER_STATUSES, type OrderStatusCode } from '@/utils/orderStatus'
import { formatNumber, pluralize } from '@/utils/format'
import { AppButton, AppTabs, EmptyState, ErrorState, LoadingState, PageHeader, type TabItem } from '@/components/ui'
import NotificationBell from '@/components/NotificationBell.vue'
import BuyerOrderCard from '@/components/orders/BuyerOrderCard.vue'
import OrderTemplateModal from '@/components/orders/OrderTemplateModal.vue'

const router = useRouter()
const store = useShopStore()
const authStore = useAuthStore()
const toast = useToast()
const { confirm } = useConfirm()

const orders = computed(() => store.state.myOrders)
const isLoading = computed(() => store.state.ordersLoading)

const unreadCount = computed(() =>
  orders.value.filter(o => o.id > store.state.lastSeenOrderId && o.status !== 'CREATED').length
)

const updatingOrderId = ref<number | null>(null)

/* ошибка загрузки (store пишет её в state.error) — показываем, только если заказов нет */
const loadError = ref<string | null>(null)
const isRetrying = ref(false)

const loadOrders = async () => {
  store.state.ordersLoading = true
  await Promise.all([
    store.fetchMyOrders(),
    store.fetchProducts()
  ])
  loadError.value = store.state.error
  store.markOrdersSeen('BUYER')
}

const retryLoad = async () => {
  isRetrying.value = true
  try {
    await loadOrders()
  } finally {
    isRetrying.value = false
  }
}

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }
  if (authStore.user?.role !== 'BUYER') {
    router.push('/')
    return
  }
  await loadOrders()
})

/* ===== фильтр по статусам (по уже загруженным заказам) ===== */
type OrdersFilter = 'all' | 'active' | 'completed' | 'cancelled'

const activeFilter = ref<OrdersFilter>('all')

const matchesFilter = (status: string, filter: OrdersFilter) => {
  if (filter === 'active') return ACTIVE_ORDER_STATUSES.includes(status as OrderStatusCode)
  if (filter === 'completed') return status === 'COMPLETED'
  if (filter === 'cancelled') return status === 'CANCELLED'
  return true
}

const filterTabs = computed<TabItem<OrdersFilter>[]>(() => {
  const count = (filter: OrdersFilter) => orders.value.filter((o) => matchesFilter(o.status, filter)).length
  return [
    { value: 'all', label: 'Все', count: orders.value.length },
    { value: 'active', label: 'Активные', count: count('active') },
    { value: 'completed', label: 'Завершённые', count: count('completed') },
    { value: 'cancelled', label: 'Отменённые', count: count('cancelled') },
  ]
})

const filteredOrders = computed(() => orders.value.filter((o) => matchesFilter(o.status, activeFilter.value)))

const ordersSummary = computed(() => {
  const total = orders.value.length
  return `Всего ${formatNumber(total)} ${pluralize(total, ['заказ', 'заказа', 'заказов'])}`
})

/* ===== шаблон заказа ===== */
const showTemplateModal = ref(false)
const isCheckingOut = ref(false)

const templateItems = computed(() => {
  if (!store.state.orderTemplate) return []
  return store.state.orderTemplate.map(item => {
    const product = store.state.products.find(p => p.id === item.product_id)
    return {
      ...item,
      product
    }
  }).filter(item => !!item.product)
})

const templateTotal = computed(() => {
  return templateItems.value.reduce((sum, item) => {
    return sum + (item.product?.price || 0) * item.quantity
  }, 0)
})

const handleCheckoutTemplate = async () => {
  if (isCheckingOut.value) return
  isCheckingOut.value = true
  try {
    const result = await store.checkoutWithItems(store.state.orderTemplate || [])
    if (result.orders.length > 0) {
      toast.success('Шаблон успешно оформлен', `Создано заказов: ${result.orders.length}`)
      showTemplateModal.value = false
    }
  } catch (err: unknown) {
    toast.error('Не удалось оформить шаблон', getApiErrorMessage(err, 'Ошибка при оформлении шаблона'))
  } finally {
    isCheckingOut.value = false
  }
}

const handleDeleteTemplate = async () => {
  const confirmed = await confirm({
    title: 'Удалить шаблон заказа?',
    message: 'Вы уверены, что хотите удалить этот шаблон?',
    confirmLabel: 'Удалить',
    tone: 'danger',
  })
  if (confirmed) {
    store.deleteOrderTemplate()
    showTemplateModal.value = false
  }
}

/* ===== «Заказ получен» ===== */
const markDelivered = async (orderId: number) => {
  if (updatingOrderId.value) return
  updatingOrderId.value = orderId
  try {
    const updated = await store.updateOrderStatus(orderId, 'COMPLETED')
    if (updated) {
      const idx = store.state.myOrders.findIndex(o => o.id === orderId)
      if (idx !== -1) store.state.myOrders[idx] = updated
      toast.success(`Заказ №${orderId} получен`, 'Спасибо за покупку!')
    }
  } catch (err: unknown) {
    toast.error('Не удалось обновить статус', getApiErrorMessage(err, 'Ошибка при обновлении статуса'))
  } finally {
    updatingOrderId.value = null
  }
}
</script>

<template>
  <div class="page">
    <PageHeader
      title="Мои заказы"
      eyebrow="Кабинет · Заказы"
      :description="isLoading ? 'Загружаем историю заказов…' : ordersSummary"
    >
      <template #actions>
        <AppButton
          v-if="store.state.orderTemplate"
          variant="secondary"
          icon="clipboard-list"
          @click="showTemplateModal = true"
        >
          Использовать шаблон
        </AppButton>
        <NotificationBell :count="unreadCount" class="page__bell" />
      </template>
    </PageHeader>

    <LoadingState v-if="isLoading && !isRetrying" variant="skeleton" :rows="4" label="Загрузка вашей истории заказов…" />

    <ErrorState
      v-else-if="loadError && orders.length === 0"
      :message="loadError"
      :retrying="isRetrying"
      @retry="retryLoad"
    />

    <EmptyState
      v-else-if="orders.length === 0"
      icon="clipboard-list"
      title="У вас пока нет заказов"
      description="Время наполнить корзину свежими продуктами!"
    >
      <AppButton to="/catalog" icon="store">В каталог</AppButton>
    </EmptyState>

    <template v-else>
      <div class="page__toolbar">
        <AppTabs v-model="activeFilter" :items="filterTabs" aria-label="Фильтр заказов по статусу" />
      </div>

      <EmptyState
        v-if="filteredOrders.length === 0"
        compact
        icon="inbox"
        title="Нет заказов с таким статусом"
        description="Выберите другую вкладку, чтобы увидеть остальные заказы."
      >
        <AppButton variant="secondary" size="sm" @click="activeFilter = 'all'">Показать все</AppButton>
      </EmptyState>

      <div v-else class="orders" role="list">
        <div v-for="order in filteredOrders" :key="order.id" role="listitem">
          <BuyerOrderCard
            :order="order"
            :updating="updatingOrderId === order.id"
            :locked="updatingOrderId !== null"
            @delivered="markDelivered"
          />
        </div>
      </div>
    </template>

    <OrderTemplateModal
      v-model:open="showTemplateModal"
      :items="templateItems"
      :total="templateTotal"
      :checking-out="isCheckingOut"
      @checkout="handleCheckoutTemplate"
      @delete="handleDeleteTemplate"
    />
  </div>
</template>

<style scoped>
.page {
  display: grid;
  gap: 1.5rem;
  min-width: 0;
}

.page__toolbar {
  display: flex;
  min-width: 0;
}

.orders {
  display: grid;
  gap: 1rem;
}

@media (max-width: 640px) {
  /* PageHeader растягивает действия на телефоне — колокольчик оставляем квадратным */
  .page .page__bell {
    flex: 0 0 auto;
  }
}
</style>
