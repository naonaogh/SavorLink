<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

type UserProfile = {
  id: number
  email: string
  role: string
  enterprise_id: number
  created_at: string
  enterprise?: { id: number; short_name: string } | null
}

type EnterpriseProfile = {
  id: number
  short_name: string
  inn: string
  region: string
  phone?: string | null
  email?: string | null
}

const API_BASE = 'http://127.0.0.1:8001'

const user = ref<UserProfile | null>(null)
const enterprise = ref<EnterpriseProfile | null>(null)
const loading = ref(true)
const error = ref('')

const favoritesCount = ref(0)
const cartCount = ref(0)

const createdAt = computed(() => {
  if (!user.value?.created_at) return '—'
  return new Date(user.value.created_at).toLocaleDateString('ru-RU')
})

const loadProfile = async () => {
  loading.value = true
  error.value = ''

  try {
    const userRes = await fetch(`${API_BASE}/users/me`)
    if (!userRes.ok) throw new Error('Не удалось получить профиль пользователя')

    const userData: UserProfile = await userRes.json()
    user.value = userData

    if (userData.enterprise_id) {
      const entRes = await fetch(`${API_BASE}/enterprises/${userData.enterprise_id}`)
      if (entRes.ok) {
        enterprise.value = await entRes.json()
      }
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Ошибка загрузки профиля'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const rawFavorites = localStorage.getItem('shop-storage')
  if (rawFavorites) {
    try {
      const parsed = JSON.parse(rawFavorites)
      favoritesCount.value =
        (parsed?.favoriteSuppliers?.length ?? 0) + (parsed?.favoriteProducts?.length ?? 0)
      cartCount.value = (parsed?.cartItems ?? []).reduce(
        (sum: number, item: { quantityKg: number }) => sum + (item.quantityKg ?? 0),
        0,
      )
    } catch {
      favoritesCount.value = 0
      cartCount.value = 0
    }
  }

  loadProfile()
})
</script>

<template>
  <div class="profile-page">
    <header class="profile-header">
      <nav class="profile-nav">
        <router-link to="/" class="nav-logo">SavorLink</router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link">Главная</router-link>
          <router-link to="/catalog" class="nav-link">Каталог</router-link>
          <router-link to="/profile" class="nav-link nav-link--active">Профиль</router-link>
          <router-link to="/favorites" class="nav-link">Избранное ({{ favoritesCount }})</router-link>
          <router-link to="/cart" class="nav-link">Корзина ({{ cartCount }})</router-link>
        </div>
      </nav>
    </header>

    <main class="profile-main">
      <section class="profile-card">
        <div class="profile-card-head">
          <h1 class="profile-title">Профиль</h1>
          <button type="button" class="refresh-btn" @click="loadProfile">Обновить</button>
        </div>

        <p v-if="loading" class="state-text">Загрузка данных...</p>
        <p v-else-if="error" class="state-text state-text--error">{{ error }}</p>

        <div v-else-if="user" class="profile-grid">
          <article class="info-card">
            <h2 class="info-title">Аккаунт</h2>
            <dl class="info-list">
              <div class="info-row"><dt>ID</dt><dd>{{ user.id }}</dd></div>
              <div class="info-row"><dt>Email</dt><dd>{{ user.email }}</dd></div>
              <div class="info-row"><dt>Роль</dt><dd>{{ user.role }}</dd></div>
              <div class="info-row"><dt>Дата регистрации</dt><dd>{{ createdAt }}</dd></div>
            </dl>
          </article>

          <article class="info-card">
            <h2 class="info-title">Предприятие</h2>
            <dl v-if="enterprise" class="info-list">
              <div class="info-row"><dt>Название</dt><dd>{{ enterprise.short_name }}</dd></div>
              <div class="info-row"><dt>ИНН</dt><dd>{{ enterprise.inn }}</dd></div>
              <div class="info-row"><dt>Регион</dt><dd>{{ enterprise.region }}</dd></div>
              <div class="info-row"><dt>Телефон</dt><dd>{{ enterprise.phone || '—' }}</dd></div>
              <div class="info-row"><dt>Email</dt><dd>{{ enterprise.email || '—' }}</dd></div>
            </dl>
            <p v-else class="state-text">Данные предприятия не найдены.</p>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #ebe2ce;
  color: #2e2a23;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.profile-header {
  background: linear-gradient(120deg, #364128 0%, #3f4a2f 60%, #4a5638 100%);
  padding: 0.875rem 1.5rem;
  position: sticky;
  top: 0;
  z-index: 20;
}

.profile-nav {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.nav-logo { color: #f0e5d1; text-decoration: none; font-weight: 700; }
.nav-links { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
.nav-link { color: #e7dbc5; text-decoration: none; font-size: 0.94rem; }
.nav-link:hover, .nav-link--active { color: #fff; font-weight: 600; }

.profile-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
}

.profile-card {
  background: #f5ebd6;
  border: 1px solid #dcc7a2;
  border-radius: 0.8rem;
  box-shadow: 0 10px 26px rgba(72, 56, 36, 0.13);
  padding: 1.5rem;
}

.profile-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.2rem;
}

.profile-title { margin: 0; font-size: 1.7rem; color: #3f4a2f; }

.refresh-btn {
  border: none;
  border-radius: 999px;
  background: #3f4a2f;
  color: #fff;
  padding: 0.5rem 1rem;
  cursor: pointer;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.info-card {
  background: #f4ead4;
  border: 1px solid #ddc8a3;
  border-radius: 0.6rem;
  padding: 1rem;
}

.info-title { margin: 0 0 0.7rem; font-size: 1.12rem; color: #3f4a2f; }
.info-list { margin: 0; }
.info-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.45rem 0;
  border-bottom: 1px solid rgba(63, 74, 47, 0.12);
}
.info-row:last-child { border-bottom: none; }
.info-row dt { color: #6d6254; }
.info-row dd { margin: 0; font-weight: 600; text-align: right; }
.state-text { margin: 0.7rem 0; color: #5f5648; }
.state-text--error { color: #8f2d2d; }
</style>
