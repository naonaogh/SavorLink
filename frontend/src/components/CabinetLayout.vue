<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import AppAvatar from '@/components/ui/AppAvatar.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import type { IconName } from '@/components/ui/icons'

const authStore = useAuthStore()

const displayName = computed(
  () =>
    String(authStore.user?.name || authStore.user?.company || authStore.user?.email || 'Личный кабинет'),
)
const isSupplier = computed(() => authStore.user?.role === 'SUPPLIER')
const isAdmin = computed(() => authStore.user?.role === 'ADMIN')

const roleLabel = computed(() => (isAdmin.value ? 'Администратор' : isSupplier.value ? 'Поставщик' : 'Покупатель'))

const navItems = computed<{ to: string; label: string; icon: IconName }[]>(() => [
  { to: '/cabinet/profile', label: 'Профиль', icon: 'user' },
  { to: '/cabinet/orders', label: 'Заказы', icon: 'clipboard-list' },
  ...(isSupplier.value ? [{ to: '/cabinet/my-products', label: 'Мои товары', icon: 'package' as IconName }] : []),
  { to: '/cabinet/chat', label: 'Чат', icon: 'message' },
  { to: '/cabinet/analytics', label: 'Аналитика', icon: 'bar-chart' },
  { to: '/cabinet/documents', label: 'Документы', icon: 'file-text' },
  { to: '/cabinet/notifications', label: 'Уведомления', icon: 'bell' },
  ...(isAdmin.value ? [{ to: '/cabinet/admin', label: 'Администрирование', icon: 'shield' as IconName }] : []),
])
</script>

<template>
  <div class="cabinet">
    <aside class="cabinet__sidebar" aria-label="Разделы кабинета">
      <div class="cabinet__user">
        <AppAvatar :name="displayName" :size="44" />
        <div class="cabinet__user-text">
          <p class="cabinet__user-name" :title="displayName">{{ displayName }}</p>
          <AppBadge :tone="isSupplier ? 'brand' : 'accent'" size="sm">{{ roleLabel }}</AppBadge>
        </div>
      </div>

      <nav class="cabinet__nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="cabinet__link"
          active-class="is-active"
        >
          <AppIcon :name="item.icon" :size="18" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div class="cabinet__footer">
        <AppButton to="/catalog" variant="secondary" icon="store" block>Открыть каталог</AppButton>
      </div>
    </aside>

    <div class="cabinet__content">
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
.cabinet {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  gap: 1.5rem;
  align-items: start;
}

.cabinet__sidebar {
  position: sticky;
  top: calc(var(--header-h) + 1.25rem);
  display: grid;
  gap: 0.25rem;
  padding: 0.75rem;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-lg);
  box-shadow: var(--sh-xs);
}

.cabinet__user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.5rem 1rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid var(--c-border);
}

.cabinet__user-text {
  display: grid;
  justify-items: start;
  gap: 0.3rem;
  min-width: 0;
}

.cabinet__user-name {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 800;
  font-size: var(--fs-sm);
}

.cabinet__nav {
  display: grid;
  gap: 2px;
}

.cabinet__link {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.65rem 0.75rem;
  border-radius: var(--r-sm);
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  font-weight: 600;
  transition: background var(--dur) var(--ease), color var(--dur) var(--ease);
}

.cabinet__link :deep(.app-icon) {
  color: var(--c-muted);
  transition: color var(--dur) var(--ease);
}

.cabinet__link:hover {
  background: var(--c-surface-sunken);
  color: var(--c-text);
}

.cabinet__link.is-active {
  background: var(--c-accent-50);
  color: var(--c-brand-800);
  font-weight: 700;
  box-shadow: inset 3px 0 0 var(--c-accent);
}

.cabinet__link.is-active :deep(.app-icon) {
  color: var(--c-accent-700);
}

.cabinet__footer {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--c-border);
}

.cabinet__content {
  min-width: 0;
}

/* планшет и телефон: навигация — горизонтальная лента */
@media (max-width: 1024px) {
  .cabinet {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .cabinet__sidebar {
    position: static;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: center;
    gap: 0.5rem 1rem;
    padding: 0.75rem;
  }

  .cabinet__user {
    padding: 0.25rem;
    margin: 0;
    border: none;
  }

  .cabinet__footer {
    margin: 0;
    padding: 0;
    border: none;
  }

  .cabinet__nav {
    grid-column: 1 / -1;
    display: flex;
    gap: 0.35rem;
    overflow-x: auto;
    padding-top: 0.75rem;
    border-top: 1px solid var(--c-border);
    scrollbar-width: none;
  }

  .cabinet__nav::-webkit-scrollbar {
    display: none;
  }

  .cabinet__link {
    flex: 0 0 auto;
    white-space: nowrap;
    border: 1px solid var(--c-border);
  }

  .cabinet__link.is-active {
    border-color: var(--c-accent-200);
    box-shadow: none;
  }
}

@media (max-width: 520px) {
  .cabinet__sidebar {
    grid-template-columns: 1fr;
  }
}
</style>
