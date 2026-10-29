<script setup lang="ts">
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import ProductThumb from '@/components/ui/ProductThumb.vue'
import type { Product } from '@/stores/shopStore'
import { formatNumber, formatPrice } from '@/utils/format'

export interface TemplateItemView {
  product_id: number
  quantity: number
  product?: Product
}

defineProps<{
  items: TemplateItemView[]
  total: number
  checkingOut: boolean
}>()

const open = defineModel<boolean>('open', { required: true })

defineEmits<{ checkout: []; delete: [] }>()
</script>

<template>
  <AppModal
    v-model:open="open"
    title="Ваш шаблон заказа"
    description="Цены соответствуют текущим в каталоге"
    size="md"
    :persistent="checkingOut"
  >
    <ul v-if="items.length" class="tpl" aria-label="Позиции шаблона">
      <li v-for="item in items" :key="item.product_id" class="tpl__item">
        <ProductThumb :category="item.product?.category?.name" size="sm" />
        <div class="tpl__main">
          <span class="tpl__name">{{ item.product?.name }}</span>
          <span class="tpl__meta">
            <span v-if="item.product?.enterprise">{{ item.product.enterprise.short_name }}</span>
            <span v-if="item.product?.category" class="tpl__category">{{ item.product.category.name }}</span>
          </span>
          <span class="tpl__qty ui-num">
            {{ formatNumber(item.quantity) }} кг × {{ formatPrice(item.product?.price) }}
          </span>
        </div>
        <span class="tpl__sum ui-num">{{ formatPrice((item.product?.price || 0) * item.quantity) }}</span>
      </li>
    </ul>
    <EmptyState
      v-else
      compact
      icon="clipboard-list"
      title="Нет доступных позиций"
      description="Товары из шаблона не найдены в текущем каталоге."
    />

    <div class="tpl__total">
      <span class="tpl__total-label">Итого по шаблону</span>
      <span class="tpl__total-value ui-num">{{ formatPrice(total) }}</span>
    </div>

    <template #footer>
      <AppButton
        variant="danger-ghost"
        icon="trash"
        class="tpl__delete"
        :disabled="checkingOut"
        @click="$emit('delete')"
      >
        Удалить шаблон
      </AppButton>
      <AppButton icon="check" :loading="checkingOut" @click="$emit('checkout')">
        {{ checkingOut ? 'Оформление…' : 'Оформить по шаблону' }}
      </AppButton>
    </template>
  </AppModal>
</template>

<style scoped>
.tpl__delete {
  margin-right: auto;
}

.tpl {
  display: grid;
  margin: 0;
  padding: 0;
  list-style: none;
  border: 1px solid var(--c-border);
  border-radius: var(--r-md);
  background: var(--c-surface-2);
}

.tpl__item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0.9rem;
  border-bottom: 1px solid var(--c-border);
}

.tpl__item:last-child {
  border-bottom: none;
}

.tpl__main {
  display: grid;
  flex: 1 1 auto;
  gap: 0.1rem;
  min-width: 0;
}

.tpl__name {
  font-weight: 700;
  overflow-wrap: anywhere;
}

.tpl__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.15rem 0.75rem;
  color: var(--c-muted);
  font-size: var(--fs-xs);
  font-weight: 600;
}

.tpl__category {
  color: var(--c-accent-700);
}

.tpl__qty {
  color: var(--c-text-2);
  font-size: var(--fs-xs);
}

.tpl__sum {
  flex: 0 0 auto;
  font-weight: 700;
  white-space: nowrap;
}

.tpl__total {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--c-border);
}

.tpl__total-label {
  color: var(--c-text-2);
  font-weight: 700;
}

.tpl__total-value {
  font-size: var(--fs-xl);
  font-weight: 800;
  letter-spacing: -0.02em;
  white-space: nowrap;
}
</style>
