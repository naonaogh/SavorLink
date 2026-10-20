<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'

const router = useRouter()
const authStore = useAuthStore()
const store = useShopStore()

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }

  if (authStore.user?.role === 'SUPPLIER') {
    await Promise.all([store.fetchSupplierOrders(), store.fetchMyProducts()])
  } else {
    await Promise.all([store.fetchMyOrders(), store.fetchFavoriteProducts(), store.fetchFavoriteSuppliers()])
  }
})

const orders = computed(() =>
  authStore.user?.role === 'SUPPLIER' ? store.state.supplierOrders : store.state.myOrders,
)

const totalRevenue = computed(() =>
  orders.value.reduce((sum, order) => sum + Number(order.total_amount || 0), 0),
)

const completedOrders = computed(() =>
  orders.value.filter((order) => order.status === 'COMPLETED').length,
)

const activeOrders = computed(() =>
  orders.value.filter((order) => ['CREATED', 'CONFIRMED', 'IN_PROGRESS'].includes(order.status)).length,
)

const favoriteSuppliers = computed(() => store.state.favoriteSuppliers.length)
const favoriteProducts = computed(() => store.state.favoriteProducts.length)

const topProducts = computed(() => {
  const map = new Map<string, { name: string; qty: number; amount: number }>()

  for (const order of orders.value) {
    for (const item of order.items) {
      const name = item.product?.name || `Товар #${item.product_id}`
      const current = map.get(name) ?? { name, qty: 0, amount: 0 }
      current.qty += item.quantity
      current.amount += Number(item.price) * item.quantity
      map.set(name, current)
    }
  }

  return Array.from(map.values())
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 5)
})
</script>

<template>
  <main class="analytics-page">
    <section class="hero">
      <div>
        <p class="eyebrow">Аналитика</p>
        <h1>{{ authStore.user?.role === 'SUPPLIER' ? 'Показатели поставщика' : 'Показатели покупателя' }}</h1>
        <p>Ключевые цифры по заказам, позициям и избранному в одном дашборде.</p>
      </div>
      <div class="hero-card">
        <span>Всего заказов</span>
        <strong>{{ orders.length }}</strong>
      </div>
    </section>

    <section class="metrics">
      <article class="metric-card">
        <span>Оборот</span>
        <strong>{{ totalRevenue.toFixed(0) }} ₽</strong>
      </article>
      <article class="metric-card">
        <span>Завершено</span>
        <strong>{{ completedOrders }}</strong>
      </article>
      <article class="metric-card">
        <span>В работе</span>
        <strong>{{ activeOrders }}</strong>
      </article>
      <article class="metric-card">
        <span>Избранное</span>
        <strong>{{ favoriteSuppliers + favoriteProducts }}</strong>
      </article>
    </section>

    <div class="content-grid">
      <section class="panel">
        <h2>Топ позиций</h2>
        <div class="list">
          <div v-for="item in topProducts" :key="item.name" class="list-row">
            <span>{{ item.name }}</span>
            <strong>{{ item.amount.toFixed(0) }} ₽</strong>
          </div>
        </div>
      </section>

      <section class="panel">
        <h2>Краткая сводка</h2>
        <p v-if="authStore.user?.role === 'SUPPLIER'">
          У вас {{ orders.length }} заказов от покупателей. Следите за активными запросами и
          денежным потоком.
        </p>
        <p v-else>
          У вас {{ favoriteSuppliers }} избранных поставщиков и {{ favoriteProducts }} избранных
          товаров. Используйте аналитику, чтобы отслеживать самые нужные позиции.
        </p>
      </section>
    </div>
  </main>
</template>

<style scoped>
/* внешняя панель — в пару к сайдбару кабинета */
.analytics-page {
  display: grid;
  gap: 1.5rem;
  padding: clamp(1.25rem, 3vw, 2rem);
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
  color: var(--sl-ink);
}

/* ===== ШАПКА ===== */
.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.25rem 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--sl-line);
}

.eyebrow {
  margin: 0 0 0.6rem;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

.hero h1 {
  margin: 0;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  color: var(--sl-ink);
}

.hero p:not(.eyebrow) {
  margin: 0.75rem 0 0;
  max-width: 52ch;
  color: var(--sl-muted);
}

.hero-card {
  flex: 0 0 auto;
  min-width: 180px;
  display: grid;
  gap: 0.4rem;
  padding: 1rem 1.25rem;
  background: var(--sl-ink);
  border: 1px solid var(--sl-ink);
  box-shadow: inset 0 3px 0 var(--sl-lime);
}

.hero-card span {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-lime);
}

.hero-card strong {
  font-family: var(--sl-display);
  font-size: 2.2rem;
  font-weight: 600;
  line-height: 1;
  color: #fff;
}

/* ===== МЕТРИКИ ===== */
.metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1px;
  background: var(--sl-line);
  border: 1px solid var(--sl-line);
}

.metric-card {
  display: grid;
  gap: 0.75rem;
  padding: 1.15rem 1.25rem;
  background: #fff;
}

.metric-card span {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.metric-card strong {
  font-family: var(--sl-display);
  font-size: clamp(1.25rem, 2.2vw, 1.6rem);
  font-weight: 600;
  line-height: 1.1;
  color: var(--sl-ink);
  overflow-wrap: anywhere;
}

/* ===== ПАНЕЛИ ===== */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.panel {
  padding: 1.25rem;
  background: #fff;
  border: 1px solid var(--sl-line);
}

.panel h2 {
  margin: 0 0 0.75rem;
  padding-bottom: 0.85rem;
  border-bottom: 1px solid var(--sl-line);
  font-size: 1.05rem;
  color: var(--sl-ink);
}

.panel p {
  margin: 0;
  color: var(--sl-muted);
}

.list {
  display: grid;
}

.list:empty::before {
  content: 'Пока нет данных по заказам';
  padding: 0.75rem 0;
  color: var(--sl-muted);
  font-size: 0.92rem;
}

.list-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--sl-line);
}

.list-row:last-child {
  border-bottom: none;
}

.list-row span {
  min-width: 0;
  overflow-wrap: anywhere;
}

.list-row strong {
  font-family: var(--sl-display);
  font-size: 0.95rem;
  font-weight: 600;
  white-space: nowrap;
}

@media (max-width: 900px) {
  .hero {
    flex-direction: column;
    align-items: stretch;
  }

  .content-grid {
    grid-template-columns: 1fr;
  }

  .metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 420px) {
  .metric-card {
    padding: 1rem;
  }
}
</style>
