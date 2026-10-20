<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'

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

const isActive = (path: string) => {
  if (path === '/cabinet') {
    return route.path.startsWith('/cabinet')
  }

  return route.path === path
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
  if (!authStore.token) return

  await Promise.all([
    shopStore.fetchCart(),
    shopStore.fetchFavoriteProducts(),
    shopStore.fetchFavoriteSuppliers(),
  ])
})
</script>

<template>
  <header class="common-header">
    <nav class="common-nav">
      <router-link to="/" class="logo">
        <span class="logo-mark">S</span>
        <span class="logo-text">SavorLink</span>
      </router-link>

      <div class="nav-links">
        <router-link to="/" class="nav-link" :class="{ active: isActive('/') }">Главная</router-link>
        <router-link to="/catalog" class="nav-link" :class="{ active: isActive('/catalog') }">Каталог</router-link>

        <template v-if="isGuest">
          <router-link to="/features" class="nav-link" :class="{ active: isActive('/features') }">Возможности</router-link>
          <router-link to="/reviews" class="nav-link" :class="{ active: isActive('/reviews') }">Отзывы</router-link>
          <span class="nav-divider" aria-hidden="true"></span>
          <router-link to="/auth" class="nav-link">Вход</router-link>
          <router-link :to="{ path: '/auth', query: { mode: 'register' } }" class="nav-btn nav-btn--solid">
            Регистрация
          </router-link>
        </template>

        <template v-else>
          <router-link to="/cabinet/profile" class="nav-link" :class="{ active: isActive('/cabinet') }">Кабинет</router-link>
          <router-link v-if="!isSupplier" to="/favorites" class="nav-link" :class="{ active: isActive('/favorites') }">
            Избранное<span v-if="favoritesCount > 0" class="nav-count">{{ favoritesCount }}</span>
          </router-link>
          <router-link v-if="!isSupplier" to="/cart" class="nav-link" :class="{ active: isActive('/cart') }">
            Корзина<span v-if="cartCount > 0" class="nav-count">{{ cartCount }}</span>
          </router-link>
          <span class="nav-divider" aria-hidden="true"></span>
          <button type="button" class="nav-btn nav-btn--outline" @click="handleLogout">Выйти</button>
        </template>
      </div>
    </nav>
  </header>
</template>

<style scoped>
.common-header {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 1rem 0;
}

.common-nav {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem 2rem;
  padding: 0.75rem 0.75rem 0.75rem 1rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-bottom: 2px solid var(--sl-ink);
}

/* ЛОГО */
.logo {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  white-space: nowrap;
}

.logo-mark {
  width: 2.25rem;
  height: 2.25rem;
  display: grid;
  place-items: center;
  background: var(--sl-ink);
  color: var(--sl-lime);
  font-family: var(--sl-display);
  font-weight: 700;
  font-size: 1rem;
  transition: background 0.2s ease, color 0.2s ease;
}

.logo:hover .logo-mark {
  background: var(--sl-lime);
  color: var(--sl-ink);
}

.logo-text {
  font-family: var(--sl-display);
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  color: var(--sl-ink);
}

/* ССЫЛКИ */
.nav-links {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.nav-link {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.6rem 0.8rem;
  font-size: 0.92rem;
  font-weight: 600;
  color: #4a5a42;
  white-space: nowrap;
  transition: color 0.2s ease;
}

.nav-link::after {
  content: '';
  position: absolute;
  left: 0.8rem;
  right: 0.8rem;
  bottom: 0.2rem;
  height: 2px;
  background: var(--sl-leaf);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.25s ease;
}

.nav-link:hover {
  color: var(--sl-ink);
}

.nav-link:hover::after {
  transform: scaleX(1);
}

.nav-link.active {
  color: var(--sl-ink);
}

.nav-link.active::after {
  transform: scaleX(1);
  background: var(--sl-ink);
}

.nav-count {
  min-width: 1.35rem;
  height: 1.35rem;
  padding: 0 0.3rem;
  display: inline-grid;
  place-items: center;
  background: var(--sl-lime);
  color: var(--sl-ink);
  font-size: 0.72rem;
  font-weight: 800;
}

.nav-divider {
  width: 1px;
  height: 1.5rem;
  margin: 0 0.5rem;
  background: var(--sl-line);
}

/* КНОПКИ */
.nav-btn {
  display: inline-flex;
  align-items: center;
  padding: 0.65rem 1.15rem;
  border-radius: 0;
  font-size: 0.9rem;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.nav-btn--solid {
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
}

.nav-btn--solid:hover {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.nav-btn--outline {
  background: transparent;
  color: var(--sl-ink);
  border: 1px solid var(--sl-ink);
}

.nav-btn--outline:hover {
  background: var(--sl-ink);
  color: #fff;
}

.nav-link:focus-visible,
.nav-btn:focus-visible,
.logo:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

/* АДАПТИВ */
@media (max-width: 1024px) {
  .common-nav {
    align-items: flex-start;
    flex-direction: column;
  }

  .nav-links {
    margin-left: -0.8rem;
  }
}

@media (max-width: 768px) {
  .common-header {
    padding: 0.75rem 0.75rem 0;
  }

  .common-nav {
    padding: 0.75rem;
  }

  .nav-link {
    font-size: 0.85rem;
    padding: 0.5rem 0.65rem;
  }

  .nav-link::after {
    left: 0.65rem;
    right: 0.65rem;
  }

  .nav-divider {
    display: none;
  }
}
</style>
