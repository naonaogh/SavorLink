<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useShopStore } from '@/stores/shopStore'
import { useAuthStore } from '@/stores/authStore'
import { CalendarIcon, CloseIcon, DocumentIcon, DoneIcon, OrganizationIcon, TruckIcon } from '@/assets/icons/png'

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

const statusLabel: Record<string, { text: string; icon: string; class: string }> = {
  CREATED: { text: 'Новый запрос', icon: 'calendar', class: 'status-created' },
  CONFIRMED: { text: 'Подтверждён', icon: 'done', class: 'status-confirmed' },
  IN_PROGRESS: { text: 'В процессе', icon: 'truck', class: 'status-inprogress' },
  COMPLETED: { text: 'Завершён успешно', icon: 'done', class: 'status-completed' },
  CANCELLED: { text: 'Отклонён', icon: 'close', class: 'status-cancelled' },
}

const getStatusInfo = (status: string) =>
  statusLabel[status] || { text: status, icon: 'document', class: 'status-created' }

const statusIcon = (icon: string) => {
  switch (icon) {
    case 'calendar':
      return CalendarIcon
    case 'done':
      return DoneIcon
    case 'close':
      return CloseIcon
    case 'truck':
      return TruckIcon
    default:
      return DocumentIcon
  }
}

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
    <div class="page-main">
      <div class="page-head">
        <div class="header-content">
          <p class="page-kicker">Кабинет · Заказы</p>
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
          <img :src="DoneIcon" alt="" class="toast-icon" aria-hidden="true" />
          <div class="toast-body">{{ successMsg }}</div>
        </div>
        <div v-if="errorMsg" key="error" class="toast toast-error">
          <img :src="CloseIcon" alt="" class="toast-icon" aria-hidden="true" />
          <div class="toast-body">{{ errorMsg }}</div>
        </div>
      </TransitionGroup>

      <!-- Loading -->
      <div v-if="isLoading" class="loading-container">
        <div class="loader" aria-hidden="true"></div>
        <p>Синхронизация данных...</p>
      </div>

      <div v-else-if="orders.length === 0" class="empty-hero">
        <div class="hero-icon">
          <img :src="DocumentIcon" alt="" class="hero-icon-img" aria-hidden="true" />
        </div>
        <h2>Заказов пока нет</h2>
        <p>Ваши товары ждут своих покупателей. Как только кто-то оформит заказ, он появится здесь.</p>
      </div>

      <div v-else class="sections-grid">
        <!-- НОВЫЕ ЗАПРОСЫ -->
        <section v-if="pendingOrders.length > 0" class="order-section">
          <h2 class="section-heading">
            <span class="pulse-dot" aria-hidden="true"></span>
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
                  <div class="avatar">
                    <img :src="OrganizationIcon" alt="" class="avatar-icon" aria-hidden="true" />
                  </div>
                  <div class="client-details">
                    <span class="client-name">{{ order.buyer_enterprise?.short_name || 'Покупатель' }}</span>
                    <span class="client-region">{{ order.buyer_enterprise?.region || 'Регион не указан' }}</span>
                  </div>
                </div>

                <div class="products-mini">
                  <div v-for="item in order.items" :key="item.id" class="mini-item">
                    <span class="m-name">{{ item.product?.name }}</span>
                    <div class="m-dots" aria-hidden="true"></div>
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
                  <img :src="statusIcon(getStatusInfo(order.status).icon)" alt="" class="chip-icon" aria-hidden="true" />
                  {{ getStatusInfo(order.status).text }}
                </div>
                <div class="id-badge">#{{ order.id }}</div>
              </div>
              
              <div class="card-body">
                <div class="client-info">
                  <div class="avatar avatar--sm">
                    <img :src="OrganizationIcon" alt="" class="avatar-icon" aria-hidden="true" />
                  </div>
                  <div class="client-details">
                    <span class="client-name">{{ order.buyer_enterprise?.short_name }}</span>
                    <span class="client-region">{{ order.buyer_enterprise?.region }}</span>
                  </div>
                </div>

                <div class="products-mini products-mini--compact">
                  <div v-for="item in order.items" :key="item.id" class="mini-item">
                    <span class="m-name">{{ item.product?.name }}</span>
                    <div class="m-dots" aria-hidden="true"></div>
                    <span class="m-qty">{{ item.quantity }} кг</span>
                  </div>
                </div>

                <div class="total-bar compact">
                  <span class="t-value">{{ formatAmount(order.total_amount) }}</span>
                </div>
              </div>
              
              <div class="card-footer">
                <div class="wait-status">
                  <span class="dots-loader" aria-hidden="true"></span>
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
    </div>
  </div>
</template>

<style scoped>
/* ===== ПАНЕЛЬ СТРАНИЦЫ ===== */
.page {
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
  color: var(--sl-ink);
}

.page-main {
  padding: clamp(1.1rem, 3vw, 2rem);
}

/* ===== ШАПКА ===== */
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 1.5rem 2rem;
  padding-bottom: 1.5rem;
  margin-bottom: 1.75rem;
  border-bottom: 1px solid var(--sl-line);
}

.header-content {
  min-width: 0;
  flex: 1 1 320px;
}

.page-kicker {
  margin: 0 0 0.75rem;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

.title-with-bell {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.page-title {
  margin: 0;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  color: var(--sl-ink);
  overflow-wrap: anywhere;
}

.page-subtitle {
  margin: 0.6rem 0 0;
  font-size: 0.92rem;
  color: var(--sl-muted);
}

/* ===== СТАТИСТИКА ===== */
.header-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(96px, 1fr));
  gap: 1px;
  background: var(--sl-line);
  border: 1px solid var(--sl-line);
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.85rem 1.1rem;
  background: #fff;
  transition: background 0.2s ease, color 0.2s ease;
}

.stat-val {
  font-family: var(--sl-display);
  font-size: 1.5rem;
  font-weight: 600;
  line-height: 1;
  color: var(--sl-ink);
}

.stat-lab {
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.stat-card--active {
  background: var(--sl-ink);
}

.stat-card--active .stat-val {
  color: var(--sl-lime);
}

.stat-card--active .stat-lab {
  color: rgba(255, 255, 255, 0.75);
}

/* ===== ТОСТЫ ===== */
.toast {
  position: fixed;
  z-index: 1000;
  top: 90px;
  right: 2rem;
  max-width: min(420px, calc(100vw - 2rem));
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.95rem 1.2rem;
  background: #fff;
  border: 1px solid var(--sl-line);
  border-left: 4px solid var(--sl-leaf);
  box-shadow: 0 24px 48px rgba(20, 33, 15, 0.18);
  font-weight: 600;
}

.toast-success {
  color: var(--sl-ink);
}

.toast-error {
  color: #b3261e;
  border-left-color: #b3261e;
}

.toast-icon {
  display: block;
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
  object-fit: contain;
  filter: grayscale(1) brightness(0.35);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

/* ===== СЕКЦИИ ===== */
.sections-grid {
  display: grid;
  gap: 2.25rem;
}

.order-section {
  min-width: 0;
}

.section-heading {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin: 0 0 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--sl-line);
  font-size: 1.05rem;
  color: var(--sl-ink);
}

.pulse-dot {
  width: 9px;
  height: 9px;
  flex: 0 0 auto;
  background: var(--sl-leaf);
  animation: blink 1.6s ease-in-out infinite;
}

/* ===== КАРТОЧКИ ЗАКАЗОВ ===== */
.cards-stack {
  display: grid;
  gap: 1rem;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr));
  gap: 1rem;
}

.premium-card {
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #fff;
  border: 1px solid var(--sl-line);
  transition: border-color 0.2s ease;
}

.premium-card:hover {
  border-color: rgba(20, 33, 15, 0.4);
}

.premium-card--new {
  border-left: 4px solid var(--sl-leaf);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  padding: 0.85rem 1.25rem;
  border-bottom: 1px solid var(--sl-line);
}

.id-badge {
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-ink);
}

.date-tag {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--sl-muted);
}

.card-body {
  flex: 1;
  padding: 1.1rem 1.25rem 1.25rem;
}

/* клиент */
.client-info {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin-bottom: 1rem;
  min-width: 0;
}

.avatar {
  width: 42px;
  height: 42px;
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
}

.avatar--sm {
  width: 36px;
  height: 36px;
}

.avatar-icon {
  display: block;
  width: 20px;
  height: 20px;
  object-fit: contain;
  filter: grayscale(1) brightness(0.35);
}

.client-details {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.client-name {
  font-weight: 800;
  color: var(--sl-ink);
  overflow-wrap: anywhere;
}

.client-region {
  font-size: 0.8rem;
  color: var(--sl-muted);
}

/* состав */
.products-mini {
  display: grid;
  gap: 0.45rem;
  margin-bottom: 1rem;
  padding: 0.85rem 1rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
}

.mini-item {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  font-size: 0.9rem;
  min-width: 0;
}

.m-name {
  font-weight: 600;
  color: var(--sl-ink);
  overflow-wrap: anywhere;
}

.m-dots {
  flex: 1 1 1rem;
  min-width: 1rem;
  border-bottom: 1px dotted rgba(20, 33, 15, 0.35);
}

.m-qty {
  flex: 0 0 auto;
  font-weight: 800;
  white-space: nowrap;
  color: var(--sl-ink);
}

/* итог */
.total-bar {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--sl-line);
}

.total-bar.compact {
  justify-content: flex-end;
}

.t-label {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.t-value {
  font-family: var(--sl-display);
  font-size: 1.35rem;
  font-weight: 600;
  color: var(--sl-ink);
  white-space: nowrap;
}

/* действия */
.card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--sl-line);
  background: var(--sl-paper);
}

.btn-action {
  flex: 0 1 auto;
  min-height: 44px;
  padding: 0.7rem 1.2rem;
  border-radius: 0;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.btn-action--confirm {
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
}

.btn-action--confirm:hover:not(:disabled) {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.btn-action--reject {
  background: transparent;
  color: #b3261e;
  border: 1px solid #b3261e;
}

.btn-action--reject:hover:not(:disabled) {
  background: #b3261e;
  color: #fff;
}

.btn-action:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-action:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

/* подвал карточки */
.card-footer {
  padding: 0.85rem 1.25rem;
  border-top: 1px solid var(--sl-line);
  background: var(--sl-paper);
}

.wait-status {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--sl-muted);
}

.dots-loader {
  width: 7px;
  height: 7px;
  flex: 0 0 auto;
  background: var(--sl-leaf);
  animation: blink 1.6s ease-in-out infinite;
}

/* ===== СТАТУСЫ ===== */
.status-chip,
.small-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--sl-line);
  border-radius: 0;
  background: var(--sl-paper);
  color: var(--sl-ink);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  line-height: 1.4;
}

.chip-icon {
  display: block;
  width: 14px;
  height: 14px;
  flex: 0 0 auto;
  object-fit: contain;
  filter: grayscale(1) brightness(0.35);
}

.status-confirmed {
  background: #fff;
  border-color: var(--sl-ink);
  color: var(--sl-ink);
}

.status-inprogress {
  background: var(--sl-ink);
  border-color: var(--sl-ink);
  color: var(--sl-lime);
}

.status-inprogress .chip-icon {
  filter: grayscale(1) brightness(0) invert(1);
}

.status-completed {
  background: var(--sl-lime);
  border-color: var(--sl-lime);
  color: var(--sl-ink);
}

.status-cancelled {
  background: #fbeaea;
  border-color: #fbeaea;
  color: #b3261e;
}

/* ===== ИСТОРИЯ (ТАБЛИЦА) ===== */
.history-table-wrapper {
  background: #fff;
  border: 1px solid var(--sl-line);
  overflow-x: auto;
}

.history-table {
  width: 100%;
  min-width: 760px;
  border-collapse: collapse;
  table-layout: fixed;
}

.history-table th,
.history-table td {
  padding: 0.85rem 1rem;
  text-align: left;
  vertical-align: top;
}

.history-table thead th {
  background: var(--sl-paper);
  border-bottom: 1px solid var(--sl-line);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.history-table tbody tr {
  transition: background 0.2s ease;
}

.history-table tbody tr + tr td {
  border-top: 1px solid var(--sl-line);
}

.history-table tbody tr:hover {
  background: var(--sl-paper);
}

.history-table th:nth-child(1),
.history-table td:nth-child(1) {
  width: 72px;
}

.history-table th:nth-child(2),
.history-table td:nth-child(2) {
  width: 120px;
}

.history-table th:nth-child(5),
.history-table td:nth-child(5) {
  width: 130px;
}

.history-table th:nth-child(6),
.history-table td:nth-child(6) {
  width: 170px;
}

.td-id {
  font-weight: 800;
  color: var(--sl-ink);
}

.td-date {
  font-size: 0.88rem;
  color: var(--sl-muted);
}

.td-date,
.client-cell,
.items-cell {
  line-height: 1.35;
}

.client-cell,
.items-cell {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.client-cell strong {
  color: var(--sl-ink);
}

.client-cell small {
  color: var(--sl-muted);
}

.items-cell span {
  font-size: 0.9rem;
  word-break: break-word;
}

.td-amount {
  font-family: var(--sl-display);
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--sl-ink);
  white-space: nowrap;
}

/* ===== ЗАГРУЗКА ===== */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3.5rem 1rem;
  background: #fff;
  border: 1px solid var(--sl-line);
  color: var(--sl-muted);
  font-weight: 600;
}

.loading-container p {
  margin: 0;
}

.loader {
  width: 36px;
  height: 36px;
  border: 3px solid var(--sl-line);
  border-top-color: var(--sl-ink);
  animation: spin 0.9s linear infinite;
}

/* ===== ПУСТО ===== */
.empty-hero {
  padding: clamp(2.5rem, 6vw, 4rem) clamp(1.25rem, 4vw, 2rem);
  text-align: center;
  background: #fff;
  border: 1px solid var(--sl-line);
}

.hero-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  margin-bottom: 1.25rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
}

.hero-icon-img {
  display: block;
  width: 32px;
  height: 32px;
  object-fit: contain;
  filter: grayscale(1) brightness(0.35);
}

.empty-hero h2 {
  margin: 0 0 0.6rem;
  font-size: 1.25rem;
  color: var(--sl-ink);
}

.empty-hero p {
  max-width: 460px;
  margin: 0 auto;
  color: var(--sl-muted);
}

/* ===== АНИМАЦИИ ===== */
@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes blink {
  50% { opacity: 0.25; }
}

@media (prefers-reduced-motion: reduce) {
  .loader,
  .pulse-dot,
  .dots-loader {
    animation: none;
  }
}

/* ===== АДАПТИВ ===== */
@media (max-width: 900px) {
  .header-stats {
    width: 100%;
  }
}

@media (max-width: 560px) {
  .card-header,
  .card-body,
  .card-actions,
  .card-footer {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .btn-action {
    flex: 1 1 100%;
  }

  .stat-card {
    padding: 0.75rem;
  }

  .stat-lab {
    letter-spacing: 0.08em;
  }

  .toast {
    left: 1rem;
    right: 1rem;
    top: 76px;
    max-width: none;
  }
}
</style>
