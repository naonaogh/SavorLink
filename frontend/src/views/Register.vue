<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { getApiErrorMessage } from '@/api'

const route = useRoute()
const router = useRouter()
const roleQuery = computed(() => (route.query.role === 'supplier' ? 'supplier' : 'buyer'))
const role = computed(() => (roleQuery.value === 'supplier' ? 'SUPPLIER' : 'BUYER'))

const email = ref('')
const password = ref('')
const agree = ref(false)
const error = ref('')
const loading = ref(false)

const submit = async () => {
  if (!agree.value) return
  
  error.value = ''
  loading.value = true
  
  try {
    await api.post('/auth/register', {
      email: email.value,
      password: password.value,
      role: role.value,
      enterprise_ids: [] // В будущем здесь может быть создание предприятия
    })
    
    // После регистрации — на логин
    router.push('/login')
  } catch (apiError: unknown) {
    error.value = getApiErrorMessage(apiError, 'Ошибка при регистрации')
    console.error('Registration error:', apiError)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <header class="auth-header">
        <h1 class="auth-title">
          Регистрация
          <span class="auth-role">
            {{ role === 'BUYER' ? 'покупателя' : 'поставщика' }}
          </span>
        </h1>
      </header>

      <form class="auth-form" @submit.prevent="submit">
        <label class="field">
          <span class="field-label">Email</span>
          <input v-model="email" type="email" class="field-input" autocomplete="email" />
        </label>

        <label class="field">
          <span class="field-label">Password</span>
          <input v-model="password" type="password" class="field-input" autocomplete="new-password" />
        </label>

        <label class="checkbox-row">
          <input v-model="agree" type="checkbox" class="checkbox" />
          <span class="checkbox-text">
            I've read and agree with terms of service and our privacy policy
          </span>
        </label>

        <div v-if="error" class="auth-error">
          {{ error }}
        </div>

        <div class="auth-actions">
          <router-link to="/login" class="auth-circle-btn" style="text-decoration: none; display: flex; align-items: center; justify-content: center;">
            ←
          </router-link>
          <button type="submit" class="auth-submit" :disabled="loading || !agree">
            {{ loading ? 'Загрузка...' : 'Зарегистрироваться →' }}
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
  width: 520px;
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

.auth-role {
  display: block;
  margin-top: 0.3rem;
  font-size: 0.95rem;
  color: #d1d5db;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.auth-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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

.checkbox-row {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  font-size: 0.8rem;
  color: #e5e7eb;
}

.checkbox {
  margin-top: 0.15rem;
}

.checkbox-text {
  line-height: 1.4;
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
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.auth-circle-btn {
  width: 42px;
  height: 42px;
  border-radius: 999px;
  border: none;
  background: #d8bf98;
  color: #2e2a23;
  font-size: 1.1rem;
  cursor: pointer;
}

.auth-submit {
  flex: 1;
  border-radius: 999px;
  border: none;
  padding: 0.7rem 1.2rem;
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

