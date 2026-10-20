<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore, type Product, type Supplier } from '@/stores/shopStore'
import { AddIcon, DeleteIcon, DocumentIcon, MinusIcon, StarIcon } from '@/assets/icons/png'

const router = useRouter()
const authStore = useAuthStore()
const store = useShopStore()

const activeTab = ref<'products' | 'suppliers'>('products')
const selectedProduct = ref<Product | null>(null)
const quantity = ref(1)

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }

  await Promise.all([store.fetchFavoriteProducts(), store.fetchFavoriteSuppliers()])
})

const suppliers = computed(() => store.state.favoriteSuppliers)
const products = computed(() => store.state.favoriteProducts)

const openProduct = (product: Product) => {
  selectedProduct.value = product
  quantity.value = product.min_order_qty || 1
}

const closeProduct = () => {
  selectedProduct.value = null
}

const addProductToCart = async () => {
  if (!selectedProduct.value) return
  await store.addToCart(selectedProduct.value, quantity.value)
  closeProduct()
}

const removeSupplier = async (supplier: Supplier) => {
  await store.toggleFavoriteSupplier(supplier)
}
</script>

<template>
  <main class="favorites-page">
    <section class="hero">
      <div>
        <p class="eyebrow kicker">Избранное</p>
        <h1>Избранные товары и поставщики</h1>
        <p>Товары и поставщики собраны в одном месте, с быстрым переходом в карточку и удалением.</p>
      </div>
    </section>

    <div class="tabs">
      <button class="tab" :class="{ active: activeTab === 'products' }" @click="activeTab = 'products'">
        Избранные товары
      </button>
      <button class="tab" :class="{ active: activeTab === 'suppliers' }" @click="activeTab = 'suppliers'">
        Избранные поставщики
      </button>
    </div>

    <section v-if="activeTab === 'products'" class="section">
      <div v-if="products.length === 0" class="empty-card">
        Пока нет избранных товаров.
        <router-link to="/catalog" class="primary-btn">Перейти в каталог</router-link>
      </div>

      <div v-else class="products-grid">
        <article v-for="product in products" :key="product.id" class="product-card">
          <div class="product-image" @click="openProduct(product)">
            <img :src="DocumentIcon" alt="" class="product-image-icon" aria-hidden="true" />
            <span v-if="product.category" class="badge">{{ product.category.name }}</span>
          </div>
          <div class="product-body">
            <h2 @click="openProduct(product)">{{ product.name }}</h2>
            <p class="supplier" v-if="product.enterprise" @click="router.push(`/suppliers/${product.enterprise.id}`)">
              {{ product.enterprise.short_name }}
            </p>
            <p class="description">{{ product.description }}</p>
            <div class="price-row">
              <strong>{{ Number(product.price).toFixed(0) }} ₽/кг</strong>
              <span>На складе: {{ product.quantity_in_stock ?? 0 }} кг</span>
            </div>
            <div class="actions">
              <button class="primary-btn" @click="openProduct(product)">В корзину</button>
              <button class="secondary-btn" @click="store.toggleFavoriteProduct(product)">Убрать</button>
            </div>
          </div>
        </article>
      </div>
    </section>

    <section v-else class="section">
      <div v-if="suppliers.length === 0" class="empty-card">
        Пока нет избранных поставщиков.
        <router-link to="/catalog" class="primary-btn">Перейти в каталог</router-link>
      </div>

      <div v-else class="suppliers-grid">
        <article v-for="supplier in suppliers" :key="supplier.id" class="supplier-card">
          <div class="supplier-head" @click="router.push(`/suppliers/${supplier.id}`)">
            <div class="avatar">{{ supplier.name.charAt(0) }}</div>
            <div>
              <h2>{{ supplier.name }}</h2>
              <p>{{ supplier.region }}{{ supplier.city ? ` · ${supplier.city}` : '' }}</p>
            </div>
          </div>
          <div class="supplier-meta">
            <span class="rating">
              <img :src="StarIcon" alt="" class="rating-icon" aria-hidden="true" />
              {{ supplier.rating.toFixed(1) }}
            </span>
            <span>{{ supplier.products.length }} товаров</span>
          </div>
          <div class="supplier-actions">
            <button class="primary-btn" @click="router.push(`/suppliers/${supplier.id}`)">Открыть</button>
            <button class="secondary-btn" @click="removeSupplier(supplier)">
              <img :src="DeleteIcon" alt="" class="action-icon" aria-hidden="true" />
              Удалить
            </button>
          </div>
        </article>
      </div>
    </section>
  </main>

  <teleport to="body">
    <div v-if="selectedProduct" class="modal-backdrop" @click.self="closeProduct">
      <div class="modal-card">
        <p class="kicker">Товар</p>
        <h2>{{ selectedProduct.name }}</h2>
        <p>{{ selectedProduct.description || 'Описание отсутствует' }}</p>
        <div class="qty-row">
          <button class="qty-btn" @click="quantity = Math.max(1, quantity - 1)">
            <img :src="MinusIcon" alt="" class="qty-icon" aria-hidden="true" />
          </button>
          <span>{{ quantity }} кг</span>
          <button class="qty-btn" @click="quantity += 1">
            <img :src="AddIcon" alt="" class="qty-icon" aria-hidden="true" />
          </button>
        </div>
        <div class="modal-total">
          {{ (Number(selectedProduct.price) * quantity).toFixed(0) }} ₽
        </div>
        <div class="actions modal-actions">
          <button class="primary-btn" @click="addProductToCart">Добавить</button>
          <button class="secondary-btn" @click="closeProduct">Отмена</button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<style scoped>
.favorites-page {
  display: grid;
  gap: 1.25rem;
  padding-bottom: 2rem;
  color: var(--sl-ink);
}

h1,
h2 {
  margin: 0;
  color: var(--sl-ink);
}

.kicker {
  margin: 0 0 0.6rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

.product-image-icon,
.qty-icon,
.action-icon,
.rating-icon {
  display: block;
  object-fit: contain;
  filter: grayscale(1) brightness(0.35);
}

.product-image-icon {
  width: 36px;
  height: 36px;
}

.qty-icon {
  width: 16px;
  height: 16px;
}

.action-icon {
  width: 15px;
  height: 15px;
  transition: filter 0.2s ease;
}

.rating-icon {
  width: 13px;
  height: 13px;
}

/* ===== ЗАГОЛОВОК ===== */
.hero {
  padding: clamp(1.25rem, 3vw, 2.25rem);
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
}

.hero h1 {
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  line-height: 1.15;
}

.hero p:not(.kicker) {
  margin: 0.85rem 0 0;
  max-width: 60ch;
  color: var(--sl-muted);
}

/* ===== ТАБЫ ===== */
.tabs {
  display: flex;
  flex-wrap: wrap;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
}

.tab {
  position: relative;
  padding: 0.85rem 1.25rem;
  background: transparent;
  border: none;
  border-right: 1px solid var(--sl-line);
  border-bottom: 2px solid transparent;
  border-radius: 0;
  color: #3f4a37;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.tab:hover {
  color: var(--sl-ink);
  border-bottom-color: var(--sl-leaf);
}

.tab.active {
  background: var(--sl-ink);
  border-bottom-color: var(--sl-lime);
  color: #fff;
}

/* ===== СЕКЦИЯ ===== */
.section {
  padding: clamp(1rem, 3vw, 2rem);
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
}

.empty-card {
  display: grid;
  justify-items: center;
  gap: 1rem;
  padding: clamp(1.5rem, 4vw, 2.5rem);
  background: #fff;
  border: 1px dashed rgba(20, 33, 15, 0.3);
  text-align: center;
  color: var(--sl-muted);
}

.products-grid,
.suppliers-grid {
  display: grid;
  gap: 0.75rem;
}

.products-grid {
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
}

.suppliers-grid {
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
}

/* ===== ТОВАР ===== */
.product-card,
.supplier-card {
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid var(--sl-line);
  transition: border-color 0.2s ease;
}

.product-card:hover,
.supplier-card:hover {
  border-color: var(--sl-ink);
}

.product-image {
  position: relative;
  min-height: 130px;
  display: grid;
  place-items: center;
  background:
    repeating-linear-gradient(135deg, rgba(20, 33, 15, 0.04) 0 1px, transparent 1px 12px),
    var(--sl-paper);
  border-bottom: 1px solid var(--sl-line);
  cursor: pointer;
}

.badge {
  position: absolute;
  left: 0.75rem;
  top: 0.75rem;
  padding: 0.2rem 0.5rem;
  background: var(--sl-ink);
  color: var(--sl-lime);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.product-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 1.1rem 1.1rem 1.2rem;
}

.product-body h2 {
  font-family: inherit;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.35;
  letter-spacing: 0;
  cursor: pointer;
}

.product-body h2:hover {
  color: var(--sl-leaf);
}

.supplier {
  align-self: flex-start;
  margin: 0.35rem 0 0;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--sl-leaf);
  border-bottom: 1px solid transparent;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.supplier:hover {
  border-bottom-color: var(--sl-leaf);
}

.description {
  margin: 0.6rem 0 0;
  font-size: 0.92rem;
  line-height: 1.5;
  color: #3f4a37;
}

.price-row {
  display: grid;
  gap: 0.25rem;
  margin-top: 1rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--sl-line);
}

.price-row strong {
  font-family: var(--sl-display);
  font-size: 1.2rem;
  font-weight: 600;
}

.price-row span {
  font-size: 0.88rem;
  color: var(--sl-muted);
}

.actions,
.supplier-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: auto;
  padding-top: 1rem;
}

/* ===== ПОСТАВЩИК ===== */
.supplier-card {
  padding: 1.1rem 1.1rem 1.2rem;
}

.supplier-head {
  display: grid;
  grid-template-columns: 56px 1fr;
  gap: 0.9rem;
  align-items: center;
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

.supplier-card:hover .avatar {
  background: var(--sl-ink);
  color: var(--sl-lime);
}

.supplier-head h2 {
  font-family: inherit;
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0;
  line-height: 1.35;
}

.supplier-head p {
  margin: 0.25rem 0 0;
  font-size: 0.88rem;
  color: var(--sl-muted);
}

.supplier-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 1rem;
}

.supplier-meta > span {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.5rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

/* ===== КНОПКИ ===== */
.primary-btn,
.secondary-btn,
.qty-btn {
  border-radius: 0;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.primary-btn,
.secondary-btn {
  flex: 1 1 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  padding: 0.7rem 1.2rem;
}

.primary-btn {
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
}

.primary-btn:hover {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.secondary-btn {
  background: transparent;
  color: var(--sl-ink);
  border: 1px solid var(--sl-ink);
}

.secondary-btn:hover {
  background: var(--sl-ink);
  color: #fff;
}

.secondary-btn:hover .action-icon {
  filter: grayscale(1) brightness(0) invert(1);
}

.empty-card .primary-btn {
  flex: 0 0 auto;
}

.primary-btn:focus-visible,
.secondary-btn:focus-visible,
.qty-btn:focus-visible,
.tab:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

/* ===== МОДАЛКА ===== */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(20, 33, 15, 0.55);
  display: grid;
  place-items: center;
  padding: 1rem;
  z-index: 2000;
}

.modal-card {
  width: min(520px, 100%);
  max-height: calc(100vh - 2rem);
  overflow-y: auto;
  padding: clamp(1.25rem, 4vw, 2rem);
  background: #fff;
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
  border-radius: 0;
  box-shadow: 0 24px 48px rgba(20, 33, 15, 0.18);
  color: var(--sl-ink);
}

.modal-card h2 {
  font-size: clamp(1.2rem, 2.6vw, 1.5rem);
}

.modal-card > p:not(.kicker) {
  margin: 0.75rem 0 0;
  color: #3f4a37;
}

.qty-row {
  display: flex;
  align-items: center;
  width: fit-content;
  margin-top: 1.25rem;
  border: 1px solid var(--sl-line);
}

.qty-row > span {
  min-width: 6rem;
  text-align: center;
  font-weight: 800;
}

.qty-btn {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  padding: 0;
  background: var(--sl-paper);
  border: none;
}

.qty-btn:hover {
  background: var(--sl-lime);
}

.modal-total {
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid var(--sl-line);
  font-family: var(--sl-display);
  font-size: 1.6rem;
  font-weight: 600;
  color: var(--sl-ink);
}

.modal-actions {
  margin-top: 1.25rem;
  padding-top: 0;
}

/* ===== АДАПТИВ ===== */
@media (max-width: 520px) {
  .tabs {
    display: grid;
    grid-template-columns: 1fr;
  }

  .tab {
    text-align: left;
    border-right: none;
  }

  .tab + .tab {
    border-top: 1px solid var(--sl-line);
  }

  .empty-card .primary-btn {
    justify-self: stretch;
  }
}
</style>
