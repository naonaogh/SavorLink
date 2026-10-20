<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useShopStore } from '@/stores/shopStore'
import { useAuthStore } from '@/stores/authStore'
import { useRouter } from 'vue-router'
import { AddIcon, BagIcon, CloseIcon, DeleteIcon, DocumentIcon, DoneIcon, MinusIcon, OrganizationIcon } from '@/assets/icons/png'

const store = useShopStore()
const authStore = useAuthStore()
const router = useRouter()

const isLoading = ref(false)
const isCheckingOut = ref(false)
const orderError = ref<string | null>(null)
const successMsg = ref<string | null>(null)

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
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

const showOrderSentAndRedirect = () => {
  successMsg.value = 'Ваш заказ отправлен'
  setTimeout(() => {
    successMsg.value = null
    router.push('/my-orders')
  }, 1200)
}

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
      showOrderSentAndRedirect()
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

const handleCreateTemplate = () => {
  store.saveOrderTemplate()
  successMsg.value = 'Ваш шаблон создан, вы можете использовать его на странице «Мои заказы»'
  setTimeout(() => { successMsg.value = null }, 6000)
}

</script>

<template>
  <div class="page">
    <main class="page-main">
      <header class="page-head">
        <p class="page-kicker">Шаг 01 / Покупки</p>
        <h1 class="page-title">Корзина</h1>
      </header>

      <Transition name="toast">
        <div v-if="successMsg" class="template-toast">
          <img :src="DoneIcon" alt="" class="t-icon" aria-hidden="true" />
          <div class="t-content">
            <p>{{ successMsg }}</p>
            <router-link to="/my-orders" class="t-link">Перейти к заказам →</router-link>
          </div>
          <button @click="successMsg = null" class="t-close" aria-label="Закрыть">
            <img :src="CloseIcon" alt="" class="close-icon" aria-hidden="true" />
          </button>
        </div>
      </Transition>

      <div v-if="isLoading" class="status-msg">Загрузка корзины...</div>

      <div v-else-if="cartItems.length === 0" class="empty-state">
        <div class="empty-icon">
          <img :src="BagIcon" alt="" class="empty-icon-img" aria-hidden="true" />
        </div>
        <p>Ваша корзина пуста</p>
        <router-link to="/catalog" class="btn-go-catalog">Перейти в каталог</router-link>
      </div>

      <div v-else class="cart-layout">
        <div class="cart-items">
          <div v-for="item in cartItems" :key="item.id" class="cart-item-card">
            <div class="cart-item-image">
              <img :src="DocumentIcon" alt="" class="item-icon" aria-hidden="true" />
            </div>

            <div class="cart-item-info">
              <h3 class="item-name">{{ item.product.name }}</h3>
              <p class="item-category" v-if="item.product.category">{{ item.product.category.name }}</p>
              <p class="item-supplier" v-if="item.product.enterprise">
                <img :src="OrganizationIcon" alt="" class="supplier-icon" aria-hidden="true" />
                {{ item.product.enterprise.short_name }}
              </p>
              <p class="item-desc" v-if="item.product.description">{{ item.product.description }}</p>
            </div>

            <div class="cart-item-controls">
              <p class="item-price-unit">{{ item.product.price }} ₽/кг</p>

              <div class="qty-control">
                <button class="qty-btn" @click="handleDecrease(item)" aria-label="Уменьшить">
                  <img :src="MinusIcon" alt="" class="qty-icon" aria-hidden="true" />
                </button>
                <span class="qty-val">{{ item.quantity }} кг</span>
                <button class="qty-btn" @click="handleIncrease(item)" aria-label="Увеличить">
                  <img :src="AddIcon" alt="" class="qty-icon" aria-hidden="true" />
                </button>
              </div>

              <p class="item-subtotal">
                {{ (Number(item.product.price) * item.quantity).toFixed(0) }} ₽
              </p>

              <button class="btn-remove" @click="handleRemove(item.product_id)" aria-label="Удалить из корзины">
                <img :src="DeleteIcon" alt="" class="remove-icon" aria-hidden="true" />
              </button>
            </div>
          </div>
        </div>

        <div class="order-summary">
          <p class="summary-kicker">Сводка</p>
          <h2 class="summary-title">Итог заказа</h2>

          <div class="summary-rows">
            <div class="summary-row" v-for="item in cartItems" :key="item.id">
              <span>{{ item.product.name }}</span>
              <span class="summary-row-val">
                {{ (Number(item.product.price) * item.quantity).toFixed(0) }} ₽
              </span>
            </div>
          </div>

          <div class="summary-divider"></div>

          <div class="summary-total">
            <span>Итого</span>
            <span class="total-amount">
              {{ cartTotal.toFixed(0) }} ₽
            </span>
          </div>

          <div v-if="orderError" class="order-error">{{ orderError }}</div>

          <div class="checkout-actions">
            <button class="btn-checkout" @click="handleCheckout" :disabled="isCheckingOut">
              {{ isCheckingOut ? 'Оформление...' : 'Оформить заказ' }}
            </button>
            <router-link to="/checkout" class="btn-checkout-secondary">Перейти к проверке</router-link>
          </div>

          <button class="btn-checkout-secondary btn-save-template" @click="handleCreateTemplate">
            <img :src="DocumentIcon" alt="" class="btn-icon" aria-hidden="true" />
            Создать шаблон заказа
          </button>

          <router-link to="/catalog" class="btn-continue">
            ← Продолжить покупки
          </router-link>
        </div>
      </div>
    </main>
  </div>
</template>


<style scoped>
.page {
  color: var(--sl-ink);
  padding: 1.25rem 0 2rem;
}

.page-main {
  display: grid;
  gap: 1.25rem;
}

p,
h1,
h2,
h3 {
  margin: 0;
}

/* ЗАГОЛОВОК */
.page-head {
  padding: clamp(1.25rem, 3vw, 2rem) clamp(1.25rem, 3vw, 2.25rem);
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
}

.page-kicker,
.summary-kicker {
  margin-bottom: 0.6rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

.page-title {
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  color: var(--sl-ink);
}

/* СОСТОЯНИЯ */
.status-msg {
  padding: 1.25rem 1.5rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  color: var(--sl-muted);
  font-weight: 600;
}

.empty-state {
  display: grid;
  justify-items: center;
  gap: 1rem;
  padding: clamp(2.5rem, 6vw, 4rem) 1.5rem;
  text-align: center;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
}

.empty-icon {
  width: 88px;
  height: 88px;
  display: grid;
  place-items: center;
  background: #fff;
  border: 1px solid var(--sl-line);
}

.empty-state p {
  font-weight: 700;
  font-size: 1.1rem;
}

.btn-go-catalog {
  display: inline-flex;
  padding: 0.8rem 1.4rem;
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
  font-weight: 700;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.btn-go-catalog:hover {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

/* РАСКЛАДКА */
.cart-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 1.25rem;
  align-items: start;
}

/* СПИСОК ТОВАРОВ */
.cart-items {
  display: grid;
  gap: 1px;
  background: var(--sl-line);
  border: 1px solid var(--sl-line);
}

.cart-item-card {
  position: relative;
  display: grid;
  grid-template-columns: 56px minmax(0, 1fr) auto;
  gap: 1.25rem;
  align-items: start;
  padding: 1.35rem 1.25rem;
  background: #fff;
  transition: background 0.2s ease;
}

.cart-item-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--sl-leaf);
  transform: scaleY(0);
  transition: transform 0.25s ease;
}

.cart-item-card:hover {
  background: var(--sl-paper);
}

.cart-item-card:hover::before {
  transform: scaleY(1);
}

.cart-item-image {
  width: 56px;
  height: 56px;
  display: grid;
  place-items: center;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
}

.cart-item-info {
  display: grid;
  gap: 0.35rem;
  min-width: 0;
}

.item-name {
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.3;
  color: var(--sl-ink);
}

.item-category {
  justify-self: start;
  padding: 0.2rem 0.5rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.item-supplier {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--sl-ink);
}

.item-desc {
  font-size: 0.86rem;
  line-height: 1.5;
  color: var(--sl-muted);
}

/* УПРАВЛЕНИЕ */
.cart-item-controls {
  display: grid;
  justify-items: end;
  gap: 0.6rem;
}

.item-price-unit {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--sl-muted);
}

.qty-control {
  display: flex;
  align-items: stretch;
  border: 1px solid var(--sl-line);
  background: #fff;
}

.qty-btn {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: background 0.2s ease;
}

.qty-btn:hover {
  background: var(--sl-lime);
}

.qty-val {
  min-width: 64px;
  display: grid;
  place-items: center;
  border-inline: 1px solid var(--sl-line);
  font-size: 0.9rem;
  font-weight: 700;
}

.item-subtotal {
  font-family: var(--sl-display);
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--sl-ink);
  white-space: nowrap;
}

.btn-remove {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  padding: 0;
  background: transparent;
  border: 1px solid rgba(179, 38, 30, 0.45);
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.btn-remove:hover {
  background: #b3261e;
  border-color: #b3261e;
}

.btn-remove:hover .remove-icon {
  filter: brightness(0) invert(1);
}

/* ИТОГ */
.order-summary {
  position: sticky;
  top: 1rem;
  display: grid;
  padding: 1.5rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
}

.summary-title {
  font-size: 1.15rem;
  color: var(--sl-ink);
  padding-bottom: 1rem;
  margin-bottom: 0.25rem;
  border-bottom: 1px solid var(--sl-line);
}

.summary-rows {
  display: grid;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.55rem 0;
  border-bottom: 1px solid var(--sl-line);
  font-size: 0.88rem;
  color: var(--sl-muted);
}

.summary-row-val {
  font-weight: 700;
  color: var(--sl-ink);
  white-space: nowrap;
}

.summary-divider {
  height: 2px;
  margin: 0 0 1rem;
  background: var(--sl-ink);
}

.summary-total {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.total-amount {
  font-family: var(--sl-display);
  font-size: 1.75rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  text-transform: none;
  color: var(--sl-ink);
  white-space: nowrap;
}

.order-error {
  margin-top: 1rem;
  padding: 0.8rem 1rem;
  background: #fbeaea;
  border: 1px solid #b3261e;
  color: #b3261e;
  font-size: 0.9rem;
  font-weight: 600;
}

/* КНОПКИ */
.checkout-actions {
  display: grid;
  gap: 0.5rem;
  margin-top: 1.25rem;
}

.btn-checkout,
.btn-checkout-secondary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.85rem 1.2rem;
  border-radius: 0;
  font-weight: 700;
  text-align: center;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.btn-checkout {
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
}

.btn-checkout:hover:not(:disabled) {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.btn-checkout:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-checkout-secondary {
  background: transparent;
  color: var(--sl-ink);
  border: 1px solid var(--sl-ink);
}

.btn-checkout-secondary:hover {
  background: var(--sl-ink);
  color: #fff;
}

.btn-checkout-secondary:hover .btn-icon {
  filter: brightness(0) invert(1);
}

.btn-save-template {
  margin-top: 0.5rem;
}

.btn-continue {
  justify-self: center;
  margin-top: 1rem;
  padding: 0.3rem 0;
  border-bottom: 1px solid transparent;
  font-weight: 700;
  color: var(--sl-ink);
  transition: border-color 0.2s ease;
}

.btn-continue:hover {
  border-bottom-color: var(--sl-ink);
}

.btn-go-catalog:focus-visible,
.btn-checkout:focus-visible,
.btn-checkout-secondary:focus-visible,
.btn-continue:focus-visible,
.qty-btn:focus-visible,
.btn-remove:focus-visible,
.t-close:focus-visible,
.t-link:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

/* ТОСТ */
.template-toast {
  position: fixed;
  top: 80px;
  left: 50%;
  z-index: 1000;
  transform: translateX(-50%);
  width: min(460px, calc(100vw - 1.5rem));
  display: flex;
  align-items: flex-start;
  gap: 0.9rem;
  padding: 1rem 1rem 1rem 1.25rem;
  background: #fff;
  border: 1px solid var(--sl-line);
  border-left: 4px solid var(--sl-leaf);
  box-shadow: 0 24px 48px rgba(20, 33, 15, 0.18);
}

.t-content {
  flex: 1;
}

.t-content p {
  margin: 0 0 0.4rem;
  font-weight: 700;
  color: var(--sl-ink);
}

.t-content .t-link {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--sl-leaf);
  border-bottom: 1px solid currentColor;
}

.t-close {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  padding: 0;
  background: transparent;
  border: 1px solid var(--sl-line);
  cursor: pointer;
  transition: background 0.2s ease;
}

.t-close:hover {
  background: var(--sl-paper);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
}

/* ИКОНКИ — монохром под палитру */
.t-icon,
.close-icon,
.empty-icon-img,
.item-icon,
.qty-icon,
.remove-icon,
.btn-icon,
.supplier-icon {
  object-fit: contain;
}

.close-icon,
.empty-icon-img,
.item-icon,
.qty-icon,
.btn-icon,
.supplier-icon {
  filter: grayscale(1) brightness(0.35);
}

.t-icon,
.close-icon,
.remove-icon,
.btn-icon {
  width: 18px;
  height: 18px;
}

.qty-icon {
  width: 14px;
  height: 14px;
}

.empty-icon-img {
  width: 44px;
}

.item-icon {
  width: 24px;
}

.supplier-icon {
  width: 14px;
  height: 14px;
  flex: 0 0 auto;
}

/* АДАПТИВ */
@media (max-width: 900px) {
  .cart-layout {
    grid-template-columns: 1fr;
  }

  .order-summary {
    position: static;
  }
}

@media (max-width: 600px) {
  .page {
    padding-top: 0.75rem;
  }

  .cart-item-card {
    grid-template-columns: 44px minmax(0, 1fr);
    gap: 0.9rem;
    padding: 1.1rem 1rem;
  }

  .cart-item-image {
    width: 44px;
    height: 44px;
  }

  .cart-item-controls {
    grid-column: 1 / -1;
    grid-template-columns: 1fr auto auto;
    justify-items: start;
    align-items: center;
    padding-top: 0.9rem;
    border-top: 1px solid var(--sl-line);
  }

  .item-price-unit {
    grid-column: 1 / -1;
  }

  .qty-control {
    grid-column: 1;
  }

  .order-summary {
    padding: 1.25rem 1rem;
  }
}
</style>
