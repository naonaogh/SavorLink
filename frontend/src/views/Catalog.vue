<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore, type Supplier } from '@/stores/shopStore'
import { useRequireAuth } from '@/composables/useRequireAuth'

const router = useRouter()
const authStore = useAuthStore()
const store = useShopStore()
const requireAuth = useRequireAuth()

const toggleSupplierFavorite = (supplier: Supplier) => {
  if (!requireAuth()) return
  store.toggleFavoriteSupplier(supplier)
}

const search = ref('')
const selectedCategoryId = ref<number | null>(null)
const selectedRegion = ref('all')
const selectedCity = ref('all')

onMounted(async () => {
  await store.fetchSuppliers()
  if (authStore.token) {
    await Promise.all([
      store.fetchFavoriteProducts(),
      store.fetchFavoriteSuppliers(),
    ])
  }
})

const categories = computed(() => {
  const map = new Map<number, string>()

  for (const supplier of store.state.suppliers) {
    for (const product of supplier.products) {
      if (product.category?.id) {
        map.set(product.category.id, product.category.name)
      }
    }
  }

  return Array.from(map.entries()).map(([id, name]) => ({ id, name }))
})

const regions = computed(() =>
  Array.from(new Set(store.state.suppliers.map((s) => s.region).filter(Boolean) as string[]))
)

const availableCities = computed(() => {
  const list =
    selectedRegion.value === 'all'
      ? store.state.suppliers
      : store.state.suppliers.filter(s => s.region === selectedRegion.value)

  return Array.from(new Set(list.map((s) => s.city).filter(Boolean) as string[]))
})

watch(selectedRegion, () => {
  if (!availableCities.value.includes(selectedCity.value)) {
    selectedCity.value = 'all'
  }
})

const filteredSuppliers = computed(() => {
  const term = search.value.toLowerCase()

  return store.state.suppliers.filter(s => {
    const matchSearch =
      !term ||
      s.name.toLowerCase().includes(term) ||
      s.products.some(p => p.name.toLowerCase().includes(term))

    const matchCategory =
      selectedCategoryId.value === null ||
      s.products.some(p => p.category?.id === selectedCategoryId.value)

    const matchRegion =
      selectedRegion.value === 'all' || s.region === selectedRegion.value

    const matchCity =
      selectedCity.value === 'all' || s.city === selectedCity.value

    return matchSearch && matchCategory && matchRegion && matchCity
  })
})

const hasActiveFilters = computed(
  () =>
    search.value ||
    selectedCategoryId.value !== null ||
    selectedRegion.value !== 'all' ||
    selectedCity.value !== 'all'
)

const resetFilters = () => {
  search.value = ''
  selectedCategoryId.value = null
  selectedRegion.value = 'all'
  selectedCity.value = 'all'
}
</script>

<template>
  <main class="catalog-page">
    <section class="catalog-panel">
      <header class="page-head">
        <div>
          <p class="kicker">Каталог</p>
          <h1>Поставщики</h1>
        </div>

        <!-- КНОПКИ -->
        <div class="top-bar">
          <router-link to="/compare" class="compare-link">
            Сравнить ({{ store.state.comparisonSupplierIds.length }})
          </router-link>

          <button
            class="reset-btn"
            @click="resetFilters"
            :disabled="!hasActiveFilters"
          >
            Сбросить
          </button>
        </div>
      </header>

      <!-- ФИЛЬТРЫ -->
      <section class="filters">
        <input v-model="search" placeholder="Поиск..." />

        <select v-model="selectedCategoryId">
          <option :value="null">Категории</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">
            {{ c.name }}
          </option>
        </select>

        <select v-model="selectedRegion">
          <option value="all">Регион</option>
          <option v-for="r in regions" :key="r">
            {{ r }}
          </option>
        </select>

        <select v-model="selectedCity">
          <option value="all">Город</option>
          <option v-for="c in availableCities" :key="c">
            {{ c }}
          </option>
        </select>
      </section>

      <p class="result-count">Найдено: {{ filteredSuppliers.length }}</p>

      <!-- КАРТОЧКИ -->
      <section class="catalog-grid">
        <article
          v-for="supplier in filteredSuppliers"
          :key="supplier.id"
          class="card"
        >

          <!-- ❤️ -->
          <button
            class="fav"
            @click="toggleSupplierFavorite(supplier)"
          >
            {{ store.isSupplierFavorite(supplier.id) ? '❤️' : '🤍' }}
          </button>

          <div class="body" @click="router.push(`/suppliers/${supplier.id}`)">
            <div class="avatar">
              {{ supplier.name[0] }}
            </div>

            <h3>{{ supplier.name }}</h3>

            <div class="rating">
              ⭐ {{ supplier.rating.toFixed(1) }}
            </div>
          </div>

          <button
            class="btn"
            @click="router.push(`/suppliers/${supplier.id}`)"
          >
            Подробнее <span class="arrow" aria-hidden="true">→</span>
          </button>
        </article>
      </section>
    </section>
  </main>
</template>

<style scoped>
.catalog-page {
  display: grid;
  gap: 1.25rem;
  padding-bottom: 2rem;
  color: var(--sl-ink);
}

.catalog-panel {
  display: grid;
  gap: 1.25rem;
  padding: clamp(1.25rem, 3vw, 2.25rem);
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
}

/* ЗАГОЛОВОК */
.page-head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem 2rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--sl-line);
}

.kicker {
  margin: 0 0 0.6rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

.page-head h1 {
  margin: 0;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  color: var(--sl-ink);
}

/* TOP */
.top-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.compare-link,
.reset-btn,
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.7rem 1.2rem;
  border-radius: 0;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.compare-link {
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
}

.compare-link:hover {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.reset-btn {
  background: transparent;
  color: var(--sl-ink);
  border: 1px solid var(--sl-ink);
}

.reset-btn:hover:not(:disabled) {
  background: var(--sl-ink);
  color: #fff;
}

.reset-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.compare-link:focus-visible,
.reset-btn:focus-visible,
.btn:focus-visible,
.fav:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

/* FILTERS */
.filters {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) repeat(3, minmax(0, 1fr));
  gap: 0.5rem;
}

.filters input,
.filters select {
  width: 100%;
  min-width: 0;
  padding: 0.75rem 0.9rem;
  border-radius: 0;
  border: 1px solid var(--sl-line);
  background: #fff;
  color: var(--sl-ink);
}

.filters input:focus,
.filters select:focus {
  border-color: var(--sl-leaf);
}

.result-count {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

/* GRID */
.catalog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.75rem;
}

/* CARD */
.card {
  position: relative;
  padding: 1.5rem 1.25rem 1.25rem;
  background: #fff;
  border: 1px solid var(--sl-line);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1.25rem;
  transition: border-color 0.2s ease;
}

.card:hover {
  border-color: var(--sl-ink);
}

.card::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  width: 0;
  height: 3px;
  background: var(--sl-lime);
  transition: width 0.3s ease;
}

.card:hover::before {
  width: calc(100% + 2px);
}

/* FAV */
.fav {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  padding: 0;
  border: 1px solid var(--sl-line);
  border-radius: 0;
  background: #fff;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.fav:hover {
  border-color: var(--sl-ink);
  background: var(--sl-paper);
}

/* BODY */
.body {
  display: grid;
  justify-items: start;
  gap: 0.6rem;
  cursor: pointer;
}

.avatar {
  width: 56px;
  height: 56px;
  display: grid;
  place-items: center;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  font-family: var(--sl-display);
  font-weight: 600;
  font-size: 1.3rem;
  color: var(--sl-ink);
  transition: background 0.2s ease, color 0.2s ease;
}

.card:hover .avatar {
  background: var(--sl-ink);
  color: var(--sl-lime);
}

h3 {
  margin: 0.4rem 0 0;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.35;
  color: var(--sl-ink);
}

.rating {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  font-size: 0.8rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  color: var(--sl-ink);
}

/* BTN */
.btn {
  width: 100%;
  justify-content: space-between;
  background: transparent;
  color: var(--sl-ink);
  border: 1px solid var(--sl-ink);
}

.btn .arrow {
  transition: transform 0.2s ease;
}

.btn:hover {
  background: var(--sl-ink);
  color: #fff;
}

.btn:hover .arrow {
  transform: translateX(3px);
}

@media (max-width: 900px) {
  .filters {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .filters {
    grid-template-columns: minmax(0, 1fr);
  }

  .top-bar,
  .top-bar > * {
    flex: 1 1 auto;
  }
}
</style>
