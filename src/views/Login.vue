<script setup lang="ts">
import { ref } from 'vue'

const email = ref('')
const password = ref('')

const submit = () => {
  console.log('login', { email: email.value, password: password.value })
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

        <div class="auth-actions">
          <button type="submit" class="auth-submit">
            Войти →
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
  background: radial-gradient(circle at top left, #647c6b 0%, #4b5f54 40%, #3d4e45 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
}

.auth-card {
  width: 420px;
  max-width: 90vw;
  padding: 2.2rem 2.4rem 2rem;
  border-radius: 1.75rem;
  background: rgba(33, 42, 37, 0.9);
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

.auth-actions {
  margin-top: 0.3rem;
  display: flex;
  justify-content: flex-end;
}

.auth-submit {
  border-radius: 999px;
  border: none;
  padding: 0.7rem 1.6rem;
  background: #f9fafb;
  color: #111827;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
}
</style>

