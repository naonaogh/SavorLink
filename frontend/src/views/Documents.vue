<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'

const router = useRouter()
const authStore = useAuthStore()
const store = useShopStore()

const documentType = ref('Счёт')
const selectedOrderId = ref<number | null>(null)

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }

  if (authStore.user?.role === 'SUPPLIER') {
    await store.fetchSupplierOrders()
  } else {
    await store.fetchMyOrders()
  }
})

const orders = computed(() =>
  authStore.user?.role === 'SUPPLIER' ? store.state.supplierOrders : store.state.myOrders,
)

const selectedOrder = computed(() => orders.value.find((order) => order.id === selectedOrderId.value) ?? null)

const previewText = computed(() => {
  if (!selectedOrder.value) return 'Выберите заказ для генерации документа.'

  const lines = [
    `${documentType.value} по заказу #${selectedOrder.value.id}`,
    `Статус: ${selectedOrder.value.status}`,
    `Поставщик: ${selectedOrder.value.seller_enterprise.short_name}`,
    `Покупатель: ${selectedOrder.value.buyer_enterprise?.short_name || 'Не указан'}`,
    `Сумма: ${selectedOrder.value.total_amount ?? 0} ₽`,
    '',
    'Позиции:',
    ...selectedOrder.value.items.map(
      (item) => `- ${item.product?.name || `Товар #${item.product_id}`} — ${item.quantity} кг`,
    ),
  ]

  return lines.join('\n')
})

const downloadDocument = () => {
  const blob = new Blob([previewText.value], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `document-order-${selectedOrder.value?.id || 'draft'}.txt`
  link.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <main class="documents-page">
    <section class="hero">
      <div>
        <p class="eyebrow">Документы</p>
        <h1>Генератор документов для заказа</h1>
        <p>Пока используем быстрый шаблон. Позже его можно заменить на PDF-генерацию с бэка.</p>
      </div>
      <button class="primary-btn" @click="downloadDocument" :disabled="!selectedOrder">
        Скачать документ
      </button>
    </section>

    <div class="layout">
      <section class="panel">
        <div class="field">
          <label>Заказ</label>
          <select v-model="selectedOrderId">
            <option :value="null">Выберите заказ</option>
            <option v-for="order in orders" :key="order.id" :value="order.id">Заказ #{{ order.id }}</option>
          </select>
        </div>

        <div class="field">
          <label>Тип документа</label>
          <select v-model="documentType">
            <option>Счёт</option>
            <option>Договор</option>
            <option>Акт</option>
          </select>
        </div>

        <div class="preview">
          <pre>{{ previewText }}</pre>
        </div>
      </section>

      <aside class="panel hint">
        <h2>Что дальше</h2>
        <p>
          Когда на бэке появится генерация файлов, сюда можно подключить настоящий PDF и выгрузку из
          сохранённых документов заказа.
        </p>
      </aside>
    </div>
  </main>
</template>

<style scoped>
/* внешняя панель — в пару к сайдбару кабинета */
.documents-page {
  display: grid;
  gap: 1.5rem;
  padding: clamp(1.25rem, 3vw, 2rem);
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
  color: var(--sl-ink);
}

/* ===== ШАПКА ===== */
.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.25rem 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--sl-line);
}

.eyebrow {
  margin: 0 0 0.6rem;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

.hero h1 {
  margin: 0;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  color: var(--sl-ink);
}

.hero p:not(.eyebrow) {
  margin: 0.75rem 0 0;
  max-width: 56ch;
  color: var(--sl-muted);
}

/* ===== КНОПКА ===== */
.primary-btn {
  flex: 0 0 auto;
  padding: 0.7rem 1.2rem;
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
  border-radius: 0;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.primary-btn:hover:not(:disabled) {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.primary-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.primary-btn:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

/* ===== РАБОЧАЯ ОБЛАСТЬ ===== */
.layout {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(0, 0.7fr);
  gap: 1rem;
  align-items: start;
}

.panel {
  padding: 1.25rem;
  background: #fff;
  border: 1px solid var(--sl-line);
}

.field {
  display: grid;
  gap: 0.4rem;
  margin-bottom: 1rem;
}

.field label {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

select {
  width: 100%;
  min-width: 0;
  padding: 0.7rem 0.9rem;
  border: 1px solid var(--sl-line);
  border-radius: 0;
  background: #fff;
  color: var(--sl-ink);
  transition: border-color 0.2s ease;
}

select:hover {
  border-color: rgba(20, 33, 15, 0.4);
}

select:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: -1px;
}

.preview {
  margin-top: 1.25rem;
  padding: 1rem 1.1rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-left: 3px solid var(--sl-ink);
  overflow: auto;
}

pre {
  margin: 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  font-family: inherit;
  font-size: 0.92rem;
  line-height: 1.6;
  color: var(--sl-ink);
}

/* подсказка — тёмный акцентный блок */
.hint {
  background: var(--sl-forest);
  border-color: var(--sl-forest);
  color: #fff;
}

.hint h2 {
  margin: 0 0 0.75rem;
  padding-bottom: 0.85rem;
  border-bottom: 1px solid rgba(198, 236, 154, 0.25);
  font-size: 1.05rem;
  color: var(--sl-lime);
}

.hint p {
  margin: 0;
  color: rgba(255, 255, 255, 0.78);
}

@media (max-width: 900px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .primary-btn {
    width: 100%;
  }
}
</style>
