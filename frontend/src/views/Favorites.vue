<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useShopStore, type Product } from '@/data/shopStore'
import { useAuthStore } from '@/data/authStore'
import CommonNavbar from '@/components/CommonNavbar.vue'

const router = useRouter()
const store = useShopStore()
const authStore = useAuthStore()

const selectedProduct = ref<Product | null>(null)
const quantity = ref(1)
const isAddingToCart = ref(false)

onMounted(async () => {
  if (!authStore.token) {
    router.push('/login')
    return
  }
  await store.fetchFavoriteProducts()
})

const totalForSelected = computed(() =>
  selectedProduct.value ? selectedProduct.value.pricePerKg * quantity.value : 0,
)

const openProduct = (product: Product) => {
  selectedProduct.value = product
  quantity.value = product.min_order_qty || 1
}

const closeProduct = () => {
  selectedProduct.value = null
}

const decreaseQty = () => {
  if (selectedProduct.value && quantity.value > (selectedProduct.value.min_order_qty || 1)) {
    quantity.value -= 1
  }
}

const increaseQty = () => {
  quantity.value += 1
}

const addSelectedToCart = async () => {
  if (!selectedProduct.value) return
  isAddingToCart.value = true
  try {
    await store.addToCart(selectedProduct.value, quantity.value)
    closeProduct()
  } finally {
    isAddingToCart.value = false
  }
}

const removeFavorite = async (product: Product) => {
  await store.toggleFavoriteProduct(product)
}

const goSupplier = (product: Product) => {
  if (product.enterprise?.id) {
    router.push({ name: 'SupplierDetail', params: { id: product.enterprise.id } })
  }
}
</script>

<template>
  <div class="page">
    <CommonNavbar />

    <main class="page-main">
      <h1 class="page-title">Избранные товары</h1>

      <div v-if="store.state.loading" class="status-msg">
        Загрузка избранного...
      </div>

      <div v-else-if="store.state.favoriteProducts.length === 0" class="empty-state">
        <div class="empty-icon">🤍</div>
        <p>У вас пока нет избранных товаров</p>
        <router-link to="/catalog" class="btn-go-catalog">Перейти в каталог</router-link>
      </div>

      <div v-else class="products-grid">
        <div
          v-for="product in store.state.favoriteProducts"
          :key="product.id"
          class="product-card"
        >
          <div class="product-image-placeholder" @click="openProduct(product)">
            <span class="image-icon">🌿</span>
            <span class="cat-label" v-if="product.category">{{ product.category.name }}</span>
          </div>
          <div class="product-body">
            <h3 class="product-name" @click="openProduct(product)">{{ product.name }}</h3>
            <p class="product-supplier" v-if="product.enterprise" @click="goSupplier(product)">
              🏭 {{ product.enterprise.short_name }}
            </p>
            <p class="product-desc">{{ product.description }}</p>
            <p class="product-price">
              <span class="price-main">{{ product.pricePerKg }} ₽</span>
              <span class="price-unit"> / кг</span>
            </p>
            <p class="product-stock">На складе: {{ product.stockKg }} кг</p>
            <div class="card-actions">
              <button type="button" class="btn-add-cart" @click="openProduct(product)">
                В корзину
              </button>
              <button type="button" class="btn-remove-fav" @click="removeFavorite(product)" title="Убрать из избранного">
                ❌
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Product Modal -->
      <div v-if="selectedProduct" class="product-modal-backdrop" @click.self="closeProduct">
        <div class="product-modal">
          <button class="modal-close" @click="closeProduct">×</button>
          <header class="product-modal-header">
            <p class="modal-cat" v-if="selectedProduct.category">{{ selectedProduct.category.name }}</p>
            <h2 class="product-modal-title">{{ selectedProduct.name }}</h2>
          </header>

          <div class="product-modal-body">
            <p class="modal-description" v-if="selectedProduct.description">
              {{ selectedProduct.description }}
            </p>

            <p class="product-modal-price-row">
              <span class="product-modal-price">{{ selectedProduct.pricePerKg }} ₽/кг</span>
              <span class="product-modal-note">На складе: {{ selectedProduct.stockKg }} кг</span>
            </p>

            <div class="product-modal-qty-row">
              <span>Количество:</span>
              <div class="qty-control">
                <button type="button" class="qty-btn" @click="decreaseQty">−</button>
                <span class="qty-value">{{ quantity }} кг</span>
                <button type="button" class="qty-btn" @click="increaseQty">+</button>
              </div>
              <span class="product-modal-total">{{ totalForSelected }} ₽</span>
            </div>
          </div>

          <footer class="product-modal-footer">
            <button type="button" class="product-modal-secondary" @click="addSelectedToCart" :disabled="isAddingToCart">
              {{ isAddingToCart ? 'Добавляем...' : 'Добавить в корзину' }}
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
  background: #ebe2ce;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #2e2a23;
}

.page-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #3f4a2f;
  margin: 0 0 1.75rem;
}

.status-msg {
  text-align: center;
  padding: 3rem;
  font-size: 1.1rem;
  color: #4b5563;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(255,255,255,0.4);
  border-radius: 1.5rem;
  border: 2px dashed #dcd1ba;
}

.empty-icon {
  font-size: 3.5rem;
  margin-bottom: 1rem;
}

.empty-state p {
  color: #6b7280;
  font-size: 1rem;
  margin-bottom: 1.5rem;
}

.btn-go-catalog {
  display: inline-block;
  background: #3f4a2f;
  color: #fff;
  text-decoration: none;
  padding: 0.75rem 1.75rem;
  border-radius: 999px;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-go-catalog:hover {
  background: #4a5638;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.5rem;
}

.product-card {
  background: #f4ead4;
  border-radius: 0.75rem;
  border: 1px solid #ddc8a3;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(72, 56, 36, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(72, 56, 36, 0.15);
}

.product-image-placeholder {
  background: linear-gradient(135deg, #d4edda, #a8d5b5);
  height: 155px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  cursor: pointer;
}

.image-icon {
  font-size: 2.5rem;
}

.cat-label {
  position: absolute;
  bottom: 0.5rem;
  right: 0.5rem;
  background: rgba(63, 74, 47, 0.8);
  color: #fff;
  font-size: 0.72rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.product-body {
  padding: 1rem;
}

.product-name {
  font-size: 1rem;
  font-weight: 700;
  margin: 0 0 0.2rem;
  cursor: pointer;
  color: #1f2937;
}

.product-name:hover {
  color: #3f4a2f;
}

.product-supplier {
  font-size: 0.82rem;
  color: #a97c50;
  margin: 0 0 0.3rem;
  cursor: pointer;
}

.product-supplier:hover {
  text-decoration: underline;
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
  margin: 0 0 0.2rem;
  font-size: 0.95rem;
}

.price-main {
  font-weight: 700;
  color: #3f4a2f;
  font-size: 1.05rem;
}

.price-unit {
  color: #6b7280;
}

.product-stock {
  margin: 0 0 0.75rem;
  font-size: 0.8rem;
  color: #6b7280;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-add-cart {
  flex: 1;
  background: #3f4a2f;
  color: #fff;
  border: none;
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.88rem;
  transition: background 0.2s;
}

.btn-add-cart:hover {
  background: #4a5638;
}

.btn-remove-fav {
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 0.4rem 0.65rem;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background 0.2s;
}

.btn-remove-fav:hover {
  background: #fecaca;
}

/* Modal */
.product-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 40;
  padding: 1rem;
}

.product-modal {
  background: #fff;
  border-radius: 1.25rem;
  padding: 1.75rem;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
  position: relative;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1.25rem;
  border: none;
  background: none;
  font-size: 1.75rem;
  cursor: pointer;
  color: #9ca3af;
  line-height: 1;
}

.product-modal-header {
  margin-bottom: 1rem;
}

.modal-cat {
  font-size: 0.78rem;
  color: #3f4a2f;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.3rem;
}

.product-modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
}

.product-modal-body {
  font-size: 0.9rem;
  color: #111827;
}

.modal-description {
  font-size: 0.88rem;
  color: #4b5563;
  line-height: 1.55;
  margin-bottom: 0.75rem;
  padding: 0.6rem 0.8rem;
  background: #f9f9f7;
  border-radius: 0.5rem;
  border-left: 3px solid #d8bf98;
}

.product-modal-price-row {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  margin: 0 0 0.75rem;
}

.product-modal-price {
  font-weight: 700;
  font-size: 1.1rem;
  color: #059669;
}

.product-modal-note {
  color: #4b5563;
  font-size: 0.85rem;
}

.product-modal-qty-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.qty-control {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.qty-btn {
  width: 30px;
  height: 30px;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  background: #f9fafb;
  cursor: pointer;
  font-size: 1rem;
}

.qty-value {
  min-width: 60px;
  text-align: center;
  font-weight: 600;
}

.product-modal-total {
  font-weight: 700;
  font-size: 1rem;
  color: #3f4a2f;
}

.product-modal-footer {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  border-top: 1px solid #f3f4f6;
  padding-top: 1rem;
}

.product-modal-secondary {
  flex: 1;
  border-radius: 999px;
  border: none;
  background: #3f4a2f;
  color: #fff;
  padding: 0.65rem 1rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.product-modal-secondary:hover:not(:disabled) {
  background: #4a5638;
}

.product-modal-secondary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
