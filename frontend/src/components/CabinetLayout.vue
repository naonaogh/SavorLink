<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { BagIcon, DocumentIcon, NotificationIcon, OrganizationIcon, TruckIcon } from '@/assets/icons/png'

const authStore = useAuthStore()

const displayName = computed(() => authStore.user?.name || authStore.user?.company || authStore.user?.email || 'Личный кабинет')
const isSupplier = computed(() => authStore.user?.role === 'SUPPLIER')

const navItems = computed(() => [
  { to: '/cabinet/profile', label: 'Профиль', icon: OrganizationIcon },
  {
    to: '/cabinet/orders',
    label: 'Заказы',
    icon: TruckIcon,
  },
  ...(isSupplier.value
    ? [
        { to: '/cabinet/my-products', label: 'Мои товары', icon: BagIcon },
      ]
    : []),
  { to: '/cabinet/chat', label: 'Чат', icon: NotificationIcon },
  { to: '/cabinet/analytics', label: 'Аналитика', icon: NotificationIcon },
  { to: '/cabinet/documents', label: 'Документы', icon: DocumentIcon },
  { to: '/cabinet/notifications', label: 'Уведомления', icon: NotificationIcon },
  ...(authStore.user?.role === 'ADMIN'
    ? [{ to: '/cabinet/admin', label: 'Администрирование', icon: DocumentIcon }]
    : []),
])
</script>

<template>
  <div class="cabinet-page">
    <div class="cabinet-layout">
      <aside class="cabinet-sidebar">
        <div class="cabinet-summary">
          <p class="cabinet-kicker">Кабинет</p>
          <h2>{{ displayName }}</h2>
          <p>
            {{ isSupplier ? 'Управление товарами, заказами и коммуникацией.' : 'Заказы, чат, документы и уведомления в одном месте.' }}
          </p>
        </div>

        <nav class="cabinet-nav">
          <RouterLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="cabinet-link"
            active-class="cabinet-link--active"
          >
            <img :src="item.icon" alt="" aria-hidden="true" class="cabinet-link-icon" />
            <span>{{ item.label }}</span>
          </RouterLink>
        </nav>

        <div class="cabinet-footer">
          <RouterLink to="/catalog" class="cabinet-catalog-link">Открыть каталог</RouterLink>
        </div>
      </aside>

      <main class="cabinet-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.cabinet-page {
  width: 100%;
  padding: 1.25rem 0 2rem;
}

.cabinet-layout {
  display: grid;
  grid-template-columns: 270px minmax(0, 1fr);
  gap: 1.25rem;
  align-items: start;
}

/* САЙДБАР */
.cabinet-sidebar {
  position: sticky;
  top: 1rem;
  display: grid;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
}

.cabinet-summary {
  padding: 1.35rem 1.25rem 1.25rem;
  border-bottom: 1px solid var(--sl-line);
}

.cabinet-kicker {
  margin: 0 0 0.6rem;
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: var(--sl-leaf);
}

.cabinet-summary h2 {
  margin: 0;
  color: var(--sl-ink);
  font-size: 1.05rem;
  overflow-wrap: anywhere;
}

.cabinet-summary p {
  margin: 0.6rem 0 0;
  font-size: 0.9rem;
  color: var(--sl-muted);
}

/* НАВИГАЦИЯ */
.cabinet-nav {
  display: grid;
}

.cabinet-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1.25rem;
  border-bottom: 1px solid var(--sl-line);
  color: #3f4a37;
  font-weight: 600;
  transition: background 0.2s ease, color 0.2s ease, padding-left 0.2s ease;
}

.cabinet-link::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--sl-leaf);
  transform: scaleY(0);
  transition: transform 0.2s ease;
}

.cabinet-link:hover {
  background: #fff;
  color: var(--sl-ink);
  padding-left: 1.5rem;
}

.cabinet-link:hover::before {
  transform: scaleY(1);
}

.cabinet-link--active,
.cabinet-link--active:hover {
  background: var(--sl-ink);
  color: #fff;
  padding-left: 1.25rem;
}

.cabinet-link--active::before {
  transform: scaleY(1);
  background: var(--sl-lime);
}

.cabinet-link-icon {
  width: 18px;
  height: 18px;
  object-fit: contain;
  flex: 0 0 auto;
}

/* цветные png-иконки приводим к монохрому */
.cabinet-link-icon {
  filter: grayscale(1) brightness(0.35);
}

.cabinet-link--active .cabinet-link-icon {
  filter: grayscale(1) brightness(0) invert(1);
}

/* НИЖНЯЯ КНОПКА */
.cabinet-footer {
  padding: 1.25rem;
}

.cabinet-catalog-link {
  display: block;
  width: 100%;
  padding: 0.8rem 1rem;
  text-align: center;
  border: 1px solid var(--sl-ink);
  color: var(--sl-ink);
  font-weight: 700;
  transition: background 0.2s ease, color 0.2s ease;
}

.cabinet-catalog-link:hover {
  background: var(--sl-ink);
  color: #fff;
}

.cabinet-link:focus-visible,
.cabinet-catalog-link:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: -2px;
}

.cabinet-content {
  min-width: 0;
}

@media (max-width: 1024px) {
  .cabinet-layout {
    grid-template-columns: 1fr;
  }

  .cabinet-sidebar {
    position: static;
  }

  .cabinet-nav {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }

  /* одиночный последний пункт (например, «Администрирование») — на всю ширину */
  .cabinet-link:last-child:nth-child(odd) {
    grid-column: 1 / -1;
  }

  .cabinet-link span {
    min-width: 0;
    overflow-wrap: anywhere;
  }
}

@media (max-width: 768px) {
  .cabinet-page {
    padding-top: 0.75rem;
  }
}
</style>
