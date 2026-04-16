<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useShopStore } from '@/data/shopStore'
import { useAuthStore } from '@/data/authStore'
import CommonNavbar from '@/components/CommonNavbar.vue'
import api from '@/api'

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
    <CommonNavbar />

    <main class="main-content">
      <div class="content-header">
        <h1 class="title">Управление товарами</h1>
        <button @click="openCreateModal" class="btn-add">
          <span class="plus">+</span> Добавить товар
        </button>
      </div>

      <div v-if="isLoading && products.length === 0" class="status-msg">
        Загрузка ваших товаров...
      </div>
      <div v-else-if="error" class="status-msg error">
        {{ error }}
      </div>
      <div v-else-if="products.length === 0" class="empty-state">
        <div class="empty-icon">📦</div>
        <p>У вас пока нет товаров. Самое время создать первый!</p>
        <button @click="openCreateModal" class="btn-add-large">Создать товар</button>
      </div>

      <div v-else class="products-grid">
        <div v-for="product in products" :key="product.id" class="product-card">
          <div class="card-image">
            <span class="card-icon">🌿</span>
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
    </main>

    <!-- Modal Form -->
    <Transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
          <button class="modal-close" @click="showModal = false">×</button>
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
.my-products-page {
  min-height: 100vh;
  background: #ebe2ce;
  color: #2e2a23;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.main-content {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #3f4a2f;
  margin: 0;
}

.btn-add {
  background: #3f4a2f;
  color: #fff;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: transform 0.2s, background 0.2s;
  box-shadow: 0 4px 12px rgba(63, 74, 47, 0.2);
}

.btn-add:hover {
  background: #4a5638;
  transform: translateY(-2px);
}

.plus {
  font-size: 1.2rem;
  line-height: 1;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.product-card {
  background: #f4ead4;
  border: 1px solid #ddc8a3;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  transition: box-shadow 0.2s, transform 0.2s;
}

.product-card:hover {
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.card-image {
  height: 130px;
  background: linear-gradient(135deg, #d4edda, #a8d5b5);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.card-icon {
  font-size: 3rem;
}

.card-cat {
  position: absolute;
  bottom: 0.5rem;
  right: 0.5rem;
  background: rgba(63, 74, 47, 0.85);
  color: #fff;
  font-size: 0.72rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.card-info {
  padding: 1.25rem;
  flex: 1;
}

.product-name {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0 0 0.4rem;
  color: #1f2937;
}

.product-desc {
  font-size: 0.88rem;
  line-height: 1.5;
  color: #4b5563;
  margin-bottom: 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  font-weight: 600;
  margin-bottom: 0.3rem;
}

.price {
  color: #3f4a2f;
  font-size: 1.05rem;
}

.stock {
  color: #a97c50;
  font-size: 0.88rem;
}

.min-order {
  font-size: 0.8rem;
  color: #6b7280;
  margin: 0;
}

.card-actions {
  display: flex;
  gap: 0.6rem;
  padding: 0 1.25rem 1.25rem;
}

.btn-edit {
  flex: 1;
  background: #fff;
  border: 1px solid #3f4a2f;
  color: #3f4a2f;
  padding: 0.6rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.88rem;
  transition: background 0.15s;
}

.btn-edit:hover {
  background: #f0f4ec;
}

.btn-delete {
  padding: 0.6rem 1rem;
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fecaca;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.88rem;
  transition: background 0.15s;
}

.btn-delete:hover {
  background: #fecaca;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(45, 38, 31, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: #fdfaf3;
  width: 100%;
  max-width: 520px;
  border-radius: 24px;
  padding: 2rem;
  box-shadow: 0 20px 50px rgba(0,0,0,0.25);
  position: relative;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1.25rem;
  border: none;
  background: none;
  font-size: 1.75rem;
  cursor: pointer;
  color: #9ca3af;
  line-height: 1;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0 0 1.5rem;
  color: #3f4a2f;
}

.product-form {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

label {
  font-size: 0.83rem;
  font-weight: 700;
  color: #6d6254;
}

input, select, textarea {
  padding: 0.75rem 1rem;
  border: 1px solid #dcd1ba;
  border-radius: 10px;
  background: #fff;
  font-family: inherit;
  font-size: 0.95rem;
  color: #1f2937;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #3f4a2f;
  box-shadow: 0 0 0 3px rgba(63, 74, 47, 0.1);
}

textarea {
  resize: vertical;
  min-height: 90px;
}

.form-error {
  background: #fee2e2;
  color: #dc2626;
  padding: 0.65rem 1rem;
  border-radius: 8px;
  font-size: 0.88rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 0.5rem;
}

.btn-cancel {
  background: transparent;
  border: none;
  color: #6d6254;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.95rem;
}

.btn-submit {
  background: #3f4a2f;
  color: #fff;
  border: none;
  padding: 0.75rem 1.75rem;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  font-size: 0.95rem;
  transition: background 0.2s;
}

.btn-submit:hover:not(:disabled) {
  background: #4a5638;
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Animations */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.25s;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}

.status-msg {
  text-align: center;
  padding: 3rem;
  font-size: 1.1rem;
  color: #4b5563;
}

.status-msg.error {
  color: #dc2626;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(255,255,255,0.4);
  border-radius: 24px;
  border: 2px dashed #dcd1ba;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.btn-add-large {
  margin-top: 1.5rem;
  background: #3f4a2f;
  color: #fff;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  font-size: 1rem;
}
</style>
