<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore, type Supplier } from '@/stores/shopStore'
import { useRequireAuth } from '@/composables/useRequireAuth'
import {
  AppAvatar,
  AppBadge,
  AppButton,
  AppIcon,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
  RatingStars,
} from '@/components/ui'
import { pluralize } from '@/utils/format'

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

/* ── только для отображения ─────────────────── */
const isInitialLoading = computed(() => store.state.loading && store.state.suppliers.length === 0)
const loadError = computed(() => (store.state.suppliers.length === 0 ? store.state.error : null))
const compareCount = computed(() => store.state.comparisonSupplierIds.length)

const resultLabel = computed(() => {
  const n = filteredSuppliers.value.length
  return `Найдено ${n} ${pluralize(n, ['поставщик', 'поставщика', 'поставщиков'])}`
})

const locationOf = (supplier: Supplier) => [supplier.region, supplier.city].filter(Boolean).join(', ')

const MAX_CATEGORY_CHIPS = 3
const supplierCategories = (supplier: Supplier) => {
  const names = new Set<string>()
  for (const product of supplier.products) {
    if (product.category?.name) names.add(product.category.name)
  }
  return Array.from(names)
}
</script>

<template>
  <div class="page">
    <PageHeader
      eyebrow="Каталог"
      title="Поставщики"
      description="Найдите поставщика по товарам, категории, региону и городу."
    >
      <template #actions>
        <AppButton to="/compare" variant="secondary" icon="scale">
          Сравнить (<span class="ui-num">{{ compareCount }}</span>)
        </AppButton>
      </template>
    </PageHeader>

    <!-- ФИЛЬТРЫ -->
    <section class="filters ui-card" aria-label="Фильтры каталога">
      <div class="filters__search">
        <AppIcon name="search" :size="18" class="filters__search-icon" />
        <input
          v-model="search"
          type="search"
          class="filters__input"
          placeholder="Поставщик или товар"
          aria-label="Поиск по названию поставщика или товара"
        />
      </div>

      <select v-model="selectedCategoryId" aria-label="Категория товаров">
        <option :value="null">Все категории</option>
        <option v-for="c in categories" :key="c.id" :value="c.id">
          {{ c.name }}
        </option>
      </select>

      <select v-model="selectedRegion" aria-label="Регион">
        <option value="all">Все регионы</option>
        <option v-for="r in regions" :key="r">
          {{ r }}
        </option>
      </select>

      <select v-model="selectedCity" aria-label="Город" :disabled="availableCities.length === 0">
        <option value="all">{{ availableCities.length ? 'Все города' : 'Город не указан' }}</option>
        <option v-for="c in availableCities" :key="c">
          {{ c }}
        </option>
      </select>

      <AppButton variant="ghost" icon="x" :disabled="!hasActiveFilters" class="filters__reset" @click="resetFilters">
        Сбросить
      </AppButton>
    </section>

    <LoadingState v-if="isInitialLoading" variant="cards" :rows="6" label="Загружаем поставщиков…" />

    <ErrorState
      v-else-if="loadError"
      :message="loadError"
      :retrying="store.state.loading"
      @retry="store.fetchSuppliers()"
    />

    <template v-else>
      <p class="results-count" aria-live="polite">
        <AppIcon name="store" :size="16" />
        <span class="ui-num">{{ resultLabel }}</span>
      </p>

      <EmptyState
        v-if="filteredSuppliers.length === 0 && hasActiveFilters"
        icon="search"
        title="Ничего не найдено"
        description="Попробуйте изменить запрос или сбросить фильтры — в каталоге есть и другие поставщики."
      >
        <AppButton variant="secondary" icon="x" @click="resetFilters">Сбросить фильтры</AppButton>
      </EmptyState>

      <EmptyState
        v-else-if="filteredSuppliers.length === 0"
        icon="store"
        title="Поставщиков пока нет"
        description="Как только поставщики зарегистрируются на платформе, они появятся здесь."
      />

      <ul v-else class="catalog-grid">
        <li v-for="supplier in filteredSuppliers" :key="supplier.id">
          <article class="supplier-card ui-card ui-card--interactive">
            <div class="supplier-card__top">
              <AppAvatar :name="supplier.name" :size="52" />
              <button
                type="button"
                class="fav-btn"
                :class="{ 'is-on': store.isSupplierFavorite(supplier.id) }"
                :aria-pressed="store.isSupplierFavorite(supplier.id)"
                :aria-label="
                  store.isSupplierFavorite(supplier.id)
                    ? `Убрать «${supplier.name}» из избранного`
                    : `Добавить «${supplier.name}» в избранное`
                "
                :title="store.isSupplierFavorite(supplier.id) ? 'Убрать из избранного' : 'В избранное'"
                @click="toggleSupplierFavorite(supplier)"
              >
                <AppIcon name="heart" :size="18" :filled="store.isSupplierFavorite(supplier.id)" />
              </button>
            </div>

            <div class="supplier-card__body">
              <h2 class="supplier-card__name">
                <RouterLink :to="`/suppliers/${supplier.id}`" class="supplier-card__link">
                  {{ supplier.name }}
                </RouterLink>
              </h2>

              <p class="supplier-card__location">
                <AppIcon name="map-pin" :size="15" />
                <span>{{ locationOf(supplier) || 'Регион не указан' }}</span>
              </p>

              <div class="supplier-card__rating">
                <RatingStars
                  v-if="supplier.reviews > 0"
                  :value="supplier.rating"
                  :size="14"
                  show-value
                  :count="supplier.reviews"
                />
                <span v-else class="ui-muted">Пока нет отзывов</span>
              </div>
            </div>

            <div class="supplier-card__meta">
              <span class="supplier-card__products">
                <AppIcon name="package" :size="15" />
                <span class="ui-num">
                  {{ supplier.products.length }}
                  {{ pluralize(supplier.products.length, ['товар', 'товара', 'товаров']) }}
                </span>
              </span>
              <ul v-if="supplierCategories(supplier).length" class="supplier-card__cats" aria-label="Категории товаров">
                <li v-for="name in supplierCategories(supplier).slice(0, MAX_CATEGORY_CHIPS)" :key="name">
                  <AppBadge size="sm">{{ name }}</AppBadge>
                </li>
                <li v-if="supplierCategories(supplier).length > MAX_CATEGORY_CHIPS">
                  <AppBadge size="sm">+{{ supplierCategories(supplier).length - MAX_CATEGORY_CHIPS }}</AppBadge>
                </li>
              </ul>
            </div>

            <AppButton
              :to="`/suppliers/${supplier.id}`"
              variant="secondary"
              icon-right="arrow-right"
              block
              class="supplier-card__more"
            >
              Подробнее
            </AppButton>
          </article>
        </li>
      </ul>
    </template>
  </div>
</template>

<style scoped>
.page {
  display: grid;
  gap: 1.5rem;
}

/* ── Фильтры ───────────────────────────────── */
.filters {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) repeat(3, minmax(0, 1fr)) auto;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem;
}

.filters__search {
  position: relative;
  min-width: 0;
}

.filters__search-icon {
  position: absolute;
  top: 50%;
  left: 0.85rem;
  transform: translateY(-50%);
  color: var(--c-muted);
  pointer-events: none;
}

/* специфичность выше глобального правила для input в base.css */
.filters .filters__search .filters__input[type='search'] {
  padding-left: 2.5rem;
}

.filters select {
  min-width: 0;
}

.results-count {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin-top: -0.25rem;
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  font-weight: 600;
}

.results-count .app-icon {
  color: var(--c-accent-600);
}

/* ── Сетка карточек ────────────────────────── */
.catalog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.catalog-grid > li {
  display: flex;
}

.supplier-card {
  position: relative;
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 1rem;
  padding: 1.25rem;
}

.supplier-card__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.fav-btn {
  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  padding: 0;
  border: 1px solid var(--c-border);
  border-radius: var(--r-full);
  background: var(--c-surface);
  color: var(--c-muted);
  transition:
    color var(--dur) var(--ease),
    border-color var(--dur) var(--ease),
    background var(--dur) var(--ease);
}

.fav-btn:hover {
  border-color: var(--c-border-strong);
  color: var(--c-danger);
}

.fav-btn.is-on {
  border-color: var(--c-danger-bg);
  background: var(--c-danger-bg);
  color: var(--c-danger);
}

.supplier-card__body {
  display: grid;
  gap: 0.45rem;
}

.supplier-card__name {
  font-size: var(--fs-lg);
  line-height: 1.3;
  overflow-wrap: anywhere;
}

.supplier-card__link {
  color: var(--c-text);
  transition: color var(--dur) var(--ease);
}

/* вся карточка кликабельна через ссылку в заголовке */
.supplier-card__link::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
}

.supplier-card:hover .supplier-card__link {
  color: var(--c-brand-700);
}

.supplier-card__link:focus-visible {
  outline: none;
}

.supplier-card:has(.supplier-card__link:focus-visible) {
  outline: 2px solid var(--c-accent);
  outline-offset: 2px;
}

.supplier-card__location {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--c-muted);
  font-size: var(--fs-sm);
}

.supplier-card__location .app-icon {
  flex: 0 0 auto;
}

.supplier-card__rating {
  min-height: 1.5rem;
  font-size: var(--fs-sm);
}

.supplier-card__meta {
  display: grid;
  gap: 0.6rem;
  margin-top: auto;
  padding-top: 0.9rem;
  border-top: 1px solid var(--c-border);
}

.supplier-card__products {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  font-weight: 600;
}

.supplier-card__products .app-icon {
  color: var(--c-accent-600);
}

.supplier-card__cats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.supplier-card__more {
  position: relative;
  z-index: 1;
}

/* ── Адаптив ───────────────────────────────── */
@media (max-width: 1024px) {
  .filters {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .filters__search {
    grid-column: 1 / -1;
  }

  .filters__reset {
    grid-column: 1 / -1;
    justify-self: end;
  }
}

@media (max-width: 640px) {
  .filters {
    grid-template-columns: minmax(0, 1fr);
  }

  .filters__reset {
    justify-self: stretch;
  }
}
</style>
