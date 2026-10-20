<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'

type UserProfile = {
  id: number
  email: string
  phone?: string | null
  first_name?: string | null
  last_name?: string | null
  role: string
  enterprise_id: number | null
  created_at: string
  enterprise?: { id: number; short_name: string } | null
}

type EnterpriseProfile = {
  id: number
  short_name: string
  inn: string
  region: string
  city?: string | null
  phone?: string | null
  email?: string | null
}

type NoticeType = 'success' | 'error'

const authStore = useAuthStore()

const user = ref<UserProfile | null>(null)
const enterprise = ref<EnterpriseProfile | null>(null)
const loading = ref(true)
const error = ref('')

const notice = ref<{ text: string; type: NoticeType } | null>(null)
let noticeTimer: number | null = null

const isEditingAccount = ref(false)
const savingAccount = ref(false)
const accountForm = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  old_password: '',
  password: '',
  password_confirm: '',
})

const isEditingEnterprise = ref(false)
const isCreatingEnterprise = ref(false)
const isJoiningEnterprise = ref(false)
const savingEnterprise = ref(false)
const joinableEnterprises = ref<EnterpriseProfile[]>([])
const loadingEnterprises = ref(false)

const createForm = ref({
  short_name: '',
  inn: '',
  region: '',
  city: '',
  phone: '',
  email: '',
})

const editForm = ref<EnterpriseProfile>({
  id: 0,
  short_name: '',
  inn: '',
  region: '',
  city: '',
  phone: '',
  email: '',
})

const showNotice = (text: string, type: NoticeType = 'success') => {
  notice.value = { text, type }
  if (noticeTimer) {
    clearTimeout(noticeTimer)
  }
  noticeTimer = window.setTimeout(() => {
    notice.value = null
  }, 5000)
}

const createdAt = computed(() => {
  if (!user.value?.created_at) return '—'
  return new Date(user.value.created_at).toLocaleDateString('ru-RU')
})

const startEditAccount = () => {
  if (!user.value) return
  accountForm.value = {
    first_name: user.value.first_name || '',
    last_name: user.value.last_name || '',
    email: user.value.email || '',
    phone: user.value.phone || '',
    old_password: '',
    password: '',
    password_confirm: '',
  }
  isEditingAccount.value = true
}

const cancelEditAccount = () => {
  isEditingAccount.value = false
  accountForm.value.old_password = ''
  accountForm.value.password = ''
  accountForm.value.password_confirm = ''
}

const saveAccount = async () => {
  if (!user.value || savingAccount.value) return

  const wantsPasswordUpdate = !!accountForm.value.password || !!accountForm.value.old_password
  if (wantsPasswordUpdate && accountForm.value.password !== accountForm.value.password_confirm) {
    showNotice('Новый пароль и подтверждение не совпадают', 'error')
    return
  }

  savingAccount.value = true
  try {
    const payload: Record<string, string | null> = {
      first_name: accountForm.value.first_name.trim() || null,
      last_name: accountForm.value.last_name.trim() || null,
      email: accountForm.value.email.trim(),
      phone: accountForm.value.phone.trim() || null,
    }

    if (wantsPasswordUpdate) {
      payload.old_password = accountForm.value.old_password
      payload.password = accountForm.value.password
    }

    const res = await api.patch('/users/me', payload)
    user.value = res.data

    if (authStore.token) {
      authStore.setAuth(authStore.token, { ...(authStore.user ?? {}), ...res.data })
    }

    isEditingAccount.value = false
    accountForm.value.old_password = ''
    accountForm.value.password = ''
    accountForm.value.password_confirm = ''
    showNotice('Данные аккаунта успешно сохранены')
  } catch (e: any) {
    showNotice(e.response?.data?.detail || 'Ошибка при сохранении профиля', 'error')
  } finally {
    savingAccount.value = false
  }
}

const startEditEnterprise = () => {
  if (enterprise.value) {
    editForm.value = { ...enterprise.value }
    isEditingEnterprise.value = true
  }
}

const createEnterprise = async () => {
  savingEnterprise.value = true
  try {
    const res = await api.post('/enterprises', createForm.value)
    enterprise.value = res.data
    isCreatingEnterprise.value = false
    if (user.value) user.value.enterprise_id = res.data.id
    showNotice('Предприятие создано и привязано к аккаунту')
  } catch (e: any) {
    showNotice(e.response?.data?.detail || 'Ошибка при создании предприятия', 'error')
  } finally {
    savingEnterprise.value = false
  }
}

const startJoinEnterprise = async () => {
  isJoiningEnterprise.value = true
  loadingEnterprises.value = true
  try {
    const res = await api.get('/enterprises')
    joinableEnterprises.value = res.data
  } catch {
    showNotice('Ошибка при загрузке списка предприятий', 'error')
  } finally {
    loadingEnterprises.value = false
  }
}

const joinEnterprise = async (id: number) => {
  savingEnterprise.value = true
  try {
    const res = await api.post(`/enterprises/${id}/join`)
    enterprise.value = res.data
    isJoiningEnterprise.value = false
    if (user.value) user.value.enterprise_id = res.data.id
    showNotice('Предприятие успешно привязано')
  } catch (e: any) {
    showNotice(e.response?.data?.detail || 'Ошибка при присоединении к предприятию', 'error')
  } finally {
    savingEnterprise.value = false
  }
}

const saveEnterprise = async () => {
  if (!enterprise.value) return
  savingEnterprise.value = true
  try {
    const res = await api.patch(`/enterprises/${enterprise.value.id}`, editForm.value)
    enterprise.value = res.data
    isEditingEnterprise.value = false
    showNotice('Данные предприятия обновлены')
  } catch (e: any) {
    showNotice(e.response?.data?.detail || 'Ошибка при сохранении предприятия', 'error')
  } finally {
    savingEnterprise.value = false
  }
}

const loadProfile = async () => {
  loading.value = true
  error.value = ''

  try {
    const userRes = await api.get('/users/me')
    const userData: UserProfile = userRes.data
    user.value = userData

    if (userData.enterprise_id) {
      const entRes = await api.get(`/enterprises/${userData.enterprise_id}`)
      enterprise.value = entRes.data
    } else {
      enterprise.value = null
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Ошибка загрузки профиля'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<template>
  <div class="profile-page">
    <main class="profile-main">
      <Transition name="profile-toast">
        <div v-if="notice" class="notice" :class="notice.type === 'success' ? 'notice--success' : 'notice--error'">
          {{ notice.text }}
        </div>
      </Transition>

      <section class="profile-card">
        <div class="profile-card-head">
          <div>
            <p class="kicker">Личные данные</p>
            <h1 class="profile-title">Профиль</h1>
          </div>
          <button type="button" class="refresh-btn" @click="loadProfile">Обновить</button>
        </div>

        <p v-if="loading" class="state-text">Загрузка данных...</p>
        <p v-else-if="error" class="state-text state-text--error">{{ error }}</p>

        <div v-else-if="user" class="profile-grid">
          <article class="info-card">
            <div class="card-header">
              <h2 class="info-title"><span class="card-index" aria-hidden="true">01</span>Аккаунт</h2>
              <button v-if="!isEditingAccount" type="button" class="edit-btn" @click="startEditAccount">
                Изменить
              </button>
            </div>

            <form v-if="isEditingAccount" class="edit-form" @submit.prevent="saveAccount">
              <div class="form-group">
                <label>Имя</label>
                <input v-model="accountForm.first_name" type="text" placeholder="Иван" />
              </div>
              <div class="form-group">
                <label>Фамилия</label>
                <input v-model="accountForm.last_name" type="text" placeholder="Иванов" />
              </div>
              <div class="form-group">
                <label>Email</label>
                <input v-model="accountForm.email" type="email" required />
              </div>
              <div class="form-group">
                <label>Телефон</label>
                <input v-model="accountForm.phone" type="text" placeholder="+7 (999) 123-45-67" />
              </div>
              <div class="form-group">
                <label>Текущий пароль (если меняете пароль)</label>
                <input v-model="accountForm.old_password" type="password" autocomplete="current-password" />
              </div>
              <div class="form-group">
                <label>Новый пароль</label>
                <input v-model="accountForm.password" type="password" autocomplete="new-password" />
              </div>
              <div class="form-group">
                <label>Подтверждение нового пароля</label>
                <input v-model="accountForm.password_confirm" type="password" autocomplete="new-password" />
              </div>

              <div class="edit-actions">
                <button type="button" class="cancel-btn" @click="cancelEditAccount">Отмена</button>
                <button type="submit" class="save-btn" :disabled="savingAccount">
                  {{ savingAccount ? 'Сохранение...' : 'Сохранить' }}
                </button>
              </div>
            </form>

            <dl v-else class="info-list">
              <div class="info-row"><dt>ID</dt><dd>{{ user.id }}</dd></div>
              <div class="info-row"><dt>Имя</dt><dd>{{ user.first_name || '—' }}</dd></div>
              <div class="info-row"><dt>Фамилия</dt><dd>{{ user.last_name || '—' }}</dd></div>
              <div class="info-row"><dt>Email</dt><dd>{{ user.email }}</dd></div>
              <div class="info-row"><dt>Телефон</dt><dd>{{ user.phone || '—' }}</dd></div>
              <div class="info-row"><dt>Роль</dt><dd>{{ user.role }}</dd></div>
              <div class="info-row"><dt>Дата регистрации</dt><dd>{{ createdAt }}</dd></div>
            </dl>
          </article>

          <article class="info-card">
            <div class="card-header">
              <h2 class="info-title"><span class="card-index" aria-hidden="true">02</span>Предприятие</h2>
              <button
                v-if="user.role === 'SUPPLIER' && enterprise && !isEditingEnterprise"
                type="button"
                class="edit-btn"
                @click="startEditEnterprise"
              >
                Изменить
              </button>
            </div>

            <div v-if="enterprise" class="card-body">
              <form v-if="isEditingEnterprise" @submit.prevent="saveEnterprise" class="edit-form">
                <div class="form-group">
                  <label>Название</label>
                  <input v-model="editForm.short_name" type="text" required />
                </div>
                <div class="form-group">
                  <label>ИНН</label>
                  <input v-model="editForm.inn" type="text" required />
                </div>
                <div class="form-group">
                  <label>Регион</label>
                  <input v-model="editForm.region" type="text" required />
                </div>
                <div class="form-group">
                  <label>Город</label>
                  <input v-model="editForm.city" type="text" placeholder="Если нужно, укажите город" />
                </div>
                <div class="form-group">
                  <label>Телефон</label>
                  <input v-model="editForm.phone" type="text" />
                </div>
                <div class="form-group">
                  <label>Email</label>
                  <input v-model="editForm.email" type="email" />
                </div>
                <div class="edit-actions">
                  <button type="button" @click="isEditingEnterprise = false" class="cancel-btn">Отмена</button>
                  <button type="submit" class="save-btn" :disabled="savingEnterprise">
                    {{ savingEnterprise ? 'Сохранение...' : 'Сохранить' }}
                  </button>
                </div>
              </form>

              <dl v-else class="info-list">
                <div class="info-row"><dt>Название</dt><dd>{{ enterprise.short_name }}</dd></div>
                <div class="info-row"><dt>ИНН</dt><dd>{{ enterprise.inn }}</dd></div>
                <div class="info-row"><dt>Регион</dt><dd>{{ enterprise.region }}</dd></div>
                <div class="info-row"><dt>Город</dt><dd>{{ enterprise.city || '—' }}</dd></div>
                <div class="info-row"><dt>Телефон</dt><dd>{{ enterprise.phone || '—' }}</dd></div>
                <div class="info-row"><dt>Email</dt><dd>{{ enterprise.email || '—' }}</dd></div>
              </dl>
            </div>

            <div v-else class="card-body">
              <div v-if="isCreatingEnterprise">
                <form @submit.prevent="createEnterprise" class="edit-form">
                  <div class="form-group">
                    <label>Название</label>
                    <input v-model="createForm.short_name" required />
                  </div>
                  <div class="form-group">
                    <label>ИНН</label>
                    <input v-model="createForm.inn" required />
                  </div>
                  <div class="form-group">
                    <label>Регион</label>
                    <input v-model="createForm.region" required />
                  </div>
                  <div class="form-group">
                    <label>Город</label>
                    <input v-model="createForm.city" placeholder="Необязательно" />
                  </div>
                  <div class="form-group">
                    <label>Телефон</label>
                    <input v-model="createForm.phone" />
                  </div>
                  <div class="form-group">
                    <label>Email</label>
                    <input v-model="createForm.email" type="email" />
                  </div>
                  <div class="edit-actions">
                    <button type="button" @click="isCreatingEnterprise = false" class="cancel-btn">Отмена</button>
                    <button type="submit" class="save-btn" :disabled="savingEnterprise">
                      {{ savingEnterprise ? 'Создание...' : 'Создать предприятие' }}
                    </button>
                  </div>
                </form>
              </div>

              <div v-else-if="isJoiningEnterprise">
                <div class="join-list">
                  <p v-if="loadingEnterprises" class="state-text">Загрузка списка...</p>
                  <div v-else class="enterprise-items">
                    <div v-for="ent in joinableEnterprises" :key="ent.id" class="enterprise-item">
                      <div class="ent-info">
                        <strong>{{ ent.short_name }}</strong>
                        <span>ИНН: {{ ent.inn }}</span>
                      </div>
                      <button @click="joinEnterprise(ent.id)" class="join-btn-small">Выбрать</button>
                    </div>
                  </div>
                  <button @click="isJoiningEnterprise = false" class="cancel-btn mt-2">Назад</button>
                </div>
              </div>

              <div v-else class="no-enterprise-actions">
                <p class="state-text">Вы пока не привязаны к предприятию</p>
                <div class="action-buttons">
                  <button @click="isCreatingEnterprise = true" class="primary-btn">Создать</button>
                  <button @click="startJoinEnterprise" class="secondary-btn">Присоединиться</button>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.profile-page {
  color: var(--sl-ink);
}

.profile-main {
  display: grid;
}

/* ===== ТОСТ ===== */
.notice {
  position: fixed;
  top: 84px;
  right: 1.5rem;
  z-index: 1000;
  max-width: min(420px, calc(100vw - 2rem));
  padding: 0.9rem 1.1rem;
  font-weight: 700;
  background: #fff;
  border: 1px solid var(--sl-line);
  border-left: 4px solid var(--sl-leaf);
  box-shadow: 0 24px 48px rgba(20, 33, 15, 0.18);
}

.notice--success {
  color: var(--sl-ink);
}

.notice--error {
  color: #b3261e;
  background: #fbeaea;
  border-color: rgba(179, 38, 30, 0.3);
  border-left-color: #b3261e;
}

.profile-toast-enter-active,
.profile-toast-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.profile-toast-enter-from,
.profile-toast-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ===== ПАНЕЛЬ ===== */
.profile-card {
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
  padding: clamp(1.25rem, 3vw, 2rem);
}

.profile-card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
  padding-bottom: 1.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--sl-line);
}

.kicker {
  margin: 0 0 0.6rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

.profile-title {
  margin: 0;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  color: var(--sl-ink);
}

/* ===== КНОПКИ ===== */
.refresh-btn,
.primary-btn,
.save-btn,
.join-btn-small,
.secondary-btn,
.edit-btn,
.cancel-btn {
  border-radius: 0;
  padding: 0.7rem 1.2rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.primary-btn,
.save-btn,
.join-btn-small {
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
}

.primary-btn:hover,
.save-btn:hover,
.join-btn-small:hover {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.refresh-btn,
.secondary-btn,
.edit-btn,
.cancel-btn {
  background: transparent;
  color: var(--sl-ink);
  border: 1px solid var(--sl-ink);
}

.refresh-btn:hover,
.secondary-btn:hover,
.edit-btn:hover,
.cancel-btn:hover {
  background: var(--sl-ink);
  color: #fff;
}

.edit-btn,
.join-btn-small {
  padding: 0.45rem 0.85rem;
  font-size: 0.85rem;
}

.refresh-btn:focus-visible,
.primary-btn:focus-visible,
.save-btn:focus-visible,
.join-btn-small:focus-visible,
.secondary-btn:focus-visible,
.edit-btn:focus-visible,
.cancel-btn:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

/* ===== КАРТОЧКИ ===== */
.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1px;
  background: var(--sl-line);
  border: 1px solid var(--sl-line);
}

.info-card {
  min-width: 0;
  background: #fff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  min-height: 4rem;
  padding: 0.85rem 1.25rem;
  border-bottom: 1px solid var(--sl-line);
}

.info-title {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin: 0;
  font-size: 1.1rem;
  color: var(--sl-ink);
}

.card-index {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--sl-leaf);
}

.info-card > .edit-form,
.info-card > .info-list,
.card-body {
  padding: 0.5rem 1.25rem 1.25rem;
}

.info-card > .edit-form,
.card-body > .edit-form {
  padding-top: 1.25rem;
}

.info-list {
  margin: 0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.8rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--sl-line);
}

.info-row:last-child {
  border-bottom: none;
}

.info-row dt {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.info-row dd {
  margin: 0;
  text-align: right;
  font-weight: 700;
  color: var(--sl-ink);
  overflow-wrap: anywhere;
}

/* ===== ФОРМЫ ===== */
.edit-form {
  display: grid;
  gap: 0.9rem;
  padding-top: 0.75rem;
}

.form-group {
  display: grid;
  gap: 0.35rem;
}

.form-group label {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.form-group input {
  width: 100%;
  min-width: 0;
  border-radius: 0;
  border: 1px solid var(--sl-line);
  background: #fff;
}

.form-group input:focus-visible {
  border-color: var(--sl-leaf);
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
  padding-top: 1rem;
  margin-top: 0.25rem;
  border-top: 1px solid var(--sl-line);
}

/* ===== СОСТОЯНИЯ ===== */
.state-text {
  margin: 0;
  color: var(--sl-muted);
}

.state-text--error {
  padding: 0.9rem 1rem;
  color: #b3261e;
  background: #fbeaea;
  border: 1px solid rgba(179, 38, 30, 0.3);
}

.no-enterprise-actions {
  display: grid;
  gap: 1rem;
  padding: 1rem 0 0.25rem;
}

.action-buttons {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

/* ===== ПРИСОЕДИНЕНИЕ ===== */
.join-list {
  display: grid;
  gap: 1rem;
  padding-top: 0.75rem;
  justify-items: start;
}

.enterprise-items {
  justify-self: stretch;
  display: grid;
  max-height: 280px;
  overflow: auto;
  border: 1px solid var(--sl-line);
}

.enterprise-item {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: center;
  padding: 0.75rem 0.9rem;
  border-bottom: 1px solid var(--sl-line);
  background: #fff;
  transition: background 0.2s ease;
}

.enterprise-item:last-child {
  border-bottom: none;
}

.enterprise-item:hover {
  background: var(--sl-paper);
}

.ent-info {
  display: grid;
  gap: 0.15rem;
  min-width: 0;
}

.ent-info strong {
  color: var(--sl-ink);
  overflow-wrap: anywhere;
}

.ent-info span {
  font-size: 0.82rem;
  color: var(--sl-muted);
}

.mt-2 {
  margin-top: 0;
}

@media (max-width: 900px) {
  .info-row {
    flex-direction: column;
    gap: 0.2rem;
  }

  .info-row dd {
    text-align: left;
  }

  .edit-actions {
    flex-direction: column-reverse;
  }

  .edit-actions button {
    width: 100%;
  }
}

@media (max-width: 520px) {
  .profile-card-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .profile-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .card-header,
  .info-card > .edit-form,
  .info-card > .info-list,
  .card-body {
    padding-left: 1rem;
    padding-right: 1rem;
  }
}
</style>
