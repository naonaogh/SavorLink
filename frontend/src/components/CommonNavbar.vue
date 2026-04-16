<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/data/authStore'
import { useShopStore } from '@/data/shopStore'

const authStore = useAuthStore()
const shopStore = useShopStore()
const router = useRouter()
const route = useRoute()

const favoritesCount = computed(() => shopStore.state.favoriteProducts.length)

const cartCount = computed(() =>
  shopStore.state.cartItems.reduce((sum, item) => sum + item.quantity, 0),
)

const handleLogout = () => {
  authStore.logout()
  shopStore.state.cartItems = []
  shopStore.state.favoriteProducts = []
  shopStore.state.favoriteProductIds = []
  router.push('/')
}

const isGuest = computed(() => !authStore.token)
const isSupplier = computed(() => authStore.user?.role === 'SUPPLIER')

const isActive = (path: string) => route.path === path

onMounted(async () => {
  if (authStore.token) {
    await Promise.all([
      shopStore.fetchCart(),
      shopStore.fetchFavoriteProducts(),
    ])
  }
})
</script>

<template>
  <header class="common-header">
    <nav class="common-nav">
      <router-link to="/" class="logo">SavorLink</router-link>

      <div class="nav-links">
        <!-- Всегда видимые -->
        <router-link to="/" class="nav-link" :class="{ active: isActive('/') }">Главная</router-link>
        <router-link to="/catalog" class="nav-link" :class="{ active: isActive('/catalog') }">Каталог</router-link>

        <!-- Только гостям -->
        <template v-if="isGuest">
          <router-link to="/features" class="nav-link">Возможности</router-link>
          <router-link to="/reviews" class="nav-link">Отзывы</router-link>
          <span class="nav-sep">|</span>
          <router-link to="/register" class="nav-link">Регистрация</router-link>
          <router-link to="/login" class="nav-link nav-link--cta">Вход</router-link>
        </template>

        <!-- Авторизованным пользователям -->
        <template v-else>
          <router-link to="/profile" class="nav-link" :class="{ active: isActive('/profile') }">Профиль</router-link>

          <!-- Заказы - для всех ролей, но ведут на разные страницы -->
          <router-link
            :to="isSupplier ? '/supplier-orders' : '/my-orders'"
            class="nav-link"
            :class="{ active: isActive(isSupplier ? '/supplier-orders' : '/my-orders') }"
          >
            {{ isSupplier ? 'Заказы' : 'Мои заказы' }}
          </router-link>

          <router-link v-if="isSupplier" to="/my-products" class="nav-link" :class="{ active: isActive('/my-products') }">
            Мои товары
          </router-link>

          <router-link to="/favorites" class="nav-link" :class="{ active: isActive('/favorites') }">
            Избранное{{ favoritesCount > 0 ? ` (${favoritesCount})` : '' }}
          </router-link>
          <router-link to="/cart" class="nav-link" :class="{ active: isActive('/cart') }">
            Корзина{{ cartCount > 0 ? ` (${cartCount})` : '' }}
          </router-link>

          <button @click="handleLogout" class="btn-logout">Выйти</button>
        </template>
      </div>
    </nav>
  </header>
</template>

<style scoped>
.common-header {
  background: linear-gradient(120deg, #364128 0%, #3f4a2f 60%, #4a5638 100%);
  padding: 0.875rem 1.5rem;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 10px rgba(0,0,0,0.15);
  min-height: 64px;
  display: flex;
  align-items: center;
}

.common-nav {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f0e5d1;
  text-decoration: none;
  letter-spacing: 0.02em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.nav-link {
  color: #e7dbc5;
  text-decoration: none;
  font-size: 0.95rem;
  transition: color 0.2s;
  white-space: nowrap;
}

.nav-link:hover,
.nav-link.active {
  color: #fff;
}

.nav-link--cta {
  background: rgba(255,255,255,0.15);
  padding: 0.3rem 0.85rem;
  border-radius: 6px;
  color: #fff;
}

.nav-link--cta:hover {
  background: rgba(255,255,255,0.25);
}

.nav-sep {
  color: rgba(255,255,255,0.25);
}

.btn-logout {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  padding: 0.4rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-logout:hover {
  background: rgba(255,255,255,0.22);
}

@media (max-width: 768px) {
  .nav-links {
    gap: 0.75rem;
  }
  .nav-link {
    font-size: 0.82rem;
  }
}
</style>
