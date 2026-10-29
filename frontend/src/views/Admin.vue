<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api, { getApiErrorMessage } from '@/services/apiClient'
import {
  AppBadge,
  AppButton,
  AppIcon,
  AppModal,
  AppSection,
  AppTabs,
  EmptyState,
  FormField,
  LoadingState,
  PageHeader,
} from '@/components/ui'
import type { TabItem } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { formatNumber, pluralize } from '@/utils/format'

type AdminTab = 'users' | 'categories' | 'enterprises' | 'status'

const toast = useToast()
const { confirm } = useConfirm()

const activeTab = ref<AdminTab>('users')

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
  } catch {
    toast.error('Ошибка загрузки пользователей')
  } finally {
    loadingUsers.value = false
  }
}

const updateRole = async (userId: number, currentRole: string, newRole: string) => {
  if (!newRole || newRole === currentRole) return
  if (!['ADMIN', 'BUYER', 'SUPPLIER'].includes(newRole)) {
    toast.error('Неверная роль')
    return
  }
  try {
    await api.patch(`/users/${userId}/role`, { role: newRole })
    toast.success('Роль обновлена')
    loadUsers()
  } catch {
    toast.error('Ошибка изменения роли')
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
  } catch {
    toast.error('Ошибка загрузки категорий')
  } finally {
    loadingCategories.value = false
  }
}

const createCategory = async (name: string) => {
  if (!name) return
  try {
    await api.post('/products/categories', { name })
    toast.success('Категория создана')
    loadCategories()
  } catch {
    toast.error('Ошибка создания категории')
  }
}

const editCategory = async (catId: number, currentName: string, name: string) => {
  if (!name || name === currentName) return
  try {
    await api.patch(`/products/categories/${catId}`, { name })
    toast.success('Категория обновлена')
    loadCategories()
  } catch {
    toast.error('Ошибка обновления категории')
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
  } catch {
    toast.error('Ошибка загрузки предприятий')
  } finally {
    loadingEnterprises.value = false
  }
}

const deletingId = ref<number | null>(null)

const deleteEnterprise = async (id: number, name: string) => {
  const ok = await confirm({
    title: `Удалить предприятие «${name}»?`,
    message: 'Это также удалит все его товары и заказы! Действие нельзя отменить.',
    confirmLabel: 'Удалить',
    tone: 'danger',
  })
  if (!ok) return
  deletingId.value = id
  try {
    await api.delete(`/enterprises/${id}`)
    toast.success('Предприятие удалено')
    loadEnterprises()
  } catch (e) {
    toast.error('Ошибка удаления', getApiErrorMessage(e, 'Попробуйте ещё раз'))
  } finally {
    deletingId.value = null
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
  } catch {
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

/* ── Отображение ───────────────────────────────── */
const ROLE_OPTIONS = [
  { value: 'BUYER', label: 'Покупатель', tone: 'accent' as const },
  { value: 'SUPPLIER', label: 'Поставщик', tone: 'brand' as const },
  { value: 'ADMIN', label: 'Администратор', tone: 'info' as const },
]

const roleMeta = (role: string) =>
  ROLE_OPTIONS.find((r) => r.value === role) ?? { value: role, label: role || '—', tone: 'neutral' as const }

const tabs = computed<TabItem<AdminTab>[]>(() => [
  { value: 'users', label: 'Пользователи', icon: 'users', count: users.value.length },
  { value: 'categories', label: 'Категории', icon: 'tag', count: categories.value.length },
  { value: 'enterprises', label: 'Предприятия', icon: 'building', count: enterprises.value.length },
  { value: 'status', label: 'Мониторинг', icon: 'bar-chart' },
])

const statusTone = (value: string) =>
  value.startsWith('Ошибка') ? 'danger' : value.startsWith('ОК') ? 'success' : 'neutral'

const statusLabel = (value: string) =>
  value.startsWith('Ошибка') ? 'Недоступно' : value.startsWith('ОК') ? 'Работает' : 'Проверка'

const checkingStatus = computed(() => systemStatus.value.api === 'Проверка...')

/* модалка смены роли */
const roleModalOpen = ref(false)
const roleTarget = ref<{ id: number; email: string; role: string } | null>(null)
const roleValue = ref('')
const savingRole = ref(false)

const openRoleModal = (u: { id: number; email: string; role: string }) => {
  roleTarget.value = { id: u.id, email: u.email, role: u.role }
  roleValue.value = u.role
  roleModalOpen.value = true
}

const submitRole = async () => {
  if (!roleTarget.value) return
  savingRole.value = true
  await updateRole(roleTarget.value.id, roleTarget.value.role, roleValue.value)
  savingRole.value = false
  roleModalOpen.value = false
}

/* модалка категории (создание / переименование) */
const categoryModalOpen = ref(false)
const categoryTarget = ref<{ id: number; name: string } | null>(null)
const categoryName = ref('')
const savingCategory = ref(false)

const openCreateCategory = () => {
  categoryTarget.value = null
  categoryName.value = ''
  categoryModalOpen.value = true
}

const openEditCategory = (cat: { id: number; name: string }) => {
  categoryTarget.value = { id: cat.id, name: cat.name }
  categoryName.value = cat.name
  categoryModalOpen.value = true
}

const submitCategory = async () => {
  const name = categoryName.value.trim()
  savingCategory.value = true
  if (categoryTarget.value) {
    await editCategory(categoryTarget.value.id, categoryTarget.value.name, name)
  } else {
    await createCategory(name)
  }
  savingCategory.value = false
  categoryModalOpen.value = false
}
</script>

<template>
  <div class="admin">
    <PageHeader
      eyebrow="Администрирование"
      title="Панель администратора"
      description="Управление пользователями, справочниками и мониторинг"
    />

    <AppTabs v-model="activeTab" :items="tabs" variant="underline" aria-label="Разделы администрирования" />

    <!-- ТАБ ПОЛЬЗОВАТЕЛИ -->
    <AppSection
      v-if="activeTab === 'users'"
      :title="`Управление пользователями (${formatNumber(users.length)})`"
      description="Роли и привязка к предприятиям"
      flush
    >
      <template #actions>
        <AppButton variant="secondary" size="sm" icon="refresh" :loading="loadingUsers" @click="loadUsers">
          Обновить
        </AppButton>
      </template>

      <LoadingState v-if="loadingUsers && users.length === 0" variant="skeleton" :rows="5" />
      <div v-else-if="users.length === 0" class="admin__empty">
        <EmptyState compact icon="users" title="Пользователей нет" />
      </div>
      <div v-else class="ui-table-wrap admin__table-wrap">
        <table class="ui-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Email</th>
              <th>Роль</th>
              <th>Предприятия</th>
              <th class="admin__th-actions">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td class="ui-num admin__id">{{ u.id }}</td>
              <td class="admin__strong">{{ u.email }}</td>
              <td>
                <AppBadge :tone="roleMeta(u.role).tone" size="sm">{{ roleMeta(u.role).label }}</AppBadge>
              </td>
              <td>
                <div v-if="u.enterprises?.length" class="admin__tags">
                  <span v-for="ent in u.enterprises" :key="ent.id" class="admin__tag">
                    {{ ent.short_name }} <span class="ui-num ui-muted">#{{ ent.id }}</span>
                  </span>
                </div>
                <span v-else class="ui-muted">—</span>
              </td>
              <td class="admin__td-actions">
                <AppButton variant="secondary" size="sm" icon="shield" @click="openRoleModal(u)">
                  Сменить роль
                </AppButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </AppSection>

    <!-- ТАБ КАТЕГОРИИ -->
    <AppSection
      v-else-if="activeTab === 'categories'"
      title="Управление справочниками"
      description="Категории товаров в каталоге"
      flush
    >
      <template #actions>
        <AppButton variant="secondary" size="sm" icon="refresh" :loading="loadingCategories" @click="loadCategories">
          Обновить
        </AppButton>
        <AppButton size="sm" icon="plus" @click="openCreateCategory">Создать категорию</AppButton>
      </template>

      <LoadingState v-if="loadingCategories && categories.length === 0" variant="skeleton" :rows="5" />
      <div v-else-if="categories.length === 0" class="admin__empty">
        <EmptyState compact icon="tag" title="Категорий пока нет" description="Создайте первую категорию товаров.">
          <AppButton size="sm" icon="plus" @click="openCreateCategory">Создать категорию</AppButton>
        </EmptyState>
      </div>
      <div v-else class="ui-table-wrap admin__table-wrap">
        <table class="ui-table admin__table--narrow">
          <thead>
            <tr>
              <th>ID</th>
              <th>Название</th>
              <th class="admin__th-actions">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cat in categories" :key="cat.id">
              <td class="ui-num admin__id">{{ cat.id }}</td>
              <td class="admin__strong">{{ cat.name }}</td>
              <td class="admin__td-actions">
                <AppButton variant="ghost" size="sm" icon="pencil" @click="openEditCategory(cat)">
                  Редактировать
                </AppButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </AppSection>

    <!-- ТАБ ПРЕДПРИЯТИЯ -->
    <AppSection
      v-else-if="activeTab === 'enterprises'"
      title="Управление предприятиями"
      :description="`${formatNumber(enterprises.length)} ${pluralize(enterprises.length, ['предприятие', 'предприятия', 'предприятий'])} на платформе`"
      flush
    >
      <template #actions>
        <AppButton variant="secondary" size="sm" icon="refresh" :loading="loadingEnterprises" @click="loadEnterprises">
          Обновить
        </AppButton>
      </template>

      <LoadingState v-if="loadingEnterprises && enterprises.length === 0" variant="skeleton" :rows="5" />
      <div v-else-if="enterprises.length === 0" class="admin__empty">
        <EmptyState compact icon="building" title="Предприятий нет" />
      </div>
      <div v-else class="ui-table-wrap admin__table-wrap">
        <table class="ui-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>ИНН</th>
              <th>Название</th>
              <th>Регион</th>
              <th class="admin__th-actions">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ent in enterprises" :key="ent.id">
              <td class="ui-num admin__id">{{ ent.id }}</td>
              <td class="ui-num">{{ ent.inn || '—' }}</td>
              <td class="admin__strong">{{ ent.short_name }}</td>
              <td>{{ ent.region || '—' }}, {{ ent.city || '—' }}</td>
              <td class="admin__td-actions">
                <AppButton
                  variant="danger-ghost"
                  size="sm"
                  icon="trash"
                  :loading="deletingId === ent.id"
                  @click="deleteEnterprise(ent.id, ent.short_name)"
                >
                  Удалить
                </AppButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </AppSection>

    <!-- ТАБ СТАТУС -->
    <template v-else-if="activeTab === 'status'">
      <AppSection title="Состояние сервисов" description="Проверка доступности API и базы данных">
        <template #actions>
          <AppButton variant="secondary" size="sm" icon="refresh" :loading="checkingStatus" @click="checkStatus">
            Проверить сейчас
          </AppButton>
        </template>

        <div class="status-grid">
          <div class="status-card">
            <span class="status-card__icon" :class="`is-${statusTone(systemStatus.api)}`">
              <AppIcon name="trending-up" :size="20" />
            </span>
            <div class="status-card__body">
              <div class="status-card__top">
                <h3 class="status-card__title">Backend API</h3>
                <AppBadge :tone="statusTone(systemStatus.api)" size="sm" dot>{{ statusLabel(systemStatus.api) }}</AppBadge>
              </div>
              <p class="status-card__value ui-num" :class="{ 'is-error': systemStatus.api.startsWith('Ошибка') }">
                {{ systemStatus.api }}
              </p>
            </div>
          </div>
          <div class="status-card">
            <span class="status-card__icon" :class="`is-${statusTone(systemStatus.db)}`">
              <AppIcon name="clipboard-list" :size="20" />
            </span>
            <div class="status-card__body">
              <div class="status-card__top">
                <h3 class="status-card__title">База данных</h3>
                <AppBadge :tone="statusTone(systemStatus.db)" size="sm" dot>{{ statusLabel(systemStatus.db) }}</AppBadge>
              </div>
              <p class="status-card__value" :class="{ 'is-error': systemStatus.db.startsWith('Ошибка') }">
                {{ systemStatus.db }}
              </p>
            </div>
          </div>
        </div>
      </AppSection>

      <AppSection title="Эксплуатация">
        <ul class="ops">
          <li class="ops__item">
            <AppIcon name="alert-circle" :size="18" class="ops__icon" />
            <p>
              <strong>Мониторинг ошибок:</strong> Ошибки автоматически логгируются в stderr контейнера backend.
            </p>
          </li>
          <li class="ops__item">
            <AppIcon name="download" :size="18" class="ops__icon" />
            <p>
              <strong>Резервное копирование:</strong> Postgres-том <code>postgres_data</code> сохраняется на уровне
              файловой системы Docker-хоста. Рекомендуется настроить cron для создания ежедневных pg_dump.
            </p>
          </li>
        </ul>
      </AppSection>
    </template>

    <!-- МОДАЛКА: СМЕНА РОЛИ -->
    <AppModal
      v-model:open="roleModalOpen"
      title="Сменить роль"
      :description="roleTarget ? `Пользователь ${roleTarget.email}` : undefined"
      size="sm"
      :persistent="savingRole"
    >
      <form id="admin-role-form" class="admin__form" @submit.prevent="submitRole">
        <FormField
          label="Роль"
          required
          :hint="roleTarget ? `Текущая роль: ${roleMeta(roleTarget.role).label}` : undefined"
          v-slot="{ id, describedBy, invalid }"
        >
          <select :id="id" v-model="roleValue" required :aria-describedby="describedBy" :aria-invalid="invalid">
            <option v-for="option in ROLE_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }} ({{ option.value }})
            </option>
          </select>
        </FormField>
      </form>
      <template #footer>
        <AppButton variant="ghost" :disabled="savingRole" @click="roleModalOpen = false">Отмена</AppButton>
        <AppButton
          type="submit"
          form="admin-role-form"
          icon="check"
          :loading="savingRole"
          :disabled="!roleTarget || roleValue === roleTarget.role"
        >
          Сохранить роль
        </AppButton>
      </template>
    </AppModal>

    <!-- МОДАЛКА: КАТЕГОРИЯ -->
    <AppModal
      v-model:open="categoryModalOpen"
      :title="categoryTarget ? 'Редактировать категорию' : 'Новая категория'"
      :description="categoryTarget ? `Категория #${categoryTarget.id}` : 'Категория появится в каталоге и фильтрах'"
      size="sm"
      :persistent="savingCategory"
    >
      <form id="admin-category-form" class="admin__form" @submit.prevent="submitCategory">
        <FormField label="Название" required v-slot="{ id, describedBy, invalid }">
          <input
            :id="id"
            v-model="categoryName"
            type="text"
            required
            autocomplete="off"
            placeholder="Например, Молочная продукция"
            :aria-describedby="describedBy"
            :aria-invalid="invalid"
          />
        </FormField>
      </form>
      <template #footer>
        <AppButton variant="ghost" :disabled="savingCategory" @click="categoryModalOpen = false">Отмена</AppButton>
        <AppButton
          type="submit"
          form="admin-category-form"
          :icon="categoryTarget ? 'check' : 'plus'"
          :loading="savingCategory"
          :disabled="!categoryName.trim() || (!!categoryTarget && categoryName.trim() === categoryTarget.name)"
        >
          {{ categoryTarget ? 'Сохранить' : 'Создать' }}
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<style scoped>
.admin {
  display: grid;
  gap: 1.25rem;
  min-width: 0;
}

.admin > :deep(.app-tabs--underline) {
  margin-bottom: -0.25rem;
}

.admin__empty {
  padding: clamp(1.1rem, 2.5vw, 1.5rem);
}

/* таблица внутри секции: без второй рамки */
.admin__table-wrap {
  border: none;
  border-radius: 0 0 var(--r-lg) var(--r-lg);
}

.admin__table-wrap .ui-table {
  min-width: 640px;
}

.admin__table-wrap .admin__table--narrow {
  min-width: 420px;
}

.admin__id {
  width: 4rem;
  color: var(--c-muted);
}

.admin__strong {
  font-weight: 700;
  color: var(--c-text);
  overflow-wrap: anywhere;
}

.admin__th-actions,
.admin__td-actions {
  width: 1%;
  text-align: right;
  white-space: nowrap;
}

.admin__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.admin__tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.15rem 0.55rem;
  border: 1px solid var(--c-border);
  border-radius: var(--r-full);
  background: var(--c-surface-2);
  font-size: var(--fs-xs);
  font-weight: 600;
  white-space: nowrap;
}

.admin__form {
  display: grid;
  gap: 1rem;
}

/* ── Мониторинг ────────────────────────────────── */
.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.status-card {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  padding: 1rem 1.1rem;
  border: 1px solid var(--c-border);
  border-radius: var(--r-md);
  background: var(--c-surface-2);
}

.status-card__icon {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: var(--r-md);
  background: var(--c-surface-sunken);
  color: var(--c-text-2);
}

.status-card__icon.is-success {
  background: var(--c-success-bg);
  color: var(--c-success);
}

.status-card__icon.is-danger {
  background: var(--c-danger-bg);
  color: var(--c-danger);
}

.status-card__body {
  display: grid;
  gap: 0.3rem;
  min-width: 0;
}

.status-card__top {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem 0.6rem;
}

.status-card__title {
  font-size: var(--fs-md);
}

.status-card__value {
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  overflow-wrap: anywhere;
}

.status-card__value.is-error {
  color: var(--c-danger-600);
  font-weight: 600;
}

.ops {
  display: grid;
  gap: 0.85rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.ops__item {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  color: var(--c-text-2);
  font-size: var(--fs-sm);
}

.ops__icon {
  flex-shrink: 0;
  margin-top: 0.15rem;
  color: var(--c-muted);
}

.ops__item strong {
  color: var(--c-text);
}

.ops__item code {
  padding: 0.05rem 0.35rem;
  border-radius: var(--r-xs);
  background: var(--c-surface-sunken);
  font-size: 0.85em;
}
</style>
