<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import HeroImage from '@/assets/images/home-hero.jpg'
import api from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'
import AppAvatar from '@/components/ui/AppAvatar.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import RatingStars from '@/components/ui/RatingStars.vue'
import type { IconName } from '@/components/ui/icons'
import { formatDate, pluralize } from '@/utils/format'

const router = useRouter()
const authStore = useAuthStore()

const isGuest = computed(() => !authStore.token)
const isSupplier = computed(() => authStore.user?.role === 'SUPPLIER')

const steps: { title: string; text: string; icon: IconName }[] = [
  {
    title: 'Выбираете поставщика и товары в каталоге',
    text: 'Фильтры по категории, региону и городу, сравнение поставщиков бок о бок.',
    icon: 'search',
  },
  {
    title: 'Оформляете заказ и отслеживаете статусы',
    text: 'Корзина собирает заказы сразу по нескольким поставщикам, статус виден в кабинете.',
    icon: 'truck',
  },
  {
    title: 'Получаете документы и аналитику в одном месте',
    text: 'Документы по заказам и ключевые показатели закупок — без таблиц и переписки.',
    icon: 'file-text',
  },
]

const advantages = [
  'Работа без посредников и скрытых наценок',
  'Карточки поставщиков и товаров в едином стиле',
  'Чат, документы и уведомления доступны из одного интерфейса',
]

const audiences: { title: string; icon: IconName; points: string[]; action: string; role: 'buyer' | 'supplier' }[] = [
  {
    title: 'Ресторанам и кафе',
    icon: 'store',
    role: 'buyer',
    action: 'Я покупатель',
    points: [
      'Каталог поставщиков с фильтрами и сравнением',
      'Корзина и шаблоны для регулярных закупок',
      'Статусы заказов, документы и аналитика',
    ],
  },
  {
    title: 'Поставщикам продуктов',
    icon: 'package',
    role: 'supplier',
    action: 'Я поставщик',
    points: [
      'Карточки товаров с ценами и остатками',
      'Входящие заказы: принять или отклонить в один клик',
      'Чат с покупателями прямо в кабинете',
    ],
  },
]

/* отзывы о платформе — из БД */
interface PlatformReview {
  id: number
  author_name: string
  author_position: string | null
  company_name: string | null
  rating: number
  comment: string
  created_at: string
}

const reviews = ref<PlatformReview[]>([])
const reviewsTotal = ref(0)
const reviewsAverage = ref<number | null>(null)

onMounted(async () => {
  try {
    const { data } = await api.get('/platform-reviews')
    reviews.value = data.items.slice(0, 3)
    reviewsTotal.value = data.total
    reviewsAverage.value = data.average_rating
  } catch {
    // блок отзывов необязательный: при ошибке просто не показываем его
  }
})

const goRegisterBuyer = () => router.push({ path: '/auth', query: { mode: 'register', role: 'buyer' } })
const goRegisterSupplier = () => router.push({ path: '/auth', query: { mode: 'register', role: 'supplier' } })
const goCatalog = () => router.push('/catalog')
const goAudience = (role: 'buyer' | 'supplier') => (role === 'buyer' ? goRegisterBuyer() : goRegisterSupplier())
</script>

<template>
  <div class="home">
    <!-- ===== HERO ===== -->
    <section class="hero">
      <div class="hero__copy">
        <p class="hero__eyebrow">
          <AppIcon name="leaf" :size="14" :stroke-width="2.4" />
          B2B-платформа для ресторанов и поставщиков
        </p>
        <h1 class="hero__title">Поставщики и&nbsp;рестораны находят друг друга <span>быстрее</span></h1>
        <p class="hero__lead">
          Каталог поставщиков, заказы, документы и переписка — в одном рабочем пространстве для закупок.
        </p>

        <div class="hero__actions">
          <template v-if="isGuest">
            <AppButton size="lg" icon-right="arrow-right" @click="goRegisterBuyer">Я покупатель</AppButton>
            <AppButton size="lg" variant="secondary" @click="goRegisterSupplier">Я поставщик</AppButton>
          </template>
          <template v-else>
            <AppButton size="lg" icon-right="arrow-right" to="/cabinet/profile">Открыть кабинет</AppButton>
            <AppButton v-if="isSupplier" size="lg" variant="secondary" to="/cabinet/my-products">Мои товары</AppButton>
          </template>
          <AppButton size="lg" variant="ghost" icon="store" @click="goCatalog">Смотреть каталог</AppButton>
        </div>
      </div>

      <div class="hero__media">
        <img :src="HeroImage" alt="Свежие овощи, зелень и фрукты" class="hero__img" />
      </div>
    </section>

    <!-- ===== КАК ЭТО РАБОТАЕТ ===== -->
    <section class="section" aria-labelledby="how-title">
      <div class="section__head">
        <p class="ui-eyebrow">Как это работает</p>
        <h2 id="how-title" class="section__title">Закупка в три шага</h2>
        <p class="section__lead">
          Покупка и работа с поставщиками проходят в несколько простых шагов без лишних переходов и путаницы.
        </p>
      </div>

      <ol class="steps">
        <li v-for="(step, index) in steps" :key="step.title" class="step ui-card">
          <div class="step__top">
            <span class="step__icon"><AppIcon :name="step.icon" :size="22" /></span>
            <span class="step__num">0{{ index + 1 }}</span>
          </div>
          <h3 class="step__title">{{ step.title }}</h3>
          <p class="step__text">{{ step.text }}</p>
        </li>
      </ol>
    </section>

    <!-- ===== ДЛЯ КОГО ===== -->
    <section class="section" aria-labelledby="who-title">
      <div class="section__head">
        <p class="ui-eyebrow">Для кого</p>
        <h2 id="who-title" class="section__title">Удобно обеим сторонам сделки</h2>
      </div>

      <div class="audiences">
        <article v-for="item in audiences" :key="item.title" class="audience" :class="`audience--${item.role}`">
          <span class="audience__icon"><AppIcon :name="item.icon" :size="22" /></span>
          <h3 class="audience__title">{{ item.title }}</h3>
          <ul class="audience__list">
            <li v-for="point in item.points" :key="point">
              <AppIcon name="check" :size="16" :stroke-width="2.6" />
              <span>{{ point }}</span>
            </li>
          </ul>
          <AppButton
            v-if="isGuest"
            :variant="item.role === 'buyer' ? 'accent' : 'secondary'"
            icon-right="arrow-right"
            class="audience__cta"
            @click="goAudience(item.role)"
          >
            {{ item.action }}
          </AppButton>
        </article>
      </div>
    </section>

    <!-- ===== ПОЧЕМУ ЭТО УДОБНО ===== -->
    <section class="why ui-card" aria-labelledby="why-title">
      <div class="why__head">
        <p class="ui-eyebrow">Преимущества</p>
        <h2 id="why-title" class="section__title">Почему это удобно</h2>
      </div>
      <ul class="why__list">
        <li v-for="item in advantages" :key="item" class="why__item">
          <span class="why__check"><AppIcon name="check" :size="16" :stroke-width="2.6" /></span>
          <span>{{ item }}</span>
        </li>
      </ul>
    </section>

    <!-- ===== ОТЗЫВЫ (из БД) ===== -->
    <section v-if="reviews.length" class="section" aria-labelledby="reviews-title">
      <div class="section__head section__head--row">
        <div>
          <p class="ui-eyebrow">Отзывы</p>
          <h2 id="reviews-title" class="section__title">Что говорят о SavorLink</h2>
        </div>
        <div class="reviews-summary">
          <RatingStars v-if="reviewsAverage !== null" :value="reviewsAverage" show-value />
          <span class="ui-muted">
            {{ reviewsTotal }} {{ pluralize(reviewsTotal, ['отзыв', 'отзыва', 'отзывов']) }}
          </span>
          <AppButton to="/reviews" variant="ghost" size="sm" icon-right="arrow-right">Все отзывы</AppButton>
        </div>
      </div>

      <ul class="reviews">
        <li v-for="review in reviews" :key="review.id" class="review ui-card">
          <RatingStars :value="review.rating" :size="14" />
          <p class="review__text">«{{ review.comment }}»</p>
          <div class="review__author">
            <AppAvatar :name="review.author_name" :size="36" tone="accent" />
            <div class="review__meta">
              <p class="review__name">{{ review.author_name }}</p>
              <p class="review__company">
                {{ [review.author_position, review.company_name].filter(Boolean).join(' · ') }}
              </p>
            </div>
            <time class="review__date" :datetime="review.created_at">{{ formatDate(review.created_at, 'short') }}</time>
          </div>
        </li>
      </ul>
    </section>

    <!-- ===== CTA ===== -->
    <section v-if="isGuest" class="cta" aria-labelledby="cta-title">
      <div>
        <h2 id="cta-title" class="cta__title">Начните работу с SavorLink</h2>
        <p class="cta__text">Регистрация займёт пару минут — выберите роль и подключите своё предприятие.</p>
      </div>
      <div class="cta__actions">
        <AppButton variant="accent" size="lg" @click="goRegisterBuyer">Я покупатель</AppButton>
        <AppButton variant="secondary" size="lg" @click="goRegisterSupplier">Я поставщик</AppButton>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home {
  display: grid;
  gap: clamp(3rem, 7vw, 5.5rem);
}

/* ===== HERO ===== */
.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr);
  align-items: center;
  gap: clamp(1.5rem, 4vw, 3.5rem);
  padding-top: clamp(0.5rem, 2vw, 1.5rem);
}

.hero__copy {
  display: grid;
  gap: 1.25rem;
  justify-items: start;
}

.hero__eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.8rem 0.35rem 0.65rem;
  border: 1px solid var(--c-accent-200);
  border-radius: var(--r-full);
  background: var(--c-accent-50);
  color: var(--c-accent-700);
  font-size: var(--fs-xs);
  font-weight: 700;
}

.hero__title {
  font-size: var(--fs-display);
  line-height: 1.05;
  letter-spacing: -0.035em;
  color: var(--c-brand-900);
}

.hero__title span {
  color: var(--c-accent-600);
}

.hero__lead {
  max-width: 520px;
  color: var(--c-text-2);
  font-size: var(--fs-lg);
  line-height: 1.6;
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.hero__media {
  position: relative;
  border-radius: var(--r-xl);
  overflow: hidden;
  box-shadow: var(--sh-lg);
  aspect-ratio: 5 / 4;
  background: var(--c-brand-900);
}

.hero__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* ===== СЕКЦИИ ===== */
.section {
  display: grid;
  gap: 1.75rem;
}

.section__head {
  display: grid;
  gap: 0.5rem;
  max-width: 680px;
}

.section__head--row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  max-width: none;
}

.section__head--row > div:first-child {
  display: grid;
  gap: 0.5rem;
}

.section__title {
  font-size: var(--fs-3xl);
  letter-spacing: -0.03em;
}

.section__lead {
  color: var(--c-muted);
  font-size: var(--fs-lg);
}

/* шаги */
.steps {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.step {
  display: grid;
  align-content: start;
  gap: 0.75rem;
  padding: 1.5rem;
}

.step__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.step__icon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: var(--r-md);
  background: var(--c-accent-50);
  color: var(--c-accent-700);
}

.step__num {
  font-size: var(--fs-2xl);
  font-weight: 800;
  color: var(--c-border-strong);
  font-variant-numeric: tabular-nums;
}

.step__title {
  font-size: var(--fs-lg);
}

.step__text {
  color: var(--c-muted);
  font-size: var(--fs-sm);
  line-height: 1.6;
}

/* для кого */
.audiences {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.audience {
  display: grid;
  align-content: start;
  gap: 1rem;
  padding: clamp(1.5rem, 3vw, 2rem);
  border-radius: var(--r-xl);
}

.audience--buyer {
  background: var(--c-brand-800);
  color: #fff;
}

.audience--supplier {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
}

.audience__icon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: var(--r-md);
  background: rgba(255, 255, 255, 0.1);
  color: var(--c-accent);
}

.audience--supplier .audience__icon {
  background: var(--c-accent-50);
  color: var(--c-accent-700);
}

.audience__title {
  font-size: var(--fs-xl);
  color: inherit;
}

.audience__list {
  display: grid;
  gap: 0.7rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.audience__list li {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
}

.audience__list .app-icon {
  margin-top: 0.2rem;
  color: var(--c-accent);
}

.audience--buyer .audience__list li {
  color: rgba(255, 255, 255, 0.85);
}

.audience--supplier .audience__list .app-icon {
  color: var(--c-accent-600);
}

.audience__cta {
  justify-self: start;
  margin-top: 0.5rem;
}

/* почему удобно */
.why {
  display: grid;
  grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr);
  align-items: center;
  gap: 1.5rem 3rem;
  padding: clamp(1.5rem, 4vw, 2.5rem);
}

.why__head {
  display: grid;
  gap: 0.5rem;
}

.why__list {
  display: grid;
  gap: 0.25rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.why__item {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.85rem 0;
  border-bottom: 1px solid var(--c-border);
  font-weight: 600;
}

.why__item:last-child {
  border-bottom: none;
}

.why__check {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--c-accent-100);
  color: var(--c-brand-800);
}

/* отзывы */
.reviews-summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 1rem;
  font-size: var(--fs-sm);
}

.reviews {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.review {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
}

.review__text {
  flex: 1;
  color: var(--c-text-2);
  line-height: 1.6;
}

.review__author {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding-top: 1rem;
  border-top: 1px solid var(--c-border);
}

.review__meta {
  flex: 1;
  min-width: 0;
}

.review__name {
  font-weight: 700;
  font-size: var(--fs-sm);
}

.review__company {
  color: var(--c-muted);
  font-size: var(--fs-xs);
}

.review__date {
  align-self: flex-start;
  color: var(--c-muted);
  font-size: var(--fs-xs);
  white-space: nowrap;
}

/* CTA */
.cta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: clamp(1.75rem, 4vw, 2.75rem);
  border-radius: var(--r-xl);
  background:
    radial-gradient(120% 140% at 100% 0%, rgba(47, 184, 98, 0.22), transparent 55%),
    var(--c-brand-900);
  color: #fff;
}

.cta__title {
  color: #fff;
  font-size: var(--fs-3xl);
}

.cta__text {
  margin-top: 0.4rem;
  color: rgba(255, 255, 255, 0.75);
}

.cta__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

/* ===== АДАПТИВ ===== */
@media (max-width: 1024px) {
  .reviews {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .hero__media {
    aspect-ratio: 16 / 9;
    order: -1;
  }

  .steps,
  .audiences {
    grid-template-columns: 1fr;
  }

  .why {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 520px) {
  .hero__actions > *,
  .cta__actions > * {
    flex: 1 1 100%;
  }

  .review__author {
    flex-wrap: wrap;
  }
}
</style>
