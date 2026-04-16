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

const showComparisonModal = ref(false)
const comparisonSuppliers = computed(() => 
  store.state.suppliers.filter(s => store.state.comparisonSupplierIds.includes(s.id))
)

const handleToggleComparison = (id: number) => {
  try {
    store.toggleComparison(id)
  } catch (e: any) {
    alert(e.message)
  }
}

const isComparing = (id: number) => store.state.comparisonSupplierIds.includes(id)

const getBestValue = (key: 'minOrder' | 'delivery', suppliers: any[]) => {
  // Simple heuristic for best value (shortest delivery or lowest min order)
  if (suppliers.length < 2) return null
  // In a real app we would parse strings or use numeric values
  return null
}
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
              <div class="card-actions">
                <button
                  type="button"
                  class="btn-action btn-compare"
                  :class="{ 'btn-compare--active': isComparing(supplier.id) }"
                  @click.prevent.stop="handleToggleComparison(supplier.id)"
                  title="Сравнить условия"
                >
                  ⚖️
                </button>
                <button
                  type="button"
                  class="btn-action supplier-fav"
                  :class="{ 'supplier-fav--active': isSupplierFavorite(supplier.id) }"
                  @click.prevent.stop="toggleFavoriteSupplier(supplier)"
                >
                  {{ isSupplierFavorite(supplier.id) ? '❤️' : '🤍' }}
                </button>
              </div>
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

    <!-- Comparison Bar -->
    <Transition name="slide-up">
      <div v-if="store.state.comparisonSupplierIds.length > 0" class="comparison-bar">
        <div class="comparison-bar-content">
          <div class="selected-suppliers">
            <span class="comparison-label">Сравнение:</span>
            <div 
              v-for="s in comparisonSuppliers" 
              :key="s.id" 
              class="selected-avatar"
              @click="store.toggleComparison(s.id)"
              title="Убрать из сравнения"
            >
              {{ s.name.charAt(0) }}
              <span class="remove-tiny">×</span>
            </div>
          </div>
          <div class="bar-actions">
            <button class="btn-clear-comp" @click="store.clearComparison">Очистить</button>
            <button class="btn-open-comp" @click="showComparisonModal = true">
              Сравнить условия ({{ store.state.comparisonSupplierIds.length }})
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Comparison Modal -->
    <Transition name="modal">
      <div v-if="showComparisonModal" class="modal-overlay" @click.self="showComparisonModal = false">
        <div class="modal-comparison">
          <button class="btn-close-modal" @click="showComparisonModal = false">✕</button>
          <h2 class="modal-title">Сравнение условий</h2>
          
          <div class="comparison-table-wrapper">
            <table class="comparison-table">
              <thead>
                <tr>
                  <th class="sticky-col">Параметр</th>
                  <th v-for="s in comparisonSuppliers" :key="s.id">
                    <div class="comp-header-cell">
                      <div class="comp-avatar">{{ s.name.charAt(0) }}</div>
                      <span class="comp-name">{{ s.name }}</span>
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="sticky-col">Рейтинг</td>
                  <td v-for="s in comparisonSuppliers" :key="s.id">
                    <span class="t-rating">★ {{ s.rating.toFixed(1) }}</span>
                  </td>
                </tr>
                <tr>
                  <td class="sticky-col">Мин. заказ</td>
                  <td v-for="s in comparisonSuppliers" :key="s.id">
                    <span class="t-value">{{ s.minOrder }}</span>
                  </td>
                </tr>
                <tr>
                  <td class="sticky-col">Срок поставки</td>
                  <td v-for="s in comparisonSuppliers" :key="s.id">
                    <span class="t-value">{{ s.delivery }}</span>
                  </td>
                </tr>
                <tr>
                  <td class="sticky-col">Условия оплаты</td>
                  <td v-for="s in comparisonSuppliers" :key="s.id">
                    <span class="t-value">Безналичный расчет / Отсрочка</span>
                  </td>
                </tr>
                <tr>
                  <td class="sticky-col">Регион</td>
                  <td v-for="s in comparisonSuppliers" :key="s.id">
                    <span class="t-value">📍 {{ s.locations }}</span>
                  </td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td class="sticky-col"></td>
                  <td v-for="s in comparisonSuppliers" :key="s.id">
                    <router-link :to="`/suppliers/${s.id}`" class="btn-view-profile">
                      Перейти в профиль
                    </router-link>
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
    </Transition>
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

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  border: none;
  background: white;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.95rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: all 0.2s;
}

.btn-compare:hover { background: #f1f5f9; }
.btn-compare--active { background: #3f4a2f; color: white; transform: scale(1.1); }

/* Comparison Bar */
.comparison-bar {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 800px;
  background: rgba(30, 41, 59, 0.85);
  backdrop-filter: blur(16px);
  border-radius: 20px;
  padding: 1rem 1.5rem;
  box-shadow: 0 20px 50px rgba(0,0,0,0.3);
  z-index: 1000;
  border: 1px solid rgba(255,255,255,0.1);
}

.comparison-bar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.selected-suppliers {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.comparison-label {
  color: #94a3b8;
  font-weight: 700;
  font-size: 0.85rem;
  text-transform: uppercase;
  margin-right: 0.5rem;
}

.selected-avatar {
  width: 36px;
  height: 36px;
  background: #d8bf98;
  color: #3f4a2f;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.9rem;
  cursor: pointer;
  position: relative;
  transition: transform 0.2s;
}

.selected-avatar:hover { transform: scale(1.1); }
.remove-tiny {
  position: absolute;
  top: -2px;
  right: -2px;
  background: #ef4444;
  color: white;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bar-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-clear-comp {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-clear-comp:hover { color: #f8fafc; }

.btn-open-comp {
  background: #3f4a2f;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-open-comp:hover { background: #4a5638; transform: translateY(-2px); }

/* Comparison Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(8px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-comparison {
  background: #fdfaf3;
  width: 100%;
  max-width: 1000px;
  border-radius: 32px;
  padding: 3rem 2rem;
  position: relative;
  box-shadow: 0 40px 100px rgba(0,0,0,0.4);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.btn-close-modal {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  background: #f1f5f9;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-title {
  font-size: 2rem;
  font-weight: 900;
  color: #3f4a2f;
  margin-bottom: 2.5rem;
  text-align: center;
}

.comparison-table-wrapper {
  overflow-x: auto;
  border-radius: 16px;
  background: white;
  border: 1px solid #e2e8f0;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.comparison-table th, .comparison-table td {
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.sticky-col {
  position: sticky;
  left: 0;
  background: #f8fafc;
  font-weight: 700;
  color: #64748b;
  min-width: 160px;
  z-index: 10;
}

.comp-header-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  text-align: center;
}

.comp-avatar {
  width: 50px;
  height: 50px;
  background: #d8bf98;
  color: #3f4a2f;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 1.25rem;
}

.comp-name {
  font-weight: 800;
  color: #1e293b;
}

.t-rating { color: #d97706; font-weight: 800; }
.t-value { font-weight: 600; color: #334155; }

.btn-view-profile {
  display: inline-block;
  background: #f1f5f9;
  color: #3f4a2f;
  text-decoration: none;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.btn-view-profile:hover { background: #3f4a2f; color: white; }

/* Transitions */
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.slide-up-enter-from, .slide-up-leave-to { transform: translate(-50%, 100px); opacity: 0; }

.modal-enter-active { animation: pop-in 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); }
.modal-leave-active { transition: opacity 0.3s, transform 0.3s; }
.modal-leave-to { opacity: 0; transform: scale(0.9); }

@keyframes pop-in {
  from { opacity: 0; transform: scale(0.6) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

@media (max-width: 600px) {
  .comparison-bar-content { flex-direction: column; gap: 1rem; }
  .bar-actions { width: 100%; justify-content: space-between; }
}
</style>
