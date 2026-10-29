<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useShopStore, type CartItem } from '@/stores/shopStore'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from '@/composables/useToast'
import {
  AppButton,
  AppIcon,
  EmptyState,
  LoadingState,
  PageHeader,
  ProductThumb,
  QuantityStepper,
} from '@/components/ui'
import { formatNumber, formatPrice, pluralize } from '@/utils/format'

const store = useShopStore()
const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()

const isLoading = ref(false)
const isCheckingOut = ref(false)
const orderError = ref<string | null>(null)
/* шаблон сохранён — показываем ссылку на «Мои заказы» в сводке */
const templateSaved = ref(false)

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

const lineTotal = (item: CartItem) => Number(item.product.price) * item.quantity

/* группировка позиций по поставщику — только для отображения */
const supplierGroups = computed(() => {
  const map = new Map<number, { id: number; name: string; items: CartItem[]; amount: number }>()
  for (const item of cartItems.value) {
    const supplier = item.product.enterprise
    const id = supplier?.id ?? 0
    const group = map.get(id) ?? { id, name: supplier?.short_name || 'Поставщик не указан', items: [], amount: 0 }
    group.items.push(item)
    group.amount += lineTotal(item)
    map.set(id, group)
  }
  return Array.from(map.values())
})

const positionsLabel = computed(() => {
  const n = cartItems.value.length
  return `${n} ${pluralize(n, ['позиция', 'позиции', 'позиций'])}`
})

const showOrderSentAndRedirect = () => {
  toast.success('Ваш заказ отправлен', 'Открываем страницу «Мои заказы»…')
  setTimeout(() => {
    router.push('/my-orders')
  }, 1200)
}

const handleDecrease = async (item: CartItem) => {
  const newQty = item.quantity - 1
  if (newQty <= 0) {
    await store.removeFromCart(item.product_id)
  } else {
    await store.setCartQuantity(item.product_id, newQty)
  }
}

const handleIncrease = async (item: CartItem) => {
  await store.setCartQuantity(item.product_id, item.quantity + 1)
}

/* Степпер: кнопки ±1 работают как раньше, ручной ввод отправляется после паузы */
const quantityTimers = new Map<number, number>()

const handleQuantityChange = (item: CartItem, value: number) => {
  const pending = quantityTimers.get(item.product_id)
  if (pending) {
    window.clearTimeout(pending)
    quantityTimers.delete(item.product_id)
  }
  if (value === item.quantity) return
  if (value === item.quantity + 1) {
    handleIncrease(item)
    return
  }
  if (value === item.quantity - 1) {
    handleDecrease(item)
    return
  }
  quantityTimers.set(
    item.product_id,
    window.setTimeout(() => {
      quantityTimers.delete(item.product_id)
      store.setCartQuantity(item.product_id, value)
    }, 600),
  )
}

onBeforeUnmount(() => {
  quantityTimers.forEach((timer) => window.clearTimeout(timer))
  quantityTimers.clear()
})

const handleRemove = async (productId: number) => {
  const name = cartItems.value.find((i) => i.product_id === productId)?.product.name
  await store.removeFromCart(productId)
  if (store.state.cartItems.some((i) => i.product_id === productId)) {
    toast.error('Не удалось удалить товар', 'Попробуйте ещё раз немного позже.')
  } else {
    toast.success('Товар удалён из корзины', name)
  }
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
  templateSaved.value = true
  toast.success('Шаблон заказа создан', 'Использовать его можно на странице «Мои заказы».')
}
</script>

<template>
  <div class="page">
    <PageHeader
      eyebrow="Покупки"
      title="Корзина"
      description="Проверьте позиции и количество. Заказ оформляется отдельно по каждому поставщику."
    >
      <p v-if="!isLoading && cartItems.length" class="page-meta ui-num">
        {{ positionsLabel }} · {{ supplierGroups.length }}
        {{ pluralize(supplierGroups.length, ['поставщик', 'поставщика', 'поставщиков']) }}
      </p>
    </PageHeader>

    <LoadingState v-if="isLoading" variant="skeleton" :rows="4" label="Загрузка корзины…" />

    <div v-else-if="cartItems.length === 0" class="ui-card">
      <EmptyState
        icon="cart"
        title="Ваша корзина пуста"
        description="Добавьте товары из каталога поставщиков — они появятся здесь, сгруппированные по поставщикам."
      >
        <AppButton to="/catalog" icon="store">Перейти в каталог</AppButton>
      </EmptyState>
    </div>

    <div v-else class="cart-layout">
      <div class="groups">
        <section
          v-for="group in supplierGroups"
          :key="group.id"
          class="group ui-card"
          :aria-labelledby="`supplier-${group.id}`"
        >
          <header class="group__head">
            <span class="group__icon"><AppIcon name="building" :size="18" /></span>
            <div class="group__titles">
              <h2 :id="`supplier-${group.id}`" class="group__title">
                <RouterLink v-if="group.id" :to="`/suppliers/${group.id}`" class="group__link">{{ group.name }}</RouterLink>
                <template v-else>{{ group.name }}</template>
              </h2>
              <p class="group__meta ui-num">
                {{ group.items.length }} {{ pluralize(group.items.length, ['позиция', 'позиции', 'позиций']) }}
              </p>
            </div>
            <p class="group__amount ui-num">{{ formatPrice(group.amount) }}</p>
          </header>

          <ul class="items">
            <li v-for="item in group.items" :key="item.id" class="item">
              <ProductThumb :category="item.product.category?.name" class="item__thumb" />

              <div class="item__info">
                <h3 class="item__name">{{ item.product.name }}</h3>
                <p class="item__meta">
                  <span v-if="item.product.category">{{ item.product.category.name }}</span>
                  <span v-if="item.product.category && item.product.enterprise" aria-hidden="true">·</span>
                  <span v-if="item.product.enterprise">{{ item.product.enterprise.short_name }}</span>
                </p>
                <p v-if="item.product.description" class="item__desc">{{ item.product.description }}</p>
              </div>

              <p class="item__price ui-num">
                {{ formatPrice(item.product.price) }}<span class="ui-muted">/кг</span>
              </p>

              <QuantityStepper
                class="item__qty"
                size="sm"
                unit="кг"
                :model-value="item.quantity"
                :label="`Количество: ${item.product.name}`"
                @update:model-value="handleQuantityChange(item, $event)"
              />

              <p class="item__sum ui-num">{{ formatPrice(lineTotal(item)) }}</p>

              <AppButton
                class="item__remove"
                variant="danger-ghost"
                size="sm"
                icon="trash"
                icon-only
                :label="`Удалить из корзины: ${item.product.name}`"
                @click="handleRemove(item.product_id)"
              />
            </li>
          </ul>
        </section>
      </div>

      <aside class="summary ui-card" aria-labelledby="summary-title">
        <div class="summary__head">
          <p class="ui-eyebrow">Сводка</p>
          <h2 id="summary-title" class="summary__title">Итог заказа</h2>
        </div>

        <ul class="summary__rows">
          <li v-for="item in cartItems" :key="item.id" class="summary__row">
            <span class="summary__name">
              {{ item.product.name }}
              <span class="ui-muted ui-num">× {{ formatNumber(item.quantity) }} кг</span>
            </span>
            <span class="ui-num">{{ formatPrice(lineTotal(item)) }}</span>
          </li>
        </ul>

        <div class="summary__total">
          <span>Итого</span>
          <strong class="ui-num">{{ formatPrice(cartTotal) }}</strong>
        </div>

        <p v-if="supplierGroups.length > 1" class="summary__note">
          <AppIcon name="info" :size="16" />
          <span>
            Будет создано {{ supplierGroups.length }}
            {{ pluralize(supplierGroups.length, ['заказ', 'заказа', 'заказов']) }} — по одному на каждого поставщика.
          </span>
        </p>

        <p v-if="orderError" class="summary__error" role="alert">
          <AppIcon name="alert-circle" :size="18" />
          <span>{{ orderError }}</span>
        </p>

        <div class="summary__actions">
          <AppButton block size="lg" icon-right="arrow-right" :loading="isCheckingOut" @click="handleCheckout">
            {{ isCheckingOut ? 'Оформление…' : 'Оформить заказ' }}
          </AppButton>
          <AppButton block variant="secondary" to="/checkout" icon="clipboard-list">Перейти к проверке</AppButton>
          <AppButton block variant="secondary" icon="file-text" @click="handleCreateTemplate">
            Создать шаблон заказа
          </AppButton>
          <p v-if="templateSaved" class="summary__saved" role="status">
            <AppIcon name="check-circle" :size="16" />
            <span>
              Шаблон сохранён.
              <RouterLink to="/cabinet/orders" class="summary__link">Перейти к заказам</RouterLink>
            </span>
          </p>
          <AppButton block variant="ghost" to="/catalog" icon="arrow-left">Продолжить покупки</AppButton>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.page {
  display: grid;
  gap: 1.5rem;
}

.page-meta {
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  font-weight: 600;
}

/* ── Раскладка ─────────────────────────────── */
.cart-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 1.5rem;
  align-items: start;
}

.groups {
  display: grid;
  gap: 1.25rem;
  min-width: 0;
}

/* ── Группа поставщика ─────────────────────── */
.group {
  overflow: hidden;
}

.group__head {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background: var(--c-surface-2);
  border-bottom: 1px solid var(--c-border);
}

.group__icon {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  width: 36px;
  height: 36px;
  border-radius: var(--r-sm);
  background: var(--c-accent-50);
  color: var(--c-accent-700);
}

.group__titles {
  flex: 1;
  min-width: 0;
}

.group__title {
  font-size: var(--fs-md);
  overflow-wrap: anywhere;
}

.group__link {
  transition: color var(--dur) var(--ease);
}

.group__link:hover {
  color: var(--c-accent-700);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.group__meta {
  color: var(--c-muted);
  font-size: var(--fs-xs);
}

.group__amount {
  font-weight: 700;
  white-space: nowrap;
}

/* ── Позиция ───────────────────────────────── */
.items {
  margin: 0;
  padding: 0;
  list-style: none;
}

.item {
  display: grid;
  grid-template-columns: 56px minmax(0, 1fr) auto auto 7rem auto;
  grid-template-areas: 'thumb info price qty sum remove';
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--c-border);
}

.item:last-child {
  border-bottom: none;
}

.item__thumb {
  grid-area: thumb;
}

.item__info {
  grid-area: info;
  display: grid;
  gap: 0.2rem;
  min-width: 0;
}

.item__name {
  font-size: var(--fs-md);
  overflow-wrap: anywhere;
}

.item__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  color: var(--c-muted);
  font-size: var(--fs-sm);
}

.item__desc {
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item__price {
  grid-area: price;
  font-size: var(--fs-sm);
  font-weight: 600;
  white-space: nowrap;
}

.item__qty {
  grid-area: qty;
}

.item__sum {
  grid-area: sum;
  font-weight: 800;
  text-align: right;
  white-space: nowrap;
}

.item__remove {
  grid-area: remove;
}

/* ── Сводка ────────────────────────────────── */
.summary {
  position: sticky;
  top: calc(var(--header-h) + 1rem);
  display: grid;
  gap: 1.1rem;
  padding: 1.5rem;
}

.summary__head {
  display: grid;
  gap: 0.25rem;
}

.summary__title {
  font-size: var(--fs-xl);
}

.summary__rows {
  display: grid;
  gap: 0.6rem;
  max-height: 240px;
  margin: 0;
  padding: 0 0 1rem;
  overflow-y: auto;
  list-style: none;
  border-bottom: 1px solid var(--c-border);
  font-size: var(--fs-sm);
}

.summary__row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.summary__name {
  min-width: 0;
  color: var(--c-text-2);
  overflow-wrap: anywhere;
}

.summary__row > .ui-num {
  font-weight: 600;
  white-space: nowrap;
}

.summary__total {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  font-weight: 700;
}

.summary__total strong {
  font-size: var(--fs-2xl);
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--c-brand-900);
}

.summary__note,
.summary__error,
.summary__saved {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.7rem 0.85rem;
  border-radius: var(--r-sm);
  font-size: var(--fs-sm);
  line-height: 1.45;
}

.summary__note .app-icon,
.summary__error .app-icon,
.summary__saved .app-icon {
  flex: 0 0 auto;
  margin-top: 0.1rem;
}

.summary__note {
  background: var(--c-info-bg);
  color: var(--c-info);
}

.summary__error {
  background: var(--c-danger-bg);
  color: var(--c-danger-600);
  font-weight: 600;
}

.summary__saved {
  background: var(--c-success-bg);
  color: var(--c-success);
}

.summary__link {
  font-weight: 700;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.summary__actions {
  display: grid;
  gap: 0.6rem;
}

/* ── Адаптив ───────────────────────────────── */
@media (max-width: 1180px) {
  .item {
    grid-template-columns: 56px minmax(0, 1fr) auto auto;
    grid-template-areas:
      'thumb info info remove'
      'thumb price qty sum';
    row-gap: 0.75rem;
  }
}

@media (max-width: 1024px) {
  .cart-layout {
    grid-template-columns: 1fr;
  }

  .summary {
    position: static;
  }
}

@media (max-width: 560px) {
  .group__head,
  .item {
    padding-inline: 1rem;
  }

  .item {
    grid-template-columns: 40px minmax(0, 1fr) auto;
    grid-template-areas:
      'thumb info remove'
      'price price price'
      'qty qty sum';
    column-gap: 0.75rem;
  }

  .item__thumb {
    width: 40px;
    height: 40px;
    align-self: start;
  }

  .item__remove {
    align-self: start;
  }

  .item__sum {
    font-size: var(--fs-lg);
  }

  .summary {
    padding: 1.25rem;
  }
}
</style>
