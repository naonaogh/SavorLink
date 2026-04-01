<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { mockSuppliers } from '@/data/mockSuppliers'
import { mockProducts, type Product } from '@/data/mockProducts'
import { useShopStore } from '@/data/shopStore'

const route = useRoute()
const store = useShopStore()

const supplierId = computed(() => Number(route.params.id ?? 1))

const supplier = computed(
  () => mockSuppliers.find((s) => s.id === supplierId.value) ?? mockSuppliers[0]!,
)

const supplierProducts = computed(() =>
  mockProducts.filter((product) => product.supplierId === supplierId.value),
)

const selectedProduct = ref<Product | null>(null)
const quantityKg = ref(10)

const isSelectedFavorite = computed(() =>
  selectedProduct.value ? store.isProductFavorite(selectedProduct.value.id) : false,
)

const modalTotal = computed(() =>
  selectedProduct.value ? selectedProduct.value.pricePerKg * quantityKg.value : 0,
)

const favoritesCount = computed(
  () => store.state.favoriteSuppliers.length + store.state.favoriteProducts.length,
)

const cartCount = computed(() =>
  store.state.cartItems.reduce((sum, item) => sum + item.quantityKg, 0),
)

const openProduct = (product: Product) => {
  selectedProduct.value = product
  quantityKg.value = 10
}

const closeProduct = () => {
  selectedProduct.value = null
}

const decreaseQty = () => {
  if (quantityKg.value > 1) quantityKg.value -= 1
}

const increaseQty = () => {
  quantityKg.value += 1
}

const toggleSelectedFavorite = () => {
  if (!selectedProduct.value) return
  store.toggleFavoriteProduct(selectedProduct.value)
}

const addSelectedToCart = () => {
  if (!selectedProduct.value) return
  store.addToCart(selectedProduct.value, quantityKg.value)
}

const toggleSupplierFavorite = () => {
  if (!supplier.value) return
  store.toggleFavoriteSupplier(supplier.value)
}
</script>

<template>
  <div class="supplier-page">
    <header class="supplier-header">
      <nav class="supplier-nav">
        <router-link to="/catalog" class="nav-back">← Каталог поставщиков</router-link>
        <div class="nav-actions">
          <router-link to="/" class="nav-link">Главная</router-link>
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

    <main class="supplier-main">
      <section class="supplier-hero-card">
        <div class="supplier-hero-left">
          <div class="supplier-hero-title-row">
            <h1 class="supplier-hero-name">{{ supplier.name }}</h1>
            <div class="supplier-hero-rating">
              <span class="stars">★★★★★</span>
              <span class="rating-value">{{ supplier.rating.toFixed(1) }}</span>
              <span class="rating-reviews">({{ supplier.reviews }} отзывов)</span>
            </div>
          </div>
          <p class="supplier-hero-location">{{ supplier.locations }}</p>
          <p class="supplier-hero-text">
            {{ supplier.description }} Работает с {{ supplier.since }}.
          </p>
          <p class="supplier-hero-meta">
            Мин. заказ: <strong>{{ supplier.minOrder }}</strong><br />
            Доставка: {{ supplier.delivery }}
          </p>
        </div>
        <div class="supplier-hero-right">
          <button
            type="button"
            class="supplier-fav-large"
            aria-label="Добавить в избранное"
            @click="toggleSupplierFavorite"
          >
            🤍
          </button>
          <button type="button" class="supplier-contact">Написать</button>
        </div>
      </section>

      <section class="products-section">
        <h2 class="products-title">Товары поставщика</h2>
        <div class="products-grid">
          <button
            v-for="product in supplierProducts"
            :key="product.id"
            type="button"
            class="product-card"
            @click="openProduct(product)"
          >
            <div class="product-image-placeholder">
              <span class="image-icon">🖼</span>
            </div>
            <div class="product-body">
              <h3 class="product-name">{{ product.name }}</h3>
              <p class="product-desc">{{ product.description }}</p>
              <p class="product-price">
                <span class="price-main">{{ product.pricePerKg }} ₽</span>
                <span class="price-unit">/ {{ product.unit }}</span>
              </p>
              <p class="product-stock">На складе: {{ product.stockKg }} кг</p>
            </div>
            <div class="product-footer">
              <span class="product-more">Подробнее</span>
            </div>
          </button>
        </div>
      </section>

      <div v-if="selectedProduct" class="product-modal-backdrop" @click.self="closeProduct">
        <div class="product-modal">
          <header class="product-modal-header">
            <div>
              <h2 class="product-modal-title">{{ selectedProduct.name }}</h2>
              <p class="product-modal-sub">{{ supplier?.name }}</p>
            </div>
            <div class="product-modal-actions">
              <button
                type="button"
                class="icon-btn"
                :class="{ 'icon-btn--active': isSelectedFavorite }"
                aria-label="Добавить в избранное"
                @click.stop="toggleSelectedFavorite"
              >
                {{ isSelectedFavorite ? '❤️' : '🤍' }}
              </button>
              <button
                type="button"
                class="icon-btn"
                aria-label="Закрыть"
                @click="closeProduct"
              >
                ✕
              </button>
            </div>
          </header>

          <div class="product-modal-body">
            <p class="product-modal-price-row">
              <span class="product-modal-price">
                {{ selectedProduct.pricePerKg }} ₽/{{ selectedProduct.unit }}
              </span>
              <span class="product-modal-note">
                Осталось: {{ selectedProduct.stockKg }} кг · Доставка завтра 06:00–10:00
              </span>
            </p>
            <ul class="product-modal-list">
              <li>Бесплатно от 5000 ₽ у этого поставщика</li>
              <li>Верифицированный поставщик</li>
              <li>Идеальны для салатов и украшения блюд</li>
            </ul>

            <div class="product-modal-qty-row">
              <span>Количество:</span>
              <div class="qty-control">
                <button type="button" class="qty-btn" @click="decreaseQty">−</button>
                <span class="qty-value">{{ quantityKg }} кг</span>
                <button type="button" class="qty-btn" @click="increaseQty">+</button>
              </div>
              <span class="product-modal-total">Сумма: {{ modalTotal }} ₽</span>
            </div>
          </div>

          <footer class="product-modal-footer">
            <button type="button" class="product-modal-secondary" @click="addSelectedToCart">
              Добавить в корзину
            </button>
            <button type="button" class="product-modal-primary">
              Заказать
            </button>
          </footer>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.supplier-page {
  min-height: 100vh;
  background: #ebe2ce;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
  color: #2e2a23;
}

.supplier-header {
  background: linear-gradient(120deg, #364128 0%, #3f4a2f 60%, #4a5638 100%);
  padding: 0.875rem 1.5rem;
  position: sticky;
  top: 0;
  z-index: 20;
}

.supplier-nav {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.nav-back {
  color: #f0e5d1;
  text-decoration: none;
  font-size: 0.95rem;
}

.nav-back:hover {
  text-decoration: underline;
}

.nav-actions {
  display: flex;
  gap: 1rem;
}

.nav-link {
  color: #e7dbc5;
  text-decoration: none;
  font-size: 0.9rem;
}

.nav-link:hover {
  color: #ffffff;
}

.supplier-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
}

.supplier-hero-card {
  background: #f5ebd6;
  border: 1px solid #dcc7a2;
  border-radius: 1.5rem;
  padding: 1.8rem 2rem;
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.25);
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 1fr);
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.supplier-hero-left {
  min-width: 0;
}

.supplier-hero-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.supplier-hero-name {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
}

.supplier-hero-rating {
  white-space: nowrap;
  font-size: 0.95rem;
}

.stars {
  color: #facc15;
  margin-right: 0.25rem;
}

.rating-value {
  font-weight: 600;
}

.rating-reviews {
  color: #6b7280;
  margin-left: 0.3rem;
}

.supplier-hero-location {
  margin: 0 0 0.4rem;
  font-size: 0.95rem;
  color: #4b5563;
}

.supplier-hero-text {
  margin: 0 0 0.6rem;
  font-size: 0.95rem;
  color: #111827;
}

.supplier-hero-meta {
  margin: 0;
  font-size: 0.9rem;
  color: #4b5563;
}

.supplier-hero-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
}

.supplier-fav-large {
  border-radius: 999px;
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #d1d5db;
  background: #ffffff;
  cursor: pointer;
  font-size: 1.2rem;
}

.supplier-contact {
  border-radius: 999px;
  border: 1px solid #6c5537;
  background: #d9bf99;
  color: #2b261f;
  padding: 0.6rem 1.6rem;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
}

.products-section {
  margin-top: 2rem;
}

.products-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #3f4a2f;
  margin: 0 0 1.5rem;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 1.5rem;
}

.product-card {
  background: #f4ead4;
  border-radius: 0.35rem;
  border: 1px solid #c8d1bc;
  padding: 0;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 18px rgba(72, 56, 36, 0.16);
  overflow: hidden;
}

.product-image-placeholder {
  background: linear-gradient(180deg, #f4ead4 0%, #edf0e3 100%);
  border-radius: 0;
  height: 210px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0;
}

.image-icon {
  font-size: 2rem;
  color: #ccb996;
}

.product-body {
  flex: 1;
  padding: 0.8rem 0.9rem 0.4rem;
  background: #e5deca;
  border-top: 1px solid rgba(63, 74, 47, 0.18);
  text-align: center;
}

.product-name {
  font-size: 1rem;
  font-weight: 800;
  color: #2f3a24;
  text-transform: uppercase;
  margin: 0 0 0.25rem;
}

.product-desc {
  font-size: 0.78rem;
  color: #5c4a34;
  margin: 0 0 0.35rem;
  text-transform: uppercase;
}

.product-price {
  margin: 0 0 0.15rem;
  font-size: 0.94rem;
}

.price-main {
  font-weight: 700;
}

.price-unit {
  color: #6b7280;
  margin-left: 0.1rem;
}

.product-stock {
  font-size: 0.82rem;
  color: #4e5b3b;
  margin: 0 0 0.4rem;
}

.product-footer {
  display: flex;
  justify-content: center;
  padding: 0 0.9rem 0.85rem;
  background: #e5deca;
}

.product-more {
  border: none;
  background: #4f5e3c;
  color: #ffffff;
  padding: 0.42rem 1rem;
  border-radius: 999px;
  font-size: 0.8rem;
  cursor: pointer;
}

.product-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 40;
}

.product-modal {
  background: #ffffff;
  border-radius: 1rem;
  padding: 1.5rem 1.8rem 1.4rem;
  width: 420px;
  max-width: 90vw;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
}

.product-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.product-modal-title {
  margin: 0 0 0.15rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.product-modal-sub {
  margin: 0;
  font-size: 0.88rem;
  color: #6b7280;
}

.product-modal-actions {
  display: flex;
  gap: 0.5rem;
}

.icon-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 1.1rem;
}

.icon-btn--active {
  transform: scale(1.05);
}

.product-modal-body {
  font-size: 0.9rem;
  color: #111827;
}

.product-modal-price-row {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  margin: 0 0 0.75rem;
}

.product-modal-price {
  font-weight: 700;
}

.product-modal-note {
  color: #4b5563;
}

.product-modal-list {
  list-style: none;
  padding: 0;
  margin: 0 0 0.9rem;
}

.product-modal-list li::before {
  content: '✓ ';
}

.product-modal-qty-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.qty-control {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.qty-btn {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  background: #f9fafb;
  cursor: pointer;
}

.qty-value {
  min-width: 60px;
  text-align: center;
}

.product-modal-total {
  font-weight: 600;
}

.product-modal-footer {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 1.1rem;
}

.product-modal-secondary {
  flex: 1;
  border-radius: 999px;
  border: 1px solid #111827;
  background: #ffffff;
  color: #111827;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  cursor: pointer;
}

.product-modal-primary {
  flex: 1;
  border-radius: 999px;
  border: none;
  background: #111827;
  color: #ffffff;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  cursor: pointer;
}
</style>
