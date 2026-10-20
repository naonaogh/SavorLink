<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useShopStore } from '@/stores/shopStore'
import { useAuthStore } from '@/stores/authStore'
import { CalendarIcon, CloseIcon, DeleteIcon, DoneIcon, DocumentIcon, TruckIcon } from '@/assets/icons/png'

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
    router.push('/auth')
    return
  }
  if (authStore.user?.role !== 'BUYER') {
    router.push('/')
    return
  }
  store.state.ordersLoading = true
  await Promise.all([
    store.fetchMyOrders(),
    store.fetchProducts()
  ])
  store.markOrdersSeen('BUYER')
})

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
      successMsg.value = `Шаблон успешно оформлен! Создано заказов: ${result.orders.length}`
      showTemplateModal.value = false
      setTimeout(() => { successMsg.value = null }, 5000)
    }
  } catch (err: any) {
    errorMsg.value = err.message || 'Ошибка при оформлении шаблона'
  } finally {
    isCheckingOut.value = false
  }
}

const handleDeleteTemplate = () => {
  if (confirm('Вы уверены, что хотите удалить этот шаблон?')) {
    store.deleteOrderTemplate()
    showTemplateModal.value = false
  }
}

const statusLabel: Record<string, { text: string; icon: string; class: string }> = {
  CREATED: { text: 'На рассмотрении', icon: 'calendar', class: 'status-created' },
  CONFIRMED: { text: 'Принят в работу', icon: 'done', class: 'status-confirmed' },
  IN_PROGRESS: { text: 'В пути', icon: 'truck', class: 'status-inprogress' },
  COMPLETED: { text: 'Доставлен', icon: 'done', class: 'status-completed' },
  CANCELLED: { text: 'Отклонён поставщиком', icon: 'close', class: 'status-cancelled' },
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
    case 'document':
    default:
      return DocumentIcon
  }
}

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
    <main class="page-main">
      <div class="page-header">
        <div class="title-block">
          <p class="page-kicker">Кабинет · Заказы</p>
          <div class="title-wrapper">
            <h1 class="page-title">Мои заказы</h1>
            <NotificationBell :count="unreadCount" />
          </div>
        </div>
        <div class="header-actions">
          <button 
            v-if="store.state.orderTemplate" 
            class="btn-use-template" 
            @click="showTemplateModal = true"
          >
            <img :src="DocumentIcon" alt="" class="btn-icon" aria-hidden="true" />
            Использовать шаблон
          </button>
          <p class="page-count" v-if="!isLoading">Всего заказов: {{ orders.length }}</p>
        </div>
      </div>

      <!-- Toast -->
      <TransitionGroup name="toast">
        <div v-if="successMsg" key="success" class="toast toast-success">
          <img :src="DoneIcon" alt="" class="t-icon" aria-hidden="true" />
          {{ successMsg }}
        </div>
        <div v-if="errorMsg" key="error" class="toast toast-error">
          <img :src="CloseIcon" alt="" class="t-icon" aria-hidden="true" />
          {{ errorMsg }}
        </div>
      </TransitionGroup>

      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Загрузка вашей истории заказов...</p>
      </div>

      <div v-else-if="orders.length === 0" class="empty-state">
        <div class="empty-illustration">
          <img :src="DocumentIcon" alt="" class="empty-icon" aria-hidden="true" />
        </div>
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
              <img :src="statusIcon(getStatusInfo(order.status).icon)" alt="" class="badge-icon" aria-hidden="true" />
              {{ getStatusInfo(order.status).text }}
            </div>
          </div>

          <div class="card-body">
            <div class="supplier-info">
              <span class="info-label">Поставщик</span>
              <span class="info-value">{{ order.seller_enterprise?.short_name }}</span>
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
                {{ updatingOrderId === order.id ? 'Обновляем...' : 'Заказ получен' }}
              </button>
              <p class="footer-hint" v-if="order.status === 'CONFIRMED'">
                Нажмите, когда товар будет у вас
              </p>
            </template>
            
            <div v-else-if="order.status === 'COMPLETED'" class="note-success">
              Сделка успешно завершена
            </div>
            <div v-else-if="order.status === 'CANCELLED'" class="note-error">
              Заказ был отменён
            </div>
            <div v-else class="note-pending">
              Ожидайте подтверждения от поставщика
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Template Modal -->
    <Transition name="modal">
      <div v-if="showTemplateModal" class="modal-overlay" @click.self="showTemplateModal = false">
        <div class="modal-template">
          <button class="btn-close-modal" @click="showTemplateModal = false">
            <img :src="CloseIcon" alt="" class="btn-icon" aria-hidden="true" />
          </button>
          <h2 class="modal-title">Ваш шаблон заказа</h2>
          
          <div class="template-items-list">
            <div v-for="item in templateItems" :key="item.product_id" class="template-item-card">
              <div class="t-item-icon">
                <img :src="DocumentIcon" alt="" class="item-icon-img" aria-hidden="true" />
              </div>
              <div class="t-item-main">
                <div class="t-item-top">
                  <span class="t-item-name">{{ item.product?.name }}</span>
                  <span class="t-item-category" v-if="item.product?.category">{{ item.product.category.name }}</span>
                </div>
                <div class="t-item-details">
                  <span class="t-item-supplier" v-if="item.product?.enterprise">{{ item.product.enterprise.short_name }}</span>
                  <span class="t-item-qty">{{ item.quantity }} кг × {{ item.product?.price }} ₽</span>
                </div>
              </div>
              <div class="t-item-subtotal">
                {{ ((item.product?.price || 0) * item.quantity).toFixed(0) }} ₽
              </div>
            </div>
          </div>

          <div class="template-footer">
            <div class="template-total">
              <span>Итого по шаблону</span>
              <span class="t-total-val">{{ templateTotal.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') }} ₽</span>
            </div>
            
            <div class="template-actions">
              <button class="btn-checkout-template" @click="handleCheckoutTemplate" :disabled="isCheckingOut">
                <span v-if="isCheckingOut" class="spinner-sm"></span>
                {{ isCheckingOut ? 'Оформление...' : 'Оформить по шаблону' }}
              </button>
              <button class="btn-delete-template" @click="handleDeleteTemplate">
                <img :src="DeleteIcon" alt="" class="btn-icon" aria-hidden="true" />
                Удалить шаблон
              </button>
            </div>
            <p class="template-hint">* Цены соответствуют текущим в каталоге</p>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.page {
  color: var(--sl-ink);
}

/* ===== ПАНЕЛЬ СТРАНИЦЫ ===== */
.page-main {
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
  padding: clamp(1.25rem, 3vw, 2rem);
}

.page-header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem 1.5rem;
  padding-bottom: 1.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--sl-line);
}

.page-kicker {
  margin: 0 0 0.6rem;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

.title-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.page-title {
  margin: 0;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  color: var(--sl-ink);
}

.header-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.6rem;
}

.page-count {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

/* ===== ИКОНКИ ===== */
.t-icon,
.btn-icon,
.badge-icon,
.empty-icon,
.item-icon-img {
  display: block;
  object-fit: contain;
  flex-shrink: 0;
  filter: grayscale(1) brightness(0.35);
}

.t-icon,
.btn-icon {
  width: 16px;
  height: 16px;
}

.badge-icon {
  width: 12px;
  height: 12px;
}

.empty-icon {
  width: 40px;
  height: 40px;
}

.item-icon-img {
  width: 20px;
  height: 20px;
}

/* ===== КНОПКИ ===== */
.btn-use-template,
.btn-delivered,
.btn-catalog,
.btn-checkout-template,
.btn-delete-template {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.7rem 1.2rem;
  border-radius: 0;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

/* primary */
.btn-delivered,
.btn-catalog,
.btn-checkout-template {
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
}

.btn-delivered:hover:not(:disabled),
.btn-catalog:hover,
.btn-checkout-template:hover:not(:disabled) {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

/* secondary */
.btn-use-template {
  background: transparent;
  color: var(--sl-ink);
  border: 1px solid var(--sl-ink);
}

.btn-use-template:hover {
  background: var(--sl-ink);
  color: #fff;
}

.btn-use-template:hover .btn-icon {
  filter: grayscale(1) brightness(0) invert(1);
}

/* danger */
.btn-delete-template {
  background: transparent;
  color: #b3261e;
  border: 1px solid #b3261e;
}

.btn-delete-template .btn-icon {
  filter: none;
}

.btn-delete-template:hover {
  background: #b3261e;
  color: #fff;
}

.btn-delete-template:hover .btn-icon {
  filter: grayscale(1) brightness(0) invert(1);
}

.btn-delivered:disabled,
.btn-checkout-template:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-use-template:focus-visible,
.btn-delivered:focus-visible,
.btn-catalog:focus-visible,
.btn-checkout-template:focus-visible,
.btn-delete-template:focus-visible,
.btn-close-modal:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

/* ===== ТОСТ ===== */
.toast {
  position: fixed;
  top: 90px;
  right: 2rem;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  max-width: min(420px, calc(100vw - 2rem));
  padding: 0.9rem 1.25rem;
  background: #fff;
  border: 1px solid var(--sl-line);
  border-left: 4px solid var(--sl-leaf);
  border-radius: 0;
  box-shadow: 0 24px 48px rgba(20, 33, 15, 0.18);
  color: var(--sl-ink);
  font-weight: 700;
}

.toast-error {
  border-left-color: #b3261e;
  color: #b3261e;
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
}

/* ===== СПИСОК ЗАКАЗОВ ===== */
.orders-grid {
  display: grid;
  gap: 1rem;
}

.order-card {
  position: relative;
  background: #fff;
  border: 1px solid var(--sl-line);
  border-radius: 0;
  transition: border-color 0.2s ease;
}

.order-card:hover {
  border-color: rgba(20, 33, 15, 0.4);
}

.order-card--completed {
  box-shadow: inset 3px 0 0 var(--sl-leaf);
}

.order-card--cancelled {
  box-shadow: inset 3px 0 0 #b3261e;
}

.order-card--cancelled .order-content,
.order-card--cancelled .order-number,
.order-card--cancelled .total-value {
  opacity: 0.7;
}

.card-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem 1rem;
  padding: 1.1rem 1.25rem;
  border-bottom: 1px solid var(--sl-line);
}

.order-meta {
  display: grid;
  gap: 0.3rem;
}

.order-number {
  font-family: var(--sl-display);
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--sl-ink);
}

.order-date {
  font-size: 0.82rem;
  color: var(--sl-muted);
}

/* статус — прямоугольный бейдж */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.2rem 0.5rem;
  border: 1px solid transparent;
  border-radius: 0;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  white-space: nowrap;
}

.status-created {
  background: var(--sl-paper);
  border-color: var(--sl-line);
  color: var(--sl-ink);
}

.status-confirmed,
.status-inprogress {
  background: var(--sl-ink);
  border-color: var(--sl-ink);
  color: var(--sl-lime);
}

.status-confirmed .badge-icon,
.status-inprogress .badge-icon {
  filter: grayscale(1) brightness(0) invert(1);
}

.status-completed {
  background: var(--sl-lime);
  border-color: var(--sl-lime);
  color: var(--sl-ink);
}

.status-cancelled {
  background: #fbeaea;
  border-color: rgba(179, 38, 30, 0.3);
  color: #b3261e;
}

.status-cancelled .badge-icon {
  filter: none;
}

.card-body {
  padding: 1.1rem 1.25rem 0;
}

.supplier-info {
  margin-bottom: 1rem;
}

.info-label,
.total-label {
  display: block;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.info-label {
  margin-bottom: 0.3rem;
}

.info-value {
  font-weight: 700;
  color: var(--sl-ink);
  overflow-wrap: anywhere;
}

/* позиции заказа */
.order-content {
  border: 1px solid var(--sl-line);
  background: var(--sl-paper);
}

.item-row {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  padding: 0.6rem 0.85rem;
  border-bottom: 1px solid var(--sl-line);
}

.item-row:last-child {
  border-bottom: none;
}

.item-name {
  min-width: 0;
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--sl-ink);
  overflow-wrap: anywhere;
}

.item-dots {
  flex: 1 1 1rem;
  min-width: 1rem;
  border-bottom: 1px dotted rgba(20, 33, 15, 0.25);
}

.item-vals {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  flex-shrink: 0;
}

.item-qty {
  font-size: 0.85rem;
  color: var(--sl-muted);
}

.item-price {
  min-width: 4.5rem;
  text-align: right;
  font-size: 0.92rem;
  font-weight: 700;
  color: var(--sl-ink);
}

.order-total {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  padding: 1rem 0;
}

.total-value {
  font-family: var(--sl-display);
  font-size: 1.35rem;
  font-weight: 600;
  color: var(--sl-ink);
  white-space: nowrap;
}

.card-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem 1rem;
  padding: 0.9rem 1.25rem;
  border-top: 1px solid var(--sl-line);
  background: var(--sl-paper);
}

.footer-hint {
  order: -1;
  margin: 0;
  font-size: 0.82rem;
  color: var(--sl-muted);
}

.note-success,
.note-error,
.note-pending {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.note-success::before,
.note-error::before,
.note-pending::before {
  content: '';
  width: 8px;
  height: 8px;
  flex-shrink: 0;
  background: currentColor;
}

.note-success {
  color: var(--sl-leaf);
}

.note-error {
  color: #b3261e;
}

.note-pending {
  color: var(--sl-muted);
}

.note-pending::before {
  background: transparent;
  border: 1px solid currentColor;
}

/* ===== ПУСТОЕ СОСТОЯНИЕ ===== */
.empty-state {
  display: grid;
  justify-items: center;
  gap: 0.75rem;
  padding: clamp(2.5rem, 6vw, 4rem) 1.5rem;
  background: #fff;
  border: 1px solid var(--sl-line);
  text-align: center;
}

.empty-illustration {
  width: 72px;
  height: 72px;
  display: grid;
  place-items: center;
  margin-bottom: 0.5rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
}

.empty-state h2 {
  margin: 0;
  font-size: clamp(1.15rem, 2.4vw, 1.5rem);
  color: var(--sl-ink);
}

.empty-state p {
  margin: 0 0 1rem;
  color: var(--sl-muted);
}

/* ===== ЗАГРУЗКА ===== */
.loading-state {
  display: grid;
  justify-items: center;
  gap: 1rem;
  padding: 3.5rem 0;
  color: var(--sl-muted);
}

.loading-state p {
  margin: 0;
}

.loading-spinner {
  width: 28px;
  height: 28px;
  border: 2px solid var(--sl-line);
  border-top-color: var(--sl-ink);
  border-radius: 0;
  animation: spin 0.9s linear infinite;
}

.spinner-sm,
.loading-sm {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 0;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ===== МОДАЛКА ШАБЛОНА ===== */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(20, 33, 15, 0.55);
}

.modal-template {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 620px;
  max-height: 90vh;
  padding: clamp(1.25rem, 4vw, 2rem);
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
  border-radius: 0;
  box-shadow: 0 24px 48px rgba(20, 33, 15, 0.18);
}

.btn-close-modal {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  background: #fff;
  border: 1px solid var(--sl-line);
  border-radius: 0;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.btn-close-modal:hover {
  background: var(--sl-ink);
  border-color: var(--sl-ink);
}

.btn-close-modal:hover .btn-icon {
  filter: grayscale(1) brightness(0) invert(1);
}

.modal-title {
  margin: 0 0 1.25rem;
  padding: 0 3rem 1.25rem 0;
  border-bottom: 1px solid var(--sl-line);
  font-size: clamp(1.2rem, 3vw, 1.5rem);
  color: var(--sl-ink);
}

.template-items-list {
  display: grid;
  gap: 1px;
  margin-bottom: 1.25rem;
  overflow-y: auto;
  background: var(--sl-line);
  border: 1px solid var(--sl-line);
}

.template-item-card {
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr) auto;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem 1rem;
  background: #fff;
}

.t-item-icon {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
}

.t-item-main {
  display: grid;
  gap: 0.3rem;
  min-width: 0;
}

.t-item-top {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem 0.6rem;
}

.t-item-name {
  font-weight: 700;
  color: var(--sl-ink);
}

.t-item-category {
  padding: 0.15rem 0.45rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-radius: 0;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--sl-ink);
}

.t-item-details {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.25rem 1rem;
  font-size: 0.82rem;
  color: var(--sl-muted);
}

.t-item-supplier {
  font-weight: 600;
}

.t-item-subtotal {
  font-family: var(--sl-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--sl-ink);
  white-space: nowrap;
}

.template-footer {
  padding-top: 1.25rem;
  border-top: 1px solid var(--sl-line);
}

.template-total {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.template-total span:first-child {
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.t-total-val {
  font-family: var(--sl-display);
  font-size: clamp(1.35rem, 3vw, 1.75rem);
  font-weight: 600;
  color: var(--sl-ink);
  white-space: nowrap;
}

.template-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 0.9rem;
}

.btn-checkout-template,
.btn-delete-template {
  padding: 0.9rem 1.2rem;
}

.template-hint {
  margin: 0;
  font-size: 0.8rem;
  color: var(--sl-muted);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .loading-spinner,
  .spinner-sm,
  .loading-sm {
    animation-duration: 2.4s;
  }
}

/* ===== АДАПТИВ ===== */
@media (max-width: 640px) {
  .page-header {
    align-items: flex-start;
  }

  .header-actions {
    align-items: flex-start;
  }

  .card-header,
  .card-body,
  .card-footer {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .card-footer {
    justify-content: flex-start;
  }

  .btn-delivered {
    width: 100%;
  }

  .footer-hint {
    order: 0;
  }

  .item-row {
    flex-wrap: wrap;
  }

  .item-name {
    flex: 1 1 100%;
  }

  .item-dots {
    display: none;
  }

  .item-vals {
    width: 100%;
    justify-content: space-between;
  }

  .toast {
    left: 1rem;
    right: 1rem;
    max-width: none;
  }

  .template-item-card {
    grid-template-columns: 40px minmax(0, 1fr);
  }

  .t-item-subtotal {
    grid-column: 2;
  }

  .template-actions {
    grid-template-columns: 1fr;
  }
}
</style>
