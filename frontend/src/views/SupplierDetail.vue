<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore, type Product, type Supplier } from '@/stores/shopStore'
import { useRequireAuth } from '@/composables/useRequireAuth'
import {
  AddIcon,
  CalendarIcon,
  CloseIcon,
  DocumentIcon,
  LocationIcon,
  MinusIcon,
  NotificationIcon,
  StarIcon,
} from '@/assets/icons/png'

const route = useRoute()
const router = useRouter()
const store = useShopStore()
const authStore = useAuthStore()
const requireAuth = useRequireAuth()

const supplierId = computed(() => Number(route.params.id))
const supplier = computed(() => store.state.currentSupplier)

const showReviews = ref(true)
const showReviewModal = ref(false)
const selectedProduct = ref<Product | null>(null)
const quantity = ref(1)
const ratingValue = ref(5)
const reviewComment = ref('')
const isSubmittingReview = ref(false)

const isBuyer = computed(() => authStore.user?.role === 'BUYER')

onMounted(async () => {
  if (supplierId.value) {
    await Promise.all([store.fetchSupplierDetail(supplierId.value), store.fetchSupplierReviews(supplierId.value)])
  }
})

const openProductModal = (product: Product) => {
  if (!requireAuth()) return
  selectedProduct.value = product
  quantity.value = product.min_order_qty || 1
}

const closeProductModal = () => {
  selectedProduct.value = null
}

const totalForProduct = computed(() =>
  selectedProduct.value ? Number(selectedProduct.value.price) * quantity.value : 0,
)

const addToCart = async () => {
  if (!selectedProduct.value || !requireAuth()) return
  await store.addToCart(selectedProduct.value, quantity.value)
  closeProductModal()
}

const toggleSupplierFavorite = (target: Supplier) => {
  if (!requireAuth()) return
  store.toggleFavoriteSupplier(target)
}

const toggleProductFavorite = (product: Product) => {
  if (!requireAuth()) return
  store.toggleFavoriteProduct(product)
}

const submitReview = async () => {
  if (!supplier.value || isSubmittingReview.value) return

  isSubmittingReview.value = true
  try {
    await store.submitReview(supplier.value.id, ratingValue.value, reviewComment.value)
    reviewComment.value = ''
    ratingValue.value = 5
    showReviewModal.value = false
    showReviews.value = true
  } catch (error: any) {
    alert(error?.response?.data?.detail || error?.message || 'Не удалось отправить отзыв')
  } finally {
    isSubmittingReview.value = false
  }
}

const formatDate = (value: string) =>
  new Date(value).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  })
</script>

<template>
  <main class="supplier-page">
    <div v-if="store.state.loading" class="status-box">Загрузка данных поставщика...</div>
    <div v-else-if="store.state.error" class="status-box status-box--error">{{ store.state.error }}</div>

    <template v-else-if="supplier">
      <section class="hero-card">
        <div class="hero-main">
          <div class="avatar">{{ supplier.name.charAt(0) }}</div>
          <div>
            <p class="eyebrow kicker">Поставщик</p>
            <h1>{{ supplier.name }}</h1>
            <p class="subline">{{ supplier.company }}</p>
            <p class="supplier-desc" v-if="supplier.description">{{ supplier.description }}</p>
            <div class="meta">
              <span class="meta-item">
                <img :src="StarIcon" alt="" class="meta-icon" aria-hidden="true" />
                {{ supplier.rating.toFixed(1) }} ({{ supplier.reviews }})
              </span>
              <span class="meta-item">
                <img :src="LocationIcon" alt="" class="meta-icon" aria-hidden="true" />
                {{ supplier.locations }}
              </span>
              <span class="meta-item">
                <img :src="CalendarIcon" alt="" class="meta-icon" aria-hidden="true" />
                с {{ supplier.since }}
              </span>
            </div>
          </div>
        </div>

        <div class="hero-actions">
          <button 
            v-if="authStore.user && supplier.users?.[0] && supplier.users[0].id !== authStore.user.id" 
            class="action-btn action-btn--chat" 
            @click="router.push(`/chat?userId=${supplier.users[0].id}`)"
          >
            <img :src="NotificationIcon" alt="" class="btn-icon-chat" />
            Написать
          </button>
          <button v-if="isBuyer" class="action-btn action-btn--primary" @click="showReviewModal = true">
            Оценить
          </button>
          <button class="action-btn" @click="toggleSupplierFavorite(supplier)">
            {{ store.isSupplierFavorite(supplier.id) ? 'В избранном' : 'В избранное' }}
          </button>
        </div>
      </section>

      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="kicker">Ассортимент</p>
            <h2>Продукция</h2>
          </div>
          <button class="link-btn" @click="showReviews = !showReviews">
            {{ showReviews ? 'Скрыть отзывы' : 'Показать отзывы' }}
          </button>
        </div>

        <div class="products-grid">
          <article v-for="product in supplier.products" :key="product.id" class="product-card">
            <div class="product-image">
              <img :src="DocumentIcon" alt="" class="product-image-icon" aria-hidden="true" />
            </div>
            <div class="product-body">
              <h3>{{ product.name }}</h3>
              <p>{{ product.category?.name || 'Без категории' }}</p>
              <div class="product-meta">
                <strong>{{ Number(product.price).toFixed(0) }} ₽/кг</strong>
                <span>Остаток: {{ product.quantity_in_stock ?? 0 }} кг</span>
              </div>
              <div class="product-actions">
                <button class="action-btn action-btn--primary" @click="openProductModal(product)">В корзину</button>
                <button class="action-btn" @click="toggleProductFavorite(product)">
                  {{ store.isProductFavorite(product.id) ? 'В избранном' : 'В избранное' }}
                </button>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section v-if="showReviews" class="panel">
        <div class="panel-head">
          <div>
            <p class="kicker">Покупатели</p>
            <h2>Отзывы</h2>
          </div>
        </div>
        <div v-if="store.state.supplierReviews.length === 0" class="empty-inline">
          Отзывов пока нет.
        </div>
        <div v-else class="reviews-list">
        <article v-for="review in store.state.supplierReviews" :key="review.id" class="review-card">
          <div class="review-head">
            <div>
              <strong>Покупатель #{{ review.author_user_id }}</strong>
              <div class="review-date">{{ formatDate(review.created_at) }}</div>
            </div>
            <div class="stars">
              <span v-for="index in 5" :key="index" :class="{ active: index <= review.rating }">
                <img :src="StarIcon" alt="" class="star-icon" aria-hidden="true" />
              </span>
            </div>
          </div>
          <p>{{ review.comment || 'Без комментария' }}</p>
        </article>
        </div>
      </section>
    </template>
  </main>

  <teleport to="body">
    <div v-if="selectedProduct" class="modal-backdrop" @click.self="closeProductModal">
      <div class="modal-card">
        <button class="modal-close" @click="closeProductModal">
          <img :src="CloseIcon" alt="" class="close-icon" aria-hidden="true" />
        </button>
        <p class="kicker">Товар</p>
        <h2>{{ selectedProduct.name }}</h2>
        <p>{{ selectedProduct.description || 'Описание отсутствует' }}</p>
        <div class="modal-meta">
          <span>{{ Number(selectedProduct.price).toFixed(0) }} ₽/кг</span>
          <span>Мин. заказ: {{ selectedProduct.min_order_qty || 1 }} кг</span>
        </div>

        <div class="qty-row">
          <button class="qty-btn" @click="quantity = Math.max(1, quantity - 1)">
            <img :src="MinusIcon" alt="" class="qty-icon" aria-hidden="true" />
          </button>
          <span>{{ quantity }} кг</span>
          <button class="qty-btn" @click="quantity += 1">
            <img :src="AddIcon" alt="" class="qty-icon" aria-hidden="true" />
          </button>
        </div>

        <div class="modal-total">{{ totalForProduct.toFixed(0) }} ₽</div>

        <div class="modal-actions">
          <button class="action-btn action-btn--primary" @click="addToCart">Добавить</button>
          <button class="action-btn" @click="closeProductModal">Отмена</button>
        </div>
      </div>
    </div>

    <div v-if="showReviewModal" class="modal-backdrop" @click.self="showReviewModal = false">
      <div class="modal-card">
        <button class="modal-close" @click="showReviewModal = false">
          <img :src="CloseIcon" alt="" class="close-icon" aria-hidden="true" />
        </button>
        <p class="kicker">Отзыв</p>
        <h2>Оставить отзыв</h2>
        <div class="field">
          <label>Оценка</label>
          <select v-model="ratingValue">
            <option :value="5">5</option>
            <option :value="4">4</option>
            <option :value="3">3</option>
            <option :value="2">2</option>
            <option :value="1">1</option>
          </select>
        </div>
        <div class="field">
          <label>Комментарий</label>
          <textarea v-model="reviewComment" rows="4" placeholder="Поделитесь впечатлением"></textarea>
        </div>
        <div class="modal-actions">
          <button class="action-btn action-btn--primary" :disabled="isSubmittingReview" @click="submitReview">
            {{ isSubmittingReview ? 'Отправка...' : 'Отправить' }}
          </button>
          <button class="action-btn" @click="showReviewModal = false">Отмена</button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<style scoped>
.supplier-page {
  display: grid;
  gap: 1.25rem;
  padding-bottom: 2rem;
  color: var(--sl-ink);
}

h1,
h2,
h3 {
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

/* ===== СТАТУС ===== */
.status-box {
  padding: 1rem 1.25rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-left: 4px solid var(--sl-leaf);
  font-weight: 600;
}

.status-box--error {
  color: #b3261e;
  background: #fbeaea;
  border-color: #b3261e;
}

/* ===== HERO ===== */
.hero-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 1.5rem 2rem;
  padding: clamp(1.25rem, 3vw, 2.25rem);
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
}

.hero-main {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
  min-width: 0;
}

.hero-main > div:last-child {
  min-width: 0;
}

.avatar {
  flex: 0 0 auto;
  width: 84px;
  height: 84px;
  display: grid;
  place-items: center;
  background: var(--sl-ink);
  color: var(--sl-lime);
  font-family: var(--sl-display);
  font-weight: 600;
  font-size: 2rem;
}

.hero-card h1 {
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  line-height: 1.15;
  overflow-wrap: anywhere;
}

.subline {
  margin: 0.5rem 0 0;
  font-weight: 600;
  color: var(--sl-muted);
}

.supplier-desc {
  margin: 0.75rem 0 0;
  max-width: 640px;
  line-height: 1.5;
  color: #3f4a37;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
  margin-top: 1.1rem;
  border: 1px solid var(--sl-line);
  background: #fff;
  width: fit-content;
  max-width: 100%;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.5rem 0.85rem;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--sl-ink);
}

.meta-item + .meta-item {
  border-left: 1px solid var(--sl-line);
}

.meta-icon,
.close-icon,
.product-image-icon,
.star-icon,
.qty-icon,
.btn-icon-chat {
  display: block;
  object-fit: contain;
  filter: grayscale(1) brightness(0.35);
}

.meta-icon {
  width: 15px;
  height: 15px;
}

.close-icon {
  width: 14px;
  height: 14px;
}

.hero-actions {
  display: grid;
  gap: 0.5rem;
  min-width: 200px;
}

/* ===== КНОПКИ ===== */
.action-btn,
.link-btn,
.qty-btn {
  border-radius: 0;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.7rem 1.2rem;
  background: transparent;
  color: var(--sl-ink);
  border: 1px solid var(--sl-ink);
}

.action-btn:hover:not(:disabled) {
  background: var(--sl-ink);
  color: #fff;
}

.action-btn--primary {
  background: var(--sl-ink);
  color: #fff;
}

.action-btn--primary:hover:not(:disabled) {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.action-btn--chat {
  background: #fff;
  border-color: var(--sl-line);
}

.action-btn--chat:hover:not(:disabled) {
  background: var(--sl-lime);
  border-color: var(--sl-lime);
  color: var(--sl-ink);
}

.action-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-icon-chat {
  width: 16px;
  height: 16px;
}

.link-btn {
  padding: 0.4rem 0;
  background: none;
  border: none;
  border-bottom: 1px solid transparent;
  color: var(--sl-ink);
}

.link-btn:hover {
  border-bottom-color: var(--sl-ink);
}

.action-btn:focus-visible,
.link-btn:focus-visible,
.qty-btn:focus-visible,
.modal-close:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

/* ===== ПАНЕЛИ ===== */
.panel {
  padding: clamp(1.25rem, 3vw, 2.25rem);
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
}

.panel-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 1.25rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--sl-line);
}

.panel h2 {
  font-size: clamp(1.25rem, 2.4vw, 1.6rem);
}

/* ===== ТОВАРЫ ===== */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.75rem;
}

.product-card {
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid var(--sl-line);
  transition: border-color 0.2s ease;
}

.product-card:hover {
  border-color: var(--sl-ink);
}

.product-image {
  min-height: 130px;
  display: grid;
  place-items: center;
  background:
    repeating-linear-gradient(135deg, rgba(20, 33, 15, 0.04) 0 1px, transparent 1px 12px),
    var(--sl-paper);
  border-bottom: 1px solid var(--sl-line);
}

.product-image-icon {
  width: 36px;
  height: 36px;
}

.product-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 1.1rem 1.1rem 1.2rem;
}

.product-body h3 {
  margin: 0 0 0.5rem;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.35;
}

.product-body p {
  align-self: flex-start;
  margin: 0;
  padding: 0.2rem 0.5rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.product-meta {
  display: grid;
  gap: 0.25rem;
  margin-top: 1rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--sl-line);
}

.product-meta strong {
  font-family: var(--sl-display);
  font-size: 1.2rem;
  font-weight: 600;
}

.product-meta span {
  font-size: 0.88rem;
  color: var(--sl-muted);
}

.product-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: auto;
  padding-top: 1rem;
}

.product-actions .action-btn {
  flex: 1 1 auto;
  padding-inline: 0.55rem;
  font-size: 0.9rem;
  white-space: nowrap;
}

/* ===== ОТЗЫВЫ ===== */
.reviews-list {
  display: grid;
  gap: 0.75rem;
}

.review-card {
  padding: 1.1rem 1.25rem;
  background: #fff;
  border: 1px solid var(--sl-line);
}

.review-card p {
  margin: 0;
  line-height: 1.55;
  color: #3f4a37;
}

.review-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--sl-line);
}

.review-date {
  margin-top: 0.15rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.stars {
  display: flex;
  gap: 0.2rem;
}

.stars span {
  opacity: 0.2;
}

.stars .active {
  opacity: 1;
}

.star-icon {
  width: 14px;
  height: 14px;
}

.empty-inline {
  padding: 1.25rem;
  background: #fff;
  border: 1px dashed var(--sl-line);
  color: var(--sl-muted);
}

/* ===== МОДАЛКИ ===== */
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
  position: relative;
  width: min(560px, 100%);
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
  padding-right: 2.5rem;
  font-size: clamp(1.2rem, 2.6vw, 1.5rem);
}

.modal-card > p:not(.kicker) {
  margin: 0.75rem 0 0;
  color: #3f4a37;
}

.modal-close {
  position: absolute;
  top: 0.9rem;
  right: 0.9rem;
  width: 34px;
  height: 34px;
  padding: 0;
  display: grid;
  place-items: center;
  background: #fff;
  border: 1px solid var(--sl-line);
  border-radius: 0;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.modal-close:hover {
  border-color: var(--sl-ink);
  background: var(--sl-paper);
}

.modal-meta,
.qty-row,
.modal-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1.25rem;
}

.modal-meta span {
  padding: 0.2rem 0.5rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.qty-row {
  align-items: center;
  gap: 0;
  width: fit-content;
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

.qty-icon {
  width: 16px;
  height: 16px;
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

.modal-actions .action-btn {
  flex: 1 1 auto;
}

.field {
  display: grid;
  gap: 0.4rem;
  margin-top: 1.1rem;
}

.field label {
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

select,
textarea {
  width: 100%;
  border-radius: 0;
  border: 1px solid var(--sl-line);
  background: #fff;
  padding: 0.75rem 0.9rem;
  color: var(--sl-ink);
}

select:focus,
textarea:focus {
  border-color: var(--sl-leaf);
}

/* ===== АДАПТИВ ===== */
@media (max-width: 900px) {
  .hero-card {
    grid-template-columns: 1fr;
  }

  .hero-actions {
    min-width: 0;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  }

  .review-head,
  .panel-head {
    display: grid;
  }

  .panel-head .link-btn {
    justify-self: start;
  }
}

@media (max-width: 520px) {
  .hero-main {
    display: grid;
    gap: 1rem;
  }

  .avatar {
    width: 64px;
    height: 64px;
    font-size: 1.5rem;
  }

  .meta {
    width: 100%;
  }

  .meta-item {
    flex: 1 1 100%;
  }

  .meta-item + .meta-item {
    border-left: none;
    border-top: 1px solid var(--sl-line);
  }
}
</style>
