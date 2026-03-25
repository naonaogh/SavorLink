<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useShopStore } from '@/data/shopStore'
import type { Product } from '@/data/mockProducts'

const router = useRouter()
const store = useShopStore()

const selectedProduct = ref<Product | null>(null)
const quantityKg = ref(10)

const favoritesCount = computed(
  () => store.state.favoriteSuppliers.length + store.state.favoriteProducts.length,
)

const cartCount = computed(() =>
  store.state.cartItems.reduce((sum, item) => sum + item.quantityKg, 0),
)

const totalForSelected = computed(() =>
  selectedProduct.value ? selectedProduct.value.pricePerKg * quantityKg.value : 0,
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

const addSelectedToCart = () => {
  if (!selectedProduct.value) return
  store.addToCart(selectedProduct.value, quantityKg.value)
}

const goSupplier = (id: number) => {
  router.push({ name: 'SupplierDetail', params: { id } })
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <nav class="page-nav">
        <router-link to="/" class="nav-logo">SavorLink</router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link">Главная</router-link>
          <router-link to="/catalog" class="nav-link">Каталог</router-link>
          <router-link to="/profile" class="nav-link">Профиль</router-link>
          <router-link to="/favorites" class="nav-link nav-link--active">
            Избранное ({{ favoritesCount }})
          </router-link>
          <router-link to="/cart" class="nav-link">
            Корзина ({{ cartCount }})
          </router-link>
        </div>
      </nav>
    </header>

    <main class="page-main">
      <section class="section">
        <h1 class="section-title">Избранные поставщики</h1>
        <div class="suppliers-grid">
          <button
            v-for="supplier in store.state.favoriteSuppliers"
            :key="supplier.id"
            type="button"
            class="supplier-card"
            @click="goSupplier(supplier.id)"
          >
            <div class="supplier-card-top">
              <div class="supplier-avatar">П</div>
              <span class="supplier-rating">
                ★ {{ supplier.rating.toFixed(1) }}
                <span class="supplier-reviews">({{ supplier.reviews }})</span>
              </span>
            </div>
            <div class="supplier-card-body">
              <h3 class="supplier-name">{{ supplier.name }}</h3>
              <p class="supplier-company">{{ supplier.company }}</p>
              <p class="supplier-location">{{ supplier.locations }}</p>
              <p class="supplier-desc">{{ supplier.description }}</p>
            </div>
          </button>
        </div>
      </section>

      <section class="section">
        <h2 class="section-title">Избранные товары</h2>
        <div class="products-grid">
          <button
            v-for="product in store.state.favoriteProducts"
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
          </button>
        </div>
      </section>

      <div v-if="selectedProduct" class="product-modal-backdrop" @click.self="closeProduct">
        <div class="product-modal">
          <header class="product-modal-header">
            <h2 class="product-modal-title">{{ selectedProduct.name }}</h2>
          </header>

          <div class="product-modal-body">
            <p class="product-modal-price-row">
              <span class="product-modal-price">
                {{ selectedProduct.pricePerKg }} ₽/{{ selectedProduct.unit }}
              </span>
              <span class="product-modal-note">
                Осталось: {{ selectedProduct.stockKg }} кг
              </span>
            </p>

            <div class="product-modal-qty-row">
              <span>Количество:</span>
              <div class="qty-control">
                <button type="button" class="qty-btn" @click="decreaseQty">−</button>
                <span class="qty-value">{{ quantityKg }} кг</span>
                <button type="button" class="qty-btn" @click="increaseQty">+</button>
              </div>
              <span class="product-modal-total">Сумма: {{ totalForSelected }} ₽</span>
            </div>
          </div>

          <footer class="product-modal-footer">
            <button type="button" class="product-modal-secondary" @click="addSelectedToCart">
              Добавить в корзину
            </button>
            <button type="button" class="product-modal-primary" @click="closeProduct">
              Заказать
            </button>
          </footer>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: #51645b;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
  color: #111827;
}

.page-header {
  background: linear-gradient(135deg, #485a50 0%, #51645b 100%);
  padding: 0.875rem 1.5rem;
  position: sticky;
  top: 0;
  z-index: 20;
}

.page-nav {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
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
}

.nav-link {
  color: #d1d5db;
  text-decoration: none;
  font-size: 0.95rem;
}

.nav-link--active {
  font-weight: 600;
  color: #ffffff;
}

.nav-link:hover {
  color: #ffffff;
}

.page-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
}

.section {
  margin-bottom: 2.5rem;
}

.section-title {
  margin: 0 0 1.2rem;
  font-size: 1.3rem;
  font-weight: 600;
  color: #f9fafb;
}

.suppliers-grid,
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 1.5rem;
}

.supplier-card,
.product-card {
  background: #f3f4f6;
  border-radius: 1rem;
  padding: 1rem 1.1rem 0.9rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.18);
  text-align: left;
  border: none;
  cursor: pointer;
}

.supplier-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.65rem;
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
}

.supplier-name {
  margin: 0 0 0.15rem;
  font-size: 1rem;
  font-weight: 600;
}

.supplier-company,
.supplier-location,
.supplier-desc {
  margin: 0;
  font-size: 0.85rem;
  color: #4b5563;
}

.supplier-location {
  color: #6b7280;
}

.supplier-desc {
  margin-top: 0.25rem;
}

.product-image-placeholder {
  background: #d1d5db;
  border-radius: 0.75rem;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.7rem;
}

.image-icon {
  font-size: 1.7rem;
  color: #f9fafb;
}

.product-name {
  margin: 0 0 0.25rem;
  font-size: 0.98rem;
  font-weight: 600;
}

.product-desc {
  margin: 0 0 0.45rem;
  font-size: 0.85rem;
  color: #4b5563;
}

.product-price {
  margin: 0 0 0.25rem;
  font-size: 0.95rem;
}

.price-main {
  font-weight: 700;
}

.price-unit {
  color: #6b7280;
}

.product-stock {
  margin: 0;
  font-size: 0.8rem;
  color: #6b7280;
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
  margin-bottom: 0.75rem;
}

.product-modal-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
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

