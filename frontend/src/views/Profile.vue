<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api from '@/api'
import CommonNavbar from '@/components/CommonNavbar.vue'

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

const user = ref<UserProfile | null>(null)
const enterprise = ref<EnterpriseProfile | null>(null)
const loading = ref(true)
const error = ref('')

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
  phone: '',
  email: ''
})

const editForm = ref<EnterpriseProfile>({
  id: 0,
  short_name: '',
  inn: '',
  region: '',
  phone: '',
  email: ''
})

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
  } catch (e: any) {
    alert(e.response?.data?.detail || 'Ошибка при создании')
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
  } catch (e: any) {
    alert('Ошибка при загрузке списка предприятий')
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
  } catch (e: any) {
    alert(e.response?.data?.detail || 'Ошибка при присоединении')
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
  } catch (e: any) {
    alert(e.response?.data?.detail || 'Ошибка при сохранении')
  } finally {
    savingEnterprise.value = false
  }
}

const createdAt = computed(() => {
  if (!user.value?.created_at) return '—'
  return new Date(user.value.created_at).toLocaleDateString('ru-RU')
})

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
    <CommonNavbar />

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
            <div class="card-header">
              <h2 class="info-title">Предприятие</h2>
              <button 
                v-if="user.role === 'SUPPLIER' && !isEditingEnterprise" 
                @click="startEditEnterprise" 
                class="edit-btn"
              >
                Изменить
              </button>
            </div>

            <div v-if="enterprise">
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
                <div class="info-row"><dt>Телефон</dt><dd>{{ enterprise.phone || '—' }}</dd></div>
                <div class="info-row"><dt>Email</dt><dd>{{ enterprise.email || '—' }}</dd></div>
              </dl>
            </div>
            <div v-else>
              <div v-if="isCreatingEnterprise">
                <form @submit.prevent="createEnterprise" class="edit-form">
                  <div class="form-group">
                    <label>Название</label>
                    <input v-model="createForm.short_name" type="text" required placeholder="Например: ООО 'МясоПром'" />
                  </div>
                  <div class="form-group">
                    <label>ИНН</label>
                    <input v-model="createForm.inn" type="text" required placeholder="10 или 12 цифр" />
                  </div>
                  <div class="form-group">
                    <label>Регион</label>
                    <input v-model="createForm.region" type="text" required placeholder="Например: Москва" />
                  </div>
                  <div class="form-group">
                    <label>Телефон</label>
                    <input v-model="createForm.phone" type="text" placeholder="+7 (999) 000-00-00" />
                  </div>
                  <div class="form-group">
                    <label>Email</label>
                    <input v-model="createForm.email" type="email" placeholder="email@company.ru" />
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
                  <p v-if="loadingEnterprises">Загрузка списка...</p>
                  <div v-else class="enterprise-items">
                    <div v-for="ent in joinableEnterprises" :key="ent.id" class="enterprise-item">
                      <div class="ent-info">
                        <strong>{{ ent.short_name }}</strong>
                        <span>ИНН: {{ ent.inn }}</span>
                      </div>
                      <button @click="joinEnterprise(ent.id)" :disabled="savingEnterprise" class="join-btn-small">Выбрать</button>
                    </div>
                  </div>
                  <button @click="isJoiningEnterprise = false" class="cancel-btn mt-2">Назад</button>
                </div>
              </div>
              <div v-else class="no-enterprise-actions">
                <p class="state-text">Вы пока не привязаны к предприятию. Для совершения заказов необходимо создать новое или выбрать существующее.</p>
                <div class="action-buttons">
                  <button @click="isCreatingEnterprise = true" class="primary-btn">Создать новое</button>
                  <button @click="startJoinEnterprise" class="secondary-btn">Присоединиться к существующему</button>
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

.state-text--error { color: #8f2d2d; }

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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}

.edit-btn {
  background: transparent;
  border: 1px solid #3f4a2f;
  color: #3f4a2f;
  padding: 0.3rem 0.8rem;
  border-radius: 999px;
  font-size: 0.85rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.edit-btn:hover {
  background: #3f4a2f;
  color: #fff;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-group label {
  font-size: 0.8rem;
  font-weight: 700;
  color: #6d6254;
}

.form-group input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #dcc7a2;
  border-radius: 0.4rem;
  background: #fff;
  font-family: inherit;
  font-size: 0.94rem;
}

.form-group input:focus {
  outline: none;
  border-color: #3f4a2f;
}

.edit-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.cancel-btn {
  background: transparent;
  border: none;
  color: #6d6254;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.9rem;
}

.save-btn {
  background: #3f4a2f;
  color: #fff;
  border: none;
  padding: 0.5rem 1.25rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.9rem;
}

.save-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.no-enterprise-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.primary-btn {
  background: #3f4a2f;
  color: #fff;
  border: none;
  padding: 0.6rem 1.25rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.secondary-btn {
  background: #fff;
  color: #3f4a2f;
  border: 1px solid #3f4a2f;
  padding: 0.6rem 1.25rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.secondary-btn:hover {
  background: #f0e5d1;
}

.join-list {
  background: #fff;
  border: 1px solid #dcc7a2;
  border-radius: 0.4rem;
  padding: 0.5rem;
}

.enterprise-items {
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.enterprise-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-bottom: 1px solid #eee;
}

.enterprise-item:last-child {
  border-bottom: none;
}

.ent-info {
  display: flex;
  flex-direction: column;
}

.ent-info strong {
  font-size: 0.95rem;
  color: #3f4a2f;
}

.ent-info span {
  font-size: 0.8rem;
  color: #666;
}

.join-btn-small {
  background: #3f4a2f;
  color: #fff;
  border: none;
  padding: 0.35rem 0.75rem;
  border-radius: 0.4rem;
  font-size: 0.85rem;
  cursor: pointer;
}

.mt-2 {
  margin-top: 1rem;
}
</style>
