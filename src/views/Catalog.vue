<script setup lang="ts">
import { computed, ref } from 'vue'
import { mockSuppliers } from '@/data/mockSuppliers'
import { useShopStore } from '@/data/shopStore'

const search = ref('')
const { state, toggleFavoriteSupplier, isSupplierFavorite } = useShopStore()

const filteredSuppliers = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return mockSuppliers
  return mockSuppliers.filter((s) => s.name.toLowerCase().includes(term))
})

const favoritesCount = computed(
  () => state.favoriteSuppliers.length + state.favoriteProducts.length,
)

const cartCount = computed(() =>
  state.cartItems.reduce((sum, item) => sum + item.quantityKg, 0),
)
</script>

<template>
  <div class="catalog-page">
    <header class="catalog-header">
      <nav class="catalog-nav">
        <router-link to="/" class="nav-logo">SavorLink</router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link">Главная</router-link>
          <router-link to="/catalog" class="nav-link nav-link--active">Каталог</router-link>
          <router-link to="/profile" class="nav-link">Профиль</router-link>
          <router-link to="/favorites" class="nav-link">
            Избранное ({{ favoritesCount }})
          </router-link>
          <router-link to="/cart" class="nav-link">
            Корзина ({{ cartCount }})
          </router-link>
        </div>
      </nav>
    </header>

    <main class="catalog-main">
      <section class="catalog-search-section">
        <div class="catalog-search-bar">
          <input
            v-model="search"
            type="text"
            class="search-input"
            placeholder="Поиск поставщика по названию"
          />
          <button type="button" class="search-filter" aria-label="Фильтры">
            ⚙
          </button>
          <button type="button" class="search-submit" aria-label="Поиск">
            🔍
          </button>
        </div>
      </section>

      <section class="catalog-grid-section">
        <div class="suppliers-grid">
          <router-link
            v-for="supplier in filteredSuppliers"
            :key="supplier.id"
            :to="`/suppliers/${supplier.id}`"
            class="supplier-card"
          >
            <div class="supplier-card-top">
              <div class="supplier-avatar">П</div>
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
              <p class="supplier-company">{{ supplier.company }}</p>
              <p class="supplier-location">{{ supplier.location }}</p>
              <p class="supplier-desc">
                {{ supplier.description }}
              </p>
            </div>
            <div class="supplier-card-footer">
              <span class="supplier-min-order">Мин. заказ: от 50&nbsp;000&nbsp;₽</span>
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
  background: #51645b;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
  color: #1a1a1a;
}

.catalog-header {
  background: linear-gradient(135deg, #485a50 0%, #51645b 100%);
  padding: 0.875rem 1.5rem;
  position: sticky;
  top: 0;
  z-index: 20;
}

.catalog-nav {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.nav-logo {
  font-size: 1.1rem;
  font-weight: 700;
  color: #e5e7eb;
  text-decoration: none;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.nav-link {
  color: #d1d5db;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 400;
}

.nav-link--active {
  font-weight: 600;
  color: #ffffff;
}

.nav-link:hover {
  color: #ffffff;
}

.catalog-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
}

.catalog-search-section {
  margin-bottom: 2rem;
  display: flex;
  justify-content: center;
}

.catalog-search-bar {
  width: 100%;
  max-width: 520px;
  display: grid;
  grid-template-columns: 1fr auto auto;
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

.search-filter,
.search-submit {
  border: none;
  background: transparent;
  padding: 0 0.9rem;
  cursor: pointer;
  font-size: 1rem;
}

.search-submit {
  background: #111827;
  color: #ffffff;
}

.catalog-grid-section {
  margin-top: 1.5rem;
}

.suppliers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 1.5rem;
}

.supplier-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: #f3f4f6;
  border-radius: 1rem;
  padding: 1rem 1.1rem 0.9rem;
  text-decoration: none;
  color: inherit;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.18);
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}

.supplier-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.22);
}

.supplier-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.supplier-avatar {
  width: 42px;
  height: 42px;
  border-radius: 999px;
  background: #d1fae5;
  color: #064e3b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1rem;
}

.supplier-fav {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 1.1rem;
}

.supplier-card-body {
  flex: 1;
}

.supplier-title-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}

.supplier-name {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.supplier-rating {
  font-size: 0.9rem;
  color: #111827;
}

.supplier-reviews {
  color: #6b7280;
  margin-left: 0.15rem;
}

.supplier-company {
  font-size: 0.9rem;
  color: #4b5563;
  margin: 0 0 0.2rem;
}

.supplier-location {
  font-size: 0.85rem;
  color: #6b7280;
  margin: 0 0 0.2rem;
}

.supplier-desc {
  font-size: 0.85rem;
  color: #4b5563;
  margin: 0.15rem 0 0.4rem;
}

.supplier-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.4rem;
}

.supplier-min-order {
  font-size: 0.8rem;
  color: #6b7280;
}

.supplier-more {
  border: none;
  background: #111827;
  color: #ffffff;
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  font-size: 0.8rem;
  cursor: pointer;
}

.supplier-fav--active {
  transform: scale(1.05);
}
</style>

