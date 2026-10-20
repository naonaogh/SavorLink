<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useShopStore } from '@/stores/shopStore'
import { useAuthStore } from '@/stores/authStore'
import api from '@/services/apiClient'
import { AddIcon, CloseIcon, DeleteIcon, DocumentIcon } from '@/assets/icons/png'

const router = useRouter()
const shopStore = useShopStore()
const authStore = useAuthStore()

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

onMounted(async () => {
  if (authStore.user?.role !== 'SUPPLIER') {
    router.push('/')
    return
  }
  await shopStore.fetchMyProducts()
  await fetchCategories()
})

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

const openCreateModal = () => {
  isEditing.value = false
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
  currentProduct.value = { ...product, category_id: product.category?.id || product.category_id }
  showModal.value = true
}

const handleSave = async () => {
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
    // Обновляем список товаров
    await shopStore.fetchMyProducts()
  } catch (err) {
    // Ошибка уже в сторе
    console.error(err)
  }
}

const handleDelete = async (id: number) => {
  if (confirm('Вы уверены, что хотите удалить этот товар?')) {
    await shopStore.deleteProduct(id)
  }
}

</script>

<template>
  <div class="my-products-page">
    <div class="main-content">
      <div class="content-header">
        <div class="header-text">
          <p class="page-kicker">Кабинет · Мои товары</p>
          <h1 class="title">Управление товарами</h1>
        </div>
        <button @click="openCreateModal" class="btn-add">
          <img :src="AddIcon" alt="" class="btn-icon" aria-hidden="true" />
          Добавить товар
        </button>
      </div>

      <div v-if="isLoading && products.length === 0" class="status-msg">
        Загрузка ваших товаров...
      </div>
      <div v-else-if="error" class="status-msg error">
        {{ error }}
      </div>
      <div v-else-if="products.length === 0" class="empty-state">
        <div class="empty-icon">
          <img :src="DocumentIcon" alt="" class="empty-icon-img" aria-hidden="true" />
        </div>
        <p>У вас пока нет товаров. Самое время создать первый!</p>
        <button @click="openCreateModal" class="btn-add-large">Создать товар</button>
      </div>

      <div v-else class="products-grid">
        <div v-for="product in products" :key="product.id" class="product-card">
          <div class="card-image">
            <img :src="DocumentIcon" alt="" class="card-icon" aria-hidden="true" />
            <span class="card-cat" v-if="product.category">{{ product.category.name }}</span>
          </div>
          <div class="card-info">
            <h3 class="product-name">{{ product.name }}</h3>
            <p class="product-desc">{{ product.description || 'Описание не добавлено' }}</p>
            <div class="product-meta">
              <span class="price">{{ product.price }} ₽/кг</span>
              <span class="stock">На складе: {{ product.quantity_in_stock ?? 0 }} кг</span>
            </div>
            <p class="min-order" v-if="product.min_order_qty">Мин. заказ: {{ product.min_order_qty }} кг</p>
          </div>
          <div class="card-actions">
            <button @click="openEditModal(product)" class="btn-edit">Изменить</button>
            <button @click="handleDelete(product.id)" class="btn-delete">Удалить</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Form -->
    <Transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
          <button type="button" class="modal-close" aria-label="Закрыть" @click="showModal = false">
            <img :src="CloseIcon" alt="" class="close-icon" aria-hidden="true" />
          </button>
          <p class="modal-kicker">Карточка товара</p>
          <h2 class="modal-title">{{ isEditing ? 'Редактировать товар' : 'Новый товар' }}</h2>
          <form @submit.prevent="handleSave" class="product-form">
            <div class="form-group">
              <label>Название *</label>
              <input v-model="currentProduct.name" type="text" required placeholder="Например: Помидоры Черри" />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Категория *</label>
                <select v-model="currentProduct.category_id" required>
                  <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                    {{ cat.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Цена (₽/кг) *</label>
                <input v-model.number="currentProduct.price" type="number" step="0.01" min="0.01" required />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Мин. заказ (кг)</label>
                <input v-model.number="currentProduct.min_order_qty" type="number" min="0" />
              </div>
              <div class="form-group">
                <label>В наличии (кг)</label>
                <input v-model.number="currentProduct.quantity_in_stock" type="number" min="0" />
              </div>
            </div>

            <div class="form-group">
              <label>Описание</label>
              <textarea v-model="currentProduct.description" rows="4" placeholder="Расскажите о качестве, происхождении и особенностях товара..."></textarea>
            </div>

            <div v-if="error" class="form-error">{{ error }}</div>

            <div class="modal-actions">
              <button type="button" @click="showModal = false" class="btn-cancel">Отмена</button>
              <button type="submit" class="btn-submit" :disabled="isLoading">
                {{ isLoading ? 'Сохранение...' : (isEditing ? 'Обновить' : 'Создать') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* ===== ПАНЕЛЬ СТРАНИЦЫ ===== */
.my-products-page {
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
  color: var(--sl-ink);
}

.main-content {
  padding: clamp(1.1rem, 3vw, 2rem);
}

/* ===== ШАПКА ===== */
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 1.25rem 2rem;
  padding-bottom: 1.5rem;
  margin-bottom: 1.75rem;
  border-bottom: 1px solid var(--sl-line);
}

.header-text {
  min-width: 0;
}

.page-kicker,
.modal-kicker {
  margin: 0 0 0.75rem;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

.title {
  margin: 0;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  color: var(--sl-ink);
  overflow-wrap: anywhere;
}

/* ===== КНОПКИ ===== */
.btn-add,
.btn-add-large,
.btn-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  min-height: 44px;
  padding: 0.7rem 1.2rem;
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
  border-radius: 0;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.btn-add:hover,
.btn-add-large:hover,
.btn-submit:hover:not(:disabled) {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.btn-add-large {
  margin-top: 1.5rem;
  padding: 0.85rem 1.6rem;
}

.btn-icon {
  display: block;
  width: 16px;
  height: 16px;
  object-fit: contain;
  filter: grayscale(1) brightness(0) invert(1);
}

.btn-edit {
  flex: 1 1 auto;
  min-height: 42px;
  padding: 0.6rem 1rem;
  background: transparent;
  color: var(--sl-ink);
  border: 1px solid var(--sl-ink);
  border-radius: 0;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.btn-edit:hover {
  background: var(--sl-ink);
  color: #fff;
}

.btn-delete {
  flex: 0 0 auto;
  min-height: 42px;
  padding: 0.6rem 1rem;
  background: transparent;
  color: #b3261e;
  border: 1px solid #b3261e;
  border-radius: 0;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.btn-delete:hover {
  background: #b3261e;
  color: #fff;
}

.btn-cancel {
  padding: 0.7rem 0.25rem;
  background: none;
  border: none;
  border-bottom: 1px solid transparent;
  border-radius: 0;
  color: var(--sl-muted);
  font-weight: 700;
  cursor: pointer;
  transition: color 0.2s ease, border-color 0.2s ease;
}

.btn-cancel:hover {
  color: var(--sl-ink);
  border-bottom-color: var(--sl-ink);
}

.btn-submit:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-add:focus-visible,
.btn-add-large:focus-visible,
.btn-edit:focus-visible,
.btn-delete:focus-visible,
.btn-submit:focus-visible,
.btn-cancel:focus-visible,
.modal-close:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

/* ===== СЕТКА ТОВАРОВ ===== */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 260px), 1fr));
  gap: 1rem;
}

.product-card {
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #fff;
  border: 1px solid var(--sl-line);
  transition: border-color 0.2s ease;
}

.product-card:hover {
  border-color: rgba(20, 33, 15, 0.4);
}

.card-image {
  position: relative;
  height: 112px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--sl-paper);
  border-bottom: 1px solid var(--sl-line);
}

.card-icon {
  display: block;
  width: 34px;
  height: 34px;
  object-fit: contain;
  filter: grayscale(1) brightness(0.35);
  opacity: 0.55;
}

.card-cat {
  position: absolute;
  left: 0.75rem;
  top: 0.75rem;
  max-width: calc(100% - 1.5rem);
  padding: 0.2rem 0.5rem;
  background: var(--sl-ink);
  color: var(--sl-lime);
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1.1rem 1.15rem 1rem;
}

.product-name {
  margin: 0 0 0.4rem;
  font-size: 1.05rem;
  font-weight: 800;
  line-height: 1.3;
  color: var(--sl-ink);
  overflow-wrap: anywhere;
}

.product-desc {
  margin: 0 0 1rem;
  font-size: 0.86rem;
  line-height: 1.45;
  color: var(--sl-muted);
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.35rem 0.75rem;
  margin-top: auto;
  padding-top: 0.85rem;
  border-top: 1px solid var(--sl-line);
}

.price {
  font-family: var(--sl-display);
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--sl-ink);
  white-space: nowrap;
}

.stock {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--sl-muted);
}

.min-order {
  margin: 0.4rem 0 0;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  padding: 0.9rem 1.15rem 1.15rem;
}

/* ===== ПУСТО / ЗАГРУЗКА / ОШИБКА ===== */
.empty-state {
  padding: clamp(2.5rem, 6vw, 4rem) clamp(1.25rem, 4vw, 2rem);
  text-align: center;
  background: #fff;
  border: 1px solid var(--sl-line);
}

.empty-state p {
  max-width: 420px;
  margin: 0 auto;
  color: var(--sl-muted);
}

.empty-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  margin-bottom: 1.25rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
}

.empty-icon-img {
  display: block;
  width: 32px;
  height: 32px;
  object-fit: contain;
  filter: grayscale(1) brightness(0.35);
}

.status-msg {
  padding: 3rem 1rem;
  text-align: center;
  background: #fff;
  border: 1px solid var(--sl-line);
  color: var(--sl-muted);
  font-weight: 600;
}

.status-msg.error {
  background: #fbeaea;
  border-color: #b3261e;
  color: #b3261e;
}

/* ===== МОДАЛКА ===== */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(20, 33, 15, 0.55);
}

.modal-content {
  position: relative;
  width: 100%;
  max-width: 560px;
  max-height: calc(100vh - 3rem);
  overflow-y: auto;
  padding: 2rem 2rem 1.75rem;
  background: #fff;
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
  border-radius: 0;
  box-shadow: 0 24px 48px rgba(20, 33, 15, 0.18);
  color: var(--sl-ink);
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: #fff;
  border: 1px solid var(--sl-line);
  border-radius: 0;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.close-icon {
  display: block;
  width: 16px;
  height: 16px;
  object-fit: contain;
  filter: grayscale(1) brightness(0.35);
  transition: filter 0.2s ease;
}

.modal-close:hover {
  background: var(--sl-ink);
  border-color: var(--sl-ink);
}

.modal-close:hover .close-icon {
  filter: grayscale(1) brightness(0) invert(1);
}

.modal-kicker {
  padding-right: 3rem;
}

.modal-title {
  margin: 0 0 1.5rem;
  padding-right: 3rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--sl-line);
  font-size: clamp(1.25rem, 2.6vw, 1.6rem);
  color: var(--sl-ink);
}

/* ===== ФОРМА ===== */
.product-form {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  min-width: 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 1rem;
}

label {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

input,
select,
textarea {
  width: 100%;
  min-width: 0;
  padding: 0.75rem 0.9rem;
  background: #fff;
  border: 1px solid var(--sl-line);
  border-radius: 0;
  font-size: 1rem;
  color: var(--sl-ink);
  transition: border-color 0.2s ease;
}

input::placeholder,
textarea::placeholder {
  color: rgba(92, 111, 87, 0.7);
}

input:hover,
select:hover,
textarea:hover {
  border-color: rgba(20, 33, 15, 0.4);
}

input:focus,
select:focus,
textarea:focus {
  outline: 2px solid var(--sl-leaf);
  outline-offset: -1px;
  border-color: var(--sl-leaf);
}

textarea {
  min-height: 120px;
  resize: vertical;
}

.form-error {
  padding: 0.85rem 1rem;
  background: #fbeaea;
  border-left: 3px solid #b3261e;
  color: #b3261e;
  font-size: 0.9rem;
  font-weight: 700;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 1.25rem;
  margin-top: 0.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--sl-line);
}

.btn-submit {
  min-width: 160px;
}

/* ===== АНИМАЦИЯ ===== */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.25s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: translateY(12px);
}

@media (prefers-reduced-motion: reduce) {
  .modal-enter-active,
  .modal-leave-active,
  .modal-enter-active .modal-content,
  .modal-leave-active .modal-content {
    transition: none;
  }
}

/* ===== АДАПТИВ ===== */
@media (max-width: 560px) {
  .btn-add {
    width: 100%;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .modal-overlay {
    padding: 0.75rem;
    align-items: flex-start;
  }

  .modal-content {
    max-height: calc(100vh - 1.5rem);
    padding: 1.5rem 1.15rem 1.25rem;
  }

  .modal-actions {
    flex-direction: column-reverse;
    align-items: stretch;
    gap: 0.5rem;
  }

  .btn-submit {
    width: 100%;
  }

  .btn-cancel {
    text-align: center;
  }
}
</style>
