<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'
import AppAvatar from '@/components/ui/AppAvatar.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppIcon from '@/components/ui/AppIcon.vue'

const authStore = useAuthStore()
const shopStore = useShopStore()
const router = useRouter()
const route = useRoute()

const favoritesCount = computed(
  () => shopStore.state.favoriteProducts.length + shopStore.state.favoriteSuppliers.length,
)

const cartCount = computed(() => shopStore.state.cartItems.length)

const isGuest = computed(() => !authStore.token)
const isSupplier = computed(() => authStore.user?.role === 'SUPPLIER')

const ROLE_LABELS: Record<string, string> = {
  BUYER: 'Покупатель',
  SUPPLIER: 'Поставщик',
  ADMIN: 'Администратор',
}
const accountName = computed(() => String(authStore.user?.email ?? 'Аккаунт'))
const accountRole = computed(() => ROLE_LABELS[String(authStore.user?.role ?? '')] ?? '')

const isActive = (path: string) => {
  if (path === '/cabinet') {
    return route.path.startsWith('/cabinet')
  }

  return route.path === path
}

const navLinks = computed(() => [
  { to: '/', label: 'Главная' },
  { to: '/catalog', label: 'Каталог' },
  ...(isGuest.value
    ? [
        { to: '/features', label: 'Возможности' },
        { to: '/reviews', label: 'Отзывы' },
      ]
    : [{ to: '/cabinet', label: 'Кабинет' }]),
])

/* мобильное меню */
const menuOpen = ref(false)
const closeMenu = () => {
  menuOpen.value = false
}
watch(() => route.fullPath, closeMenu)

const onKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && menuOpen.value) closeMenu()
}

const handleLogout = () => {
  authStore.logout()
  shopStore.state.cartItems = []
  shopStore.state.favoriteProducts = []
  shopStore.state.favoriteProductIds = []
  shopStore.state.favoriteSuppliers = []
  router.push('/')
}

onMounted(async () => {
  window.addEventListener('keydown', onKeydown)
  if (!authStore.token) return

  await Promise.all([
    shopStore.fetchCart(),
    shopStore.fetchFavoriteProducts(),
    shopStore.fetchFavoriteSuppliers(),
  ])
})

onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <header class="site-header">
    <div class="site-header__inner ui-container">
      <RouterLink to="/" class="logo" aria-label="SavorLink — на главную">
        <span class="logo__mark"><AppIcon name="leaf" :size="18" :stroke-width="2.2" /></span>
        <span class="logo__text">SavorLink</span>
      </RouterLink>

      <nav class="main-nav" aria-label="Основная навигация">
        <RouterLink
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to === '/cabinet' ? '/cabinet/profile' : link.to"
          class="main-nav__link"
          :class="{ 'is-active': isActive(link.to) }"
          :aria-current="isActive(link.to) ? 'page' : undefined"
        >
          {{ link.label }}
        </RouterLink>
      </nav>

      <div class="header-actions">
        <template v-if="!isGuest && !isSupplier">
          <RouterLink
            to="/favorites"
            class="icon-link"
            :class="{ 'is-active': isActive('/favorites') }"
            :aria-label="`Избранное${favoritesCount ? `: ${favoritesCount}` : ''}`"
            title="Избранное"
          >
            <AppIcon name="heart" :size="20" />
            <span v-if="favoritesCount > 0" class="icon-link__count" aria-hidden="true">{{ favoritesCount }}</span>
          </RouterLink>
          <RouterLink
            to="/cart"
            class="icon-link"
            :class="{ 'is-active': isActive('/cart') }"
            :aria-label="`Корзина${cartCount ? `: ${cartCount}` : ''}`"
            title="Корзина"
          >
            <AppIcon name="cart" :size="20" />
            <span v-if="cartCount > 0" class="icon-link__count" aria-hidden="true">{{ cartCount }}</span>
          </RouterLink>
        </template>

        <div class="header-actions__desktop">
          <template v-if="isGuest">
            <AppButton to="/auth" variant="ghost" size="sm">Войти</AppButton>
            <AppButton :to="{ path: '/auth', query: { mode: 'register' } }" variant="primary" size="sm">
              Регистрация
            </AppButton>
          </template>

          <template v-else>
            <RouterLink to="/cabinet/profile" class="account" title="Личный кабинет">
              <AppAvatar :name="accountName" :size="32" tone="accent" />
              <span class="account__text">
                <span class="account__name">{{ accountName }}</span>
                <span v-if="accountRole" class="account__role">{{ accountRole }}</span>
              </span>
            </RouterLink>
            <AppButton variant="ghost" size="sm" icon="log-out" icon-only label="Выйти" @click="handleLogout" />
          </template>
        </div>

        <button
          type="button"
          class="burger"
          :aria-expanded="menuOpen"
          aria-controls="mobile-menu"
          :aria-label="menuOpen ? 'Закрыть меню' : 'Открыть меню'"
          @click="menuOpen = !menuOpen"
        >
          <AppIcon :name="menuOpen ? 'x' : 'menu'" :size="22" />
        </button>
      </div>
    </div>

    <!-- мобильное меню -->
    <Transition name="menu">
      <div v-if="menuOpen" id="mobile-menu" class="mobile-menu">
        <div class="ui-container mobile-menu__inner">
          <nav class="mobile-menu__nav" aria-label="Мобильная навигация">
            <RouterLink
              v-for="link in navLinks"
              :key="link.to"
              :to="link.to === '/cabinet' ? '/cabinet/profile' : link.to"
              class="mobile-menu__link"
              :class="{ 'is-active': isActive(link.to) }"
            >
              {{ link.label }}
              <AppIcon name="chevron-right" :size="18" />
            </RouterLink>
          </nav>

          <div v-if="isGuest" class="mobile-menu__actions">
            <AppButton to="/auth" variant="secondary" block>Войти</AppButton>
            <AppButton :to="{ path: '/auth', query: { mode: 'register' } }" variant="primary" block>
              Регистрация
            </AppButton>
          </div>

          <div v-else class="mobile-menu__account">
            <div class="mobile-menu__user">
              <AppAvatar :name="accountName" :size="40" tone="accent" />
              <div class="account__text">
                <span class="account__name">{{ accountName }}</span>
                <span v-if="accountRole" class="account__role">{{ accountRole }}</span>
              </div>
            </div>
            <AppButton variant="secondary" icon="log-out" block @click="handleLogout">Выйти</AppButton>
          </div>
        </div>
      </div>
    </Transition>
  </header>
  <div v-if="menuOpen" class="mobile-menu__scrim" aria-hidden="true" @click="closeMenu"></div>
</template>

<style scoped>
.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(246, 244, 239, 0.88);
  border-bottom: 1px solid var(--c-border);
  backdrop-filter: saturate(1.4) blur(12px);
}

.site-header__inner {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  height: var(--header-h);
}

/* логотип */
.logo {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  flex: 0 0 auto;
  border-radius: var(--r-sm);
}

.logo__mark {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: var(--c-brand-800);
  color: var(--c-accent);
}

.logo__text {
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--c-brand-900);
}

/* навигация */
.main-nav {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.main-nav__link {
  padding: 0.5rem 0.8rem;
  border-radius: var(--r-sm);
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  font-weight: 600;
  transition: background var(--dur) var(--ease), color var(--dur) var(--ease);
}

.main-nav__link:hover {
  background: rgba(23, 32, 27, 0.05);
  color: var(--c-text);
}

.main-nav__link.is-active {
  background: var(--c-surface);
  color: var(--c-brand-800);
  box-shadow: var(--sh-xs), inset 0 0 0 1px var(--c-border);
}

/* правая часть */
.header-actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-left: auto;
}

.header-actions__desktop {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: 0.35rem;
}

.icon-link {
  position: relative;
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: var(--r-sm);
  color: var(--c-text-2);
  transition: background var(--dur) var(--ease), color var(--dur) var(--ease);
}

.icon-link:hover,
.icon-link.is-active {
  background: rgba(23, 32, 27, 0.06);
  color: var(--c-brand-800);
}

.icon-link__count {
  position: absolute;
  top: 3px;
  right: 1px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border: 2px solid var(--c-bg);
  border-radius: var(--r-full);
  background: var(--c-accent);
  color: var(--c-brand-950);
  font-size: 0.625rem;
  font-weight: 800;
  line-height: 14px;
  text-align: center;
}

.account {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  max-width: 240px;
  padding: 0.25rem 0.6rem 0.25rem 0.25rem;
  border-radius: var(--r-md);
  transition: background var(--dur) var(--ease);
}

.account:hover {
  background: rgba(23, 32, 27, 0.05);
}

.account__text {
  display: grid;
  min-width: 0;
  line-height: 1.2;
}

.account__name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: var(--fs-sm);
  font-weight: 700;
  color: var(--c-text);
}

.account__role {
  font-size: var(--fs-xs);
  color: var(--c-muted);
}

.burger {
  display: none;
  place-items: center;
  width: 42px;
  height: 42px;
  border: 1px solid var(--c-border);
  border-radius: var(--r-sm);
  background: var(--c-surface);
  color: var(--c-text);
}

/* мобильное меню */
.mobile-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 2;
  max-height: calc(100dvh - var(--header-h));
  overflow-y: auto;
  border-bottom: 1px solid var(--c-border);
  background: var(--c-surface);
  box-shadow: var(--sh-lg);
}

.mobile-menu__inner {
  display: grid;
  gap: 1rem;
  padding-block: 1rem 1.25rem;
}

.mobile-menu__nav {
  display: grid;
}

.mobile-menu__link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 0.25rem;
  border-bottom: 1px solid var(--c-border);
  font-weight: 700;
  color: var(--c-text);
}

.mobile-menu__link.is-active {
  color: var(--c-accent-700);
}

.mobile-menu__actions,
.mobile-menu__account {
  display: grid;
  gap: 0.6rem;
}

.mobile-menu__user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.25rem 0 0.5rem;
}

.mobile-menu__scrim {
  position: fixed;
  inset: 0;
  z-index: 90;
  background: rgba(11, 31, 23, 0.3);
}

.menu-enter-active,
.menu-leave-active {
  transition: opacity 0.18s var(--ease), transform 0.18s var(--ease);
}

.menu-enter-from,
.menu-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

@media (max-width: 1024px) {
  .account__text {
    display: none;
  }

  .account {
    padding-right: 0.25rem;
  }
}

@media (max-width: 860px) {
  .main-nav,
  .header-actions__desktop {
    display: none;
  }

  .burger {
    display: grid;
  }
}

@media (min-width: 861px) {
  .mobile-menu,
  .mobile-menu__scrim {
    display: none;
  }
}
</style>
