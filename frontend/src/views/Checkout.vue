<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'

const router = useRouter()
const authStore = useAuthStore()
const store = useShopStore()

const isLoading = ref(false)
const isSubmitting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const cartItems = computed(() => store.state.cartItems)

const cartTotal = computed(() =>
  cartItems.value.reduce((sum, item) => sum + Number(item.product.price) * item.quantity, 0),
)

const groupedSuppliers = computed(() => {
  const map = new Map<number, { id: number; name: string; amount: number }>()

  for (const item of cartItems.value) {
    const supplier = item.product.enterprise
    if (!supplier) continue

    const current = map.get(supplier.id) ?? { id: supplier.id, name: supplier.short_name, amount: 0 }
    current.amount += Number(item.product.price) * item.quantity
    map.set(supplier.id, current)
  }

  return Array.from(map.values())
})

const orderType = ref('Обычный заказ')
const deliveryNote = ref('Доставить в рабочие часы')

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }

  isLoading.value = true
  try {
    await Promise.all([store.fetchCart(), store.fetchProducts()])
  } finally {
    isLoading.value = false
  }
})

const submitCheckout = async () => {
  if (isSubmitting.value) return
  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const result = await store.checkoutCart()
    if (result.orders.length === 0) {
      errorMessage.value = 'В корзине нет товаров для оформления.'
      return
    }

    successMessage.value = `Заказ оформлен. Создано заказов: ${result.orders.length}.`
    setTimeout(() => router.push('/my-orders'), 1600)
  } catch (error: any) {
    errorMessage.value = error?.message || 'Не удалось оформить заказ.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="checkout-page">
    <section class="hero-card">
      <div>
        <p class="eyebrow"><span class="eyebrow-num" aria-hidden="true">Шаг 02 /</span> Проверка заказа</p>
        <h1 class="page-title">Оформление заказа</h1>
        <p class="page-text">Проверьте состав, поставщиков и сумму перед отправкой заказа.</p>
      </div>
      <div class="hero-total">
        <span>К оплате</span>
        <strong>{{ cartTotal.toFixed(0) }} ₽</strong>
      </div>
    </section>

    <div v-if="isLoading" class="state-box">Загрузка корзины...</div>

    <div v-else-if="cartItems.length === 0" class="state-box">
      <p>Корзина пуста. Сначала добавьте товары в каталоге.</p>
      <router-link to="/catalog" class="primary-link">Перейти в каталог</router-link>
    </div>

    <div v-else class="checkout-layout">
      <section class="card-list">
        <p class="block-kicker">Состав заказа</p>
        <div v-for="item in cartItems" :key="item.id" class="order-row">
          <div>
            <h2>{{ item.product.name }}</h2>
            <p>{{ item.product.enterprise?.short_name }} · {{ item.product.category?.name }}</p>
          </div>
          <div class="row-meta">
            <span>{{ item.quantity }} кг</span>
            <strong>{{ (Number(item.product.price) * item.quantity).toFixed(0) }} ₽</strong>
          </div>
        </div>
      </section>

      <aside class="summary-card">
        <p class="block-kicker">Детали</p>
        <div class="field">
          <label>Тип заказа</label>
          <input v-model="orderType" type="text" />
        </div>

        <div class="field">
          <label>Комментарий к доставке</label>
          <textarea v-model="deliveryNote" rows="4"></textarea>
        </div>

        <div class="summary-list">
          <p class="summary-list-label">Поставщики</p>
          <div v-for="supplier in groupedSuppliers" :key="supplier.id" class="summary-line">
            <span>{{ supplier.name }}</span>
            <strong>{{ supplier.amount.toFixed(0) }} ₽</strong>
          </div>
        </div>

        <div v-if="errorMessage" class="message message--error">{{ errorMessage }}</div>
        <div v-if="successMessage" class="message message--success">{{ successMessage }}</div>

        <button class="checkout-btn" :disabled="isSubmitting" @click="submitCheckout">
          {{ isSubmitting ? 'Оформляем...' : 'Подтвердить заказ' }}
        </button>
        <router-link to="/cart" class="secondary-link">Вернуться в корзину</router-link>
      </aside>
    </div>
  </main>
</template>

<style scoped>
.checkout-page {
  display: grid;
  gap: 1.25rem;
  padding: 1.25rem 0 2rem;
  color: var(--sl-ink);
}

p,
h1,
h2 {
  margin: 0;
}

/* ШАПКА СТРАНИЦЫ */
.hero-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
}

.hero-card > div:first-child {
  padding: clamp(1.25rem, 3vw, 2rem) clamp(1.25rem, 3vw, 2.25rem);
}

.eyebrow,
.block-kicker {
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

.page-text {
  margin-top: 0.75rem;
  max-width: 56ch;
  color: var(--sl-muted);
}

.hero-total {
  min-width: 240px;
  display: grid;
  align-content: center;
  gap: 0.5rem;
  padding: 1.5rem clamp(1.25rem, 3vw, 2.25rem);
  color: #fff;
  background:
    repeating-linear-gradient(135deg, rgba(198, 236, 154, 0.05) 0 1px, transparent 1px 14px),
    var(--sl-forest);
}

.hero-total span {
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-lime);
}

.hero-total strong {
  font-family: var(--sl-display);
  font-size: clamp(1.6rem, 3vw, 2.2rem);
  font-weight: 600;
  line-height: 1.1;
  white-space: nowrap;
}

/* СОСТОЯНИЯ */
.state-box {
  display: grid;
  justify-items: start;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  color: var(--sl-muted);
  font-weight: 600;
}

.state-box p {
  color: var(--sl-ink);
}

/* РАСКЛАДКА */
.checkout-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(0, 0.9fr);
  gap: 1.25rem;
  align-items: start;
}

.card-list,
.summary-card {
  padding: 1.5rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
}

.card-list .block-kicker,
.summary-card .block-kicker {
  padding-bottom: 0.9rem;
  margin-bottom: 0;
  border-bottom: 1px solid var(--sl-line);
}

/* СТРОКИ ЗАКАЗА */
.order-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 0.75rem;
  margin: 0 -0.75rem;
  border-bottom: 1px solid var(--sl-line);
  transition: background 0.2s ease;
}

.order-row:hover {
  background: #fff;
}

.order-row:last-child {
  border-bottom: none;
}

.order-row h2 {
  margin-bottom: 0.3rem;
  font-family: inherit;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0;
  color: var(--sl-ink);
}

.order-row p {
  font-size: 0.88rem;
  color: var(--sl-muted);
}

.row-meta {
  display: grid;
  justify-items: end;
  gap: 0.25rem;
  white-space: nowrap;
}

.row-meta span {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--sl-muted);
}

.row-meta strong {
  font-family: var(--sl-display);
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--sl-ink);
}

/* ПРАВАЯ ПАНЕЛЬ */
.summary-card {
  position: sticky;
  top: 1rem;
  border-top: 3px solid var(--sl-ink);
}

.summary-card .block-kicker {
  margin-bottom: 1.25rem;
}

.field {
  display: grid;
  gap: 0.45rem;
  margin-bottom: 1rem;
}

.field label,
.summary-list-label {
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.field input,
.field textarea {
  width: 100%;
  border-radius: 0;
  border: 1px solid var(--sl-line);
  background: #fff;
}

.field textarea {
  resize: vertical;
}

.summary-list {
  display: grid;
  margin: 0.5rem 0 1.25rem;
  border-bottom: 2px solid var(--sl-ink);
}

.summary-list-label {
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--sl-line);
}

.summary-line {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--sl-line);
  font-size: 0.92rem;
}

.summary-line:last-child {
  border-bottom: none;
}

.summary-line strong {
  white-space: nowrap;
}

.message {
  padding: 0.8rem 1rem;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
  font-weight: 600;
}

.message--error {
  background: #fbeaea;
  border: 1px solid #b3261e;
  color: #b3261e;
}

.message--success {
  background: var(--sl-lime);
  border: 1px solid var(--sl-lime);
  color: var(--sl-ink);
}

/* КНОПКИ */
.checkout-btn,
.secondary-link,
.primary-link {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  border-radius: 0;
  padding: 0.85rem 1.2rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.checkout-btn,
.primary-link {
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
}

.checkout-btn {
  width: 100%;
  margin-bottom: 0.5rem;
}

.checkout-btn:hover:not(:disabled),
.primary-link:hover {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.checkout-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.secondary-link {
  width: 100%;
  background: transparent;
  color: var(--sl-ink);
  border: 1px solid var(--sl-ink);
}

.secondary-link:hover {
  background: var(--sl-ink);
  color: #fff;
}

.checkout-btn:focus-visible,
.secondary-link:focus-visible,
.primary-link:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

/* АДАПТИВ */
@media (max-width: 900px) {
  .checkout-layout {
    grid-template-columns: 1fr;
  }

  .summary-card {
    position: static;
  }
}

@media (max-width: 640px) {
  .checkout-page {
    padding-top: 0.75rem;
  }

  .hero-card {
    grid-template-columns: 1fr;
  }

  .hero-total {
    min-width: 0;
  }

  .card-list,
  .summary-card {
    padding: 1.25rem 1rem;
  }

  .order-row {
    flex-direction: column;
    gap: 0.5rem;
  }

  .row-meta {
    width: 100%;
    grid-auto-flow: column;
    justify-content: space-between;
    align-items: baseline;
  }
}
</style>
