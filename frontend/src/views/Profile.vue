<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api, { getApiErrorMessage } from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'
import {
  AppAvatar,
  AppBadge,
  AppButton,
  AppIcon,
  AppSection,
  EmptyState,
  ErrorState,
  FormField,
  LoadingState,
  PageHeader,
} from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { formatDate } from '@/utils/format'

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

const authStore = useAuthStore()
const toast = useToast()

const user = ref<UserProfile | null>(null)
const enterprise = ref<EnterpriseProfile | null>(null)
const loading = ref(true)
const error = ref('')

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

/* ── Отображение ───────────────────────────────── */
const ROLE_META: Record<string, { label: string; tone: 'brand' | 'accent' | 'info' | 'neutral' }> = {
  BUYER: { label: 'Покупатель', tone: 'accent' },
  SUPPLIER: { label: 'Поставщик', tone: 'brand' },
  ADMIN: { label: 'Администратор', tone: 'info' },
}

const roleMeta = computed(() => {
  const role = user.value?.role ?? ''
  return ROLE_META[role] ?? { label: role || '—', tone: 'neutral' as const }
})

const createdAt = computed(() => formatDate(user.value?.created_at, 'long'))

const fullName = computed(() => {
  const name = [user.value?.first_name, user.value?.last_name].filter(Boolean).join(' ')
  return name || user.value?.email || ''
})

const passwordMismatch = computed(
  () =>
    !!accountForm.value.password_confirm && accountForm.value.password !== accountForm.value.password_confirm,
)

/* поиск по уже загруженному списку предприятий */
const joinQuery = ref('')
const joiningId = ref<number | null>(null)

const filteredEnterprises = computed(() => {
  const q = joinQuery.value.trim().toLowerCase()
  if (!q) return joinableEnterprises.value
  return joinableEnterprises.value.filter((ent) =>
    [ent.short_name, ent.inn, ent.region, ent.city].some((v) => (v ?? '').toLowerCase().includes(q)),
  )
})

/* ── Аккаунт ───────────────────────────────────── */
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
    toast.error('Новый пароль и подтверждение не совпадают')
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
      authStore.setAuth(authStore.token, { ...authStore.user, ...res.data })
    }

    isEditingAccount.value = false
    accountForm.value.old_password = ''
    accountForm.value.password = ''
    accountForm.value.password_confirm = ''
    toast.success('Данные аккаунта сохранены')
  } catch (e) {
    toast.error('Не удалось сохранить профиль', getApiErrorMessage(e, 'Ошибка при сохранении профиля'))
  } finally {
    savingAccount.value = false
  }
}

/* ── Предприятие ───────────────────────────────── */
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
    toast.success('Предприятие создано и привязано к аккаунту')
  } catch (e) {
    toast.error('Не удалось создать предприятие', getApiErrorMessage(e, 'Ошибка при создании предприятия'))
  } finally {
    savingEnterprise.value = false
  }
}

const startJoinEnterprise = async () => {
  isJoiningEnterprise.value = true
  loadingEnterprises.value = true
  joinQuery.value = ''
  try {
    const res = await api.get('/enterprises')
    joinableEnterprises.value = res.data
  } catch {
    toast.error('Ошибка при загрузке списка предприятий')
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
    toast.success('Предприятие успешно привязано')
  } catch (e) {
    toast.error('Не удалось присоединиться', getApiErrorMessage(e, 'Ошибка при присоединении к предприятию'))
  } finally {
    savingEnterprise.value = false
  }
}

const onJoin = async (id: number) => {
  joiningId.value = id
  await joinEnterprise(id)
  joiningId.value = null
}

const saveEnterprise = async () => {
  if (!enterprise.value) return
  savingEnterprise.value = true
  try {
    const res = await api.patch(`/enterprises/${enterprise.value.id}`, editForm.value)
    enterprise.value = res.data
    isEditingEnterprise.value = false
    toast.success('Данные предприятия обновлены')
  } catch (e) {
    toast.error('Не удалось сохранить предприятие', getApiErrorMessage(e, 'Ошибка при сохранении предприятия'))
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
  } catch (e) {
    error.value = getApiErrorMessage(e, 'Ошибка загрузки профиля')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<template>
  <div class="profile">
    <PageHeader
      eyebrow="Личный кабинет"
      title="Профиль"
      description="Данные аккаунта и предприятия, от имени которого вы работаете на платформе."
    >
      <template #actions>
        <AppButton variant="secondary" icon="refresh" :loading="loading && !!user" @click="loadProfile">
          Обновить
        </AppButton>
      </template>
    </PageHeader>

    <LoadingState v-if="loading && !user" variant="skeleton" :rows="6" label="Загружаем профиль…" />

    <ErrorState v-else-if="error" :message="error" :retrying="loading" @retry="loadProfile" />

    <div v-else-if="user" class="profile__grid">
      <!-- ===== АККАУНТ ===== -->
      <AppSection title="Аккаунт" description="Контактные данные и вход в систему">
        <template v-if="!isEditingAccount" #actions>
          <AppButton variant="secondary" size="sm" icon="pencil" @click="startEditAccount">Изменить</AppButton>
        </template>

        <form v-if="isEditingAccount" class="form" @submit.prevent="saveAccount">
          <div class="form__row">
            <FormField label="Имя" v-slot="{ id, describedBy, invalid }">
              <input
                :id="id"
                v-model="accountForm.first_name"
                type="text"
                placeholder="Иван"
                autocomplete="given-name"
                :aria-describedby="describedBy"
                :aria-invalid="invalid"
              />
            </FormField>
            <FormField label="Фамилия" v-slot="{ id, describedBy, invalid }">
              <input
                :id="id"
                v-model="accountForm.last_name"
                type="text"
                placeholder="Иванов"
                autocomplete="family-name"
                :aria-describedby="describedBy"
                :aria-invalid="invalid"
              />
            </FormField>
          </div>
          <FormField label="Email" required v-slot="{ id, describedBy, invalid }">
            <input
              :id="id"
              v-model="accountForm.email"
              type="email"
              required
              autocomplete="email"
              :aria-describedby="describedBy"
              :aria-invalid="invalid"
            />
          </FormField>
          <FormField label="Телефон" v-slot="{ id, describedBy, invalid }">
            <input
              :id="id"
              v-model="accountForm.phone"
              type="tel"
              placeholder="+7 (999) 123-45-67"
              autocomplete="tel"
              :aria-describedby="describedBy"
              :aria-invalid="invalid"
            />
          </FormField>

          <fieldset class="form__group">
            <legend class="form__legend">
              <AppIcon name="lock" :size="16" />
              Смена пароля
            </legend>
            <p class="form__note">Заполните, только если хотите сменить пароль.</p>
            <FormField label="Текущий пароль" v-slot="{ id, describedBy, invalid }">
              <input
                :id="id"
                v-model="accountForm.old_password"
                type="password"
                autocomplete="current-password"
                :aria-describedby="describedBy"
                :aria-invalid="invalid"
              />
            </FormField>
            <div class="form__row">
              <FormField label="Новый пароль" v-slot="{ id, describedBy, invalid }">
                <input
                  :id="id"
                  v-model="accountForm.password"
                  type="password"
                  autocomplete="new-password"
                  :aria-describedby="describedBy"
                  :aria-invalid="invalid"
                />
              </FormField>
              <FormField
                label="Подтверждение"
                :error="passwordMismatch ? 'Пароли не совпадают' : undefined"
                v-slot="{ id, describedBy, invalid }"
              >
                <input
                  :id="id"
                  v-model="accountForm.password_confirm"
                  type="password"
                  autocomplete="new-password"
                  :aria-describedby="describedBy"
                  :aria-invalid="invalid"
                />
              </FormField>
            </div>
          </fieldset>

          <div class="form__actions">
            <AppButton variant="ghost" :disabled="savingAccount" @click="cancelEditAccount">Отмена</AppButton>
            <AppButton type="submit" icon="check" :loading="savingAccount">Сохранить</AppButton>
          </div>
        </form>

        <template v-else>
          <div class="identity">
            <AppAvatar :name="fullName" :size="48" />
            <div class="identity__text">
              <p class="identity__name">{{ fullName }}</p>
              <AppBadge :tone="roleMeta.tone" size="sm">{{ roleMeta.label }}</AppBadge>
            </div>
          </div>

          <dl class="facts">
            <div class="facts__row">
              <dt>ID</dt>
              <dd class="ui-num">{{ user.id }}</dd>
            </div>
            <div class="facts__row">
              <dt>Имя</dt>
              <dd>{{ user.first_name || '—' }}</dd>
            </div>
            <div class="facts__row">
              <dt>Фамилия</dt>
              <dd>{{ user.last_name || '—' }}</dd>
            </div>
            <div class="facts__row">
              <dt>Email</dt>
              <dd>{{ user.email || '—' }}</dd>
            </div>
            <div class="facts__row">
              <dt>Телефон</dt>
              <dd class="ui-num">{{ user.phone || '—' }}</dd>
            </div>
            <div class="facts__row">
              <dt>Роль</dt>
              <dd>
                <AppBadge :tone="roleMeta.tone" size="sm">{{ roleMeta.label }}</AppBadge>
              </dd>
            </div>
            <div class="facts__row">
              <dt>Дата регистрации</dt>
              <dd>
                <time :datetime="user.created_at">{{ createdAt }}</time>
              </dd>
            </div>
          </dl>
        </template>
      </AppSection>

      <!-- ===== ПРЕДПРИЯТИЕ ===== -->
      <AppSection
        title="Предприятие"
        :description="
          isJoiningEnterprise
            ? 'Выберите предприятие, к которому хотите присоединиться'
            : isCreatingEnterprise
              ? 'Новая карточка компании'
              : 'Реквизиты компании'
        "
      >
        <template v-if="user.role === 'SUPPLIER' && enterprise && !isEditingEnterprise" #actions>
          <AppButton variant="secondary" size="sm" icon="pencil" @click="startEditEnterprise">Изменить</AppButton>
        </template>

        <!-- предприятие есть -->
        <template v-if="enterprise">
          <form v-if="isEditingEnterprise" class="form" @submit.prevent="saveEnterprise">
            <FormField label="Название" required v-slot="{ id, describedBy, invalid }">
              <input
                :id="id"
                v-model="editForm.short_name"
                type="text"
                required
                :aria-describedby="describedBy"
                :aria-invalid="invalid"
              />
            </FormField>
            <FormField label="ИНН" required v-slot="{ id, describedBy, invalid }">
              <input
                :id="id"
                v-model="editForm.inn"
                type="text"
                inputmode="numeric"
                required
                :aria-describedby="describedBy"
                :aria-invalid="invalid"
              />
            </FormField>
            <div class="form__row">
              <FormField label="Регион" required v-slot="{ id, describedBy, invalid }">
                <input
                  :id="id"
                  v-model="editForm.region"
                  type="text"
                  required
                  :aria-describedby="describedBy"
                  :aria-invalid="invalid"
                />
              </FormField>
              <FormField label="Город" v-slot="{ id, describedBy, invalid }">
                <input
                  :id="id"
                  v-model="editForm.city"
                  type="text"
                  placeholder="Необязательно"
                  :aria-describedby="describedBy"
                  :aria-invalid="invalid"
                />
              </FormField>
            </div>
            <div class="form__row">
              <FormField label="Телефон" v-slot="{ id, describedBy, invalid }">
                <input
                  :id="id"
                  v-model="editForm.phone"
                  type="tel"
                  :aria-describedby="describedBy"
                  :aria-invalid="invalid"
                />
              </FormField>
              <FormField label="Email" v-slot="{ id, describedBy, invalid }">
                <input
                  :id="id"
                  v-model="editForm.email"
                  type="email"
                  :aria-describedby="describedBy"
                  :aria-invalid="invalid"
                />
              </FormField>
            </div>
            <div class="form__actions">
              <AppButton variant="ghost" :disabled="savingEnterprise" @click="isEditingEnterprise = false">
                Отмена
              </AppButton>
              <AppButton type="submit" icon="check" :loading="savingEnterprise">Сохранить</AppButton>
            </div>
          </form>

          <template v-else>
            <div class="identity">
              <AppAvatar :name="enterprise.short_name" :size="48" tone="accent" />
              <div class="identity__text">
                <p class="identity__name">{{ enterprise.short_name }}</p>
                <p class="identity__sub ui-num">ИНН {{ enterprise.inn || '—' }}</p>
              </div>
            </div>

            <dl class="facts">
              <div class="facts__row">
                <dt>Название</dt>
                <dd>{{ enterprise.short_name || '—' }}</dd>
              </div>
              <div class="facts__row">
                <dt>ИНН</dt>
                <dd class="ui-num">{{ enterprise.inn || '—' }}</dd>
              </div>
              <div class="facts__row">
                <dt>Регион</dt>
                <dd>{{ enterprise.region || '—' }}</dd>
              </div>
              <div class="facts__row">
                <dt>Город</dt>
                <dd>{{ enterprise.city || '—' }}</dd>
              </div>
              <div class="facts__row">
                <dt>Телефон</dt>
                <dd class="ui-num">{{ enterprise.phone || '—' }}</dd>
              </div>
              <div class="facts__row">
                <dt>Email</dt>
                <dd>{{ enterprise.email || '—' }}</dd>
              </div>
            </dl>
          </template>
        </template>

        <!-- создание -->
        <form v-else-if="isCreatingEnterprise" class="form" @submit.prevent="createEnterprise">
          <FormField label="Название" required v-slot="{ id, describedBy, invalid }">
            <input
              :id="id"
              v-model="createForm.short_name"
              type="text"
              required
              placeholder="ООО «Ромашка»"
              :aria-describedby="describedBy"
              :aria-invalid="invalid"
            />
          </FormField>
          <FormField label="ИНН" required v-slot="{ id, describedBy, invalid }">
            <input
              :id="id"
              v-model="createForm.inn"
              type="text"
              inputmode="numeric"
              required
              :aria-describedby="describedBy"
              :aria-invalid="invalid"
            />
          </FormField>
          <div class="form__row">
            <FormField label="Регион" required v-slot="{ id, describedBy, invalid }">
              <input
                :id="id"
                v-model="createForm.region"
                type="text"
                required
                :aria-describedby="describedBy"
                :aria-invalid="invalid"
              />
            </FormField>
            <FormField label="Город" v-slot="{ id, describedBy, invalid }">
              <input
                :id="id"
                v-model="createForm.city"
                type="text"
                placeholder="Необязательно"
                :aria-describedby="describedBy"
                :aria-invalid="invalid"
              />
            </FormField>
          </div>
          <div class="form__row">
            <FormField label="Телефон" v-slot="{ id, describedBy, invalid }">
              <input
                :id="id"
                v-model="createForm.phone"
                type="tel"
                :aria-describedby="describedBy"
                :aria-invalid="invalid"
              />
            </FormField>
            <FormField label="Email" v-slot="{ id, describedBy, invalid }">
              <input
                :id="id"
                v-model="createForm.email"
                type="email"
                :aria-describedby="describedBy"
                :aria-invalid="invalid"
              />
            </FormField>
          </div>
          <div class="form__actions">
            <AppButton variant="ghost" :disabled="savingEnterprise" @click="isCreatingEnterprise = false">
              Отмена
            </AppButton>
            <AppButton type="submit" icon="plus" :loading="savingEnterprise">Создать предприятие</AppButton>
          </div>
        </form>

        <!-- присоединение -->
        <div v-else-if="isJoiningEnterprise" class="join">
          <LoadingState v-if="loadingEnterprises" variant="skeleton" :rows="4" label="Загружаем список предприятий…" />

          <template v-else>
            <div v-if="joinableEnterprises.length" class="join__search">
              <AppIcon name="search" :size="18" class="join__search-icon" />
              <label for="join-search" class="sr-only">Поиск предприятия</label>
              <input
                id="join-search"
                v-model="joinQuery"
                type="search"
                placeholder="Название, ИНН или город"
                autocomplete="off"
              />
            </div>
            <p v-if="joinableEnterprises.length" class="join__count ui-muted">
              Найдено: <span class="ui-num">{{ filteredEnterprises.length }}</span>
            </p>

            <ul v-if="filteredEnterprises.length" class="join__list">
              <li v-for="ent in filteredEnterprises" :key="ent.id" class="join__item">
                <AppAvatar :name="ent.short_name" :size="36" tone="neutral" />
                <div class="join__info">
                  <p class="join__name">{{ ent.short_name }}</p>
                  <p class="join__meta">
                    <span class="ui-num">ИНН {{ ent.inn || '—' }}</span>
                    <span v-if="ent.region || ent.city">
                      · {{ [ent.region, ent.city].filter(Boolean).join(', ') }}
                    </span>
                  </p>
                </div>
                <AppButton
                  size="sm"
                  variant="secondary"
                  :loading="joiningId === ent.id"
                  :disabled="savingEnterprise && joiningId !== ent.id"
                  @click="onJoin(ent.id)"
                >
                  Выбрать
                </AppButton>
              </li>
            </ul>

            <EmptyState
              v-else
              compact
              icon="building"
              :title="joinableEnterprises.length ? 'Ничего не найдено' : 'Список предприятий пуст'"
              :description="
                joinableEnterprises.length ? 'Попробуйте изменить запрос.' : 'Вы можете создать своё предприятие.'
              "
            >
              <AppButton v-if="joinQuery" variant="ghost" size="sm" @click="joinQuery = ''">Сбросить поиск</AppButton>
            </EmptyState>
          </template>

          <div class="form__actions form__actions--start">
            <AppButton variant="ghost" icon="arrow-left" @click="isJoiningEnterprise = false">Назад</AppButton>
          </div>
        </div>

        <!-- нет предприятия -->
        <EmptyState
          v-else
          icon="building"
          title="Вы пока не привязаны к предприятию"
          description="Создайте карточку своей компании или присоединитесь к уже зарегистрированной на платформе."
        >
          <AppButton icon="plus" @click="isCreatingEnterprise = true">Создать</AppButton>
          <AppButton variant="secondary" icon="user-plus" @click="startJoinEnterprise">Присоединиться</AppButton>
        </EmptyState>
      </AppSection>
    </div>
  </div>
</template>

<style scoped>
.profile {
  display: grid;
  gap: 1.5rem;
  min-width: 0;
}

.profile__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: start;
  gap: 1.25rem;
}

/* ── Шапка карточки: аватар + имя ─────────────── */
.identity {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding-bottom: 1rem;
  margin-bottom: 0.25rem;
  border-bottom: 1px solid var(--c-border);
}

.identity__text {
  display: grid;
  justify-items: start;
  gap: 0.3rem;
  min-width: 0;
}

.identity__name {
  font-weight: 800;
  font-size: var(--fs-lg);
  line-height: 1.25;
  overflow-wrap: anywhere;
}

.identity__sub {
  color: var(--c-muted);
  font-size: var(--fs-sm);
}

/* ── Список «подпись — значение» ──────────────── */
.facts {
  margin: 0;
}

.facts__row {
  display: grid;
  grid-template-columns: minmax(120px, 0.8fr) minmax(0, 1.2fr);
  align-items: center;
  gap: 0.25rem 1rem;
  padding: 0.7rem 0;
  border-bottom: 1px solid var(--c-border);
}

.facts__row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.facts__row dt {
  color: var(--c-muted);
  font-size: var(--fs-sm);
  font-weight: 600;
}

.facts__row dd {
  margin: 0;
  color: var(--c-text);
  font-weight: 600;
  overflow-wrap: anywhere;
}

/* ── Формы ─────────────────────────────────────── */
.form {
  display: grid;
  gap: 1rem;
}

.form__row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.form__group {
  display: grid;
  gap: 1rem;
  margin: 0;
  padding: 1rem;
  border: 1px solid var(--c-border);
  border-radius: var(--r-md);
  background: var(--c-surface-2);
  min-width: 0;
}

.form__legend {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0 0.35rem;
  font-weight: 700;
  font-size: var(--fs-sm);
  color: var(--c-text-2);
}

.form__note {
  margin-top: -0.5rem;
  color: var(--c-muted);
  font-size: var(--fs-sm);
}

.form__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.6rem;
  padding-top: 1rem;
  border-top: 1px solid var(--c-border);
}

.form__actions--start {
  justify-content: flex-start;
}

/* ── Присоединение ─────────────────────────────── */
.join {
  display: grid;
  gap: 0.85rem;
}

.join__search {
  position: relative;
}

.join__search-icon {
  position: absolute;
  top: 50%;
  left: 0.85rem;
  transform: translateY(-50%);
  color: var(--c-muted);
  pointer-events: none;
}

.join__search input {
  padding-left: 2.6rem;
}

.join__count {
  font-size: var(--fs-sm);
}

.join__list {
  display: grid;
  max-height: 360px;
  margin: 0;
  padding: 0;
  overflow: auto;
  list-style: none;
  border: 1px solid var(--c-border);
  border-radius: var(--r-md);
}

.join__item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0.9rem;
  border-bottom: 1px solid var(--c-border);
  transition: background var(--dur) var(--ease);
}

.join__item:last-child {
  border-bottom: none;
}

.join__item:hover {
  background: var(--c-surface-2);
}

.join__info {
  flex: 1;
  display: grid;
  gap: 0.1rem;
  min-width: 0;
}

.join__name {
  font-weight: 700;
  overflow-wrap: anywhere;
}

.join__meta {
  color: var(--c-muted);
  font-size: var(--fs-sm);
}

@media (max-width: 1024px) {
  .profile__grid {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 520px) {
  .facts__row {
    grid-template-columns: minmax(0, 1fr);
  }

  .form__actions {
    flex-direction: column-reverse;
  }

  .form__actions > * {
    width: 100%;
  }

  .join__item {
    flex-wrap: wrap;
  }

  .join__item > :last-child {
    margin-left: auto;
  }
}
</style>
