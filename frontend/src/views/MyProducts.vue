<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useShopStore, type Product } from '@/stores/shopStore'
import { useAuthStore } from '@/stores/authStore'
import api, { getApiErrorMessage } from '@/services/apiClient'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import {
  AppBadge,
  AppButton,
  AppIcon,
  AppModal,
  AppTabs,
  EmptyState,
  ErrorState,
  FormField,
  LoadingState,
  PageHeader,
  ProductThumb,
} from '@/components/ui'
import type { TabItem } from '@/components/ui'
import type { StatusTone } from '@/utils/orderStatus'
import { formatNumber, formatPrice, pluralize } from '@/utils/format'

const router = useRouter()
const shopStore = useShopStore()
const authStore = useAuthStore()
const toast = useToast()
const { confirm } = useConfirm()

const products = computed(() => shopStore.state.products)
const isLoading = computed(() => shopStore.state.loading)
const error = computed(() => shopStore.state.error)

const showModal = ref(false)
const isEditing = ref(false)
const currentProduct = ref<any>({
  name: '',
  description: '',
  price: 0,
  min_order_qty: 1,
  quantity_in_stock: 0,
  category_id: null as number | null
})

const categories = ref<{ id: number; name: string }[]>([])

/* ── локальное UI-состояние ─────────────────────── */
/** список «моих товаров» загружен (в сторе до этого могут лежать товары каталога) */
const loaded = ref(false)
const loadFailed = ref(false)
const retrying = ref(false)
const saving = ref(false)
const deletingId = ref<number | null>(null)

const search = ref('')
const categoryFilter = ref('')
type ViewMode = 'grid' | 'table'
const viewMode = ref<ViewMode>('grid')
const viewTabs: TabItem<ViewMode>[] = [
  { value: 'grid', label: 'Карточки', icon: 'grid' },
  { value: 'table', label: 'Таблица', icon: 'list' },
]

const loadMyProducts = async () => {
  await shopStore.fetchMyProducts()
  loadFailed.value = !!shopStore.state.error
  loaded.value = true
}

onMounted(async () => {
  if (authStore.user?.role !== 'SUPPLIER') {
    router.push('/')
    return
  }
  await loadMyProducts()
  await fetchCategories()
})

const retryLoad = async () => {
  retrying.value = true
  try {
    await loadMyProducts()
  } finally {
    retrying.value = false
  }
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/products/categories')
    categories.value = res.data
  } catch (err) {
    console.error('Ошибка при получении категорий:', err)
    // Запасной вариант — категории из БД
    categories.value = [
      { id: 1, name: 'Овощи и зелень' },
      { id: 2, name: 'Мясо и птица' },
      { id: 3, name: 'Молочные продукты' },
      { id: 4, name: 'Бакалея' },
      { id: 5, name: 'Напитки' },
    ]
  }
}

/* ── фильтрация уже загруженного списка (только отображение) ── */
const categoryOptions = computed(() => {
  const names = new Set<string>()
  for (const p of products.value) {
    if (p.category?.name) names.add(p.category.name)
  }
  return Array.from(names).sort((a, b) => a.localeCompare(b, 'ru'))
})

const filteredProducts = computed(() => {
  const query = search.value.trim().toLowerCase()
  return products.value.filter((p) => {
    if (categoryFilter.value && p.category?.name !== categoryFilter.value) return false
    if (!query) return true
    return p.name.toLowerCase().includes(query) || (p.description || '').toLowerCase().includes(query)
  })
})

const hasFilters = computed(() => !!search.value.trim() || !!categoryFilter.value)
const resetFilters = () => {
  search.value = ''
  categoryFilter.value = ''
}

/* ── подсказка по остатку — только по реальным полям товара ── */
const stockState = (product: Product): { label: string; tone: StatusTone } | null => {
  const stock = product.quantity_in_stock ?? 0
  if (stock <= 0) return { label: 'Нет в наличии', tone: 'danger' }
  if (product.min_order_qty && stock < product.min_order_qty) return { label: 'Мало — меньше мин. заказа', tone: 'warning' }
  return null
}

/* ── модалка ─────────────────────────────────────── */
type FieldKey = 'name' | 'category_id' | 'price' | 'min_order_qty' | 'quantity_in_stock' | 'description'
const errors = reactive<Partial<Record<FieldKey, string>>>({})
const clearErrors = () => {
  for (const key of Object.keys(errors) as FieldKey[]) delete errors[key]
}

const isNonNegativeInt = (value: unknown) => typeof value === 'number' && Number.isInteger(value) && value >= 0

const validate = () => {
  clearErrors()
  const p = currentProduct.value
  const name = String(p.name ?? '').trim()
  if (!name) errors.name = 'Укажите название товара'
  else if (name.length > 200) errors.name = 'Не длиннее 200 символов'
  if (!p.category_id) errors.category_id = 'Выберите категорию'
  if (typeof p.price !== 'number' || Number.isNaN(p.price) || p.price <= 0) errors.price = 'Цена должна быть больше 0'
  if (!isNonNegativeInt(p.min_order_qty)) errors.min_order_qty = 'Целое число, не меньше 0'
  if (!isNonNegativeInt(p.quantity_in_stock)) errors.quantity_in_stock = 'Целое число, не меньше 0'
  if (String(p.description ?? '').length > 4000) errors.description = 'Не длиннее 4000 символов'
  return Object.keys(errors).length === 0
}

const openCreateModal = () => {
  isEditing.value = false
  clearErrors()
  currentProduct.value = {
    name: '',
    description: '',
    price: 0,
    min_order_qty: 1,
    quantity_in_stock: 0,
    category_id: categories.value[0]?.id || null
  }
  showModal.value = true
}

const openEditModal = (product: any) => {
  isEditing.value = true
  clearErrors()
  currentProduct.value = { ...product, category_id: product.category?.id || product.category_id }
  showModal.value = true
}

const handleSave = async () => {
  if (!validate()) return
  saving.value = true
  const wasEditing = isEditing.value
  try {
    if (isEditing.value) {
      await shopStore.updateProduct(currentProduct.value.id, {
        name: currentProduct.value.name,
        description: currentProduct.value.description,
        price: currentProduct.value.price,
        min_order_qty: currentProduct.value.min_order_qty,
        quantity_in_stock: currentProduct.value.quantity_in_stock,
        category_id: currentProduct.value.category_id,
      })
    } else {
      await shopStore.createProduct({
        name: currentProduct.value.name,
        description: currentProduct.value.description,
        price: currentProduct.value.price,
        min_order_qty: currentProduct.value.min_order_qty,
        quantity_in_stock: currentProduct.value.quantity_in_stock,
        category_id: currentProduct.value.category_id,
      })
    }
    showModal.value = false
    toast.success(wasEditing ? 'Товар обновлён' : 'Товар добавлен')
    // Обновляем список товаров
    await shopStore.fetchMyProducts()
  } catch (err) {
    console.error(err)
    toast.error('Не удалось сохранить товар', getApiErrorMessage(err, error.value || 'Попробуйте ещё раз'))
  } finally {
    saving.value = false
  }
}

const handleDelete = async (id: number) => {
  const product = products.value.find((p) => p.id === id)
  const accepted = await confirm({
    title: 'Удалить товар?',
    message: product ? `«${product.name}» исчезнет из вашего каталога.` : 'Товар исчезнет из вашего каталога.',
    confirmLabel: 'Удалить',
    tone: 'danger',
  })
  if (!accepted) return
  deletingId.value = id
  try {
    await shopStore.deleteProduct(id)
    toast.success('Товар удалён')
  } catch (err) {
    toast.error('Не удалось удалить товар', getApiErrorMessage(err, 'Ошибка при удалении товара'))
  } finally {
    deletingId.value = null
  }
}
</script>

<template>
  <div class="products-page">
    <PageHeader
      eyebrow="Кабинет · Мои товары"
      title="Управление товарами"
      description="Цены, остатки и минимальный заказ по вашему каталогу"
    >
      <template #actions>
        <AppButton icon="plus" @click="openCreateModal">Добавить товар</AppButton>
      </template>
    </PageHeader>

    <LoadingState v-if="!loaded || (isLoading && products.length === 0)" variant="cards" :rows="6" label="Загрузка ваших товаров…" />

    <div v-else-if="loadFailed" class="ui-card">
      <ErrorState
        :message="error || 'Ошибка при загрузке ваших товаров'"
        :retrying="retrying"
        @retry="retryLoad"
      />
    </div>

    <div v-else-if="products.length === 0" class="ui-card">
      <EmptyState
        icon="package"
        title="У вас пока нет товаров"
        description="Добавьте первый товар — покупатели увидят его в каталоге с ценой и остатком."
      >
        <AppButton icon="plus" @click="openCreateModal">Добавить товар</AppButton>
      </EmptyState>
    </div>

    <template v-else>
      <!-- ФИЛЬТРЫ -->
      <div class="toolbar ui-card">
        <label class="toolbar__search">
          <span class="sr-only">Поиск по товарам</span>
          <AppIcon name="search" :size="18" class="toolbar__search-icon" />
          <input v-model="search" type="search" placeholder="Поиск по названию или описанию" />
        </label>
        <label class="toolbar__select">
          <span class="sr-only">Категория</span>
          <select v-model="categoryFilter">
            <option value="">Все категории</option>
            <option v-for="name in categoryOptions" :key="name" :value="name">{{ name }}</option>
          </select>
        </label>
        <AppTabs v-model="viewMode" :items="viewTabs" aria-label="Вид списка" class="toolbar__view" />
      </div>

      <div class="summary">
        <p class="summary__count ui-num" role="status">
          {{ hasFilters ? 'Найдено' : 'Всего' }}: {{ filteredProducts.length }}
          {{ pluralize(filteredProducts.length, ['товар', 'товара', 'товаров']) }}
        </p>
        <AppButton v-if="hasFilters" variant="ghost" size="sm" icon="x" @click="resetFilters">Сбросить</AppButton>
      </div>

      <div v-if="filteredProducts.length === 0" class="ui-card">
        <EmptyState compact icon="search" title="Ничего не найдено" description="Измените запрос или выберите другую категорию.">
          <AppButton variant="secondary" size="sm" @click="resetFilters">Сбросить фильтры</AppButton>
        </EmptyState>
      </div>

      <!-- СЕТКА -->
      <ul v-else-if="viewMode === 'grid'" class="grid">
        <li v-for="product in filteredProducts" :key="product.id" class="card ui-card">
          <div class="card__top">
            <ProductThumb :category="product.category?.name" size="md" />
            <div class="card__titles">
              <h2 class="card__name">{{ product.name }}</h2>
              <AppBadge v-if="product.category" tone="neutral" size="sm">{{ product.category.name }}</AppBadge>
            </div>
          </div>

          <p class="card__desc" :class="{ 'card__desc--empty': !product.description }">
            {{ product.description || 'Описание не добавлено' }}
          </p>

          <div class="card__price">
            <span class="card__price-value ui-num">{{ formatPrice(product.price) }}</span>
            <span class="card__price-unit">/ кг</span>
          </div>

          <dl class="card__facts">
            <div>
              <dt>На складе</dt>
              <dd class="ui-num">{{ formatNumber(product.quantity_in_stock ?? 0) }} кг</dd>
            </div>
            <div v-if="product.min_order_qty">
              <dt>Мин. заказ</dt>
              <dd class="ui-num">{{ formatNumber(product.min_order_qty) }} кг</dd>
            </div>
          </dl>
          <AppBadge
            v-if="stockState(product)"
            :tone="stockState(product)?.tone"
            size="sm"
            icon="alert-circle"
            class="card__stock"
          >
            {{ stockState(product)?.label }}
          </AppBadge>

          <div class="card__actions">
            <AppButton variant="secondary" size="sm" icon="pencil" @click="openEditModal(product)">Изменить</AppButton>
            <AppButton
              variant="danger-ghost"
              size="sm"
              icon="trash"
              :loading="deletingId === product.id"
              @click="handleDelete(product.id)"
            >
              Удалить
            </AppButton>
          </div>
        </li>
      </ul>

      <!-- ТАБЛИЦА -->
      <div v-else class="ui-table-wrap">
        <table class="ui-table products-table">
          <thead>
            <tr>
              <th scope="col">Товар</th>
              <th scope="col">Категория</th>
              <th scope="col" class="num">Цена, ₽/кг</th>
              <th scope="col" class="num">На складе</th>
              <th scope="col" class="num">Мин. заказ</th>
              <th scope="col"><span class="sr-only">Действия</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in filteredProducts" :key="product.id">
              <td>
                <div class="products-table__product">
                  <ProductThumb :category="product.category?.name" size="sm" />
                  <span class="products-table__name">{{ product.name }}</span>
                </div>
              </td>
              <td>{{ product.category?.name || '—' }}</td>
              <td class="num ui-num products-table__price">{{ formatPrice(product.price) }}</td>
              <td class="num">
                <div class="products-table__stock">
                  <span class="ui-num">{{ formatNumber(product.quantity_in_stock ?? 0) }} кг</span>
                  <AppBadge v-if="stockState(product)" :tone="stockState(product)?.tone" size="sm">
                    {{ stockState(product)?.label }}
                  </AppBadge>
                </div>
              </td>
              <td class="num ui-num">{{ product.min_order_qty ? `${formatNumber(product.min_order_qty)} кг` : '—' }}</td>
              <td>
                <div class="products-table__actions">
                  <AppButton
                    variant="secondary"
                    size="sm"
                    icon="pencil"
                    icon-only
                    :label="`Изменить «${product.name}»`"
                    @click="openEditModal(product)"
                  />
                  <AppButton
                    variant="danger-ghost"
                    size="sm"
                    icon="trash"
                    icon-only
                    :label="`Удалить «${product.name}»`"
                    :loading="deletingId === product.id"
                    @click="handleDelete(product.id)"
                  />
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- МОДАЛКА ТОВАРА -->
    <AppModal
      v-model:open="showModal"
      :title="isEditing ? 'Редактировать товар' : 'Новый товар'"
      description="Цена и остатки указываются в килограммах"
      :persistent="saving"
    >
      <form id="product-form" class="form" novalidate @submit.prevent="handleSave">
        <FormField label="Название" required :error="errors.name" v-slot="{ id, describedBy, invalid }">
          <input
            :id="id"
            v-model="currentProduct.name"
            type="text"
            maxlength="200"
            placeholder="Например: Помидоры черри"
            :aria-describedby="describedBy"
            :aria-invalid="invalid"
          />
        </FormField>

        <div class="form__row">
          <FormField label="Категория" required :error="errors.category_id" v-slot="{ id, describedBy, invalid }">
            <select :id="id" v-model="currentProduct.category_id" :aria-describedby="describedBy" :aria-invalid="invalid">
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </FormField>
          <FormField label="Цена, ₽/кг" required :error="errors.price" v-slot="{ id, describedBy, invalid }">
            <input
              :id="id"
              v-model.number="currentProduct.price"
              type="number"
              step="0.01"
              min="0.01"
              inputmode="decimal"
              :aria-describedby="describedBy"
              :aria-invalid="invalid"
            />
          </FormField>
        </div>

        <div class="form__row">
          <FormField label="Мин. заказ, кг" hint="0 — без ограничения" :error="errors.min_order_qty" v-slot="{ id, describedBy, invalid }">
            <input
              :id="id"
              v-model.number="currentProduct.min_order_qty"
              type="number"
              min="0"
              step="1"
              inputmode="numeric"
              :aria-describedby="describedBy"
              :aria-invalid="invalid"
            />
          </FormField>
          <FormField label="В наличии, кг" :error="errors.quantity_in_stock" v-slot="{ id, describedBy, invalid }">
            <input
              :id="id"
              v-model.number="currentProduct.quantity_in_stock"
              type="number"
              min="0"
              step="1"
              inputmode="numeric"
              :aria-describedby="describedBy"
              :aria-invalid="invalid"
            />
          </FormField>
        </div>

        <FormField label="Описание" :error="errors.description" v-slot="{ id, describedBy, invalid }">
          <textarea
            :id="id"
            v-model="currentProduct.description"
            rows="4"
            placeholder="Расскажите о качестве, происхождении и особенностях товара…"
            :aria-describedby="describedBy"
            :aria-invalid="invalid"
          ></textarea>
        </FormField>
      </form>

      <template #footer>
        <AppButton variant="secondary" :disabled="saving" @click="showModal = false">Отмена</AppButton>
        <AppButton type="submit" form="product-form" icon="check" :loading="saving">
          {{ isEditing ? 'Сохранить' : 'Создать' }}
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<style scoped>
.products-page {
  display: grid;
  gap: 1.25rem;
  min-width: 0;
}

/* ===== ФИЛЬТРЫ ===== */
.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
}

.toolbar__search {
  position: relative;
  flex: 1 1 260px;
  min-width: 0;
}

.toolbar__search-icon {
  position: absolute;
  top: 50%;
  left: 0.85rem;
  color: var(--c-muted);
  transform: translateY(-50%);
  pointer-events: none;
}

.toolbar__search input {
  padding-left: 2.6rem;
}

.toolbar__select {
  flex: 0 1 220px;
  min-width: 0;
}

.toolbar__view {
  flex: 0 0 auto;
}

.summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem 1rem;
  min-height: 32px;
  margin-top: -0.5rem;
}

.summary__count {
  color: var(--c-muted);
  font-size: var(--fs-sm);
  font-weight: 600;
}

/* ===== СЕТКА ===== */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 260px), 1fr));
  gap: 1rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.card {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  min-width: 0;
  padding: 1.15rem;
}

.card__top {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  min-width: 0;
}

.card__titles {
  display: grid;
  justify-items: start;
  gap: 0.4rem;
  min-width: 0;
}

.card__name {
  font-size: var(--fs-md);
  font-weight: 800;
  line-height: 1.3;
  letter-spacing: -0.01em;
  overflow-wrap: anywhere;
}

.card__desc {
  display: -webkit-box;
  overflow: hidden;
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
}

.card__desc--empty {
  color: var(--c-muted);
  font-style: italic;
}

.card__price {
  display: flex;
  align-items: baseline;
  gap: 0.3rem;
  margin-top: auto;
}

.card__price-value {
  font-size: var(--fs-xl);
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--c-brand-800);
}

.card__price-unit {
  color: var(--c-muted);
  font-size: var(--fs-sm);
  font-weight: 600;
}

.card__facts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.5rem;
  margin: 0;
  padding: 0.75rem;
  border-radius: var(--r-md);
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
}

.card__facts div {
  display: grid;
  gap: 0.1rem;
  min-width: 0;
}

.card__facts dt {
  color: var(--c-muted);
  font-size: var(--fs-xs);
  font-weight: 600;
}

.card__facts dd {
  margin: 0;
  font-size: var(--fs-sm);
  font-weight: 700;
  color: var(--c-text);
}

.card__stock {
  justify-self: start;
  align-self: flex-start;
}

.card__actions {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--c-border);
}

.card__actions > :deep(*) {
  flex: 1 1 auto;
}

/* ===== ТАБЛИЦА ===== */
.products-table {
  min-width: 760px;
}

.products-table .num {
  text-align: right;
}

.products-table__product {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.products-table__name {
  font-weight: 700;
  color: var(--c-text);
}

.products-table__price {
  font-weight: 800;
  white-space: nowrap;
}

.products-table__stock {
  display: grid;
  justify-items: end;
  gap: 0.3rem;
  white-space: nowrap;
}

.products-table__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.4rem;
}

/* ===== ФОРМА ===== */
.form {
  display: grid;
  gap: 1rem;
}

.form__row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

/* ===== АДАПТИВ ===== */
@media (max-width: 640px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar__search,
  .toolbar__select {
    flex: 1 1 auto;
  }

  .form__row {
    grid-template-columns: 1fr;
  }
}
</style>
