<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { AppButton, AppIcon, PageHeader, type IconName } from '@/components/ui'

const authStore = useAuthStore()

const isGuest = computed(() => !authStore.token)
const isSupplier = computed(() => authStore.user?.role === 'SUPPLIER')

interface Feature {
  title: string
  text: string
  icon: IconName
  to: string
  /** страница доступна без входа */
  public?: boolean
  /** раздел только для поставщика */
  supplierOnly?: boolean
}

interface FeatureGroup {
  id: string
  eyebrow: string
  title: string
  lead: string
  items: Feature[]
}

/* Только то, что реально есть в приложении (см. src/router/index.ts и страницы) */
const groups: FeatureGroup[] = [
  {
    id: 'buyers',
    eyebrow: 'Покупателям',
    title: 'Закупки для ресторанов и кафе',
    lead: 'Поиск поставщиков, корзина по нескольким поставщикам и контроль статусов заказов.',
    items: [
      {
        title: 'Каталог с фильтрами',
        text: 'Поиск поставщиков и товаров, фильтры по категории, региону и городу.',
        icon: 'search',
        to: '/catalog',
        public: true,
      },
      {
        title: 'Сравнение поставщиков',
        text: 'Добавьте поставщиков к сравнению из каталога и сопоставьте их бок о бок.',
        icon: 'scale',
        to: '/compare',
        public: true,
      },
      {
        title: 'Избранное',
        text: 'Сохраняйте понравившиеся товары и поставщиков, чтобы быстро вернуться к ним.',
        icon: 'heart',
        to: '/favorites',
      },
      {
        title: 'Корзина и шаблоны заказов',
        text: 'Корзина собирает товары разных поставщиков и оформляет отдельный заказ каждому. Состав можно сохранить как шаблон для повторной закупки.',
        icon: 'cart',
        to: '/cart',
      },
      {
        title: 'Статусы заказов',
        text: 'В разделе «Мои заказы» виден статус каждого заказа — от рассмотрения до доставки, там же подтверждается получение.',
        icon: 'truck',
        to: '/cabinet/orders',
      },
    ],
  },
  {
    id: 'suppliers',
    eyebrow: 'Поставщикам',
    title: 'Продажи без лишней переписки',
    lead: 'Собственный кабинет с товарами, остатками и входящими заказами.',
    items: [
      {
        title: 'Товары и остатки',
        text: 'Карточки товаров с категорией, ценой за килограмм, минимальным заказом и остатком на складе.',
        icon: 'package',
        to: '/cabinet/my-products',
        supplierOnly: true,
      },
      {
        title: 'Приём и отклонение заказов',
        text: 'Входящие заказы покупателей можно принять в работу или отклонить прямо из кабинета.',
        icon: 'inbox',
        to: '/cabinet/orders',
      },
      {
        title: 'Карточка поставщика',
        text: 'Покупатели видят ваши товары, регион и отзывы на странице поставщика в каталоге.',
        icon: 'store',
        to: '/catalog',
        public: true,
      },
    ],
  },
  {
    id: 'common',
    eyebrow: 'Обеим сторонам',
    title: 'Рабочее пространство в одном кабинете',
    lead: 'Общение, документы и показатели — без таблиц и сторонних мессенджеров.',
    items: [
      {
        title: 'Чат с контрагентами',
        text: 'Диалоги между покупателями и поставщиками; начать переписку можно со страницы поставщика.',
        icon: 'message',
        to: '/cabinet/chat',
      },
      {
        title: 'Документы по заказам',
        text: 'Генератор документа по выбранному заказу с возможностью скачать файл.',
        icon: 'file-text',
        to: '/cabinet/documents',
      },
      {
        title: 'Аналитика',
        text: 'Показатели покупателя или поставщика, топ позиций и краткая сводка по заказам.',
        icon: 'bar-chart',
        to: '/cabinet/analytics',
      },
      {
        title: 'Уведомления',
        text: 'Лента событий по заказам и сообщениям в чатах.',
        icon: 'bell',
        to: '/cabinet/notifications',
      },
      {
        title: 'Профиль предприятия',
        text: 'Создайте карточку своей компании или присоединитесь к уже зарегистрированной на платформе.',
        icon: 'building',
        to: '/cabinet/profile',
      },
      {
        title: 'Отзывы',
        text: 'Покупатели оценивают поставщиков на их страницах; отзывы о самой платформе собраны в отдельном разделе.',
        icon: 'star',
        to: '/reviews',
        public: true,
      },
    ],
  },
]

/* Ссылку «Открыть» показываем только туда, куда пользователь реально может попасть */
const canOpen = (feature: Feature) => {
  if (feature.supplierOnly) return isSupplier.value
  return feature.public || !isGuest.value
}
</script>

<template>
  <div class="page">
    <PageHeader
      eyebrow="Возможности"
      title="Что умеет SavorLink"
      description="Инструменты платформы для ресторанов и поставщиков продуктов — от поиска поставщика до документов по заказу."
    >
      <nav class="jump" aria-label="Разделы страницы">
        <a v-for="group in groups" :key="group.id" :href="`#${group.id}`" class="jump__link">{{ group.eyebrow }}</a>
      </nav>
      <template #actions>
        <template v-if="isGuest">
          <AppButton :to="{ path: '/auth', query: { mode: 'register' } }" icon-right="arrow-right">
            Зарегистрироваться
          </AppButton>
          <AppButton to="/catalog" variant="secondary" icon="store">Смотреть каталог</AppButton>
        </template>
        <AppButton v-else to="/cabinet/profile" icon-right="arrow-right">Открыть кабинет</AppButton>
      </template>
    </PageHeader>

    <section
      v-for="group in groups"
      :id="group.id"
      :key="group.id"
      class="group"
      :aria-labelledby="`${group.id}-title`"
    >
      <div class="group__head">
        <p class="ui-eyebrow">{{ group.eyebrow }}</p>
        <h2 :id="`${group.id}-title`" class="group__title">{{ group.title }}</h2>
        <p class="group__lead">{{ group.lead }}</p>
      </div>

      <ul class="features">
        <li v-for="feature in group.items" :key="feature.title" class="feature ui-card">
          <span class="feature__icon"><AppIcon :name="feature.icon" :size="22" /></span>
          <h3 class="feature__title">{{ feature.title }}</h3>
          <p class="feature__text">{{ feature.text }}</p>
          <RouterLink v-if="canOpen(feature)" :to="feature.to" class="feature__link">
            Открыть
            <AppIcon name="arrow-right" :size="16" />
            <span class="sr-only">: {{ feature.title }}</span>
          </RouterLink>
          <p v-else-if="feature.supplierOnly && !isGuest" class="feature__note">Доступно в кабинете поставщика</p>
          <p v-else class="feature__note">Доступно после входа</p>
        </li>
      </ul>
    </section>

    <section class="cta" aria-labelledby="features-cta-title">
      <div>
        <h2 id="features-cta-title" class="cta__title">
          {{ isGuest ? 'Начните работу с SavorLink' : 'Все инструменты — в вашем кабинете' }}
        </h2>
        <p class="cta__text">
          {{
            isGuest
              ? 'Регистрация займёт пару минут — выберите роль и подключите своё предприятие.'
              : 'Заказы, чат, документы и аналитика доступны из бокового меню кабинета.'
          }}
        </p>
      </div>
      <div class="cta__actions">
        <template v-if="isGuest">
          <AppButton variant="accent" size="lg" :to="{ path: '/auth', query: { mode: 'register', role: 'buyer' } }">
            Я покупатель
          </AppButton>
          <AppButton variant="secondary" size="lg" :to="{ path: '/auth', query: { mode: 'register', role: 'supplier' } }">
            Я поставщик
          </AppButton>
        </template>
        <template v-else>
          <AppButton variant="accent" size="lg" to="/cabinet/orders" icon="clipboard-list">Мои заказы</AppButton>
          <AppButton variant="secondary" size="lg" to="/cabinet/profile">Открыть кабинет</AppButton>
        </template>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page {
  display: grid;
  gap: clamp(2.25rem, 5vw, 3.5rem);
}

/* быстрые ссылки по разделам */
.jump {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.6rem;
}

.jump__link {
  padding: 0.35rem 0.85rem;
  border: 1px solid var(--c-border);
  border-radius: var(--r-full);
  background: var(--c-surface);
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  font-weight: 600;
  transition:
    border-color var(--dur) var(--ease),
    color var(--dur) var(--ease);
}

.jump__link:hover {
  border-color: var(--c-accent-200);
  color: var(--c-accent-700);
}

/* группы */
.group {
  display: grid;
  gap: 1.25rem;
  scroll-margin-top: calc(var(--header-h) + 1rem);
}

.group__head {
  display: grid;
  gap: 0.4rem;
  max-width: 680px;
}

.group__title {
  font-size: var(--fs-2xl);
  letter-spacing: -0.03em;
}

.group__lead {
  color: var(--c-muted);
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.feature {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  padding: 1.5rem;
}

.feature__icon {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  margin-bottom: 0.35rem;
  border-radius: var(--r-md);
  background: var(--c-accent-50);
  color: var(--c-accent-700);
}

.feature__title {
  font-size: var(--fs-lg);
}

.feature__text {
  flex: 1;
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  line-height: 1.6;
}

.feature__link {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  align-self: flex-start;
  margin-top: 0.4rem;
  color: var(--c-accent-700);
  font-size: var(--fs-sm);
  font-weight: 700;
}

.feature__link:hover {
  text-decoration: underline;
  text-underline-offset: 3px;
}

.feature__note {
  margin-top: 0.4rem;
  color: var(--c-muted);
  font-size: var(--fs-xs);
  font-weight: 600;
}

/* CTA — как на главной */
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

@media (max-width: 520px) {
  .cta__actions > * {
    flex: 1 1 100%;
  }
}
</style>
