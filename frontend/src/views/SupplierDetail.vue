<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useShopStore, type Product } from '@/data/shopStore'
import { useAuthStore } from '@/data/authStore'
import CommonNavbar from '@/components/CommonNavbar.vue'

const route = useRoute()
const store = useShopStore()
const authStore = useAuthStore()

const supplierId = computed(() => Number(route.params.id))

onMounted(() => {
  if (supplierId.value) {
    store.fetchSupplierDetail(supplierId.value)
  }
})

const supplier = computed(() => store.state.currentSupplier)

// Modal Logic
const showModal = ref(false)
const selectedProduct = ref<Product | null>(null)
const quantity = ref(1)

const openProductModal = (product: Product) => {
  selectedProduct.value = product
  quantity.value = product.min_order_qty || 1
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedProduct.value = null
}

const handleAddToCart = async () => {
  if (selectedProduct.value) {
    await store.addToCart(selectedProduct.value, quantity.value)
    closeModal()
  }
}

const handleToggleFavorite = async (product: Product) => {
  await store.toggleFavoriteProduct(product)
}

const modalTotal = computed(() => {
  if (!selectedProduct.value) return 0
  return (selectedProduct.value.price * quantity.value).toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
})
</script>

<template>
  <div class="supplier-page">
    <CommonNavbar />

    <main class="supplier-main">
      <div class="breadcrumb">
        <router-link to="/catalog" class="breadcrumb-link">← Каталог поставщиков</router-link>
      </div>

      <div v-if="store.state.loading" class="supplier-status">
        Загрузка данных поставщика...
      </div>
      <div v-else-if="store.state.error" class="supplier-status error">
        {{ store.state.error }}
      </div>
      <div v-else-if="supplier" class="supplier-content">
        <!-- Supplier Header -->
        <section class="supplier-info-card">
          <div class="supplier-info-top">
            <div class="supplier-avatar-large">{{ supplier.name.charAt(0) }}</div>
            <div class="supplier-info-main">
              <h1 class="supplier-title">{{ supplier.name }}</h1>
              <p class="supplier-subtitle">{{ supplier.company }}</p>
              <div class="supplier-stats">
                <span class="stat-item">★ {{ supplier.rating.toFixed(1) }} ({{ supplier.reviews }} отзывов)</span>
                <span class="stat-item">📍 {{ supplier.locations }}</span>
                <span class="stat-item">📅 На SavorLink с {{ supplier.since }} года</span>
              </div>
            </div>
            <button class="btn-favorite-large" @click="store.toggleFavoriteSupplier(supplier)">
              {{ store.isSupplierFavorite(supplier.id) ? '❤️ В избранном' : '🤍 В избранное' }}
            </button>
          </div>
          <p class="supplier-description-text">{{ supplier.description }}</p>
        </section>

        <!-- Product Grid -->
        <section class="supplier-products">
          <h2 class="section-title">Продукция поставщика</h2>
          <div v-if="supplier.products.length === 0" class="no-products">
            У поставщика пока нет товаров
          </div>
          <div v-else class="products-grid">
            <div
              v-for="product in supplier.products"
              :key="product.id"
              class="product-card"
              @click="openProductModal(product)"
            >
              <div class="product-image-placeholder">
                <span class="product-category-badge" v-if="product.category">{{ product.category.name }}</span>
                <span class="product-badge-low" v-if="product.quantity_in_stock !== null && product.quantity_in_stock < 50">
                  Мало
                </span>
              </div>
              <div class="product-body">
                <h3 class="product-name">{{ product.name }}</h3>
                <p class="product-desc" v-if="product.description">{{ product.description }}</p>
                <p class="product-price">{{ product.price }} ₽/кг</p>
                <p class="product-stock">
                  На складе: {{ product.quantity_in_stock ?? 0 }} кг
                </p>
                <div class="product-actions">
                  <button
                    class="btn-fav-product"
                    :class="{ active: store.isProductFavorite(product.id) }"
                    @click.stop="handleToggleFavorite(product)"
                    v-if="authStore.token"
                  >
                    {{ store.isProductFavorite(product.id) ? '❤️' : '🤍' }}
                  </button>
                  <button class="btn-add-cart" @click.stop="openProductModal(product)">
                    В корзину
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>

    <!-- Product Modal -->
    <Transition name="fade">
      <div v-if="showModal && selectedProduct" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card">
          <button class="btn-close" @click="closeModal">×</button>

          <div class="modal-layout">
            <div class="modal-image-side">
              <div class="img-fill">
                <div class="img-placeholder-icon">🌿</div>
              </div>
            </div>

            <div class="modal-info-side">
              <p class="modal-category" v-if="selectedProduct.category">{{ selectedProduct.category.name }}</p>
              <h2 class="product-modal-name">{{ selectedProduct.name }}</h2>
              <div class="product-modal-price">{{ selectedProduct.price }} ₽/кг</div>

              <p class="product-modal-description" v-if="selectedProduct.description">
                {{ selectedProduct.description }}
              </p>

              <div class="modal-meta-grid">
                <div class="meta-row">
                  <span class="meta-label">На складе:</span>
                  <span class="meta-value">{{ selectedProduct.quantity_in_stock ?? 0 }} кг</span>
                </div>
                <div class="meta-row">
                  <span class="meta-label">Мин. заказ:</span>
                  <span class="meta-value">{{ selectedProduct.min_order_qty || 1 }} кг</span>
                </div>
                <div class="meta-row">
                  <span class="meta-label">Доставка:</span>
                  <span class="meta-value">Бесплатно сегодня</span>
                </div>
              </div>

              <div class="product-modal-qty-row">
                <div class="qty-picker">
                  <button @click="quantity = Math.max(selectedProduct.min_order_qty || 1, quantity - 1)">−</button>
                  <span class="qty-display">{{ quantity }}</span>
                  <button @click="quantity++">+</button>
                </div>
                <div class="qty-unit">кг</div>
              </div>

              <div class="modal-total-row">
                <div class="total-label">Итого</div>
                <div class="total-value">{{ modalTotal }} ₽</div>
              </div>

              <div class="modal-action-btns">
                <button
                  v-if="authStore.token"
                  class="btn-modal-fav"
                  :class="{ active: store.isProductFavorite(selectedProduct.id) }"
                  @click="handleToggleFavorite(selectedProduct)"
                >
                  {{ store.isProductFavorite(selectedProduct.id) ? '❤️ В избранном' : '🤍 Избранное' }}
                </button>
                <button class="btn-modal-add" @click="handleAddToCart" :disabled="!authStore.token">
                  {{ authStore.token ? 'Добавить в корзину' : 'Войдите для заказа' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.supplier-page {
  min-height: 100vh;
  background: #ebe2ce;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.supplier-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem 1.5rem 3rem;
}

.breadcrumb {
  margin-bottom: 1.25rem;
}

.breadcrumb-link {
  color: #4b5563;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.breadcrumb-link:hover {
  color: #3f4a2f;
}

.supplier-status {
  text-align: center;
  padding: 4rem;
  font-size: 1.1rem;
  color: #4b5563;
}

.supplier-info-card {
  background: #f4ead4;
  border: 1px solid #ddc8a3;
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

.supplier-info-top {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.supplier-avatar-large {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #d8bf98, #c0a87a);
  color: #3f4a2f;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
  flex-shrink: 0;
}

.supplier-info-main {
  flex: 1;
  min-width: 200px;
}

.supplier-title {
  font-size: 1.75rem;
  font-weight: 800;
  margin: 0 0 0.25rem;
  color: #1f2937;
}

.supplier-subtitle {
  font-size: 1rem;
  color: #4b5563;
  margin: 0 0 0.75rem;
}

.supplier-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.88rem;
  color: #6b7280;
}

.btn-favorite-large {
  background: #fff;
  border: 1px solid #d1d5db;
  padding: 0.6rem 1.25rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  color: #374151;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-favorite-large:hover {
  background: #f4ead4;
  border-color: #a97c50;
}

.supplier-description-text {
  line-height: 1.65;
  color: #4b5563;
  font-size: 0.95rem;
  margin: 0;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #3f4a2f;
  margin: 0 0 1.25rem;
}

.no-products {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
  background: rgba(255,255,255,0.4);
  border-radius: 1rem;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 1.25rem;
}

.product-card {
  background: #fff;
  border-radius: 0.75rem;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.product-image-placeholder {
  height: 150px;
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
  position: relative;
}

.product-category-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(63, 74, 47, 0.85);
  color: #fff;
  font-size: 0.72rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
}

.product-badge-low {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  background: #fef2f2;
  color: #991b1b;
  font-size: 0.72rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
}

.product-body {
  padding: 1rem;
}

.product-name {
  font-size: 1rem;
  font-weight: 700;
  margin: 0 0 0.3rem;
  color: #111827;
}

.product-desc {
  font-size: 0.82rem;
  color: #6b7280;
  margin: 0 0 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-price {
  font-size: 1.1rem;
  font-weight: 800;
  color: #059669;
  margin: 0 0 0.2rem;
}

.product-stock {
  font-size: 0.83rem;
  color: #6b7280;
  margin-bottom: 0.75rem;
}

.product-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-fav-product {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 0.5rem 0.65rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-fav-product.active {
  background: #fff0f3;
  border-color: #f9a8d4;
}

.btn-add-cart {
  flex: 1;
  background: #3f4a2f;
  color: #fff;
  border: none;
  padding: 0.55rem 0.75rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.88rem;
  transition: background 0.2s;
}

.btn-add-cart:hover {
  background: #4a5638;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1.5rem;
}

.modal-card {
  background: #fff;
  width: 100%;
  max-width: 820px;
  border-radius: 1.5rem;
  overflow: hidden;
  position: relative;
  max-height: 90vh;
  overflow-y: auto;
}

.btn-close {
  position: absolute;
  top: 1rem;
  right: 1.25rem;
  border: none;
  background: none;
  font-size: 2rem;
  cursor: pointer;
  color: #9ca3af;
  z-index: 10;
  line-height: 1;
}

.modal-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
}

@media (max-width: 640px) {
  .modal-layout {
    grid-template-columns: 1fr;
  }
  .modal-image-side {
    height: 180px;
  }
}

.modal-image-side {
  background: linear-gradient(135deg, #e8f5e9, #a5d6a7);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 250px;
}

.img-fill {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.img-placeholder-icon {
  font-size: 5rem;
}

.modal-info-side {
  padding: 2rem 2rem 1.75rem;
}

.modal-category {
  font-size: 0.82rem;
  color: #3f4a2f;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.4rem;
}

.product-modal-name {
  font-size: 1.65rem;
  font-weight: 800;
  margin: 0 0 0.4rem;
  color: #111827;
}

.product-modal-price {
  font-size: 1.5rem;
  font-weight: 800;
  color: #059669;
  margin-bottom: 1rem;
}

.product-modal-description {
  font-size: 0.92rem;
  color: #4b5563;
  line-height: 1.6;
  margin-bottom: 1.25rem;
  background: #f9fafb;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  border-left: 3px solid #d8bf98;
}

.modal-meta-grid {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-bottom: 1.25rem;
}

.meta-row {
  display: flex;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.meta-label {
  color: #6b7280;
  min-width: 110px;
}

.meta-value {
  color: #111827;
  font-weight: 600;
}

.product-modal-qty-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.qty-picker {
  display: flex;
  align-items: center;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  overflow: hidden;
}

.qty-picker button {
  width: 40px;
  height: 40px;
  border: none;
  background: #f3f4f6;
  font-size: 1.2rem;
  cursor: pointer;
  transition: background 0.15s;
}

.qty-picker button:hover {
  background: #e5e7eb;
}

.qty-display {
  width: 55px;
  text-align: center;
  font-size: 1.1rem;
  font-weight: 700;
  color: #111827;
}

.qty-unit {
  font-weight: 600;
  color: #4b5563;
}

.modal-total-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid #f3f4f6;
}

.total-label {
  font-size: 1rem;
  color: #6b7280;
}

.total-value {
  font-size: 1.65rem;
  font-weight: 800;
}

.modal-action-btns {
  display: flex;
  gap: 0.75rem;
}

.btn-modal-fav {
  background: #f9f9f9;
  border: 1px solid #e0d6c7;
  color: #374151;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-modal-fav.active {
  background: #fff0f3;
  border-color: #f9a8d4;
  color: #be185d;
}

.btn-modal-add {
  flex: 1;
  background: #3f4a2f;
  color: #fff;
  border: none;
  padding: 0.85rem 1rem;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-modal-add:hover:not(:disabled) {
  background: #4a5638;
}

.btn-modal-add:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Animations */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
