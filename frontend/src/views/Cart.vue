<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useShopStore } from '@/data/shopStore'
import { useAuthStore } from '@/data/authStore'
import { useRouter } from 'vue-router'
import CommonNavbar from '@/components/CommonNavbar.vue'

const store = useShopStore()
const authStore = useAuthStore()
const router = useRouter()

const isLoading = ref(false)
const isCheckingOut = ref(false)
const orderSuccess = ref(false)
const orderError = ref<string | null>(null)
const orderId = ref<number | null>(null)
const createdOrdersCount = ref(0)
const showTemplateModal = ref(false)
const successMsg = ref<string | null>(null)

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

onMounted(async () => {
  if (!authStore.token) {
    router.push('/login')
    return
  }
  isLoading.value = true
  await Promise.all([
    store.fetchCart(),
    store.fetchProducts()
  ])
  isLoading.value = false
})

const cartItems = computed(() => store.state.cartItems)

const cartTotal = computed(() =>
  cartItems.value.reduce(
    (sum, item) => sum + Number(item.product.price) * item.quantity,
    0,
  ),
)

const handleDecrease = async (item: any) => {
  const newQty = item.quantity - 1
  if (newQty <= 0) {
    await store.removeFromCart(item.product_id)
  } else {
    await store.setCartQuantity(item.product_id, newQty)
  }
}

const handleIncrease = async (item: any) => {
  await store.setCartQuantity(item.product_id, item.quantity + 1)
}

const handleRemove = async (productId: number) => {
  await store.removeFromCart(productId)
}

const handleCheckout = async () => {
  if (isCheckingOut.value) return
  orderError.value = null
  isCheckingOut.value = true
  try {
    const result = await store.checkoutCart()
    const firstOrder = result.orders[0]
    if (firstOrder) {
      orderId.value = firstOrder.id
      createdOrdersCount.value = result.orders.length
      orderSuccess.value = true
    } else {
      orderError.value = 'Не удалось оформить заказ. Проверьте товары в корзине.'
    }
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    orderError.value = detail || 'Произошла ошибка при оформлении заказа'
  } finally {
    isCheckingOut.value = false
  }
}

const closeSuccess = () => {
  orderSuccess.value = false
  orderId.value = null
  createdOrdersCount.value = 0
  router.push('/my-orders')
}

const handleCreateTemplate = () => {
  store.saveOrderTemplate()
  successMsg.value = 'Ваш шаблон создан, вы можете использовать его на странице мои заказы'
  setTimeout(() => { successMsg.value = null }, 6000)
}

const handleCheckoutTemplate = async () => {
  if (isCheckingOut.value) return
  orderError.value = null
  isCheckingOut.value = true
  try {
    const result = await store.checkoutWithItems(store.state.orderTemplate || [])
    const firstOrder = result.orders[0]
    if (firstOrder) {
      orderId.value = firstOrder.id
      createdOrdersCount.value = result.orders.length
      orderSuccess.value = true
      showTemplateModal.value = false
    }
  } catch (err: any) {
    orderError.value = err.message || 'Ошибка при оформлении заказа из шаблона'
  } finally {
    isCheckingOut.value = false
  }
}
</script>

<template>
  <div class="page">
    <CommonNavbar />

    <main class="page-main">
      <h1 class="page-title">Корзина</h1>

      <!-- Template notification toast -->
      <Transition name="toast">
        <div v-if="successMsg" class="template-toast">
          <span class="t-icon">✨</span>
          <div class="t-content">
            <p>{{ successMsg }}</p>
            <router-link to="/my-orders" class="t-link">Перейти к заказам →</router-link>
          </div>
          <button @click="successMsg = null" class="t-close">✕</button>
        </div>
      </Transition>

      <div v-if="isLoading" class="status-msg">Загрузка корзины...</div>

      <div v-else-if="cartItems.length === 0" class="empty-state">
        <div class="empty-icon">🛒</div>
        <p>Ваша корзина пуста</p>
        <router-link to="/catalog" class="btn-go-catalog">Перейти в каталог</router-link>
      </div>

      <div v-else class="cart-layout">
        <div class="cart-items">
          <div v-for="item in cartItems" :key="item.id" class="cart-item-card">
            <div class="cart-item-image">
              <span class="item-icon">🌿</span>
            </div>
            <div class="cart-item-info">
              <h3 class="item-name">{{ item.product.name }}</h3>
              <p class="item-category" v-if="item.product.category">{{ item.product.category.name }}</p>
              <p class="item-supplier" v-if="item.product.enterprise">
                🏢 {{ item.product.enterprise.short_name }}
              </p>
              <p class="item-desc" v-if="item.product.description">{{ item.product.description }}</p>
            </div>
            <div class="cart-item-controls">
              <p class="item-price-unit">{{ item.product.price }} ₽/кг</p>
              <div class="qty-control">
                <button class="qty-btn" @click="handleDecrease(item)">−</button>
                <span class="qty-val">{{ item.quantity }} кг</span>
                <button class="qty-btn" @click="handleIncrease(item)">+</button>
              </div>
              <p class="item-subtotal">{{ (Number(item.product.price) * item.quantity).toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') }} ₽</p>
              <button class="btn-remove" @click="handleRemove(item.product_id)" title="Удалить из корзины">
                ✕
              </button>
            </div>
          </div>
        </div>

        <!-- Order Summary -->
        <div class="order-summary">
          <h2 class="summary-title">Итог заказа</h2>
          <div class="summary-rows">
            <div class="summary-row" v-for="item in cartItems" :key="item.id">
              <span class="summary-row-name">{{ item.product.name }}</span>
              <span class="summary-row-val">{{ (Number(item.product.price) * item.quantity).toFixed(0) }} ₽</span>
            </div>
          </div>
          <div class="summary-divider"></div>
          <div class="summary-total">
            <span>Итого</span>
            <span class="total-amount">{{ cartTotal.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') }} ₽</span>
          </div>

          <div v-if="orderError" class="order-error">
            ⚠️ {{ orderError }}
          </div>

          <button
            class="btn-checkout"
            @click="handleCheckout"
            :disabled="isCheckingOut"
          >
            <span v-if="isCheckingOut" class="spinner"></span>
            {{ isCheckingOut ? 'Оформление...' : 'Оформить заказ' }}
          </button>

          <button 
            class="btn-save-template" 
            @click="handleCreateTemplate"
            v-if="cartItems.length > 0"
          >
            📂 Создать шаблон заказа
          </button>

          <button 
            class="btn-use-template" 
            @click="showTemplateModal = true"
            v-if="store.state.orderTemplate"
          >
            📝 Использовать шаблон
          </button>

          <router-link to="/catalog" class="btn-continue">
            ← Продолжить покупки
          </router-link>
        </div>
      </div>
    </main>

    <!-- Success Modal -->
    <Transition name="modal">
      <div v-if="orderSuccess" class="modal-overlay" @click.self="closeSuccess">
        <!-- ... (existing success modal content) ... -->
        <div class="modal-success">
          <div class="success-icon">✨</div>
          <h2 class="success-title">Заказ оформлен!</h2>
          <p class="success-text">
            <template v-if="createdOrdersCount === 1">
              Ваш заказ <strong>#{{ orderId }}</strong> успешно создан. Мы уведомили поставщика, и он скоро примет его в работу.
            </template>
            <template v-else>
              Создано <strong>{{ createdOrdersCount }}</strong> заказов. Поставщики уже получили уведомления и приступают к обработке.
            </template>
            <br><br>
            Следите за статусами в разделе «Мои заказы».
          </p>
          <div class="success-actions">
            <button @click="closeSuccess" class="btn-to-orders">
              К моим заказам
            </button>
            <router-link to="/catalog" class="btn-continue-shopping" @click="orderSuccess = false">
              Продолжить покупки
            </router-link>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Template Modal -->
    <Transition name="modal">
      <div v-if="showTemplateModal" class="modal-overlay" @click.self="showTemplateModal = false">
        <div class="modal-template">
          <button class="btn-close-modal" @click="showTemplateModal = false">✕</button>
          <h2 class="modal-title">Ваш шаблон заказа</h2>
          
          <div class="template-items-list">
            <div v-for="item in templateItems" :key="item.product_id" class="template-item-card">
              <div class="t-item-icon">🌿</div>
              <div class="t-item-main">
                <div class="t-item-top">
                  <span class="t-item-name">{{ item.product?.name }}</span>
                  <span class="t-item-category" v-if="item.product?.category">{{ item.product.category.name }}</span>
                </div>
                <div class="t-item-details">
                  <span class="t-item-supplier" v-if="item.product?.enterprise">🏢 {{ item.product.enterprise.short_name }}</span>
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
            
            <button class="btn-checkout-template" @click="handleCheckoutTemplate" :disabled="isCheckingOut">
              <span v-if="isCheckingOut" class="spinner"></span>
              {{ isCheckingOut ? 'Оформление...' : 'Оформить по шаблону' }}
            </button>
            <p class="template-hint">* Цены соответствуют текущим в каталоге</p>
          </div>
        </div>
      </div>
    </Transition>
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
  font-family: 'Inter', system-ui, sans-serif;
}

.page-main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 3rem 1.5rem 6rem;
}

.page-title {
  font-size: 2.25rem;
  font-weight: 900;
  color: #3f4a2f;
  margin: 0 0 2.5rem;
  letter-spacing: -0.02em;
}

.status-msg {
  text-align: center;
  padding: 3rem;
  font-size: 1.1rem;
  color: #6b7280;
}

.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(10px);
  border-radius: 30px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 10px 40px rgba(0,0,0,0.05);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 2rem;
}

.empty-state p {
  color: #6b7280;
  font-size: 1.15rem;
  margin-bottom: 2.5rem;
}

.btn-go-catalog {
  display: inline-block;
  background: #3f4a2f;
  color: #fff;
  text-decoration: none;
  padding: 1rem 2.5rem;
  border-radius: 999px;
  font-weight: 700;
  transition: all 0.3s ease;
}

.btn-go-catalog:hover {
  background: #4a5638;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(63, 74, 47, 0.2);
}

.cart-layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 3rem;
  align-items: start;
}

@media (max-width: 900px) {
  .cart-layout {
    grid-template-columns: 1fr;
  }
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.cart-item-card {
  background: white;
  border-radius: 24px;
  padding: 1.5rem;
  display: grid;
  grid-template-columns: 100px 1fr auto;
  gap: 1.5rem;
  align-items: center;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.cart-item-card:hover {
  transform: translateX(4px);
  border-color: #3f4a2f;
  box-shadow: 0 10px 25px rgba(0,0,0,0.06);
}

.cart-item-image {
  width: 100px;
  height: 100px;
  background: #f1f5f9;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-icon {
  font-size: 2.5rem;
}

.item-name {
  font-size: 1.25rem;
  font-weight: 800;
  margin: 0 0 0.4rem;
  color: #111827;
}

.item-category {
  font-size: 0.82rem;
  color: #3f4a2f;
  background: #ecf3e6;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  font-weight: 700;
  display: inline-block;
  margin-bottom: 0.5rem;
}

.item-supplier {
  display: block;
  font-size: 0.88rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.item-desc {
  font-size: 0.85rem;
  color: #9ca3af;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cart-item-controls {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.75rem;
}

.item-price-unit {
  font-size: 0.88rem;
  color: #9ca3af;
  font-weight: 600;
}

.qty-control {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border-radius: 12px;
  padding: 2px;
  border: 1px solid #e2e8f0;
}

.qty-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  font-size: 1.25rem;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3f4a2f;
}

.qty-btn:hover {
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.qty-val {
  padding: 0 1rem;
  font-weight: 800;
  font-size: 1rem;
  color: #1f2937;
}

.item-subtotal {
  font-size: 1.25rem;
  font-weight: 900;
  color: #059669;
}

.btn-remove {
  background: #fee2e2;
  border: none;
  color: #ef4444;
  cursor: pointer;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  font-size: 0.8rem;
}

.btn-remove:hover {
  background: #ef4444;
  color: white;
}

/* Summary */
.order-summary {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 24px;
  padding: 2rem;
  box-shadow: 0 20px 40px rgba(0,0,0,0.05);
  position: sticky;
  top: 100px;
}

.summary-title {
  font-size: 1.35rem;
  font-weight: 900;
  margin: 0 0 1.5rem;
  color: #3f4a2f;
}

.summary-rows {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.95rem;
  color: #6b7280;
}

.summary-row-val {
  font-weight: 700;
  color: #1f2937;
}

.summary-divider {
  height: 1px;
  background: #e2e8f0;
  margin: 1.5rem 0;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 2rem;
}

.summary-total span:first-child {
  font-weight: 700;
  color: #6b7280;
}

.total-amount {
  font-size: 2rem;
  font-weight: 900;
  color: #059669;
}

.order-error {
  background: #fef2f2;
  color: #dc2626;
  padding: 1rem;
  border-radius: 14px;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  border: 1px solid #fee2e2;
  font-weight: 600;
}

.btn-checkout {
  width: 100%;
  background: #3f4a2f;
  color: #fff;
  border: none;
  padding: 1.25rem;
  border-radius: 18px;
  font-size: 1.15rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 1rem;
  box-shadow: 0 4px 15px rgba(63, 74, 47, 0.2);
}

.btn-checkout:hover:not(:disabled) {
  background: #4a5638;
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(63, 74, 47, 0.3);
}

.btn-checkout:disabled {
  opacity: 0.6;
  cursor: wait;
}

.btn-continue {
  display: block;
  text-align: center;
  color: #9ca3af;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 600;
  transition: color 0.2s;
}

.btn-continue:hover {
  color: #3f4a2f;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(30, 25, 15, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 1rem;
}

.modal-success {
  background: #fdfaf3;
  border-radius: 32px;
  padding: 3.5rem 2.5rem;
  max-width: 480px;
  width: 100%;
  text-align: center;
  box-shadow: 0 25px 60px rgba(0,0,0,0.3);
  position: relative;
}

.success-icon {
  font-size: 4.5rem;
  margin-bottom: 1.5rem;
}

.success-title {
  font-size: 2.25rem;
  font-weight: 900;
  color: #3f4a2f;
  margin-bottom: 1rem;
}

.success-text {
  color: #6b7280;
  line-height: 1.7;
  font-size: 1.1rem;
  margin-bottom: 2.5rem;
}

.success-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn-to-orders {
  background: #059669;
  color: #fff;
  border: none;
  padding: 1.1rem;
  border-radius: 16px;
  font-size: 1.1rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-to-orders:hover {
  background: #047857;
  transform: scale(1.02);
}

.btn-continue-shopping {
  color: #9ca3af;
  text-decoration: none;
  font-weight: 700;
  transition: color 0.2s;
}

.btn-continue-shopping:hover {
  color: #3f4a2f;
}

.btn-save-template {
  width: 100%;
  background: white;
  color: #3f4a2f;
  border: 2px dashed #3f4a2f;
  padding: 1rem;
  border-radius: 18px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-save-template:hover {
  background: #f8faf6;
  border-style: solid;
  transform: translateY(-1px);
}

.btn-use-template {
  width: 100%;
  background: #ecf3e6;
  color: #3f4a2f;
  border: none;
  padding: 1rem;
  border-radius: 18px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-use-template:hover {
  background: #dbe7d1;
  transform: translateY(-1px);
}

/* Template Modal */
.modal-template {
  background: #fdfaf3;
  border-radius: 32px;
  padding: 3rem 2.5rem;
  max-width: 600px;
  width: 100%;
  box-shadow: 0 30px 70px rgba(0,0,0,0.25);
  position: relative;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.template-items-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
  overflow-y: auto;
  padding: 0.5rem;
}

.template-item-card {
  background: white;
  border-radius: 18px;
  padding: 1.25rem;
  display: grid;
  grid-template-columns: 48px 1fr auto;
  gap: 1rem;
  align-items: center;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.t-item-icon {
  width: 48px;
  height: 48px;
  background: #f1f5f9;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.t-item-main {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.t-item-top {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.t-item-name {
  font-weight: 800;
  color: #111827;
  font-size: 1rem;
}

.t-item-category {
  font-size: 0.75rem;
  color: #3f4a2f;
  background: #ecf3e6;
  padding: 0.1rem 0.5rem;
  border-radius: 4px;
  font-weight: 700;
}

.t-item-details {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
  color: #6b7280;
}

.t-item-supplier {
  font-weight: 600;
}

.t-item-qty {
  font-weight: 500;
}

.t-item-subtotal {
  font-weight: 900;
  color: #3f4a2f;
  font-size: 1.1rem;
}

.template-toast {
  background: white;
  border-radius: 20px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 15px 40px rgba(63, 74, 47, 0.15);
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 2.5rem;
  border-left: 6px solid #3f4a2f;
  position: relative;
  animation: slide-in 0.4s ease;
}

.t-content p {
  margin: 0;
  font-weight: 600;
  color: #374151;
  font-size: 0.95rem;
}

.t-link {
  display: inline-block;
  color: #3f4a2f;
  font-weight: 800;
  font-size: 0.85rem;
  text-decoration: none;
  margin-top: 0.5rem;
  border-bottom: 1px solid transparent;
  transition: all 0.2s;
}

.t-link:hover {
  border-color: #3f4a2f;
  transform: translateX(4px);
}

.t-close {
  background: transparent;
  border: none;
  font-size: 1.1rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.5rem;
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
}

@keyframes slide-in {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.toast-enter-active { animation: slide-in 0.4s ease; }
.toast-leave-active { transition: all 0.3s ease; opacity: 0; transform: translateY(-10px); }

.template-footer {
  border-top: 1px solid #e2e8f0;
  padding-top: 1.5rem;
}

.template-total {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 1.5rem;
}

.template-total span:first-child {
  font-weight: 700;
  color: #6b7280;
}

.t-total-val {
  font-size: 1.75rem;
  font-weight: 900;
  color: #059669;
}

.btn-checkout-template {
  width: 100%;
  background: #3f4a2f;
  color: #fff;
  border: none;
  padding: 1.25rem;
  border-radius: 18px;
  font-size: 1.1rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 1rem;
  box-shadow: 0 8px 25px rgba(63, 74, 47, 0.2);
}

.btn-checkout-template:hover:not(:disabled) {
  background: #4a5638;
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(63, 74, 47, 0.3);
}

.btn-checkout-template:disabled {
  opacity: 0.6;
  cursor: wait;
}

.template-hint {
  font-size: 0.8rem;
  color: #94a3b8;
  text-align: center;
  margin: 0;
  font-weight: 500;
}

.modal-enter-active { animation: pop-in 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); }
.modal-leave-active { transition: opacity 0.3s, transform 0.3s; }
.modal-leave-to { opacity: 0; transform: scale(0.9); }

@keyframes pop-in {
  from { opacity: 0; transform: scale(0.6) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
</style>
