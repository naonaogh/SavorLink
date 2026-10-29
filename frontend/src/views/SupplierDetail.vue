<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore, type Product, type Supplier } from '@/stores/shopStore'
import { useRequireAuth } from '@/composables/useRequireAuth'
import { useToast } from '@/composables/useToast'
import { getApiErrorMessage } from '@/services/apiClient'
import {
  AppAvatar,
  AppBadge,
  AppButton,
  AppIcon,
  AppModal,
  AppSection,
  EmptyState,
  ErrorState,
  FormField,
  LoadingState,
  ProductThumb,
  QuantityStepper,
  RatingStars,
} from '@/components/ui'
import { formatDate, formatNumber, formatPrice, pluralize } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const store = useShopStore()
const authStore = useAuthStore()
const requireAuth = useRequireAuth()
const toast = useToast()

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

/* локальное состояние загрузки (для отображения) */
const loaded = ref(false)
const isAddingToCart = ref(false)

const loadSupplier = async () => {
  if (supplierId.value) {
    await Promise.all([store.fetchSupplierDetail(supplierId.value), store.fetchSupplierReviews(supplierId.value)])
  }
  loaded.value = true
}

onMounted(loadSupplier)

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
  const name = selectedProduct.value.name
  isAddingToCart.value = true
  try {
    await store.addToCart(selectedProduct.value, quantity.value)
    toast.success('Товар добавлен в корзину', `${name} — ${formatNumber(quantity.value)} кг`)
    closeProductModal()
  } catch (error) {
    toast.error('Не удалось добавить товар в корзину', getApiErrorMessage(error, 'Попробуйте ещё раз'))
  } finally {
    isAddingToCart.value = false
  }
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
    toast.success('Спасибо за отзыв', 'Оценка поставщика обновлена')
  } catch (error: unknown) {
    toast.error('Не удалось отправить отзыв', getApiErrorMessage(error, 'Не удалось отправить отзыв'))
  } finally {
    isSubmittingReview.value = false
  }
}

/* ── только для отображения ─────────────────── */
const isLoading = computed(() => !loaded.value || store.state.loading)
const chatUserId = computed(() => {
  const owner = supplier.value?.users?.[0]
  return authStore.user && owner && owner.id !== authStore.user.id ? owner.id : null
})
const locationText = computed(() => (supplier.value ? [supplier.value.region, supplier.value.city].filter(Boolean).join(', ') : ''))
const productsCount = computed(() => supplier.value?.products.length ?? 0)
const reviewsCount = computed(() => store.state.supplierReviews.length)
const isSupplierFav = computed(() => (supplier.value ? store.isSupplierFavorite(supplier.value.id) : false))

const RATING_LABELS = ['Плохо', 'Ниже среднего', 'Нормально', 'Хорошо', 'Отлично']
const ratingHint = computed(() => RATING_LABELS[ratingValue.value - 1] ?? '')

const onProductModalToggle = (open: boolean) => {
  if (!open) closeProductModal()
}
</script>

<template>
  <div class="page">
    <AppButton to="/catalog" variant="ghost" size="sm" icon="arrow-left" class="back-link">Каталог</AppButton>

    <LoadingState v-if="isLoading" variant="skeleton" :rows="5" label="Загрузка данных поставщика…" />

    <ErrorState
      v-else-if="store.state.error"
      :message="store.state.error"
      :retrying="store.state.loading"
      @retry="loadSupplier"
    />

    <template v-else-if="supplier">
      <!-- ===== ШАПКА ПОСТАВЩИКА ===== -->
      <section class="hero ui-card" aria-labelledby="supplier-title">
        <AppAvatar :name="supplier.name" :size="72" />

        <div class="hero__info">
          <p class="ui-eyebrow">Поставщик</p>
          <h1 id="supplier-title" class="hero__title">{{ supplier.name }}</h1>
          <p v-if="supplier.company && supplier.company !== supplier.name" class="hero__company">
            {{ supplier.company }}
          </p>
          <p v-if="supplier.description" class="hero__desc">{{ supplier.description }}</p>

          <ul class="hero__meta">
            <li>
              <RatingStars
                v-if="supplier.reviews > 0"
                :value="supplier.rating"
                :size="16"
                show-value
              />
              <span v-else class="ui-muted">Пока нет оценок</span>
              <span v-if="supplier.reviews > 0" class="ui-muted ui-num">
                {{ supplier.reviews }} {{ pluralize(supplier.reviews, ['отзыв', 'отзыва', 'отзывов']) }}
              </span>
            </li>
            <li v-if="locationText">
              <AppIcon name="map-pin" :size="16" />
              <span>{{ locationText }}</span>
            </li>
            <li v-if="supplier.since">
              <AppIcon name="calendar" :size="16" />
              <span>На платформе с {{ supplier.since }}</span>
            </li>
            <li>
              <AppIcon name="package" :size="16" />
              <span class="ui-num">
                {{ productsCount }} {{ pluralize(productsCount, ['товар', 'товара', 'товаров']) }}
              </span>
            </li>
          </ul>
        </div>

        <div class="hero__actions">
          <AppButton
            v-if="chatUserId"
            variant="secondary"
            icon="message"
            @click="router.push(`/chat?userId=${chatUserId}`)"
          >
            Написать
          </AppButton>
          <AppButton v-if="isBuyer" icon="star" @click="showReviewModal = true">Оценить</AppButton>
          <AppButton
            variant="secondary"
            class="fav-toggle"
            :class="{ 'is-on': isSupplierFav }"
            :aria-pressed="isSupplierFav"
            @click="toggleSupplierFavorite(supplier)"
          >
            <span class="fav-toggle__inner">
              <AppIcon name="heart" :size="18" :filled="isSupplierFav" />
              {{ isSupplierFav ? 'В избранном' : 'В избранное' }}
            </span>
          </AppButton>
        </div>
      </section>

      <!-- ===== АССОРТИМЕНТ ===== -->
      <section class="block" aria-labelledby="products-title">
        <div class="block__head">
          <div class="block__titles">
            <p class="ui-eyebrow">Ассортимент</p>
            <h2 id="products-title" class="block__title">
              Продукция <span class="block__count ui-num">{{ productsCount }}</span>
            </h2>
          </div>
          <AppButton
            variant="ghost"
            size="sm"
            :icon="showReviews ? 'eye-off' : 'eye'"
            :aria-expanded="showReviews"
            aria-controls="supplier-reviews"
            @click="showReviews = !showReviews"
          >
            {{ showReviews ? 'Скрыть отзывы' : 'Показать отзывы' }}
          </AppButton>
        </div>

        <EmptyState
          v-if="productsCount === 0"
          icon="package"
          title="Товаров пока нет"
          description="Поставщик ещё не добавил продукцию в каталог."
        />

        <ul v-else class="products-grid">
          <li v-for="product in supplier.products" :key="product.id">
            <article class="product-card ui-card ui-card--interactive">
              <div class="product-card__media">
                <ProductThumb :category="product.category?.name" size="fill" />
                <button
                  type="button"
                  class="fav-btn"
                  :class="{ 'is-on': store.isProductFavorite(product.id) }"
                  :aria-pressed="store.isProductFavorite(product.id)"
                  :aria-label="
                    store.isProductFavorite(product.id)
                      ? `Убрать «${product.name}» из избранного`
                      : `Добавить «${product.name}» в избранное`
                  "
                  :title="store.isProductFavorite(product.id) ? 'В избранном' : 'В избранное'"
                  @click="toggleProductFavorite(product)"
                >
                  <AppIcon name="heart" :size="18" :filled="store.isProductFavorite(product.id)" />
                </button>
              </div>

              <div class="product-card__body">
                <AppBadge size="sm" :tone="product.category ? 'accent' : 'neutral'" class="product-card__cat">
                  {{ product.category?.name || 'Без категории' }}
                </AppBadge>
                <h3 class="product-card__name">{{ product.name }}</h3>

                <div class="product-card__price">
                  <strong class="ui-num">{{ formatPrice(product.price) }}</strong>
                  <span class="ui-muted">за кг</span>
                </div>

                <dl class="product-card__facts">
                  <div>
                    <dt>Остаток</dt>
                    <dd class="ui-num">{{ formatNumber(product.quantity_in_stock ?? 0) }} кг</dd>
                  </div>
                  <div v-if="product.min_order_qty">
                    <dt>Мин. заказ</dt>
                    <dd class="ui-num">{{ formatNumber(product.min_order_qty) }} кг</dd>
                  </div>
                </dl>

                <AppButton icon="cart" block class="product-card__cta" @click="openProductModal(product)">
                  В корзину
                </AppButton>
              </div>
            </article>
          </li>
        </ul>
      </section>

      <!-- ===== ОТЗЫВЫ ===== -->
      <AppSection
        v-if="showReviews"
        id="supplier-reviews"
        title="Отзывы покупателей"
        :description="
          reviewsCount
            ? `${reviewsCount} ${pluralize(reviewsCount, ['отзыв', 'отзыва', 'отзывов'])} о поставщике`
            : undefined
        "
      >
        <template #actions>
          <RatingStars v-if="supplier.reviews > 0" :value="supplier.rating" show-value />
        </template>

        <EmptyState
          v-if="reviewsCount === 0"
          compact
          icon="message"
          title="Отзывов пока нет"
          :description="isBuyer ? 'Работали с этим поставщиком? Поделитесь впечатлением.' : undefined"
        >
          <AppButton v-if="isBuyer" icon="star" @click="showReviewModal = true">Оставить отзыв</AppButton>
        </EmptyState>

        <ul v-else class="reviews">
          <li v-for="review in store.state.supplierReviews" :key="review.id" class="review">
            <AppAvatar name="Покупатель" :size="40" tone="neutral" />
            <div class="review__main">
              <div class="review__head">
                <div>
                  <p class="review__author">Покупатель #{{ review.author_user_id }}</p>
                  <time class="review__date" :datetime="review.created_at">
                    {{ formatDate(review.created_at, 'long') }}
                  </time>
                </div>
                <RatingStars :value="review.rating" :size="14" />
              </div>
              <p class="review__text" :class="{ 'ui-muted': !review.comment }">
                {{ review.comment || 'Без комментария' }}
              </p>
            </div>
          </li>
        </ul>
      </AppSection>
    </template>

    <EmptyState
      v-else
      icon="store"
      title="Поставщик не найден"
      description="Возможно, он был удалён или ссылка устарела."
    >
      <AppButton to="/catalog" icon="arrow-left">Вернуться в каталог</AppButton>
    </EmptyState>
  </div>

  <!-- ===== МОДАЛКА: В КОРЗИНУ ===== -->
  <AppModal
    :open="!!selectedProduct"
    :title="selectedProduct?.name ?? ''"
    :description="selectedProduct ? `${formatPrice(selectedProduct.price)} за кг` : undefined"
    size="sm"
    :persistent="isAddingToCart"
    @update:open="onProductModalToggle"
  >
    <div v-if="selectedProduct" class="cart-modal">
      <div class="cart-modal__product">
        <ProductThumb :category="selectedProduct.category?.name" size="md" />
        <div class="cart-modal__info">
          <AppBadge size="sm" :tone="selectedProduct.category ? 'accent' : 'neutral'">
            {{ selectedProduct.category?.name || 'Без категории' }}
          </AppBadge>
          <p class="cart-modal__desc" :class="{ 'ui-muted': !selectedProduct.description }">
            {{ selectedProduct.description || 'Описание отсутствует' }}
          </p>
        </div>
      </div>

      <dl class="cart-modal__facts">
        <div>
          <dt>Мин. заказ</dt>
          <dd class="ui-num">{{ formatNumber(selectedProduct.min_order_qty || 1) }} кг</dd>
        </div>
        <div>
          <dt>В наличии</dt>
          <dd class="ui-num">{{ formatNumber(selectedProduct.quantity_in_stock ?? 0) }} кг</dd>
        </div>
      </dl>

      <div class="cart-modal__qty">
        <span class="ui-label">Количество</span>
        <QuantityStepper v-model="quantity" :min="1" unit="кг" label="Количество, кг" />
      </div>

      <div class="cart-modal__total">
        <span>Итого</span>
        <strong class="ui-num">{{ formatPrice(totalForProduct) }}</strong>
      </div>
    </div>

    <template #footer>
      <AppButton variant="secondary" :disabled="isAddingToCart" @click="closeProductModal">Отмена</AppButton>
      <AppButton icon="cart" :loading="isAddingToCart" @click="addToCart">Добавить</AppButton>
    </template>
  </AppModal>

  <!-- ===== МОДАЛКА: ОТЗЫВ ===== -->
  <AppModal
    v-model:open="showReviewModal"
    title="Оставить отзыв"
    :description="supplier ? `О поставщике «${supplier.name}»` : undefined"
    size="sm"
    :persistent="isSubmittingReview"
  >
    <form id="review-form" class="review-form" @submit.prevent="submitReview">
      <fieldset class="rating-field">
        <legend class="ui-label">Оценка <span class="rating-field__req" aria-hidden="true">*</span></legend>
        <div class="rating-field__row">
          <div class="rating-field__stars">
            <button
              v-for="n in 5"
              :key="n"
              type="button"
              class="star-btn"
              :class="{ 'is-on': n <= ratingValue }"
              :aria-label="`Оценка ${n} из 5`"
              :aria-pressed="n === ratingValue"
              @click="ratingValue = n"
            >
              <AppIcon name="star" :size="28" :filled="n <= ratingValue" :stroke-width="1.6" />
            </button>
          </div>
          <span class="rating-field__hint" aria-live="polite">{{ ratingHint }}</span>
        </div>
      </fieldset>

      <FormField label="Комментарий" hint="Необязательно" v-slot="{ id, describedBy }">
        <textarea
          :id="id"
          v-model="reviewComment"
          rows="4"
          placeholder="Поделитесь впечатлением о качестве, сроках и общении"
          :aria-describedby="describedBy"
        ></textarea>
      </FormField>
    </form>

    <template #footer>
      <AppButton variant="secondary" :disabled="isSubmittingReview" @click="showReviewModal = false">Отмена</AppButton>
      <AppButton type="submit" form="review-form" icon="send" :loading="isSubmittingReview">Отправить</AppButton>
    </template>
  </AppModal>
</template>

<style scoped>
.page {
  display: grid;
  gap: 1.5rem;
}

.back-link {
  justify-self: start;
  margin: 0 0 -0.75rem -0.6rem;
}

/* ===== ШАПКА ===== */
.hero {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: start;
  gap: 1.25rem 1.5rem;
  padding: clamp(1.25rem, 3vw, 2rem);
}

.hero__info {
  display: grid;
  gap: 0.4rem;
  min-width: 0;
}

.hero__title {
  font-size: var(--fs-3xl);
  overflow-wrap: anywhere;
}

.hero__company {
  color: var(--c-text-2);
  font-weight: 600;
}

.hero__desc {
  max-width: 720px;
  color: var(--c-text-2);
  line-height: 1.6;
}

.hero__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.25rem;
  margin: 0.5rem 0 0;
  padding: 0;
  list-style: none;
  color: var(--c-text-2);
  font-size: var(--fs-sm);
}

.hero__meta li {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.hero__meta .app-icon {
  color: var(--c-accent-600);
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.6rem;
}

.fav-toggle__inner {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.fav-toggle.is-on .app-icon {
  color: var(--c-danger);
}

/* ===== БЛОКИ ===== */
.block {
  display: grid;
  gap: 1rem;
}

.block__head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.75rem 1rem;
}

.block__titles {
  display: grid;
  gap: 0.25rem;
}

.block__title {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  font-size: var(--fs-xl);
}

.block__count {
  padding: 0.1rem 0.55rem;
  border-radius: var(--r-full);
  background: var(--c-surface-sunken);
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  font-weight: 700;
}

/* ===== ТОВАРЫ ===== */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.products-grid > li {
  display: flex;
}

.product-card {
  display: flex;
  flex: 1;
  flex-direction: column;
  overflow: hidden;
}

.product-card__media {
  position: relative;
  aspect-ratio: 16 / 10;
  border-bottom: 1px solid var(--c-border);
}

.fav-btn {
  position: absolute;
  top: 0.65rem;
  right: 0.65rem;
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  padding: 0;
  border: 1px solid var(--c-border);
  border-radius: var(--r-full);
  background: var(--c-surface);
  color: var(--c-muted);
  transition:
    color var(--dur) var(--ease),
    border-color var(--dur) var(--ease),
    background var(--dur) var(--ease);
}

.fav-btn:hover {
  border-color: var(--c-border-strong);
  color: var(--c-danger);
}

.fav-btn.is-on {
  border-color: var(--c-danger-bg);
  background: var(--c-danger-bg);
  color: var(--c-danger);
}

.product-card__body {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 0.6rem;
  padding: 1rem 1.1rem 1.1rem;
}

.product-card__cat {
  align-self: flex-start;
}

.product-card__name {
  font-size: var(--fs-md);
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.product-card__price {
  display: flex;
  align-items: baseline;
  gap: 0.35rem;
  font-size: var(--fs-sm);
}

.product-card__price strong {
  color: var(--c-brand-800);
  font-size: var(--fs-xl);
  font-weight: 800;
  letter-spacing: -0.02em;
}

.product-card__facts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 1.25rem;
  margin: 0;
  font-size: var(--fs-sm);
}

.product-card__facts div {
  display: flex;
  gap: 0.35rem;
}

.product-card__facts dt {
  color: var(--c-muted);
}

.product-card__facts dd {
  margin: 0;
  font-weight: 700;
  color: var(--c-text-2);
}

.product-card__cta {
  margin-top: auto;
}

/* ===== ОТЗЫВЫ ===== */
.reviews {
  display: grid;
  margin: 0;
  padding: 0;
  list-style: none;
}

.review {
  display: flex;
  gap: 0.9rem;
  padding: 1rem 0;
  border-bottom: 1px solid var(--c-border);
}

.review:first-child {
  padding-top: 0;
}

.review:last-child {
  padding-bottom: 0;
  border-bottom: none;
}

.review__main {
  display: grid;
  flex: 1;
  gap: 0.45rem;
  min-width: 0;
}

.review__head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.35rem 1rem;
}

.review__author {
  font-weight: 700;
  font-size: var(--fs-sm);
}

.review__date {
  color: var(--c-muted);
  font-size: var(--fs-xs);
}

.review__text {
  color: var(--c-text-2);
  line-height: 1.6;
  overflow-wrap: anywhere;
}

/* ===== МОДАЛКИ ===== */
.cart-modal {
  display: grid;
  gap: 1.1rem;
}

.cart-modal__product {
  display: flex;
  align-items: flex-start;
  gap: 0.9rem;
}

.cart-modal__info {
  display: grid;
  justify-items: start;
  gap: 0.4rem;
  min-width: 0;
}

.cart-modal__desc {
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  line-height: 1.55;
}

.cart-modal__facts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.6rem;
  margin: 0;
}

.cart-modal__facts div {
  padding: 0.65rem 0.8rem;
  border-radius: var(--r-sm);
  background: var(--c-surface-sunken);
}

.cart-modal__facts dt {
  color: var(--c-muted);
  font-size: var(--fs-xs);
}

.cart-modal__facts dd {
  margin: 0;
  font-weight: 700;
}

.cart-modal__qty {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
}

.cart-modal__total {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--c-border);
  color: var(--c-text-2);
  font-weight: 600;
}

.cart-modal__total strong {
  color: var(--c-brand-800);
  font-size: var(--fs-2xl);
  font-weight: 800;
  letter-spacing: -0.02em;
}

.review-form {
  display: grid;
  gap: 1.1rem;
}

.rating-field {
  display: grid;
  gap: 0.5rem;
  margin: 0;
  padding: 0;
  border: 0;
}

.rating-field legend {
  padding: 0;
  margin-bottom: 0.5rem;
}

.rating-field__req {
  color: var(--c-danger);
}

.rating-field__row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 1rem;
}

.rating-field__stars {
  display: flex;
  gap: 0.15rem;
}

.star-btn {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  padding: 0;
  border: 0;
  border-radius: var(--r-sm);
  background: transparent;
  color: var(--c-border-strong);
  transition:
    color var(--dur) var(--ease),
    background var(--dur) var(--ease);
}

.star-btn:hover {
  background: var(--c-surface-sunken);
}

.star-btn.is-on {
  color: var(--c-warning);
}

.rating-field__hint {
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  font-weight: 700;
}

/* ===== АДАПТИВ ===== */
@media (max-width: 900px) {
  .hero {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .hero__actions {
    grid-column: 1 / -1;
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .hero {
    grid-template-columns: minmax(0, 1fr);
  }

  .hero__actions > * {
    flex: 1 1 100%;
  }

  .products-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .product-card__media {
    aspect-ratio: 16 / 7;
  }
}
</style>
