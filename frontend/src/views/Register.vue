<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const role = computed(() => (route.query.role === 'supplier' ? 'supplier' : 'buyer'))

const name = ref('')
const email = ref('')
const address = ref('')
const password = ref('')
const agree = ref(false)

const submit = () => {
  if (!agree.value) return
  // позже здесь будет реальный запрос на бек
  console.log('register', {
    role: role.value,
    name: name.value,
    email: email.value,
    address: address.value,
    password: password.value,
  })
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <header class="auth-header">
        <h1 class="auth-title">
          Регистрация
          <span class="auth-role">
            {{ role === 'buyer' ? 'покупателя' : 'поставщика' }}
          </span>
        </h1>
      </header>

      <form class="auth-form" @submit.prevent="submit">
        <div class="auth-row">
          <label class="field">
            <span class="field-label">Name</span>
            <input v-model="name" type="text" class="field-input" autocomplete="name" />
          </label>
          <label class="field">
            <span class="field-label">Email</span>
            <input v-model="email" type="email" class="field-input" autocomplete="email" />
          </label>
        </div>

        <label class="field">
          <span class="field-label">Adress</span>
          <input v-model="address" type="text" class="field-input" autocomplete="street-address" />
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

        <div class="auth-actions">
          <button type="button" class="auth-circle-btn" aria-label="Назад">
            ←
          </button>
          <button type="submit" class="auth-submit">
            Зарегистрироваться →
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
}
</style>
