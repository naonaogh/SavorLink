<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api from '@/services/apiClient'

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
  city?: string | null
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
  city: '',
  phone: '',
  email: ''
})

const editForm = ref<EnterpriseProfile>({
  id: 0,
  short_name: '',
  inn: '',
  region: '',
  city: '',
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
              <button v-if="user.role === 'SUPPLIER' && !isEditingEnterprise" @click="startEditEnterprise" class="edit-btn">
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

            <div v-else>
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
                  <p v-if="loadingEnterprises">Загрузка списка...</p>
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
  min-height: 100vh;
  font-family: 'Manrope', sans-serif;
  background: transparent;
}

.profile-main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.profile-card {
  border-radius: 1.7rem;
  padding: 2rem;
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(76,124,42,0.16);
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 60px rgba(54,87,21,0.14);
}

.profile-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.profile-title {
  font-size: 1.6rem;
  color: #20311c;
}

.refresh-btn,
.primary-btn,
.save-btn,
.join-btn-small {
  border-radius: 999px;
  padding: 0.6rem 1.2rem;
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: white;
  border: none;
  cursor: pointer;
}

.secondary-btn {
  border-radius: 999px;
  padding: 0.6rem 1.2rem;
  background: white;
  border: 1px solid rgba(76,124,42,0.2);
}

.edit-btn {
  border-radius: 999px;
  padding: 0.4rem 0.9rem;
  background: white;
  border: 1px solid rgba(76,124,42,0.2);
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
}

.info-card {
  border-radius: 1.2rem;
  padding: 1rem;
  background: rgba(255,255,255,0.7);
  border: 1px solid rgba(76,124,42,0.12);
  backdrop-filter: blur(12px);
}

.info-title {
  margin-bottom: 0.7rem;
  color: #20311c;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 0.4rem 0;
  border-bottom: 1px solid rgba(76,124,42,0.1);
}

.form-group input {
  padding: 0.6rem;
  border-radius: 0.7rem;
  border: 1px solid rgba(76,124,42,0.2);
}

.state-text {
  color: #5d6b52;
}

.state-text--error {
  color: #991b1b;
}
</style>
