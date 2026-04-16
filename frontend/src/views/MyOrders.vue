<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useShopStore } from '@/data/shopStore'
import { useAuthStore } from '@/data/authStore'
import CommonNavbar from '@/components/CommonNavbar.vue'

import NotificationBell from '@/components/NotificationBell.vue'

const router = useRouter()
const store = useShopStore()
const authStore = useAuthStore()

const orders = computed(() => store.state.myOrders)
const isLoading = computed(() => store.state.ordersLoading)

const unreadCount = computed(() => 
  orders.value.filter(o => o.id > store.state.lastSeenOrderId && o.status !== 'CREATED').length
)

const updatingOrderId = ref<number | null>(null)
const successMsg = ref<string | null>(null)
const errorMsg = ref<string | null>(null)

onMounted(async () => {
  if (!authStore.token) {
    router.push('/login')
    return
  }
  if (authStore.user?.role !== 'BUYER') {
    router.push('/')
    return
  }
  await store.fetchMyOrders()
  store.markOrdersSeen('BUYER')
})

const statusLabel: Record<string, { text: string; icon: string; class: string }> = {
  CREATED: { text: 'На рассмотрении', icon: '⏳', class: 'status-created' },
  CONFIRMED: { text: 'Принят в работу', icon: '✅', class: 'status-confirmed' },
  IN_PROGRESS: { text: 'В пути', icon: '🚚', class: 'status-inprogress' },
  COMPLETED: { text: 'Доставлен', icon: '📦', class: 'status-completed' },
  CANCELLED: { text: 'Отклонён поставщиком', icon: '❌', class: 'status-cancelled' },
}

const getStatusInfo = (status: string) =>
  statusLabel[status] || { text: status, icon: '📄', class: 'status-created' }

const formatDate = (dt: string) => {
  const d = new Date(dt)
  return d.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatAmount = (amount: number | null) => {
  if (amount === null) return '—'
  return amount.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' ₽'
}

const markDelivered = async (orderId: number) => {
  if (updatingOrderId.value) return
  updatingOrderId.value = orderId
  errorMsg.value = null
  try {
    const updated = await store.updateOrderStatus(orderId, 'COMPLETED')
    if (updated) {
      const idx = store.state.myOrders.findIndex(o => o.id === orderId)
      if (idx !== -1) store.state.myOrders[idx] = updated
      successMsg.value = `Заказ #${orderId} успешно получен! Спасибо за покупку.`
      setTimeout(() => { successMsg.value = null }, 5000)
    }
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Ошибка при обновлении статуса'
  } finally {
    updatingOrderId.value = null
  }
}
</script>

<template>
  <div class="page">
    <CommonNavbar />

    <main class="page-main">
      <div class="page-header">
        <div class="title-wrapper">
          <h1 class="page-title">Мои заказы</h1>
          <NotificationBell :count="unreadCount" />
        </div>
        <p class="page-count" v-if="!isLoading">Всего: {{ orders.length }}</p>
      </div>

      <!-- Toast -->
      <TransitionGroup name="toast">
        <div v-if="successMsg" key="success" class="toast toast-success">
          <span class="t-icon">✨</span>
          {{ successMsg }}
        </div>
        <div v-if="errorMsg" key="error" class="toast toast-error">
          <span class="t-icon">⚠️</span>
          {{ errorMsg }}
        </div>
      </TransitionGroup>

      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Загрузка вашей истории заказов...</p>
      </div>

      <div v-else-if="orders.length === 0" class="empty-state">
        <div class="empty-illustration">📭</div>
        <h2>У вас пока нет заказов</h2>
        <p>Время наполнить корзину свежими продуктами!</p>
        <router-link to="/catalog" class="btn-catalog">В каталог</router-link>
      </div>

      <div v-else class="orders-grid">
        <div
          v-for="order in orders"
          :key="order.id"
          class="order-card"
          :class="{ 
            'order-card--cancelled': order.status === 'CANCELLED', 
            'order-card--completed': order.status === 'COMPLETED' 
          }"
        >
          <div class="card-header">
            <div class="order-meta">
              <span class="order-number">Заказ #{{ order.id }}</span>
              <span class="order-date">{{ formatDate(order.created_at) }}</span>
            </div>
            <div class="status-badge" :class="getStatusInfo(order.status).class">
              <span class="badge-icon">{{ getStatusInfo(order.status).icon }}</span>
              {{ getStatusInfo(order.status).text }}
            </div>
          </div>

          <div class="card-body">
            <div class="supplier-info">
              <span class="info-label">Поставщик</span>
              <span class="info-value">🏭 {{ order.seller_enterprise?.short_name }}</span>
            </div>

            <!-- Items list -->
            <div class="order-content">
              <div v-for="item in order.items" :key="item.id" class="item-row">
                <span class="item-name">{{ item.product?.name || `Товар #${item.product_id}` }}</span>
                <span class="item-dots"></span>
                <span class="item-vals">
                  <span class="item-qty">{{ item.quantity }} кг</span>
                  <span class="item-price">{{ (item.price * item.quantity).toFixed(0) }} ₽</span>
                </span>
              </div>
            </div>

            <div class="order-total">
              <span class="total-label">Итоговая сумма</span>
              <span class="total-value">{{ formatAmount(order.total_amount) }}</span>
            </div>
          </div>

          <div class="card-footer">
            <template v-if="order.status === 'CONFIRMED' || order.status === 'IN_PROGRESS'">
              <button
                class="btn-delivered"
                @click="markDelivered(order.id)"
                :disabled="updatingOrderId === order.id"
              >
                <span v-if="updatingOrderId === order.id" class="loading-sm"></span>
                {{ updatingOrderId === order.id ? 'Обновляем...' : '📬 Заказ получен' }}
              </button>
              <p class="footer-hint" v-if="order.status === 'CONFIRMED'">
                Нажмите, когда товар будет у вас
              </p>
            </template>
            
            <div v-else-if="order.status === 'COMPLETED'" class="note-success">
              ✅ Сделка успешно завершена
            </div>
            <div v-else-if="order.status === 'CANCELLED'" class="note-error">
              ❌ Заказ был отменён
            </div>
            <div v-else class="note-pending">
              ⏳ Ожидайте подтверждения от поставщика
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background-color: #f8f6f0;
  color: #2e3524;
  font-family: 'Inter', system-ui, sans-serif;
}

.page-main {
  max-width: 800px;
  margin: 0 auto;
  padding: 3rem 1.5rem 6rem;
}

.page-header {
  margin-bottom: 2.5rem;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.page-title {
  font-size: 2rem;
  font-weight: 800;
  color: #3f4a2f;
  margin: 0;
}

.title-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.page-count {
  color: #6b7280;
  font-weight: 500;
}

/* Toast */
.toast {
  position: fixed;
  top: 90px;
  right: 2rem;
  background: white;
  padding: 1rem 1.75rem;
  border-radius: 16px;
  box-shadow: 0 12px 30px rgba(0,0,0,0.12);
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
  border: 1px solid rgba(0,0,0,0.05);
}

.toast-success { color: #059669; border-left: 5px solid #10b981; }
.toast-error { color: #dc2626; border-left: 5px solid #ef4444; }

.toast-enter-active, .toast-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.toast-enter-from { opacity: 0; transform: translateX(30px); }
.toast-leave-to { opacity: 0; transform: scale(0.95); }

/* Grid */
.orders-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.order-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.order-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.06);
}

.order-card--cancelled { opacity: 0.8; border-color: #fee2e2; }
.order-card--completed { background: #fdfdfd; border-color: #d1fae5; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.order-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.order-number {
  font-size: 1.1rem;
  font-weight: 800;
  color: #111827;
}

.order-date {
  font-size: 0.82rem;
  color: #9ca3af;
  font-weight: 500;
}

.status-badge {
  padding: 0.4rem 0.85rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  white-space: nowrap;
}

.status-created { background: #fef3c7; color: #92400e; }
.status-confirmed { background: #d1fae5; color: #065f46; }
.status-inprogress { background: #dbeafe; color: #1e40af; }
.status-completed { background: #d1fae5; color: #065f46; }
.status-cancelled { background: #fee2e2; color: #991b1b; }

.card-body {
  border-top: 1px solid #f3f4f6;
  padding-top: 1.25rem;
}

.supplier-info {
  margin-bottom: 1.25rem;
}

.info-label {
  display: block;
  font-size: 0.72rem;
  font-weight: 700;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.info-value {
  font-weight: 700;
  color: #374151;
}

.order-content {
  background: #f9fafb;
  border-radius: 14px;
  padding: 1rem;
  margin-bottom: 1.25rem;
}

.item-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}

.item-row:last-child { margin-bottom: 0; }

.item-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #4b5563;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 1;
}

.item-dots {
  flex-grow: 1;
  border-bottom: 1px dashed #d1d5db;
  height: 10px;
}

.item-vals {
  display: flex;
  gap: 1rem;
  flex-shrink: 0;
}

.item-qty { font-size: 0.85rem; color: #6b7280; font-weight: 500; }
.item-price { font-size: 0.9rem; font-weight: 700; color: #3f4a2f; }

.order-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.5rem;
}

.total-label { font-size: 0.9rem; font-weight: 600; color: #6b7280; }
.total-value { font-size: 1.35rem; font-weight: 900; color: #059669; }

.card-footer {
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid #f3f4f6;
  text-align: right;
}

.btn-delivered {
  background: #3f4a2f;
  color: white;
  border: none;
  padding: 0.75rem 1.75rem;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-delivered:hover:not(:disabled) {
  background: #4a5638;
  box-shadow: 0 4px 15px rgba(63, 74, 47, 0.25);
}

.footer-hint {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.5rem;
}

.note-success { color: #059669; font-weight: 700; font-size: 0.9rem; }
.note-error { color: #dc2626; font-weight: 600; font-size: 0.9rem; }
.note-pending { color: #92400e; font-size: 0.9rem; font-weight: 500; font-style: italic; }

/* Empty state */
.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  background: white;
  border-radius: 30px;
  border: 1px solid #e5e7eb;
}

.empty-illustration { font-size: 4rem; margin-bottom: 2rem; }
.empty-state h2 { font-weight: 800; color: #3f4a2f; }
.empty-state p { color: #6b7280; margin-bottom: 2.5rem; }

.btn-catalog {
  background: #3f4a2f;
  color: white;
  text-decoration: none;
  padding: 0.85rem 2.5rem;
  border-radius: 999px;
  font-weight: 700;
  transition: all 0.2s;
}

.btn-catalog:hover { background: #4a5638; }

/* Loading */
.loading-state {
  text-align: center;
  padding: 4rem 0;
  color: #9ca3af;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f4f6;
  border-top-color: #3f4a2f;
  border-radius: 50%;
  animation: spin 1s infinite linear;
  margin: 0 auto 1.5rem;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
