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

const orders = computed(() => store.state.supplierOrders)
const isLoading = computed(() => store.state.ordersLoading)

const unreadCount = computed(() => 
  orders.value.filter(o => o.id > store.state.lastSeenOrderId).length
)

const updatingOrderId = ref<number | null>(null)
const successMsg = ref<string | null>(null)
const errorMsg = ref<string | null>(null)

onMounted(async () => {
  if (!authStore.token) {
    router.push('/login')
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

const statusLabel: Record<string, { text: string; icon: string; class: string }> = {
  CREATED: { text: 'Новый запрос', icon: '📝', class: 'status-created' },
  CONFIRMED: { text: 'Подтверждён', icon: '✅', class: 'status-confirmed' },
  IN_PROGRESS: { text: 'В процессе', icon: '🚚', class: 'status-inprogress' },
  COMPLETED: { text: 'Завершён успешно', icon: '💎', class: 'status-completed' },
  CANCELLED: { text: 'Отклонён', icon: '❌', class: 'status-cancelled' },
}

const getStatusInfo = (status: string) =>
  statusLabel[status] || { text: status, icon: '📄', class: 'status-created' }

const formatDate = (dt: string) => {
  const d = new Date(dt)
  return d.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatAmount = (amount: number | null) => {
  if (amount === null) return '—'
  return amount.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' ₽'
}

const showToast = (msg: string, isError = false) => {
  if (isError) {
    errorMsg.value = msg
    setTimeout(() => { errorMsg.value = null }, 5000)
  } else {
    successMsg.value = msg
    setTimeout(() => { successMsg.value = null }, 5000)
  }
}

const confirmOrder = async (orderId: number) => {
  if (updatingOrderId.value) return
  updatingOrderId.value = orderId
  try {
    const updated = await store.updateOrderStatus(orderId, 'CONFIRMED')
    if (updated) {
      const idx = store.state.supplierOrders.findIndex(o => o.id === orderId)
      if (idx !== -1) store.state.supplierOrders[idx] = updated
      showToast(`Заказ #${orderId} принят в работу. Остатки на складе обновлены.`)
    }
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Ошибка при подтверждении', true)
  } finally {
    updatingOrderId.value = null
  }
}

const rejectOrder = async (orderId: number) => {
  if (!confirm(`Вы уверены, что хотите отклонить заказ #${orderId}?`)) return
  if (updatingOrderId.value) return
  updatingOrderId.value = orderId
  try {
    const updated = await store.updateOrderStatus(orderId, 'CANCELLED')
    if (updated) {
      const idx = store.state.supplierOrders.findIndex(o => o.id === orderId)
      if (idx !== -1) store.state.supplierOrders[idx] = updated
      showToast(`Заказ #${orderId} отклонён.`)
    }
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Ошибка при отклонении', true)
  } finally {
    updatingOrderId.value = null
  }
}
</script>

<template>
  <div class="page">
    <CommonNavbar />

    <main class="page-main">
      <div class="glass-header">
        <div class="header-content">
          <div class="title-with-bell">
            <h1 class="page-title">Управление заказами</h1>
            <NotificationBell :count="unreadCount" />
          </div>
          <p class="page-subtitle">Контролируйте свои продажи и остатки в реальном времени</p>
        </div>
        <div class="header-stats">
          <div class="stat-card" :class="{ 'stat-card--active': pendingOrders.length > 0 }">
            <span class="stat-val">{{ pendingOrders.length }}</span>
            <span class="stat-lab">Новых</span>
          </div>
          <div class="stat-card">
            <span class="stat-val">{{ activeOrders.length }}</span>
            <span class="stat-lab">В работе</span>
          </div>
          <div class="stat-card">
            <span class="stat-val">{{ historyOrders.length }}</span>
            <span class="stat-lab">Всего</span>
          </div>
        </div>
      </div>

      <!-- Toasts -->
      <TransitionGroup name="toast">
        <div v-if="successMsg" key="success" class="toast toast-success">
          <span class="toast-icon">✨</span>
          <div class="toast-body">{{ successMsg }}</div>
        </div>
        <div v-if="errorMsg" key="error" class="toast toast-error">
          <span class="toast-icon">⚠️</span>
          <div class="toast-body">{{ errorMsg }}</div>
        </div>
      </TransitionGroup>

      <!-- Loading -->
      <div v-if="isLoading" class="loading-container">
        <div class="loader"></div>
        <p>Синхронизация данных...</p>
      </div>

      <div v-else-if="orders.length === 0" class="empty-hero">
        <div class="hero-icon">📦</div>
        <h2>Заказов пока нет</h2>
        <p>Ваши товары ждут своих покупателей. Как только кто-то оформит заказ, он появится здесь.</p>
      </div>

      <div v-else class="sections-grid">
        <!-- НОВЫЕ ЗАПРОСЫ -->
        <section v-if="pendingOrders.length > 0" class="order-section">
          <h2 class="section-heading">
            <span class="pulse-dot"></span>
            Новые поступления
          </h2>
          <div class="cards-stack">
            <div
              v-for="order in pendingOrders"
              :key="order.id"
              class="premium-card premium-card--new"
            >
              <div class="card-header">
                <div class="id-badge">Order #{{ order.id }}</div>
                <div class="date-tag">{{ formatDate(order.created_at) }}</div>
              </div>

              <div class="card-body">
                <div class="client-info">
                  <div class="avatar">🏢</div>
                  <div class="client-details">
                    <span class="client-name">{{ order.buyer_enterprise?.short_name || 'Покупатель' }}</span>
                    <span class="client-region">{{ order.buyer_enterprise?.region || 'Регион не указан' }}</span>
                  </div>
                </div>

                <div class="products-mini">
                  <div v-for="item in order.items" :key="item.id" class="mini-item">
                    <span class="m-name">{{ item.product?.name }}</span>
                    <div class="m-dots"></div>
                    <span class="m-qty">{{ item.quantity }} кг</span>
                  </div>
                </div>

                <div class="total-bar">
                  <span class="t-label">К оплате:</span>
                  <span class="t-value">{{ formatAmount(order.total_amount) }}</span>
                </div>
              </div>

              <div class="card-actions">
                <button
                  class="btn-action btn-action--confirm"
                  @click="confirmOrder(order.id)"
                  :disabled="updatingOrderId === order.id"
                >
                  <span v-if="updatingOrderId === order.id" class="spin">⌛</span>
                  <span v-else>Принять и списать со склада</span>
                </button>
                <button
                  class="btn-action btn-action--reject"
                  @click="rejectOrder(order.id)"
                  :disabled="updatingOrderId === order.id"
                >
                  Отклонить
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- АКТИВНЫЕ -->
        <section v-if="activeOrders.length > 0" class="order-section">
          <h2 class="section-heading">Активные сделки</h2>
          <div class="cards-grid">
            <div
              v-for="order in activeOrders"
              :key="order.id"
              class="premium-card"
            >
              <div class="card-header">
                <div class="status-chip" :class="getStatusInfo(order.status).class">
                  <span class="chip-icon">{{ getStatusInfo(order.status).icon }}</span>
                  {{ getStatusInfo(order.status).text }}
                </div>
                <div class="id-badge">#{{ order.id }}</div>
              </div>
              
              <div class="card-body">
                <div class="client-info">
                  <div class="avatar avatar--sm">🏢</div>
                  <div class="client-details">
                    <span class="client-name">{{ order.buyer_enterprise?.short_name }}</span>
                    <span class="client-region">{{ order.buyer_enterprise?.region }}</span>
                  </div>
                </div>

                <div class="products-mini products-mini--compact">
                  <div v-for="item in order.items" :key="item.id" class="mini-item">
                    <span class="m-name">{{ item.product?.name }}</span>
                    <div class="m-dots"></div>
                    <span class="m-qty">{{ item.quantity }} кг</span>
                  </div>
                </div>

                <div class="total-bar compact">
                  <span class="t-value">{{ formatAmount(order.total_amount) }}</span>
                </div>
              </div>
              
              <div class="card-footer">
                <div class="wait-status">
                  <span class="dots-loader"></span>
                  Ожидание подтверждения от покупателя
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- ИСТОРИЯ -->
        <section v-if="historyOrders.length > 0" class="order-section">
          <h2 class="section-heading">Завершенные</h2>
          <div class="history-table-wrapper">
            <table class="history-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Дата</th>
                  <th>Клиент</th>
                  <th>Состав</th>
                  <th>Сумма</th>
                  <th>Статус</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in historyOrders" :key="order.id" :class="order.status.toLowerCase()">
                  <td class="td-id">#{{ order.id }}</td>
                  <td class="td-date">{{ formatDate(order.created_at) }}</td>
                  <td class="td-client">
                    <div class="client-cell">
                      <strong>{{ order.buyer_enterprise?.short_name }}</strong>
                      <small>{{ order.buyer_enterprise?.region }}</small>
                    </div>
                  </td>
                  <td class="td-items">
                    <div class="items-cell">
                      <span v-for="item in order.items" :key="item.id">
                        {{ item.product?.name }} ({{ item.quantity }} кг)
                      </span>
                    </div>
                  </td>
                  <td class="td-amount">{{ formatAmount(order.total_amount) }}</td>
                  <td>
                    <span class="small-badge" :class="getStatusInfo(order.status).class">
                      {{ getStatusInfo(order.status).text }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background-color: #f7f3e9;
  background-image: 
    radial-gradient(at 0% 0%, hsla(38,39%,89%,1) 0, transparent 50%), 
    radial-gradient(at 50% 0%, hsla(84,22%,88%,1) 0, transparent 50%), 
    radial-gradient(at 100% 0%, hsla(43,36%,86%,1) 0, transparent 50%);
  color: #2c3324;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.page-main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 3rem 1.5rem 6rem;
}

/* Header */
.glass-header {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 24px;
  padding: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3.5rem;
  box-shadow: 0 8px 32px rgba(63, 74, 47, 0.05);
}

.page-title {
  font-size: 2.25rem;
  font-weight: 900;
  color: #3f4a2f;
  margin: 0 0 0.5rem;
  letter-spacing: -0.02em;
}

.page-subtitle {
  color: #6b7280;
  font-size: 1rem;
  margin: 0;
}

.title-with-bell {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.title-with-bell .page-title {
  margin-bottom: 0;
}

.header-stats {
  display: flex;
  gap: 1rem;
}

.stat-card {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 90px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.stat-card--active {
  border-color: #fbbf24;
  background: #fffbeb;
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(251, 191, 36, 0.1);
}

.stat-val {
  font-size: 1.5rem;
  font-weight: 800;
  color: #3f4a2f;
}

.stat-lab {
  font-size: 0.75rem;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Toasts */
.toast {
  position: fixed;
  top: 90px;
  right: 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.75rem;
  border-radius: 16px;
  backdrop-filter: blur(10px);
  z-index: 1000;
  box-shadow: 0 15px 35px rgba(0,0,0,0.1);
  min-width: 300px;
  border: 1px solid rgba(255,255,255,0.3);
}

.toast-success { background: rgba(209, 250, 229, 0.9); color: #065f46; }
.toast-error { background: rgba(254, 226, 226, 0.9); color: #991b1b; }

.toast-enter-active, .toast-leave-active { transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.toast-enter-from { opacity: 0; transform: translateX(50px) scale(0.9); }
.toast-leave-to { opacity: 0; transform: translateY(-20px); }

/* Sections */
.sections-grid {
  display: flex;
  flex-direction: column;
  gap: 4rem;
}

.section-heading {
  font-size: 1.35rem;
  font-weight: 800;
  color: #3f4a2f;
  margin: 0 0 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.pulse-dot {
  width: 10px;
  height: 10px;
  background: #fbbf24;
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.7);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(251, 191, 36, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(251, 191, 36, 0); }
}

/* Cards */
.cards-stack {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.premium-card {
  background: white;
  border-radius: 24px;
  border: 1px solid #e5e7eb;
  padding: 1.75rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.premium-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.06);
}

.premium-card--new {
  border-left: 6px solid #fbbf24;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.id-badge {
  font-weight: 800;
  font-size: 0.9rem;
  color: #9ca3af;
  font-family: 'JetBrains Mono', monospace;
}

.date-tag {
  font-size: 0.85rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-weight: 500;
}

.client-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.avatar {
  width: 48px;
  height: 48px;
  background: #f1f5f9;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.client-details {
  display: flex;
  flex-direction: column;
}

.client-name {
  font-weight: 800;
  font-size: 1.15rem;
  color: #1f2937;
}

.client-region {
  font-size: 0.85rem;
  color: #6b7280;
}

.products-mini {
  background: #f9fafb;
  border-radius: 16px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

.mini-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.mini-item:last-child { margin-bottom: 0; }

.m-name { font-size: 0.95rem; font-weight: 600; color: #374151; }
.m-dots { flex: 1; border-bottom: 1px dashed #d1d5db; height: 10px; }
.m-qty { font-weight: 700; color: #3f4a2f; }

.total-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1.25rem;
  border-top: 1px solid #f3f4f6;
}

.t-label { font-size: 0.9rem; color: #6b7280; }
.t-value { font-size: 1.5rem; font-weight: 900; color: #059669; }

.card-actions {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1rem;
  margin-top: 1.75rem;
}

.btn-action {
  padding: 0.85rem 1.5rem;
  border-radius: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  font-size: 0.95rem;
}

.btn-action--confirm {
  background: #3f4a2f;
  color: white;
}

.btn-action--confirm:hover:not(:disabled) {
  background: #4a5638;
  box-shadow: 0 4px 12px rgba(63, 74, 47, 0.3);
}

.btn-action--reject {
  background: #fff;
  color: #ef4444;
  border: 1px solid #fee2e2;
}

.btn-action--reject:hover { background: #fef2f2; }

.btn-action:disabled {
  opacity: 0.5;
  cursor: wait;
}

/* Chips */
.status-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.9rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.status-confirmed { background: #dcfce7; color: #166534; }
.status-inprogress { background: #dbeafe; color: #1e40af; }
.status-completed { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
.status-cancelled { background: #fee2e2; color: #991b1b; }

/* History Table */
.history-table-wrapper {
  background: white;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.03);
  border: 1px solid #e5e7eb;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.history-table th {
  background: #f8fafc;
  padding: 1.25rem;
  text-align: left;
  font-weight: 700;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
}

.history-table td {
  padding: 1.25rem;
  border-bottom: 1px solid #f1f5f9;
}

.history-table tr:last-child td { border-bottom: none; }

.td-id { font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #94a3b8; }
.td-date { color: #64748b; }
.td-client { font-weight: 700; color: #1e293b; }
.td-amount { font-weight: 800; color: #059669; }

.small-badge {
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 800;
}

/* Animations */
.dots-loader {
  display: inline-block;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 8px 0 currentColor, 16px 0 currentColor;
  animation: dots 1.5s infinite linear;
  margin-right: 20px;
}

@keyframes dots {
  0% { box-shadow: 8px 0 rgba(0,0,0,0.2), 16px 0 rgba(0,0,0,0.2); }
  33% { box-shadow: 8px 0 currentColor, 16px 0 rgba(0,0,0,0.2); }
  66% { box-shadow: 8px 0 currentColor, 16px 0 currentColor; }
}

.loader {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top-color: #3f4a2f;
  border-radius: 50%;
  animation: spin 1s infinite linear;
  margin: 0 auto 1rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

.wait-status {
  display: flex;
  align-items: center;
  font-size: 0.85rem;
  color: #6b7280;
  font-style: italic;
  padding: 1rem 0 0;
}

.td-amount { font-weight: 800; color: #059669; }

.client-cell {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.client-cell small {
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 500;
}

.td-items {
  max-width: 250px;
}

.items-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.82rem;
  color: #475569;
}

.avatar--sm {
  width: 36px !important;
  height: 36px !important;
  font-size: 1.1rem !important;
}

.products-mini--compact {
  padding: 0.75rem 1rem !important;
  margin-bottom: 1rem !important;
}

.small-badge {
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 800;
}

/* Utility */
.spin { display: inline-block; animation: spin 2s infinite linear; }
</style>
