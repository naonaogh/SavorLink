<script setup lang="ts">
import { RouterLink } from 'vue-router'
import AppIcon from '@/components/ui/AppIcon.vue'

const year = new Date().getFullYear()

const columns = [
  {
    title: 'Навигация',
    links: [
      { to: '/catalog', label: 'Каталог' },
      { to: '/favorites', label: 'Избранное' },
      { to: '/profile', label: 'Профиль' },
    ],
  },
  {
    title: 'Сервисы',
    links: [
      { to: '/chat', label: 'Чат' },
      { to: '/analytics', label: 'Аналитика' },
      { to: '/documents', label: 'Документы' },
    ],
  },
  {
    title: 'Платформа',
    links: [
      { to: '/features', label: 'Возможности' },
      { to: '/reviews', label: 'Отзывы' },
    ],
  },
]
</script>

<template>
  <footer class="site-footer">
    <div class="ui-container">
      <div class="site-footer__top">
        <div class="site-footer__brand">
          <RouterLink to="/" class="footer-logo" aria-label="SavorLink — на главную">
            <span class="footer-logo__mark"><AppIcon name="leaf" :size="18" :stroke-width="2.2" /></span>
            <span class="footer-logo__text">SavorLink</span>
          </RouterLink>
          <p class="site-footer__about">
            Платформа для удобной работы ресторанов, поставщиков и документов в одном месте.
          </p>
        </div>

        <nav v-for="column in columns" :key="column.title" class="site-footer__col" :aria-label="column.title">
          <h2 class="site-footer__title">{{ column.title }}</h2>
          <RouterLink v-for="link in column.links" :key="link.to" :to="link.to" class="site-footer__link">
            {{ link.label }}
          </RouterLink>
        </nav>
      </div>

      <div class="site-footer__bottom">
        <span>© {{ year }} SavorLink</span>
        <span>B2B-платформа для ресторанов и поставщиков</span>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  margin-top: auto;
  background: var(--c-brand-900);
  color: rgba(255, 255, 255, 0.72);
}

.site-footer__top {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) repeat(3, minmax(0, 1fr));
  gap: 2rem;
  padding-block: clamp(2.5rem, 5vw, 3.5rem);
}

.site-footer__brand {
  display: grid;
  align-content: start;
  gap: 1rem;
  max-width: 360px;
}

.footer-logo {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  justify-self: start;
  border-radius: var(--r-sm);
}

.footer-logo__mark {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: var(--c-accent);
  color: var(--c-brand-950);
}

.footer-logo__text {
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #fff;
}

.site-footer__about {
  font-size: var(--fs-sm);
  line-height: 1.6;
}

.site-footer__col {
  display: grid;
  align-content: start;
  gap: 0.6rem;
}

.site-footer__title {
  margin-bottom: 0.25rem;
  color: #fff;
  font-size: var(--fs-sm);
  font-weight: 700;
  letter-spacing: 0;
}

.site-footer__link {
  justify-self: start;
  font-size: var(--fs-sm);
  border-radius: var(--r-xs);
  transition: color var(--dur) var(--ease);
}

.site-footer__link:hover {
  color: var(--c-accent);
}

.site-footer__bottom {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.5rem 1rem;
  padding-block: 1.25rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: var(--fs-xs);
  color: rgba(255, 255, 255, 0.5);
}

@media (max-width: 860px) {
  .site-footer__top {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .site-footer__brand {
    grid-column: 1 / -1;
  }
}

@media (max-width: 480px) {
  .site-footer__top {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
