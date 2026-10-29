<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getApiErrorMessage } from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore, type CartItem } from '@/stores/shopStore'
import {
  AppButton,
  AppIcon,
  AppSection,
  EmptyState,
  FormField,
  LoadingState,
  PageHeader,
  ProductThumb,
} from '@/components/ui'
import { formatNumber, formatPrice, pluralize } from '@/utils/format'

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

/* Состав заказа по поставщикам — только для отображения */
const lineTotal = (item: CartItem) => Number(item.product.price) * item.quantity

const supplierBlocks = computed(() => {
  const map = new Map<number, { id: number; name: string; items: CartItem[]; amount: number }>()
  for (const item of cartItems.value) {
    const id = item.product.enterprise?.id ?? 0
    const block = map.get(id) ?? {
      id,
      name: item.product.enterprise?.short_name || 'Поставщик не указан',
      items: [],
      amount: 0,
    }
    block.items.push(item)
    block.amount += lineTotal(item)
    map.set(id, block)
  }
  return Array.from(map.values())
})

const steps = [
  { label: 'Корзина', state: 'done' },
  { label: 'Проверка заказа', state: 'current' },
  { label: 'Заказ отправлен', state: 'next' },
] as const

const stepState = (index: number) => {
  if (successMessage.value) return index < 2 ? 'done' : 'current'
  return steps[index]?.state ?? 'next'
}

/*
 * «Тип заказа» и «Комментарий к доставке» пока не передаются на backend:
 * store.checkoutCart() отправляет только поставщика и позиции.
 */
const orderType = ref('Обычный заказ')
const deliveryNote = ref('Доставить в рабочие часы')
const localOnlyHint = 'Пока не передаётся поставщику — значение хранится только на этой странице.'

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
  } catch (error: unknown) {
    errorMessage.value = getApiErrorMessage(error, 'Не удалось оформить заказ.')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="page">
    <PageHeader
      eyebrow="Оформление"
      title="Оформление заказа"
      description="Проверьте состав, поставщиков и сумму перед отправкой заказа."
      back-to="/cart"
      back-label="Вернуться в корзину"
    >
      <ol class="steps" aria-label="Этапы оформления">
        <li
          v-for="(step, index) in steps"
          :key="step.label"
          class="step"
          :class="`step--${stepState(index)}`"
          :aria-current="stepState(index) === 'current' ? 'step' : undefined"
        >
          <span class="step__dot ui-num">
            <AppIcon v-if="stepState(index) === 'done'" name="check" :size="14" :stroke-width="2.6" />
            <template v-else>{{ index + 1 }}</template>
          </span>
          <span class="step__label">{{ step.label }}</span>
        </li>
      </ol>
    </PageHeader>

    <!-- Успех -->
    <section v-if="successMessage" class="success ui-card" role="status" aria-live="polite">
      <span class="success__icon"><AppIcon name="check-circle" :size="32" /></span>
      <h2 class="success__title">Заказ отправлен поставщикам</h2>
      <p class="success__text">{{ successMessage }}</p>
      <p class="success__hint">Статус заказа можно отслеживать на странице «Мои заказы» — сейчас мы её откроем.</p>
      <div class="success__actions">
        <AppButton to="/cabinet/orders" icon-right="arrow-right">Мои заказы</AppButton>
        <AppButton to="/catalog" variant="secondary" icon="store">Вернуться в каталог</AppButton>
      </div>
    </section>

    <LoadingState v-else-if="isLoading" variant="skeleton" :rows="4" label="Загрузка корзины…" />

    <div v-else-if="cartItems.length === 0" class="ui-card">
      <EmptyState icon="cart" title="Корзина пуста" description="Сначала добавьте товары в каталоге.">
        <AppButton to="/catalog" icon="store">Перейти в каталог</AppButton>
      </EmptyState>
    </div>

    <div v-else class="checkout-layout">
      <AppSection
        title="Состав заказа"
        :description="`${cartItems.length} ${pluralize(cartItems.length, ['позиция', 'позиции', 'позиций'])} · заказ будет разделён по поставщикам`"
        flush
      >
        <div v-for="block in supplierBlocks" :key="block.id" class="supplier">
          <header class="supplier__head">
            <span class="supplier__icon"><AppIcon name="building" :size="16" /></span>
            <h3 class="supplier__name">{{ block.name }}</h3>
            <span class="supplier__subtotal ui-num">
              <span class="ui-muted">Подытог</span> {{ formatPrice(block.amount) }}
            </span>
          </header>
          <ul class="lines">
            <li v-for="item in block.items" :key="item.id" class="line">
              <ProductThumb :category="item.product.category?.name" size="sm" />
              <div class="line__info">
                <p class="line__name">{{ item.product.name }}</p>
                <p class="line__meta">
                  {{ item.product.category?.name || 'Без категории' }} ·
                  <span class="ui-num">{{ formatPrice(item.product.price) }}/кг</span>
                </p>
              </div>
              <span class="line__qty ui-num">{{ formatNumber(item.quantity) }} кг</span>
              <strong class="line__sum ui-num">{{ formatPrice(lineTotal(item)) }}</strong>
            </li>
          </ul>
        </div>
      </AppSection>

      <aside class="summary ui-card" aria-labelledby="checkout-summary-title">
        <h2 id="checkout-summary-title" class="summary__title">Детали заказа</h2>

        <div class="summary__form">
          <FormField label="Тип заказа" :hint="localOnlyHint" v-slot="{ id, describedBy }">
            <input :id="id" v-model="orderType" type="text" :aria-describedby="describedBy" />
          </FormField>

          <FormField label="Комментарий к доставке" :hint="localOnlyHint" v-slot="{ id, describedBy }">
            <textarea :id="id" v-model="deliveryNote" rows="3" :aria-describedby="describedBy"></textarea>
          </FormField>

          <div class="summary__suppliers">
            <p class="ui-label">Поставщики</p>
            <div v-for="supplier in groupedSuppliers" :key="supplier.id" class="summary__line">
              <span>{{ supplier.name }}</span>
              <strong class="ui-num">{{ formatPrice(supplier.amount) }}</strong>
            </div>
          </div>

          <div class="summary__total">
            <span>К оплате</span>
            <strong class="ui-num">{{ formatPrice(cartTotal) }}</strong>
          </div>

          <p v-if="errorMessage" class="summary__error" role="alert">
            <AppIcon name="alert-circle" :size="18" />
            <span>{{ errorMessage }}</span>
          </p>

          <AppButton block size="lg" icon="check" :loading="isSubmitting" @click="submitCheckout">
            {{ isSubmitting ? 'Оформляем…' : 'Подтвердить заказ' }}
          </AppButton>
          <AppButton to="/cart" block variant="ghost" icon="arrow-left">Вернуться в корзину</AppButton>
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

/* ── Этапы ─────────────────────────────────── */
.steps {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.5rem;
  margin: 0.6rem 0 0;
  padding: 0;
  list-style: none;
}

.step {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--c-muted);
  font-size: var(--fs-sm);
  font-weight: 600;
}

.step__dot {
  display: grid;
  place-items: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1px solid var(--c-border-strong);
  background: var(--c-surface);
  font-size: var(--fs-xs);
  font-weight: 700;
}

.step--done {
  color: var(--c-text-2);
}

.step--done .step__dot {
  border-color: var(--c-accent-200);
  background: var(--c-accent-100);
  color: var(--c-accent-700);
}

.step--current {
  color: var(--c-text);
}

.step--current .step__dot {
  border-color: var(--c-brand-800);
  background: var(--c-brand-800);
  color: #fff;
}

/* ── Раскладка ─────────────────────────────── */
.checkout-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 380px;
  gap: 1.5rem;
  align-items: start;
}

/* ── Состав по поставщикам ─────────────────── */
.supplier + .supplier {
  border-top: 1px solid var(--c-border);
}

.supplier__head {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.85rem 1.25rem;
  background: var(--c-surface-2);
  border-bottom: 1px solid var(--c-border);
}

.supplier__icon {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  flex: 0 0 auto;
  border-radius: var(--r-sm);
  background: var(--c-accent-50);
  color: var(--c-accent-700);
}

.supplier__name {
  flex: 1;
  min-width: 0;
  font-size: var(--fs-md);
  overflow-wrap: anywhere;
}

.supplier__subtotal {
  font-weight: 700;
  white-space: nowrap;
}

.supplier__subtotal .ui-muted {
  margin-right: 0.35rem;
  font-size: var(--fs-xs);
  font-weight: 600;
}

.lines {
  margin: 0;
  padding: 0;
  list-style: none;
}

.line {
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr) auto 7rem;
  align-items: center;
  gap: 0.9rem;
  padding: 0.85rem 1.25rem;
}

.line + .line {
  border-top: 1px solid var(--c-border);
}

.line__info {
  min-width: 0;
}

.line__name {
  font-weight: 700;
  overflow-wrap: anywhere;
}

.line__meta {
  color: var(--c-muted);
  font-size: var(--fs-sm);
}

.line__qty {
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  font-weight: 600;
  white-space: nowrap;
}

.line__sum {
  text-align: right;
  white-space: nowrap;
}

/* ── Сводка ────────────────────────────────── */
.summary {
  position: sticky;
  top: calc(var(--header-h) + 1rem);
  display: grid;
  gap: 1.1rem;
  padding: 1.5rem;
}

.summary__title {
  font-size: var(--fs-xl);
}

.summary__form {
  display: grid;
  gap: 1.1rem;
}

.summary__suppliers {
  display: grid;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--c-border);
}

.summary__line {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  font-size: var(--fs-sm);
}

.summary__line span {
  min-width: 0;
  color: var(--c-text-2);
  overflow-wrap: anywhere;
}

.summary__line strong {
  white-space: nowrap;
}

.summary__total {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--c-border);
  font-weight: 700;
}

.summary__total strong {
  font-size: var(--fs-2xl);
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--c-brand-900);
}

.summary__error {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.7rem 0.85rem;
  border-radius: var(--r-sm);
  background: var(--c-danger-bg);
  color: var(--c-danger-600);
  font-size: var(--fs-sm);
  font-weight: 600;
  line-height: 1.45;
}

.summary__error .app-icon {
  flex: 0 0 auto;
  margin-top: 0.1rem;
}

/* ── Успех ─────────────────────────────────── */
.success {
  display: grid;
  justify-items: center;
  gap: 0.6rem;
  padding: clamp(2rem, 6vw, 3.5rem) 1.5rem;
  text-align: center;
}

.success__icon {
  display: grid;
  place-items: center;
  width: 64px;
  height: 64px;
  margin-bottom: 0.4rem;
  border-radius: 50%;
  background: var(--c-success-bg);
  color: var(--c-success);
}

.success__title {
  font-size: var(--fs-2xl);
}

.success__text {
  font-weight: 600;
  color: var(--c-text-2);
}

.success__hint {
  max-width: 460px;
  color: var(--c-muted);
  font-size: var(--fs-sm);
}

.success__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.6rem;
  margin-top: 0.75rem;
}

/* ── Адаптив ───────────────────────────────── */
@media (max-width: 1024px) {
  .checkout-layout {
    grid-template-columns: 1fr;
  }

  .summary {
    position: static;
  }
}

@media (max-width: 560px) {
  .supplier__head,
  .line {
    padding-inline: 1rem;
  }

  .supplier__head {
    flex-wrap: wrap;
  }

  .line {
    grid-template-columns: 40px minmax(0, 1fr) auto;
    grid-template-areas:
      'thumb info info'
      'thumb qty sum';
    row-gap: 0.35rem;
  }

  .line > :first-child {
    grid-area: thumb;
    align-self: start;
  }

  .line__info {
    grid-area: info;
  }

  .line__qty {
    grid-area: qty;
  }

  .line__sum {
    grid-area: sum;
  }

  .summary {
    padding: 1.25rem;
  }

  .success__actions > * {
    flex: 1 1 100%;
  }
}
</style>
