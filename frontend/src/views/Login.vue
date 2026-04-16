<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { getApiErrorMessage } from '@/api'
import { useAuthStore } from '@/data/authStore'
import { useShopStore } from '@/data/shopStore'

const router = useRouter()
const authStore = useAuthStore()
const shopStore = useShopStore()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const submit = async () => {
  error.value = ''
  loading.value = true
  try {
    const response = await api.post('/auth/login', {
      email: email.value,
      password: password.value,
    })
    
    const { token, user } = response.data
    authStore.setAuth(token, user)
    
    // Загружаем данные корзины и избранного
    await Promise.all([
      shopStore.fetchCart(),
      shopStore.fetchFavoriteProducts(),
    ])
    
    router.push('/catalog')
  } catch (apiError: unknown) {
    error.value = getApiErrorMessage(apiError, 'Ошибка при входе')
    console.error('Login error:', apiError)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <header class="auth-header">
        <h1 class="auth-title">Вход</h1>
      </header>

      <form class="auth-form" @submit.prevent="submit">
        <label class="field">
          <span class="field-label">Email</span>
          <input v-model="email" type="email" class="field-input" autocomplete="email" />
        </label>

        <label class="field">
          <span class="field-label">Password</span>
          <input v-model="password" type="password" class="field-input" autocomplete="current-password" />
        </label>

        <div v-if="error" class="auth-error">
          {{ error }}
        </div>

        <div class="auth-actions">
          <button type="submit" class="auth-submit" :disabled="loading">
            {{ loading ? 'Загрузка...' : 'Войти →' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top left, #5a6641 0%, #3f4a2f 45%, #343d27 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
}

.auth-card {
  width: 420px;
  max-width: 90vw;
  padding: 2.2rem 2.4rem 2rem;
  border-radius: 1.75rem;
  background: rgba(52, 46, 36, 0.9);
  border: 1px solid rgba(224, 200, 163, 0.35);
  box-shadow: 0 22px 60px rgba(0, 0, 0, 0.5);
  color: #f9fafb;
}

.auth-header {
  margin-bottom: 1.8rem;
}

.auth-title {
  margin: 0;
  font-size: 1.6rem;
  font-weight: 600;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.field-label {
  font-size: 0.8rem;
  color: #d1d5db;
}

.field-input {
  border-radius: 0.7rem;
  border: none;
  padding: 0.65rem 0.9rem;
  background: #f9fafb;
  font-size: 0.9rem;
}

.auth-error {
  background: rgba(220, 38, 38, 0.2);
  border: 1px solid rgba(220, 38, 38, 0.5);
  color: #fecaca;
  padding: 0.75rem;
  border-radius: 0.7rem;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.auth-actions {
  margin-top: 0.3rem;
  display: flex;
  justify-content: flex-end;
}

.auth-submit {
  border-radius: 999px;
  border: none;
  padding: 0.7rem 1.6rem;
  background: #d8bf98;
  color: #2e2a23;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.auth-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #9ca3af;
}
</style>

