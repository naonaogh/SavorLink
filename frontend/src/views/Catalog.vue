<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useShopStore } from '@/data/shopStore'
import CommonNavbar from '@/components/CommonNavbar.vue'
import api from '@/api'

const store = useShopStore()

const search = ref('')
const selectedCategoryId = ref<number | null>(null)
const categories = ref<{ id: number; name: string }[]>([])

onMounted(async () => {
  await store.fetchSuppliers()
  try {
    const res = await api.get('/products/categories')
    categories.value = res.data
  } catch (e) {
    console.error('Ошибка при загрузке категорий', e)
  }
})

// Фильтрация поставщиков по поиску
// Фильтрация по категории — показывает поставщиков у которых есть товары в нужной категории
const filteredSuppliers = computed(() => {
  let list = store.state.suppliers

  const term = search.value.trim().toLowerCase()
  if (term) {
    list = list.filter((s) => s.name.toLowerCase().includes(term))
  }

  if (selectedCategoryId.value !== null) {
    list = list.filter((s) =>
      s.products.some((p) => p.category?.id === selectedCategoryId.value),
    )
  }

  return list
})

const { toggleFavoriteSupplier, isSupplierFavorite } = store
</script>

<template>
  <div class="catalog-page">
    <CommonNavbar />

    <main class="catalog-main">
      <section class="catalog-search-section">
        <div class="catalog-search-bar">
          <input
            v-model="search"
            type="text"
            class="search-input"
            placeholder="Поиск поставщика по названию"
          />
          <button type="button" class="search-submit" aria-label="Поиск">🔍</button>
        </div>
      </section>

      <!-- Фильтры по категориям -->
      <section class="catalog-filters" v-if="categories.length > 0">
        <button
          type="button"
          class="filter-btn"
          :class="{ 'filter-btn--active': selectedCategoryId === null }"
          @click="selectedCategoryId = null"
        >
          Все
        </button>
        <button
          v-for="cat in categories"
          :key="cat.id"
          type="button"
          class="filter-btn"
          :class="{ 'filter-btn--active': selectedCategoryId === cat.id }"
          @click="selectedCategoryId = cat.id"
        >
          {{ cat.name }}
        </button>
      </section>

      <section class="catalog-grid-section">
        <div v-if="store.state.loading" class="catalog-status">Загрузка поставщиков...</div>
        <div v-else-if="store.state.error" class="catalog-status catalog-status--error">
          {{ store.state.error }}
        </div>
        <div v-else-if="filteredSuppliers.length === 0" class="catalog-status">
          Поставщики не найдены
        </div>

        <div v-else class="suppliers-grid">
          <router-link
            v-for="supplier in filteredSuppliers"
            :key="supplier.id"
            :to="`/suppliers/${supplier.id}`"
            class="supplier-card"
          >
            <div class="supplier-card-top">
              <div class="supplier-avatar">{{ supplier.name.charAt(0) }}</div>
              <button
                type="button"
                class="supplier-fav"
                :class="{ 'supplier-fav--active': isSupplierFavorite(supplier.id) }"
                aria-label="Добавить поставщика в избранное"
                @click.prevent.stop="toggleFavoriteSupplier(supplier)"
              >
                {{ isSupplierFavorite(supplier.id) ? '❤️' : '🤍' }}
              </button>
            </div>
            <div class="supplier-card-body">
              <div class="supplier-title-row">
                <h3 class="supplier-name">{{ supplier.name }}</h3>
                <span class="supplier-rating">
                  ★ {{ supplier.rating.toFixed(1) }}
                  <span class="supplier-reviews">({{ supplier.reviews }})</span>
                </span>
              </div>
              <p class="supplier-location">📍 {{ supplier.locations }}</p>
              <p class="supplier-desc">{{ supplier.description }}</p>

              <!-- Категории товаров -->
              <div class="supplier-cats" v-if="supplier.products.length > 0">
                <span
                  v-for="cat in [...new Set(supplier.products.map(p => p.category?.name).filter(Boolean))].slice(0, 3)"
                  :key="cat"
                  class="cat-badge"
                >
                  {{ cat }}
                </span>
              </div>
            </div>
            <div class="supplier-card-footer">
              <span class="supplier-product-count">{{ supplier.products.length }} товаров</span>
              <button type="button" class="supplier-more">Подробнее</button>
            </div>
          </router-link>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.catalog-page {
  min-height: 100vh;
  background: #ebe2ce;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #1a1a1a;
}

.catalog-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
}

.catalog-search-section {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: center;
}

.catalog-search-bar {
  width: 100%;
  max-width: 540px;
  display: grid;
  grid-template-columns: 1fr auto;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 999px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.18);
  overflow: hidden;
}

.search-input {
  border: none;
  padding: 0.8rem 1.2rem;
  font-size: 0.95rem;
  background: transparent;
  outline: none;
}

.search-submit {
  border: none;
  background: #3f4a2f;
  color: #ffffff;
  padding: 0 1.1rem;
  cursor: pointer;
  font-size: 1rem;
}

/* Category filters */
.catalog-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.75rem;
}

.filter-btn {
  background: rgba(255,255,255,0.65);
  border: 1px solid #ddc8a3;
  color: #3f4a2f;
  padding: 0.45rem 1rem;
  border-radius: 999px;
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s ease;
}

.filter-btn:hover {
  background: rgba(255,255,255,0.9);
  border-color: #3f4a2f;
}

.filter-btn--active {
  background: #3f4a2f;
  border-color: #3f4a2f;
  color: #fff;
}

.catalog-grid-section {
  margin-top: 0.5rem;
}

.catalog-status {
  text-align: center;
  padding: 3rem;
  font-size: 1.1rem;
  color: #4b5563;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 1rem;
}

.catalog-status--error {
  color: #dc2626;
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.2);
}

.suppliers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.supplier-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: #f4ead4;
  border-radius: 0.75rem;
  border: 1px solid #ddc8a3;
  padding: 1rem 1.1rem 0.9rem;
  text-decoration: none;
  color: inherit;
  box-shadow: 0 6px 18px rgba(72, 56, 36, 0.12);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.supplier-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.18);
}

.supplier-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.supplier-avatar {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  background: #d8bf98;
  color: #3f4a2f;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
}

.supplier-fav {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 1.1rem;
  transition: transform 0.15s;
}

.supplier-fav:hover {
  transform: scale(1.15);
}

.supplier-card-body {
  flex: 1;
}

.supplier-title-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.3rem;
}

.supplier-name {
  font-size: 1rem;
  font-weight: 700;
  margin: 0;
}

.supplier-rating {
  font-size: 0.88rem;
  color: #a97c50;
  font-weight: 600;
  white-space: nowrap;
}

.supplier-reviews {
  color: #6b7280;
  font-weight: 400;
}

.supplier-location {
  font-size: 0.83rem;
  color: #6b7280;
  margin: 0 0 0.35rem;
}

.supplier-desc {
  font-size: 0.84rem;
  color: #4b5563;
  margin: 0 0 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.supplier-cats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: 0.35rem;
}

.cat-badge {
  background: rgba(63, 74, 47, 0.1);
  color: #3f4a2f;
  font-size: 0.75rem;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-weight: 500;
}

.supplier-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.75rem;
  padding-top: 0.6rem;
  border-top: 1px solid rgba(0,0,0,0.06);
}

.supplier-product-count {
  font-size: 0.8rem;
  color: #6b7280;
}

.supplier-more {
  border: none;
  background: #3f4a2f;
  color: #ffffff;
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.2s;
}

.supplier-more:hover {
  background: #4a5638;
}

.supplier-fav--active {
  transform: scale(1.05);
}
</style>
