<script setup lang="ts">
import { computed, ref } from 'vue'
import { useShopStore } from '@/data/shopStore'
import type { Product } from '@/data/mockProducts'

const store = useShopStore()

const selectedProduct = ref<Product | null>(null)
const quantityKg = ref(10)

const favoritesCount = computed(
  () => store.state.favoriteSuppliers.length + store.state.favoriteProducts.length,
)

const cartCount = computed(() =>
  store.state.cartItems.reduce((sum, item) => sum + item.quantityKg, 0),
)

const cartTotal = computed(() =>
  store.state.cartItems.reduce(
    (sum, item) => sum + item.product.pricePerKg * item.quantityKg,
    0,
  ),
)

const openProduct = (product: Product, qty: number) => {
  selectedProduct.value = product
  quantityKg.value = qty
}

const closeProduct = () => {
  selectedProduct.value = null
}

const decreaseQty = () => {
  if (!selectedProduct.value) return
  if (quantityKg.value > 1) {
    quantityKg.value -= 1
    store.setCartQuantity(selectedProduct.value.id, quantityKg.value)
  }
}

const increaseQty = () => {
  if (!selectedProduct.value) return
  quantityKg.value += 1
  store.setCartQuantity(selectedProduct.value.id, quantityKg.value)
}

const totalForSelected = computed(() =>
  selectedProduct.value ? selectedProduct.value.pricePerKg * quantityKg.value : 0,
)
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
          <router-link to="/favorites" class="nav-link">
            Избранное ({{ favoritesCount }})
          </router-link>
          <router-link to="/cart" class="nav-link nav-link--active">
            Корзина ({{ cartCount }})
          </router-link>
        </div>
      </nav>
    </header>

    <main class="page-main">
      <section class="section">
        <h1 class="section-title">Корзина</h1>
        <div class="products-grid">
          <button
            v-for="item in store.state.cartItems"
            :key="item.product.id"
            type="button"
            class="product-card"
            @click="openProduct(item.product, item.quantityKg)"
          >
            <div class="product-image-placeholder">
              <span class="image-icon">🖼</span>
            </div>
            <div class="product-body">
              <h3 class="product-name">{{ item.product.name }}</h3>
              <p class="product-desc">{{ item.product.description }}</p>
              <p class="product-price">
                <span class="price-main">{{ item.product.pricePerKg }} ₽</span>
                <span class="price-unit">/ {{ item.product.unit }}</span>
              </p>
              <p class="product-stock">В корзине: {{ item.quantityKg }} кг</p>
            </div>
          </button>
        </div>
        <div class="cart-total-row" v-if="store.state.cartItems.length">
          <span>Итого:</span>
          <span class="cart-total-sum">{{ cartTotal }} ₽</span>
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
                В корзине: {{ quantityKg }} кг
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
            <button type="button" class="product-modal-primary" @click="closeProduct">
              Оформить заказ
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

.section-title {
  margin: 0 0 1.2rem;
  font-size: 1.3rem;
  font-weight: 600;
  color: #f9fafb;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 1.5rem;
}

.product-card {
  background: #f3f4f6;
  border-radius: 1rem;
  padding: 1rem 1.1rem 0.9rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.18);
  border: none;
  cursor: pointer;
  text-align: left;
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

.cart-total-row {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  font-size: 1rem;
  color: #f9fafb;
}

.cart-total-sum {
  font-weight: 600;
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
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.1rem;
}

.product-modal-primary {
  border-radius: 999px;
  border: none;
  background: #111827;
  color: #ffffff;
  padding: 0.5rem 1.4rem;
  font-size: 0.9rem;
  cursor: pointer;
}
</style>

