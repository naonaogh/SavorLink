<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import HeroImage from '@/assets/images/home-hero.jpg'
import api, { getApiErrorMessage } from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'
import { AUTH_REQUIRED_REASON } from '@/composables/useRequireAuth'
import { AppButton, AppIcon, AppTabs, ErrorState, FormField, type IconName, type TabItem } from '@/components/ui'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const shopStore = useShopStore()

const mode = computed<'login' | 'register'>(() =>
  route.query.mode === 'register' ? 'register' : 'login'
)

/* Роль при регистрации: объявляем до watch */
const regRole = ref<'BUYER' | 'SUPPLIER'>(
  route.query.role === 'supplier' ? 'SUPPLIER' : 'BUYER'
)

/* Синхронизируем роль с адресом (?role=supplier) */
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

/* Вкладки «Вход / Регистрация» и выбор роли — только UI */
const modeTabs: TabItem<'login' | 'register'>[] = [
  { value: 'login', label: 'Вход', icon: 'log-in' },
  { value: 'register', label: 'Регистрация', icon: 'user-plus' },
]
const switchMode = (value: 'login' | 'register') => {
  if (value === mode.value) return
  if (value === 'login') openLogin()
  else router.push(registerLink.value)
}

const roleTabs: TabItem<'BUYER' | 'SUPPLIER'>[] = [
  { value: 'BUYER', label: 'Покупатель', icon: 'store' },
  { value: 'SUPPLIER', label: 'Поставщик', icon: 'package' },
]
const roleHint = computed(() =>
  regRole.value === 'SUPPLIER'
    ? 'Размещайте товары с ценами и остатками, принимайте заказы и общайтесь с покупателями.'
    : 'Находите поставщиков в каталоге, собирайте корзину и отслеживайте статусы заказов.',
)

/* Брендовая панель: те же шаги, что на главной */
const steps: { title: string; text: string; icon: IconName }[] = [
  {
    title: 'Выбираете поставщика и товары в каталоге',
    text: 'Фильтры по категории, региону и городу, сравнение поставщиков бок о бок.',
    icon: 'search',
  },
  {
    title: 'Оформляете заказ и отслеживаете статусы',
    text: 'Корзина собирает заказы сразу по нескольким поставщикам, статус виден в кабинете.',
    icon: 'truck',
  },
  {
    title: 'Получаете документы и аналитику в одном месте',
    text: 'Документы по заказам и ключевые показатели закупок — без таблиц и переписки.',
    icon: 'file-text',
  },
]

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
  <div class="auth">
    <!-- ===== Брендовая панель ===== -->
    <aside class="brand" :style="{ backgroundImage: `url(${HeroImage})` }">
      <div class="brand__inner">
        <p class="brand__logo">
          <span class="brand__mark"><AppIcon name="leaf" :size="18" :stroke-width="2.2" /></span>
          <span>SavorLink</span>
        </p>

        <div class="brand__copy">
          <p class="brand__title">Поставщики и&nbsp;рестораны находят друг друга <span>быстрее</span></p>
          <p class="brand__lead">
            Каталог поставщиков, заказы, документы и переписка — в одном рабочем пространстве для закупок.
          </p>
        </div>

        <ol class="brand__steps">
          <li v-for="(step, index) in steps" :key="step.title" class="brand__step">
            <span class="brand__step-icon"><AppIcon :name="step.icon" :size="18" /></span>
            <div>
              <p class="brand__step-title">
                <span class="brand__step-num ui-num" aria-hidden="true">0{{ index + 1 }}</span>
                {{ step.title }}
              </p>
              <p class="brand__step-text">{{ step.text }}</p>
            </div>
          </li>
        </ol>
      </div>
    </aside>

    <!-- ===== Форма ===== -->
    <section class="panel">
      <div class="auth-card ui-card">
        <AppTabs
          :model-value="mode"
          :items="modeTabs"
          variant="underline"
          aria-label="Вход или регистрация"
          class="mode-tabs"
          @update:model-value="switchMode"
        />

        <!-- ВХОД -->
        <div v-if="mode === 'login'" class="auth-card__body">
          <header class="auth-card__head">
            <h1 class="auth-card__title">Вход</h1>
            <p class="auth-card__lead">Войдите, чтобы продолжить работу с заказами и поставщиками.</p>
          </header>

          <p v-if="authRequired" class="notice">
            <AppIcon name="info" :size="18" />
            <span>Чтобы добавлять товары в корзину и избранное, войдите в аккаунт или зарегистрируйтесь.</span>
          </p>
          <p v-if="loginNotice" class="notice notice--success">
            <AppIcon name="check-circle" :size="18" />
            <span>{{ loginNotice }}</span>
          </p>

          <form class="form" @submit.prevent="submitLogin">
            <FormField label="Email" required v-slot="{ id }">
              <input
                :id="id"
                v-model="loginEmail"
                type="email"
                required
                placeholder="name@company.ru"
                autocomplete="email"
              />
            </FormField>

            <FormField label="Пароль" required v-slot="{ id }">
              <div class="password">
                <input
                  :id="id"
                  v-model="loginPassword"
                  :type="showLoginPassword ? 'text' : 'password'"
                  required
                  placeholder="Ваш пароль"
                  autocomplete="current-password"
                />
                <button
                  type="button"
                  class="password__toggle"
                  :aria-label="showLoginPassword ? 'Скрыть пароль' : 'Показать пароль'"
                  :aria-pressed="showLoginPassword"
                  :title="showLoginPassword ? 'Скрыть пароль' : 'Показать пароль'"
                  @click="showLoginPassword = !showLoginPassword"
                >
                  <AppIcon :name="showLoginPassword ? 'eye-off' : 'eye'" :size="18" />
                </button>
              </div>
            </FormField>

            <ErrorState v-if="loginError" title="Не удалось войти" :message="loginError" :retryable="false" />

            <AppButton type="submit" block size="lg" :loading="loginLoading">Войти</AppButton>
          </form>

          <p class="switch">
            Нет аккаунта?
            <RouterLink :to="registerLink" class="switch__link">Регистрация</RouterLink>
          </p>
        </div>

        <!-- РЕГИСТРАЦИЯ -->
        <div v-else class="auth-card__body">
          <header class="auth-card__head">
            <h1 class="auth-card__title">Регистрация</h1>
            <p class="auth-card__lead">Создайте аккаунт — данные предприятия можно заполнить позже в профиле.</p>
          </header>

          <p v-if="authRequired" class="notice">
            <AppIcon name="info" :size="18" />
            <span>Сначала зарегистрируйтесь — после этого вы сможете добавлять товары в корзину и избранное.</span>
          </p>

          <div class="role">
            <p id="reg-role-label" class="ui-label">Я регистрируюсь как</p>
            <AppTabs v-model="regRole" :items="roleTabs" variant="pills" aria-label="Роль" class="role__tabs" />
            <p class="role__hint">{{ roleHint }}</p>
          </div>

          <form class="form" @submit.prevent="submitRegister">
            <FormField label="Email" required v-slot="{ id }">
              <input
                :id="id"
                v-model="regEmail"
                type="email"
                required
                placeholder="name@company.ru"
                autocomplete="email"
              />
            </FormField>

            <FormField label="Пароль" required hint="Не менее 8 символов." v-slot="{ id, describedBy }">
              <div class="password">
                <input
                  :id="id"
                  v-model="regPassword"
                  :type="showRegPassword ? 'text' : 'password'"
                  required
                  minlength="8"
                  placeholder="Придумайте пароль"
                  autocomplete="new-password"
                  :aria-describedby="describedBy"
                />
                <button
                  type="button"
                  class="password__toggle"
                  :aria-label="showRegPassword ? 'Скрыть пароль' : 'Показать пароль'"
                  :aria-pressed="showRegPassword"
                  :title="showRegPassword ? 'Скрыть пароль' : 'Показать пароль'"
                  @click="showRegPassword = !showRegPassword"
                >
                  <AppIcon :name="showRegPassword ? 'eye-off' : 'eye'" :size="18" />
                </button>
              </div>
            </FormField>

            <label class="check">
              <input v-model="regAgree" type="checkbox" />
              <span>Я согласен с условиями</span>
            </label>

            <ErrorState v-if="regError" title="Не удалось создать аккаунт" :message="regError" :retryable="false" />

            <AppButton type="submit" block size="lg" :loading="regLoading" :disabled="!regAgree">
              Создать аккаунт
            </AppButton>
          </form>

          <p class="switch">
            Уже есть аккаунт?
            <RouterLink :to="loginLink" class="switch__link">Войти</RouterLink>
          </p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.auth {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: clamp(1.25rem, 3vw, 2rem);
  align-items: stretch;
}

/* ===== Брендовая панель ===== */
.brand {
  position: relative;
  display: flex;
  min-height: 620px;
  border-radius: var(--r-xl);
  overflow: hidden;
  background-color: var(--c-brand-900);
  background-size: cover;
  background-position: center;
  color: #fff;
}

/* затемнение фото, чтобы текст читался */
.brand::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(15, 42, 31, 0.86);
}

.brand__inner {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 2rem;
  width: 100%;
  padding: clamp(1.75rem, 4vw, 2.75rem);
}

.brand__logo {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: -0.03em;
}

.brand__mark {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--c-accent);
}

.brand__copy {
  display: grid;
  gap: 0.85rem;
}

.brand__title {
  font-size: clamp(1.75rem, 3.2vw, 2.5rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.brand__title span {
  color: var(--c-accent);
}

.brand__lead {
  max-width: 440px;
  color: rgba(255, 255, 255, 0.78);
}

.brand__steps {
  display: grid;
  gap: 1rem;
  margin: 0;
  padding: 1.5rem 0 0;
  list-style: none;
  border-top: 1px solid rgba(255, 255, 255, 0.14);
}

.brand__step {
  display: flex;
  gap: 0.85rem;
}

.brand__step-icon {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  width: 36px;
  height: 36px;
  border-radius: var(--r-sm);
  background: rgba(255, 255, 255, 0.1);
  color: var(--c-accent);
}

.brand__step-title {
  font-weight: 700;
  line-height: 1.35;
}

.brand__step-num {
  margin-right: 0.35rem;
  color: var(--c-accent);
  font-size: var(--fs-sm);
}

.brand__step-text {
  margin-top: 0.15rem;
  color: rgba(255, 255, 255, 0.72);
  font-size: var(--fs-sm);
}

/* ===== Форма ===== */
.panel {
  display: grid;
  align-items: center;
  justify-items: center;
}

.auth-card {
  display: grid;
  gap: 1.5rem;
  width: 100%;
  max-width: 480px;
  padding: clamp(1.25rem, 3vw, 2rem);
}

.mode-tabs {
  width: 100%;
}

.mode-tabs :deep(.app-tabs__tab) {
  flex: 1 1 0;
  justify-content: center;
}

.auth-card__body {
  display: grid;
  gap: 1.25rem;
}

.auth-card__head {
  display: grid;
  gap: 0.35rem;
}

.auth-card__title {
  font-size: var(--fs-2xl);
}

.auth-card__lead {
  color: var(--c-muted);
  font-size: var(--fs-sm);
}

.notice {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.75rem 0.9rem;
  border: 1px solid var(--c-accent-200);
  border-radius: var(--r-md);
  background: var(--c-accent-50);
  color: var(--c-brand-800);
  font-size: var(--fs-sm);
  font-weight: 600;
  line-height: 1.45;
}

.notice .app-icon {
  flex: 0 0 auto;
  margin-top: 0.05rem;
  color: var(--c-accent-700);
}

.notice--success {
  border-color: transparent;
  background: var(--c-success-bg);
  color: var(--c-success);
}

.notice--success .app-icon {
  color: var(--c-success);
}

.form {
  display: grid;
  gap: 1rem;
}

/* поле пароля с «глазиком» */
.password {
  position: relative;
}

.password input {
  padding-right: 3rem;
}

.password__toggle {
  position: absolute;
  top: 50%;
  right: 0.35rem;
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: var(--r-sm);
  background: transparent;
  color: var(--c-muted);
  transform: translateY(-50%);
  transition:
    color var(--dur) var(--ease),
    background var(--dur) var(--ease);
}

.password__toggle:hover {
  background: var(--c-surface-sunken);
  color: var(--c-text);
}

.password__toggle[aria-pressed='true'] {
  color: var(--c-accent-700);
}

/* выбор роли */
.role {
  display: grid;
  gap: 0.5rem;
}

.role__tabs {
  display: flex;
  width: 100%;
}

.role__tabs :deep(.app-tabs__tab) {
  flex: 1 1 0;
  justify-content: center;
}

.role__hint {
  color: var(--c-muted);
  font-size: var(--fs-sm);
}

/* согласие */
.check {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  font-weight: 600;
  cursor: pointer;
}

.switch {
  color: var(--c-muted);
  font-size: var(--fs-sm);
  text-align: center;
}

.switch__link {
  margin-left: 0.25rem;
  color: var(--c-accent-700);
  font-weight: 700;
}

.switch__link:hover {
  text-decoration: underline;
  text-underline-offset: 3px;
}

/* ===== Адаптив ===== */
@media (max-width: 1024px) {
  .brand__step-text {
    display: none;
  }
}

@media (max-width: 860px) {
  .auth {
    grid-template-columns: 1fr;
  }

  .brand {
    min-height: 0;
  }

  .brand__inner {
    gap: 1rem;
    padding: 1.25rem 1.25rem 1.4rem;
  }

  .brand__title {
    font-size: var(--fs-xl);
  }

  .brand__lead,
  .brand__steps {
    display: none;
  }

  .auth-card {
    max-width: none;
  }
}
</style>
