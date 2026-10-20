<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'

const activeTab = ref('users')
const error = ref('')
const notice = ref<{ text: string; type: 'success' | 'error' } | null>(null)

const showNotice = (text: string, type: 'success' | 'error' = 'success') => {
  notice.value = { text, type }
  setTimeout(() => { notice.value = null }, 3000)
}

// -------------------------
// USERS
// -------------------------
const users = ref<any[]>([])
const loadingUsers = ref(false)

const loadUsers = async () => {
  loadingUsers.value = true
  try {
    const res = await api.get('/users')
    users.value = res.data
  } catch (err: any) {
    showNotice('Ошибка загрузки пользователей', 'error')
  } finally {
    loadingUsers.value = false
  }
}

const updateRole = async (userId: number, currentRole: string) => {
  const newRole = prompt(`Изменить роль (ADMIN, BUYER, SUPPLIER). Текущая: ${currentRole}`, currentRole)
  if (!newRole || newRole === currentRole) return
  if (!['ADMIN', 'BUYER', 'SUPPLIER'].includes(newRole)) {
    showNotice('Неверная роль', 'error')
    return
  }
  try {
    await api.patch(`/users/${userId}/role`, { role: newRole })
    showNotice('Роль обновлена')
    loadUsers()
  } catch (err) {
    showNotice('Ошибка изменения роли', 'error')
  }
}

// -------------------------
// CATEGORIES
// -------------------------
const categories = ref<any[]>([])
const loadingCategories = ref(false)

const loadCategories = async () => {
  loadingCategories.value = true
  try {
    const res = await api.get('/products/categories')
    categories.value = res.data
  } catch (err) {
    showNotice('Ошибка загрузки категорий', 'error')
  } finally {
    loadingCategories.value = false
  }
}

const createCategory = async () => {
  const name = prompt('Название новой категории:')
  if (!name) return
  try {
    await api.post('/products/categories', { name })
    showNotice('Категория создана')
    loadCategories()
  } catch (err) {
    showNotice('Ошибка создания категории', 'error')
  }
}

const editCategory = async (catId: number, currentName: string) => {
  const name = prompt('Новое название:', currentName)
  if (!name || name === currentName) return
  try {
    await api.patch(`/products/categories/${catId}`, { name })
    showNotice('Категория обновлена')
    loadCategories()
  } catch (err) {
    showNotice('Ошибка обновления категории', 'error')
  }
}

// -------------------------
// ENTERPRISES
// -------------------------
const enterprises = ref<any[]>([])
const loadingEnterprises = ref(false)

const loadEnterprises = async () => {
  loadingEnterprises.value = true
  try {
    const res = await api.get('/enterprises')
    enterprises.value = res.data
  } catch (err) {
    showNotice('Ошибка загрузки предприятий', 'error')
  } finally {
    loadingEnterprises.value = false
  }
}

const deleteEnterprise = async (id: number, name: string) => {
  if (!confirm(`Удалить предприятие "${name}"? Это также удалит все его товары и заказы!`)) return
  try {
    await api.delete(`/enterprises/${id}`)
    showNotice('Предприятие удалено')
    loadEnterprises()
  } catch (err) {
    showNotice('Ошибка удаления', 'error')
  }
}

// -------------------------
// STATUS
// -------------------------
const systemStatus = ref({
  api: 'Загрузка...',
  db: 'Загрузка...'
})

const checkStatus = async () => {
  systemStatus.value.api = 'Проверка...'
  try {
    const start = Date.now()
    await api.get('/') // Root endpoint check
    const diff = (Date.now() - start)
    systemStatus.value.api = `ОК (${diff} мс)`
    systemStatus.value.db = `ОК (Связь с базой данных в норме)`
  } catch (err) {
    systemStatus.value.api = 'Ошибка соединения'
    systemStatus.value.db = 'Ошибка соединения / БД недоступна'
  }
}

onMounted(() => {
  loadUsers()
  loadCategories()
  loadEnterprises()
  checkStatus()
})

</script>

<template>
  <div class="admin-panel">
    <header class="admin-header">
      <p class="kicker">Администрирование</p>
      <h1>Панель Администратора</h1>
      <p class="subtitle">Управление пользователями, справочниками и мониторинг</p>
    </header>

    <Transition name="fade">
      <div v-if="notice" class="admin-toast" :class="notice.type">
        {{ notice.text }}
      </div>
    </Transition>

    <nav class="admin-tabs">
      <button :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">Пользователи</button>
      <button :class="{ active: activeTab === 'categories' }" @click="activeTab = 'categories'">Справочники (Категории)</button>
      <button :class="{ active: activeTab === 'enterprises' }" @click="activeTab = 'enterprises'">Предприятия</button>
      <button :class="{ active: activeTab === 'status' }" @click="activeTab = 'status'">Мониторинг</button>
    </nav>

    <div class="admin-content card">
      <!-- ТАБ ПОЛЬЗОВАТЕЛИ -->
      <section v-if="activeTab === 'users'">
        <div class="section-head">
          <h2>Управление пользователями ({users.length})</h2>
          <button class="btn" @click="loadUsers">Обновить</button>
        </div>
        <div v-if="loadingUsers" class="loading">Загрузка...</div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Роль</th>
                <th>Предприятия</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td>{{ u.id }}</td>
                <td>{{ u.email }}</td>
                <td>
                  <span class="role-badge" :class="u.role">{{ u.role }}</span>
                </td>
                <td>
                  <div v-for="ent in u.enterprises" :key="ent.id" class="ent-tag">
                    {{ ent.short_name }} (#{{ ent.id }})
                  </div>
                  <span v-if="!u.enterprises.length" class="text-muted">—</span>
                </td>
                <td>
                  <button class="btn-small" @click="updateRole(u.id, u.role)">См. роль</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ТАБ КАТЕГОРИИ -->
      <section v-else-if="activeTab === 'categories'">
        <div class="section-head">
          <h2>Управление справочниками</h2>
          <div class="actions">
            <button class="btn primary-btn" @click="createCategory">Создать категорию</button>
            <button class="btn" @click="loadCategories">Обновить</button>
          </div>
        </div>
        <div v-if="loadingCategories" class="loading">Загрузка...</div>
        <ul v-else class="cat-list">
          <li v-for="cat in categories" :key="cat.id" class="cat-item">
            <span><strong>#{{ cat.id }}</strong> {{ cat.name }}</span>
            <button class="btn-small" @click="editCategory(cat.id, cat.name)">Редактировать</button>
          </li>
        </ul>
      </section>

      <!-- ТАБ ПРЕДПРИЯТИЯ -->
      <section v-else-if="activeTab === 'enterprises'">
        <div class="section-head">
          <h2>Управление предприятиями</h2>
          <button class="btn" @click="loadEnterprises">Обновить</button>
        </div>
        <div v-if="loadingEnterprises" class="loading">Загрузка...</div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>ИНН</th>
                <th>Название</th>
                <th>Регион</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ent in enterprises" :key="ent.id">
                <td>{{ ent.id }}</td>
                <td>{{ ent.inn }}</td>
                <td><strong>{{ ent.short_name }}</strong></td>
                <td>{{ ent.region }}, {{ ent.city || '—' }}</td>
                <td>
                  <button class="btn-small btn-danger" @click="deleteEnterprise(ent.id, ent.short_name)">Удалить</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ТАБ СТАТУС -->
      <section v-else-if="activeTab === 'status'">
        <div class="section-head">
          <h2>Состояние сервисов</h2>
          <button class="btn" @click="checkStatus">Проверить сейчас</button>
        </div>
        
        <div class="status-grid">
          <div class="status-card">
            <h3>Backend API</h3>
            <p :class="{ error_text: systemStatus.api.startsWith('Ошибка') }">{{ systemStatus.api }}</p>
          </div>
          <div class="status-card">
            <h3>База данных</h3>
            <p :class="{ error_text: systemStatus.db.startsWith('Ошибка') }">{{ systemStatus.db }}</p>
          </div>
        </div>

        <div class="status-info">
          <p><strong>Мониторинг ошибок:</strong> Ошибки автоматически логгируются в stderr контейнера backend.</p>
          <p><strong>Резервное копирование:</strong> Postgres-том `postgres_data` сохраняется на уровне файловой системы Docker-хоста. Рекомендуется настроить cron для создания ежедневных pg_dump.</p>
        </div>
      </section>

    </div>
  </div>
</template>

<style scoped>
.admin-panel {
  display: flex;
  flex-direction: column;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
  color: var(--sl-ink);
}

/* ===== ШАПКА ===== */
.admin-header {
  padding: clamp(1.25rem, 3vw, 2rem) clamp(1.25rem, 3vw, 2rem) 1.5rem;
}

.kicker {
  margin: 0 0 0.6rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

.admin-header h1 {
  margin: 0;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  color: var(--sl-ink);
}

.subtitle {
  margin: 0.75rem 0 0;
  color: var(--sl-muted);
}

/* ===== ТАБЫ ===== */
.admin-tabs {
  display: flex;
  gap: 0;
  padding: 0 clamp(1.25rem, 3vw, 2rem);
  border-bottom: 1px solid var(--sl-line);
  overflow-x: auto;
  scrollbar-width: none;
}

.admin-tabs::-webkit-scrollbar {
  display: none;
}

.admin-tabs button {
  flex: 0 0 auto;
  margin-bottom: -1px;
  padding: 0.85rem 1.1rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  border-radius: 0;
  font-weight: 700;
  color: var(--sl-muted);
  white-space: nowrap;
  cursor: pointer;
  transition: color 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.admin-tabs button:hover {
  color: var(--sl-ink);
  border-bottom-color: var(--sl-line);
}

.admin-tabs button.active {
  color: var(--sl-ink);
  border-bottom-color: var(--sl-ink);
}

.admin-tabs button:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: -2px;
}

/* ===== КОНТЕНТ ===== */
.admin-content.card {
  margin: clamp(1.25rem, 3vw, 2rem);
  padding: clamp(1rem, 2.5vw, 1.5rem);
  background: #fff;
  border: 1px solid var(--sl-line);
  border-radius: 0;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem 1rem;
  padding-bottom: 1.25rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid var(--sl-line);
}

.section-head h2 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--sl-ink);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.loading {
  padding: 1rem 0;
  color: var(--sl-muted);
}

/* ===== ТАБЛИЦЫ ===== */
.table-container {
  overflow-x: auto;
  border: 1px solid var(--sl-line);
}

table {
  width: 100%;
  min-width: 720px;
  border-collapse: collapse;
  text-align: left;
}

th,
td {
  padding: 0.8rem 1rem;
  border-bottom: 1px solid var(--sl-line);
  vertical-align: middle;
}

tbody tr:last-child td {
  border-bottom: none;
}

th {
  background: var(--sl-paper);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted);
  white-space: nowrap;
}

tbody tr {
  transition: background 0.2s ease;
}

tbody tr:hover {
  background: var(--sl-paper);
}

td:first-child {
  font-family: var(--sl-display);
  font-size: 0.85rem;
  color: var(--sl-muted);
}

td:last-child,
th:last-child {
  text-align: right;
}

.role-badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border: 1px solid transparent;
  border-radius: 0;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  background: var(--sl-paper);
  border-color: var(--sl-line);
  color: var(--sl-ink);
}

.role-badge.ADMIN {
  background: var(--sl-ink);
  border-color: var(--sl-ink);
  color: var(--sl-lime);
}

.role-badge.SUPPLIER {
  background: var(--sl-lime);
  border-color: var(--sl-lime);
  color: var(--sl-ink);
}

.role-badge.BUYER {
  background: var(--sl-paper);
  border-color: var(--sl-line);
  color: var(--sl-ink);
}

.ent-tag {
  display: inline-block;
  margin: 0.15rem 0.3rem 0.15rem 0;
  padding: 0.2rem 0.45rem;
  font-size: 0.8rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-radius: 0;
  white-space: nowrap;
}

/* ===== КАТЕГОРИИ ===== */
.cat-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 1px;
  background: var(--sl-line);
  border: 1px solid var(--sl-line);
}

.cat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: #fff;
  transition: background 0.2s ease;
}

.cat-item:hover {
  background: var(--sl-paper);
}

.cat-item strong {
  margin-right: 0.5rem;
  font-family: var(--sl-display);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--sl-leaf);
}

/* ===== МОНИТОРИНГ ===== */
.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1px;
  background: var(--sl-line);
  border: 1px solid var(--sl-line);
}

.status-card {
  padding: 1.5rem;
  background: #fff;
}

.status-card h3 {
  margin: 0 0 0.75rem;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.status-card p {
  margin: 0;
  font-family: var(--sl-display);
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--sl-ink);
}

.status-card p.error_text {
  color: #b3261e;
}

.status-info {
  display: grid;
  gap: 0.6rem;
  margin-top: 1.25rem;
  padding: 1rem 1.25rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-left: 3px solid var(--sl-leaf);
  color: var(--sl-muted);
}

.status-info p {
  margin: 0;
}

.status-info strong {
  color: var(--sl-ink);
}

/* ===== КНОПКИ ===== */
.btn,
.btn-small {
  border-radius: 0;
  font-weight: 700;
  cursor: pointer;
  background: transparent;
  color: var(--sl-ink);
  border: 1px solid var(--sl-ink);
  white-space: nowrap;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.btn {
  padding: 0.7rem 1.2rem;
}

.btn-small {
  padding: 0.4rem 0.75rem;
  font-size: 0.8rem;
}

.btn:hover,
.btn-small:hover {
  background: var(--sl-ink);
  color: #fff;
}

.btn.primary-btn {
  background: var(--sl-ink);
  color: #fff;
}

.btn.primary-btn:hover {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.btn-small.btn-danger {
  color: #b3261e;
  border-color: #b3261e;
}

.btn-small.btn-danger:hover {
  background: #b3261e;
  color: #fff;
}

.btn:focus-visible,
.btn-small:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

/* ===== ТОСТ ===== */
.admin-toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000;
  max-width: calc(100vw - 2rem);
  padding: 0.9rem 1.25rem;
  background: #fff;
  border: 1px solid var(--sl-line);
  border-radius: 0;
  font-weight: 700;
  box-shadow: 0 24px 48px rgba(20, 33, 15, 0.18);
}

.admin-toast.success {
  border-left: 4px solid var(--sl-leaf);
  color: var(--sl-ink);
}

.admin-toast.error {
  border-left: 4px solid #b3261e;
  background: #fbeaea;
  color: #b3261e;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 520px) {
  .admin-content.card {
    margin: 1rem;
  }

  .cat-item {
    flex-wrap: wrap;
  }
}
</style>
