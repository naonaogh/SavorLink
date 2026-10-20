<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'
import { StarIcon } from '@/assets/icons/png'

const router = useRouter()
const authStore = useAuthStore()
const store = useShopStore()

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }

  if (store.state.suppliers.length === 0) {
    await store.fetchSuppliers()
  }
})

const selectedSuppliers = computed(() =>
  store.state.suppliers.filter((supplier) => store.state.comparisonSupplierIds.includes(supplier.id)),
)

const allSuppliers = computed(() => store.state.suppliers)

const comparisonRows = computed(() => [
  { label: 'Рейтинг', getValue: (supplier: any) => supplier.rating.toFixed(1) },
  { label: 'Регион', getValue: (supplier: any) => supplier.region || 'Не указан' },
  { label: 'Город', getValue: (supplier: any) => supplier.city || 'Не указан' },
  { label: 'Товаров', getValue: (supplier: any) => String(supplier.products.length) },
  { label: 'Отзывы', getValue: (supplier: any) => String(supplier.reviews) },
  { label: 'Описание', getValue: (supplier: any) => supplier.description },
])
</script>

<template>
  <main class="compare-page">
    <section class="hero">
      <div class="hero-copy">
        <p class="eyebrow kicker">Сравнение поставщиков</p>
        <h1>Сравните поставщиков по ключевым параметрам</h1>
        <p>Выбранные поставщики подтягиваются из каталога. Можно быстро снять или добавить новых.</p>
      </div>
      <button class="ghost-btn" @click="store.clearComparison()">Очистить сравнение</button>
    </section>

    <div v-if="selectedSuppliers.length === 0" class="empty-card">
      <p>Пока нет выбранных поставщиков. Откройте каталог и нажмите «Сравнить».</p>
      <router-link to="/catalog" class="primary-btn">Перейти в каталог</router-link>
    </div>

    <template v-else>
      <div class="supplier-strip">
        <article v-for="supplier in selectedSuppliers" :key="supplier.id" class="supplier-card">
          <div class="supplier-top">
            <div>
              <h2>{{ supplier.name }}</h2>
              <p>{{ supplier.locations || 'Локация не указана' }}</p>
            </div>
            <button class="remove-btn" @click="store.toggleComparison(supplier.id)">Удалить</button>
          </div>
          <div class="supplier-meta">
            <span class="rating">
              <img :src="StarIcon" alt="" class="rating-icon" aria-hidden="true" />
              {{ supplier.rating.toFixed(1) }}
            </span>
            <span>{{ supplier.products.length }} товаров</span>
          </div>
        </article>
      </div>

      <section class="compare-table">
        <div class="table-head">
          <div>Параметр</div>
          <div v-for="supplier in selectedSuppliers" :key="supplier.id">{{ supplier.name }}</div>
        </div>

        <div v-for="row in comparisonRows" :key="row.label" class="table-row">
          <div class="label-cell">{{ row.label }}</div>
          <div v-for="supplier in selectedSuppliers" :key="`${row.label}-${supplier.id}`" class="value-cell">
            {{ row.getValue(supplier) }}
          </div>
        </div>
      </section>
    </template>

    <aside class="picker-card">
      <div class="picker-head">
        <p class="kicker">Выбор</p>
        <h2>Каталог для сравнения</h2>
      </div>
      <div class="picker-list">
        <button
          v-for="supplier in allSuppliers"
          :key="supplier.id"
          class="picker-item"
          :class="{ active: store.state.comparisonSupplierIds.includes(supplier.id) }"
          @click="store.toggleComparison(supplier.id)"
        >
          <span>{{ supplier.name }}</span>
          <span>{{ supplier.region }}</span>
        </button>
      </div>
    </aside>
  </main>
</template>

<style scoped>
.compare-page {
  display: grid;
  gap: 1.25rem;
  padding-bottom: 2rem;
  color: var(--sl-ink);
}

h1,
h2 {
  margin: 0;
  color: var(--sl-ink);
}

.kicker {
  margin: 0 0 0.6rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-leaf);
}

/* ===== ЗАГОЛОВОК ===== */
.hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: end;
  gap: 1.25rem 2rem;
  padding: clamp(1.25rem, 3vw, 2.25rem);
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-ink);
}

.hero h1 {
  max-width: 26ch;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  line-height: 1.15;
}

.hero p:not(.kicker) {
  margin: 0.85rem 0 0;
  max-width: 60ch;
  color: var(--sl-muted);
}

/* ===== КНОПКИ ===== */
.ghost-btn,
.remove-btn,
.primary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.7rem 1.2rem;
  border-radius: 0;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.ghost-btn {
  background: transparent;
  color: var(--sl-ink);
  border: 1px solid var(--sl-ink);
}

.ghost-btn:hover {
  background: var(--sl-ink);
  color: #fff;
}

.remove-btn {
  align-self: flex-start;
  padding: 0.4rem 0.75rem;
  font-size: 0.85rem;
  background: transparent;
  color: #b3261e;
  border: 1px solid #b3261e;
}

.remove-btn:hover {
  background: #b3261e;
  color: #fff;
}

.primary-btn {
  background: var(--sl-ink);
  color: #fff;
  border: 1px solid var(--sl-ink);
}

.primary-btn:hover {
  background: var(--sl-leaf);
  border-color: var(--sl-leaf);
}

.ghost-btn:focus-visible,
.remove-btn:focus-visible,
.primary-btn:focus-visible,
.picker-item:focus-visible {
  outline: 2px solid var(--sl-leaf);
  outline-offset: 2px;
}

/* ===== ПУСТО ===== */
.empty-card {
  display: grid;
  justify-items: center;
  gap: 1rem;
  padding: clamp(1.5rem, 4vw, 2.5rem);
  background: #fff;
  border: 1px dashed rgba(20, 33, 15, 0.3);
  text-align: center;
}

.empty-card p {
  margin: 0;
  color: var(--sl-muted);
}

/* ===== ВЫБРАННЫЕ ===== */
.supplier-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.75rem;
}

.supplier-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1.1rem 1.25rem;
  background: #fff;
  border: 1px solid var(--sl-line);
  border-top: 3px solid var(--sl-leaf);
}

.supplier-top {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.supplier-top h2 {
  font-family: inherit;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.35;
}

.supplier-card p {
  margin: 0.3rem 0 0;
  font-size: 0.88rem;
  color: var(--sl-muted);
}

.supplier-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.supplier-meta > span {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.5rem;
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.rating-icon {
  width: 13px;
  height: 13px;
  object-fit: contain;
  display: block;
  filter: grayscale(1) brightness(0.35);
}

/* ===== ТАБЛИЦА ===== */
.compare-table {
  background: #fff;
  border: 1px solid var(--sl-line);
  overflow-x: auto;
}

.table-head,
.table-row {
  display: grid;
  grid-template-columns: 180px;
  grid-auto-flow: column;
  grid-auto-columns: minmax(150px, 1fr);
}

.table-head > div,
.table-row > div {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--sl-line);
  overflow-wrap: break-word;
}

.table-head > div + div,
.table-row > div + div {
  border-left: 1px solid var(--sl-line);
}

.table-row:last-child > div {
  border-bottom: none;
}

.table-head {
  background: var(--sl-ink);
  color: #fff;
  font-weight: 700;
}

.table-head > div {
  border-bottom-color: var(--sl-ink);
}

.table-head > div:first-child {
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-lime);
}

.table-head > div + div {
  border-left-color: rgba(255, 255, 255, 0.14);
}

.table-row {
  transition: background 0.2s ease;
}

.table-row:hover {
  background: var(--sl-paper);
}

.label-cell {
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted);
  background: var(--sl-paper);
}

.value-cell {
  color: var(--sl-ink);
}

/* ===== ПИКЕР ===== */
.picker-card {
  padding: clamp(1.25rem, 3vw, 2.25rem);
  background: var(--sl-paper);
  border: 1px solid var(--sl-line);
}

.picker-head {
  padding-bottom: 1.25rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid var(--sl-line);
}

.picker-head h2 {
  font-size: clamp(1.25rem, 2.4vw, 1.6rem);
}

.picker-list {
  display: grid;
  border: 1px solid var(--sl-line);
  background: #fff;
}

.picker-item {
  position: relative;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.9rem 1.1rem;
  border: none;
  border-bottom: 1px solid var(--sl-line);
  border-radius: 0;
  background: #fff;
  color: var(--sl-ink);
  text-align: left;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.picker-item:last-child {
  border-bottom: none;
}

.picker-item > span:last-child {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--sl-muted);
  text-align: right;
}

.picker-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--sl-leaf);
  transform: scaleY(0);
  transition: transform 0.2s ease;
}

.picker-item:hover {
  background: var(--sl-paper);
}

.picker-item:hover::before,
.picker-item.active::before {
  transform: scaleY(1);
}

.picker-item.active {
  background: var(--sl-ink);
  color: #fff;
}

.picker-item.active::before {
  background: var(--sl-lime);
}

.picker-item.active > span:last-child {
  color: var(--sl-lime);
}

/* ===== АДАПТИВ ===== */
@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .ghost-btn {
    justify-self: start;
  }

  .table-head,
  .table-row {
    grid-template-columns: 118px;
    grid-auto-columns: minmax(170px, 1fr);
  }

  .table-head > div:first-child,
  .label-cell {
    letter-spacing: 0.08em;
  }

  .table-head > div:first-child,
  .table-row > .label-cell {
    position: sticky;
    left: 0;
    z-index: 1;
  }

  .table-head > div:first-child {
    background: var(--sl-ink);
  }
}

@media (max-width: 520px) {
  .ghost-btn {
    justify-self: stretch;
  }

  .supplier-top {
    display: grid;
  }

  .remove-btn {
    justify-self: start;
  }

  .picker-item {
    flex-wrap: wrap;
    gap: 0.25rem 1rem;
  }
}
</style>
