<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { getApiErrorMessage } from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'
import { AUTH_REQUIRED_REASON } from '@/composables/useRequireAuth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const shopStore = useShopStore()

const mode = computed<'login' | 'register'>(() =>
  route.query.mode === 'register' ? 'register' : 'login'
)

/* ✅ СНАЧАЛА объявляем */
const regRole = ref<'BUYER' | 'SUPPLIER'>(
  route.query.role === 'supplier' ? 'SUPPLIER' : 'BUYER'
)

/* ✅ потом watch */
watch(
  () => route.fullPath,
  () => {
    regRole.value = route.query.role === 'supplier' ? 'SUPPLIER' : 'BUYER'
  }
)

/* Пришли с кнопки «в корзину/избранное» без входа */
const authRequired = computed(() => route.query.reason === AUTH_REQUIRED_REASON)

/* Куда вернуть после входа: только внутренний путь вида "/..." (не "//host") */
const redirectTarget = computed(() => {
  const target = route.query.redirect
  if (typeof target !== 'string' || !target.startsWith('/') || target.startsWith('//')) return null
  if (target.startsWith('/auth')) return null
  return target
})

/* Переключение вход ⇄ регистрация с сохранением пояснения и адреса возврата */
const keptQuery = computed(() => {
  const query: Record<string, string> = {}
  if (authRequired.value) query.reason = AUTH_REQUIRED_REASON
  if (redirectTarget.value) query.redirect = redirectTarget.value
  return query
})
const loginLink = computed(() => ({ path: '/auth', query: keptQuery.value }))
const registerLink = computed(() => ({ path: '/auth', query: { ...keptQuery.value, mode: 'register' } }))

/* Показ пароля */
const showLoginPassword = ref(false)
const showRegPassword = ref(false)

/* Сообщение на форме входа (например, после регистрации, если автовход не удался) */
const loginNotice = ref('')

/* LOGIN */
const loginEmail = ref('')
const loginPassword = ref('')
const loginError = ref('')
const loginLoading = ref(false)

/* REGISTER */
const regEmail = ref('')
const regPassword = ref('')
const regAgree = ref(false)
const regError = ref('')
const regLoading = ref(false)

const openLogin = () => router.push(loginLink.value)

/* Вход + подгрузка корзины/избранного + возврат туда, откуда пришли */
const signIn = async (email: string, password: string) => {
  const { data } = await api.post('/auth/login', { email, password })

  authStore.setAuth(data.token, data.user)

  await Promise.all([
    shopStore.fetchCart(),
    shopStore.fetchFavoriteProducts(),
    shopStore.fetchFavoriteSuppliers(),
  ])

  router.push(redirectTarget.value || '/catalog')
}

const submitLogin = async () => {
  loginError.value = ''
  loginNotice.value = ''
  loginLoading.value = true

  try {
    await signIn(loginEmail.value, loginPassword.value)
  } catch (e) {
    loginError.value = getApiErrorMessage(e, 'Ошибка входа')
  } finally {
    loginLoading.value = false
  }
}

const submitRegister = async () => {
  if (!regAgree.value) return

  regError.value = ''
  regLoading.value = true

  try {
    await api.post('/auth/register', {
      email: regEmail.value,
      password: regPassword.value,
      role: regRole.value,
      enterprise_ids: [],
    })
  } catch (e) {
    regError.value = getApiErrorMessage(e, 'Ошибка регистрации')
    regLoading.value = false
    return
  }

  /* Аккаунт создан — сразу входим, чтобы не вводить данные второй раз */
  try {
    await signIn(regEmail.value, regPassword.value)
  } catch {
    loginEmail.value = regEmail.value
    loginNotice.value = 'Аккаунт создан. Войдите, используя свой email и пароль.'
    router.push(loginLink.value)
  } finally {
    regLoading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <aside class="auth-aside">
      <span class="corner corner--tl" aria-hidden="true"></span>
      <span class="corner corner--br" aria-hidden="true"></span>

      <p class="aside-eyebrow"><span class="aside-eyebrow-mark" aria-hidden="true"></span>SavorLink</p>
      <p class="aside-title">Поставщики и&nbsp;рестораны находят друг друга <em>быстрее</em></p>

      <ol class="aside-steps">
        <li><span class="aside-num" aria-hidden="true">/01</span>Выбираете поставщика и товары в каталоге</li>
        <li><span class="aside-num" aria-hidden="true">/02</span>Оформляете заказ и отслеживаете статусы</li>
        <li><span class="aside-num" aria-hidden="true">/03</span>Получаете документы и аналитику в одном месте</li>
      </ol>
    </aside>

    <section class="auth-panel">
      <div class="auth-card">
        <div v-if="mode === 'login'">
          <p class="kicker">01 / Аккаунт</p>
          <h1 class="title">Вход</h1>

          <p v-if="authRequired" class="notice">
            Чтобы добавлять товары в корзину и избранное, войдите в аккаунт или зарегистрируйтесь.
          </p>
          <p v-if="loginNotice" class="notice notice--success">{{ loginNotice }}</p>

          <form class="form" @submit.prevent="submitLogin">
            <input v-model="loginEmail" type="email" required placeholder="Email" autocomplete="email" class="input" />
            <div class="password-field">
              <input
                v-model="loginPassword"
                :type="showLoginPassword ? 'text' : 'password'"
                required
                placeholder="Пароль"
                autocomplete="current-password"
                class="input"
              />
              <button
                type="button"
                class="eye-btn"
                :aria-label="showLoginPassword ? 'Скрыть пароль' : 'Показать пароль'"
                :aria-pressed="showLoginPassword"
                :title="showLoginPassword ? 'Скрыть пароль' : 'Показать пароль'"
                @click="showLoginPassword = !showLoginPassword"
              >
                <svg v-if="!showLoginPassword" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
                <svg v-else viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 19c-7 0-11-7-11-7a18.45 18.45 0 0 1 5.06-5.94" />
                  <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 7 11 7a18.5 18.5 0 0 1-2.16 3.19" />
                  <path d="M14.12 14.12a3 3 0 1 1-4.24-4.24" />
                  <line x1="1" y1="1" x2="23" y2="23" />
                </svg>
              </button>
            </div>

            <p v-if="loginError" class="error">{{ loginError }}</p>

            <button class="btn" type="submit" :disabled="loginLoading">
              {{ loginLoading ? '...' : 'Войти' }}
            </button>
          </form>

          <p class="switch">
            Нет аккаунта?
            <router-link :to="registerLink" class="switch-link">Регистрация</router-link>
          </p>
        </div>
      </div>

      <Transition name="fade">
        <div v-if="mode === 'register'" class="modal-overlay" @click.self="openLogin">
          <div class="modal-card">
            <p class="kicker">02 / Новый аккаунт</p>
            <h1 class="title">Регистрация</h1>

            <p v-if="authRequired" class="notice">
              Сначала зарегистрируйтесь — после этого вы сможете добавлять товары в корзину и избранное.
            </p>

            <div class="role">
              <button type="button" @click="regRole = 'BUYER'" :class="{ active: regRole === 'BUYER' }">
                Покупатель
              </button>
              <button type="button" @click="regRole = 'SUPPLIER'" :class="{ active: regRole === 'SUPPLIER' }">
                Поставщик
              </button>
            </div>

            <form class="form" @submit.prevent="submitRegister">
              <input v-model="regEmail" type="email" required placeholder="Email" autocomplete="email" class="input" />
              <div class="password-field">
                <input
                  v-model="regPassword"
                  :type="showRegPassword ? 'text' : 'password'"
                  required
                  minlength="8"
                  placeholder="Пароль (не менее 8 символов)"
                  autocomplete="new-password"
                  class="input"
                />
                <button
                  type="button"
                  class="eye-btn"
                  :aria-label="showRegPassword ? 'Скрыть пароль' : 'Показать пароль'"
                  :aria-pressed="showRegPassword"
                  :title="showRegPassword ? 'Скрыть пароль' : 'Показать пароль'"
                  @click="showRegPassword = !showRegPassword"
                >
                  <svg v-if="!showRegPassword" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                  <svg v-else viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 19c-7 0-11-7-11-7a18.45 18.45 0 0 1 5.06-5.94" />
                    <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 7 11 7a18.5 18.5 0 0 1-2.16 3.19" />
                    <path d="M14.12 14.12a3 3 0 1 1-4.24-4.24" />
                    <line x1="1" y1="1" x2="23" y2="23" />
                  </svg>
                </button>
              </div>

              <label class="check">
                <input v-model="regAgree" type="checkbox" />
                Я согласен с условиями
              </label>

              <p v-if="regError" class="error">{{ regError }}</p>

              <button class="btn" type="submit" :disabled="regLoading || !regAgree">
                {{ regLoading ? '...' : 'Создать аккаунт' }}
              </button>
            </form>

            <p class="switch">
              Уже есть аккаунт?
              <router-link :to="loginLink" class="switch-link">Войти</router-link>
            </p>
          </div>
        </div>
      </Transition>
    </section>
  </div>
</template>

<style scoped>
.auth-page {
  display: grid;
  grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
  min-height: min(78vh, 720px);
  margin: 1.25rem 0 2rem;
  border: 1px solid var(--sl-line);
  color: var(--sl-ink);
}

p,
h1 {
  margin: 0;
}

/* ТЁМНАЯ КОЛОНКА */
.auth-aside {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 2rem;
  padding: clamp(2rem, 5vw, 3.5rem);
  color: #fff;
  background:
    repeating-linear-gradient(135deg, rgba(198, 236, 154, 0.05) 0 1px, transparent 1px 14px),
    var(--sl-forest);
}

.corner {
  position: absolute;
  width: 26px;
  height: 26px;
  border: 0 solid var(--sl-lime);
  opacity: 0.85;
}

.corner--tl { top: 1.25rem; left: 1.25rem; border-top-width: 2px; border-left-width: 2px; }
.corner--br { bottom: 1.25rem; right: 1.25rem; border-bottom-width: 2px; border-right-width: 2px; }

.aside-eyebrow {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.4rem 0.8rem;
  border: 1px solid rgba(198, 236, 154, 0.45);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--sl-lime);
}

.aside-eyebrow-mark {
  width: 8px;
  height: 8px;
  background: var(--sl-lime);
}

.aside-title {
  font-family: var(--sl-display);
  font-size: clamp(1.4rem, 2.6vw, 2.1rem);
  font-weight: 600;
  line-height: 1.18;
  letter-spacing: -0.01em;
}

.aside-title em {
  font-style: normal;
  color: var(--sl-lime);
  background: linear-gradient(var(--sl-lime), var(--sl-lime)) left 92% / 100% 3px no-repeat;
}

.aside-steps {
  list-style: none;
  margin: 0;
  padding: 0;
  border-top: 1px solid rgba(255, 255, 255, 0.14);
}

.aside-steps li {
  display: grid;
  grid-template-columns: 3rem 1fr;
  align-items: baseline;
  gap: 0.75rem;
  padding: 0.9rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.14);
  font-weight: 600;
  color: rgba(255, 255, 255, 0.86);
}

.aside-num {
  font-family: var(--sl-display);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--sl-lime);
}

/* ПАНЕЛЬ С ФОРМОЙ */
.auth-panel {
  display: grid;
  background: var(--sl-paper);
  border-top: 3px solid var(--sl-ink);
}

/* вход и регистрация занимают одну ячейку — без скачков при смене режима */
.auth-panel > * {
  grid-area: 1 / 1;
}

.auth-card:empty {
  visibility: hidden;
}

.auth-card,
.modal-overlay {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: clamp(2rem, 5vw, 3.5rem) clamp(1.25rem, 4vw, 3rem);
}

.modal-overlay {
  background: var(--sl-paper);
}

.auth-card > div,
.modal-card {
  width: 100%;
  max-width: 420px;
}

.kicker {
  margin-bottom: 0.6rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

.title {
  margin-bottom: 1.75rem;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  color: var(--sl-ink);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.input {
  width: 100%;
  padding: 0.85rem 1rem;
  border-radius: 0;
  border: 1px solid var(--sl-line);
  background: #fff;
}

.input:hover {
  border-color: rgba(20, 33, 15, 0.32);
}

.btn {
  margin-top: 0.5rem;
  padding: 0.95rem 1.5rem;
  border-radius: 0;
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
  font-weight: 700;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.btn:hover:not(:disabled) {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.error {
  padding: 0.7rem 0.9rem;
  background: #fbeaea;
  border: 1px solid #b3261e;
  color: #b3261e;
  font-size: 0.88rem;
  font-weight: 600;
}

.switch {
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--sl-line);
  font-size: 0.9rem;
  color: var(--sl-muted);
}

.switch-link {
  margin-left: 0.25rem;
  font-weight: 700;
  color: var(--sl-ink);
  border-bottom: 1px solid var(--sl-ink);
  transition: color 0.2s ease, border-color 0.2s ease;
}

.switch-link::after {
  content: ' →';
}

.switch-link:hover {
  color: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

/* ПОЯСНЕНИЕ НАД ФОРМОЙ */
.notice {
  margin-bottom: 1.25rem;
  padding: 0.8rem 1rem;
  background: var(--sl-lime);
  border-left: 3px solid var(--sl-ink);
  color: var(--sl-ink);
  font-size: 0.9rem;
  font-weight: 600;
  line-height: 1.45;
}

.notice--success {
  background: #fff;
  border: 1px solid var(--sl-line);
  border-left: 3px solid var(--sl-leaf);
}

/* ПАРОЛЬ С «ГЛАЗИКОМ» */
.password-field {
  position: relative;
}

.password-field .input {
  padding-right: 3.25rem;
}

.eye-btn {
  position: absolute;
  top: 1px;
  right: 1px;
  bottom: 1px;
  width: 2.9rem;
  display: grid;
  place-items: center;
  padding: 0;
  border: none;
  border-left: 1px solid var(--sl-line);
  border-radius: 0;
  background: #fff;
  color: var(--sl-muted);
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.eye-btn:hover {
  background: var(--sl-paper);
  color: var(--sl-ink);
}

.eye-btn[aria-pressed='true'] {
  color: var(--sl-ink);
}

.eye-btn svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* РОЛЬ — табы */
.role {
  display: grid;
  grid-template-columns: 1fr 1fr;
  margin-bottom: 1.25rem;
  border: 1px solid var(--sl-ink);
}

.role button {
  padding: 0.75rem 0.5rem;
  border: none;
  border-radius: 0;
  background: transparent;
  color: var(--sl-ink);
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.role button + button {
  border-left: 1px solid var(--sl-ink);
}

.role button:hover:not(.active) {
  background: var(--sl-lime);
}

.role .active {
  background: var(--sl-ink);
  color: #fff;
}

.check {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.25rem 0;
  font-size: 0.88rem;
  color: var(--sl-muted);
  cursor: pointer;
}

.check input {
  width: 16px;
  height: 16px;
  margin: 0;
}

.btn:focus-visible,
.eye-btn:focus-visible,
.role button:focus-visible,
.switch-link:focus-visible,
.check input:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* АДАПТИВ */
@media (max-width: 900px) {
  .auth-page {
    grid-template-columns: 1fr;
    min-height: 0;
  }

  .auth-aside {
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .auth-page {
    margin-top: 0.75rem;
  }

  .aside-steps {
    display: none;
  }
}
</style>
