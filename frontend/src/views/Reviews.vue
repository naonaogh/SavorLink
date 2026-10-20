<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { getApiErrorMessage } from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'

interface PlatformReview {
  id: number
  author_name: string
  author_position: string | null
  company_name: string | null
  author_role: 'BUYER' | 'SUPPLIER'
  city: string | null
  rating: number
  comment: string
  created_at: string
}

interface PlatformReviewList {
  items: PlatformReview[]
  total: number
  average_rating: number | null
}

type RoleFilter = 'ALL' | 'BUYER' | 'SUPPLIER'

const router = useRouter()
const authStore = useAuthStore()

const reviews = ref<PlatformReview[]>([])
const total = ref(0)
const averageRating = ref<number | null>(null)
const loading = ref(true)
const error = ref('')
const roleFilter = ref<RoleFilter>('ALL')

const roleLabels: Record<PlatformReview['author_role'], string> = {
  BUYER: 'Покупатель',
  SUPPLIER: 'Поставщик',
}

const filters: { value: RoleFilter; label: string }[] = [
  { value: 'ALL', label: 'Все' },
  { value: 'BUYER', label: 'Покупатели' },
  { value: 'SUPPLIER', label: 'Поставщики' },
]

const filteredReviews = computed(() =>
  roleFilter.value === 'ALL' ? reviews.value : reviews.value.filter((r) => r.author_role === roleFilter.value),
)

const countFor = (value: RoleFilter) =>
  value === 'ALL' ? reviews.value.length : reviews.value.filter((r) => r.author_role === value).length

const pluralReviews = (n: number) => {
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod10 === 1 && mod100 !== 11) return 'отзыв'
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return 'отзыва'
  return 'отзывов'
}

const initials = (name: string) =>
  name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('')

const formatDate = (value: string) =>
  new Date(value).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })

const loadReviews = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get<PlatformReviewList>('/platform-reviews')
    reviews.value = data.items
    total.value = data.total
    averageRating.value = data.average_rating
  } catch (e) {
    error.value = getApiErrorMessage(e, 'Не удалось загрузить отзывы')
  } finally {
    loading.value = false
  }
}

const goHome = () => router.push('/')
const goRegister = () => router.push({ path: '/auth', query: { mode: 'register' } })

onMounted(loadReviews)
</script>

<template>
  <div class="reviews-page">
    <!-- ===== ШАПКА ===== -->
    <section class="head-panel">
      <div class="head-main">
        <p class="kicker">Отзывы / Платформа</p>
        <h1>Что говорят о SavorLink</h1>
        <p class="lead">Мнения ресторанов и поставщиков, которые уже работают через платформу.</p>
      </div>

      <div class="score" aria-live="polite">
        <p class="score-label">Средняя оценка</p>
        <p class="score-value">{{ averageRating !== null ? averageRating.toFixed(1) : '—' }}</p>
        <div class="stars stars--light" :aria-label="`Оценка ${averageRating ?? 0} из 5`">
          <span
            v-for="n in 5"
            :key="n"
            class="star"
            :class="{ 'is-on': averageRating !== null && n <= Math.round(averageRating) }"
            aria-hidden="true"
            >★</span
          >
        </div>
        <p class="score-count">{{ total }} {{ pluralReviews(total) }}</p>
      </div>
    </section>

    <!-- ===== СПИСОК ===== -->
    <section class="list-panel">
      <div class="toolbar">
        <div class="tabs" role="tablist" aria-label="Фильтр по роли автора">
          <button
            v-for="f in filters"
            :key="f.value"
            type="button"
            role="tab"
            class="tab"
            :class="{ 'is-active': roleFilter === f.value }"
            :aria-selected="roleFilter === f.value"
            :disabled="loading || !!error"
            @click="roleFilter = f.value"
          >
            {{ f.label }} <span class="tab-count">{{ countFor(f.value) }}</span>
          </button>
        </div>
      </div>

      <div v-if="loading" class="state">Загружаем отзывы…</div>

      <div v-else-if="error" class="state state--error">
        <p>{{ error }}</p>
        <button type="button" class="btn btn--outline" @click="loadReviews">Повторить</button>
      </div>

      <div v-else-if="filteredReviews.length === 0" class="state">Пока нет отзывов в этой категории.</div>

      <ul v-else class="reviews-grid">
        <li v-for="review in filteredReviews" :key="review.id" class="review-card">
          <div class="review-top">
            <div class="stars" :aria-label="`Оценка ${review.rating} из 5`">
              <span v-for="n in 5" :key="n" class="star" :class="{ 'is-on': n <= review.rating }" aria-hidden="true"
                >★</span
              >
            </div>
            <span class="role-badge" :class="`role-badge--${review.author_role.toLowerCase()}`">
              {{ roleLabels[review.author_role] }}
            </span>
          </div>

          <blockquote class="review-text">{{ review.comment }}</blockquote>

          <div class="review-author">
            <span class="avatar" aria-hidden="true">{{ initials(review.author_name) }}</span>
            <div class="author-info">
              <p class="author-name">{{ review.author_name }}</p>
              <p class="author-meta">
                <template v-if="review.author_position">{{ review.author_position }}</template>
                <template v-if="review.author_position && review.company_name"> · </template>
                <template v-if="review.company_name">{{ review.company_name }}</template>
              </p>
            </div>
          </div>

          <p class="review-foot">
            <span v-if="review.city">{{ review.city }}</span>
            <time :datetime="review.created_at">{{ formatDate(review.created_at) }}</time>
          </p>
        </li>
      </ul>

      <div class="cta">
        <button type="button" class="btn btn--outline" @click="goHome">
          На главную <span class="arrow" aria-hidden="true">→</span>
        </button>
        <button v-if="!authStore.token" type="button" class="btn btn--solid" @click="goRegister">
          Присоединиться к платформе
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.reviews-page {
  display: grid;
  gap: 1.25rem;
  margin: 1.25rem 0 2rem;
  color: var(--sl-ink);
}

p,
h1,
blockquote {
  margin: 0;
}

/* ===== ШАПКА ===== */
.head-panel {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: stretch;
  gap: 1.5rem 2.5rem;
  padding: clamp(1.5rem, 4vw, 3rem);
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
}

.head-main {
  align-self: center;
}

.kicker {
  margin-bottom: 0.9rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

.head-main h1 {
  font-size: clamp(1.6rem, 3.4vw, 2.6rem);
  color: var(--sl-ink);
}

.lead {
  max-width: 560px;
  margin-top: 0.9rem;
  color: var(--sl-muted);
}

/* блок средней оценки */
.score {
  min-width: 220px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.35rem;
  padding: 1.5rem 1.75rem;
  color: #fff;
  border-top: 3px solid var(--sl-lime);
  background:
    repeating-linear-gradient(135deg, rgba(198, 236, 154, 0.05) 0 1px, transparent 1px 14px),
    var(--sl-ink);
}

.score-label,
.score-count {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--sl-lime);
}

.score-count {
  color: rgba(255, 255, 255, 0.65);
}

.score-value {
  font-family: var(--sl-display);
  font-size: 3.25rem;
  font-weight: 700;
  line-height: 1;
}

/* звёзды */
.stars {
  display: inline-flex;
  gap: 0.15rem;
  font-size: 1rem;
  line-height: 1;
}

.star {
  color: rgba(20, 33, 15, 0.18);
}

.star.is-on {
  color: var(--sl-leaf);
}

.stars--light .star {
  color: rgba(255, 255, 255, 0.22);
}

.stars--light .star.is-on {
  color: var(--sl-lime);
}

/* ===== СПИСОК ===== */
.list-panel {
  padding: clamp(1.25rem, 4vw, 3rem);
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
}

.toolbar {
  margin-bottom: 1.75rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--sl-line);
}

.tabs {
  display: inline-flex;
  flex-wrap: wrap;
  border: 1px solid var(--sl-ink);
}

.tab {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.1rem;
  border: none;
  border-radius: 0;
  background: transparent;
  color: var(--sl-ink);
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.tab + .tab {
  border-left: 1px solid var(--sl-ink);
}

.tab:hover:not(.is-active):not(:disabled) {
  background: var(--sl-lime);
}

.tab.is-active {
  background: var(--sl-ink);
  color: #fff;
}

.tab:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.tab-count {
  min-width: 1.4rem;
  padding: 0.05rem 0.35rem;
  background: var(--sl-paper);
  color: var(--sl-ink);
  font-size: 0.72rem;
  font-weight: 800;
  text-align: center;
}

.tab.is-active .tab-count {
  background: var(--sl-lime);
}

/* сетка карточек: линии между карточками */
.reviews-grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1px;
  background: var(--sl-line);
  border: 1px solid var(--sl-line);
}

.review-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 1.75rem;
  background: #fff;
}

/* одиночная последняя карточка — на всю ширину */
.review-card:last-child:nth-child(odd) {
  grid-column: 1 / -1;
}

.review-card::before {
  content: '';
  position: absolute;
  top: -1px;
  left: 0;
  width: 0;
  height: 3px;
  background: var(--sl-leaf);
  transition: width 0.35s ease;
}

.review-card:hover::before {
  width: 100%;
}

.review-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.role-badge {
  padding: 0.2rem 0.5rem;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.role-badge--buyer {
  background: var(--sl-lime);
  color: var(--sl-ink);
}

.role-badge--supplier {
  background: var(--sl-ink);
  color: var(--sl-lime);
}

.review-text {
  flex: 1;
  position: relative;
  padding-left: 1.1rem;
  border-left: 2px solid var(--sl-lime);
  font-size: 1.02rem;
  line-height: 1.6;
  color: var(--sl-ink);
}

.review-author {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.avatar {
  width: 2.75rem;
  height: 2.75rem;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  background: var(--sl-ink);
  color: var(--sl-lime);
  font-family: var(--sl-display);
  font-size: 0.9rem;
  font-weight: 700;
}

.author-info {
  min-width: 0;
}

.author-name {
  font-weight: 800;
}

.author-meta {
  font-size: 0.88rem;
  color: var(--sl-muted);
}

.review-foot {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--sl-line);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.review-foot time:only-child {
  margin-left: auto;
}

/* состояния */
.state {
  display: grid;
  justify-items: start;
  gap: 1rem;
  padding: 2rem;
  background: #fff;
  border: 1px dashed var(--sl-line);
  color: var(--sl-muted);
  font-weight: 600;
}

.state--error {
  background: #fbeaea;
  border: 1px solid #b3261e;
  color: #b3261e;
}

/* кнопки */
.cta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 2rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.8rem 1.3rem;
  border-radius: 0;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.btn--solid {
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
}

.btn--solid:hover {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.btn--outline {
  background: transparent;
  color: var(--sl-ink);
  border: 1px solid var(--sl-ink);
}

.btn--outline:hover {
  background: var(--sl-ink);
  color: #fff;
}

.btn .arrow {
  transition: transform 0.2s ease;
}

.btn:hover .arrow {
  transform: translateX(4px);
}

.btn:focus-visible,
.tab:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
  .review-card::before,
  .btn .arrow {
    transition: none;
  }
}

/* ===== АДАПТИВ ===== */
@media (max-width: 900px) {
  .head-panel {
    grid-template-columns: 1fr;
  }

  .reviews-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 520px) {
  .reviews-page {
    margin-top: 0.75rem;
  }

  .review-card {
    padding: 1.25rem;
  }

  .tabs {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .tab {
    flex-direction: column;
    justify-content: center;
    gap: 0.3rem;
    padding: 0.6rem 0.25rem;
    font-size: 0.82rem;
  }

  .review-foot {
    flex-direction: column;
    gap: 0.25rem;
  }

  .review-foot time:only-child {
    margin-left: 0;
  }

  .cta .btn {
    flex: 1 1 100%;
    justify-content: center;
  }
}
</style>
