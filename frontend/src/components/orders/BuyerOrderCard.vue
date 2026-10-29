<script setup lang="ts">
import { computed } from 'vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import ProductThumb from '@/components/ui/ProductThumb.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import type { Order } from '@/stores/shopStore'
import { formatDate, formatNumber, formatPrice, pluralize } from '@/utils/format'

const props = defineProps<{
  order: Order
  /** Идёт запрос «Заказ получен» по этому заказу */
  updating: boolean
  /** Заблокировать кнопку, пока обновляется другой заказ */
  locked: boolean
}>()

defineEmits<{ delivered: [orderId: number] }>()

const canMarkDelivered = computed(() => props.order.status === 'CONFIRMED' || props.order.status === 'IN_PROGRESS')
const itemsCount = computed(() => props.order.items.length)
const dateLabel = computed(() => {
  const date = formatDate(props.order.created_at, 'long')
  const time = formatDate(props.order.created_at, 'time', '')
  return time ? `${date}, ${time}` : date
})
</script>

<template>
  <article
    class="order ui-card"
    :class="{
      'order--completed': order.status === 'COMPLETED',
      'order--cancelled': order.status === 'CANCELLED',
    }"
    :aria-labelledby="`order-${order.id}-title`"
  >
    <header class="order__head">
      <div class="order__titles">
        <h3 :id="`order-${order.id}-title`" class="order__title">
          Заказ <span class="ui-num">№{{ order.id }}</span>
        </h3>
        <p class="order__meta">
          <span class="order__meta-item">
            <AppIcon name="calendar" :size="14" />
            <time :datetime="order.created_at">{{ dateLabel }}</time>
          </span>
          <span class="order__meta-item">
            <AppIcon name="package" :size="14" />
            <span class="ui-num">{{ itemsCount }}</span> {{ pluralize(itemsCount, ['позиция', 'позиции', 'позиций']) }}
          </span>
        </p>
      </div>
      <StatusBadge :status="order.status" perspective="buyer" />
    </header>

    <div class="order__supplier">
      <span class="order__supplier-icon"><AppIcon name="store" :size="16" /></span>
      <div class="order__supplier-text">
        <span class="order__label">Поставщик</span>
        <span class="order__supplier-name">{{ order.seller_enterprise?.short_name || '—' }}</span>
      </div>
    </div>

    <ul class="order__items" aria-label="Позиции заказа">
      <li v-for="item in order.items" :key="item.id" class="order__item">
        <ProductThumb :category="item.product?.category?.name" size="sm" />
        <div class="order__item-main">
          <span class="order__item-name">{{ item.product?.name || `Товар #${item.product_id}` }}</span>
          <span class="order__item-qty ui-num">
            {{ formatNumber(item.quantity) }} кг × {{ formatPrice(item.price) }}
          </span>
        </div>
        <span class="order__item-sum ui-num">{{ formatPrice(item.price * item.quantity) }}</span>
      </li>
    </ul>

    <footer class="order__foot">
      <div class="order__total">
        <span class="order__label">Итоговая сумма</span>
        <span class="order__total-value ui-num">{{ formatPrice(order.total_amount) }}</span>
      </div>

      <div class="order__actions">
        <template v-if="canMarkDelivered">
          <p v-if="order.status === 'CONFIRMED'" class="order__hint">Нажмите, когда товар будет у вас</p>
          <AppButton
            icon="check"
            :loading="updating"
            :disabled="locked && !updating"
            class="order__cta"
            @click="$emit('delivered', order.id)"
          >
            {{ updating ? 'Обновляем…' : 'Заказ получен' }}
          </AppButton>
        </template>
        <p v-else-if="order.status === 'COMPLETED'" class="order__note order__note--success">
          <AppIcon name="check-circle" :size="16" />
          Сделка успешно завершена
        </p>
        <p v-else-if="order.status === 'CANCELLED'" class="order__note order__note--danger">
          <AppIcon name="x-circle" :size="16" />
          Заказ был отменён
        </p>
        <p v-else class="order__note">
          <AppIcon name="clock" :size="16" />
          Ожидайте подтверждения от поставщика
        </p>
      </div>
    </footer>
  </article>
</template>

<style scoped>
.order {
  display: grid;
  min-width: 0;
  overflow: hidden;
}

.order__head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem 1rem;
  padding: 1.1rem clamp(1rem, 2.5vw, 1.5rem);
  border-bottom: 1px solid var(--c-border);
}

.order__titles {
  display: grid;
  gap: 0.3rem;
  min-width: 0;
}

.order__title {
  font-size: var(--fs-lg);
}

.order__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 1rem;
  color: var(--c-muted);
  font-size: var(--fs-sm);
}

.order__meta-item {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.order__supplier {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem clamp(1rem, 2.5vw, 1.5rem) 0.75rem;
}

.order__supplier-icon {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  width: 36px;
  height: 36px;
  border-radius: var(--r-sm);
  background: var(--c-brand-50);
  color: var(--c-brand-700);
}

.order__supplier-text {
  display: grid;
  min-width: 0;
}

.order__label {
  color: var(--c-muted);
  font-size: var(--fs-xs);
  font-weight: 600;
}

.order__supplier-name {
  font-weight: 700;
  overflow-wrap: anywhere;
}

/* позиции */
.order__items {
  display: grid;
  margin: 0 clamp(1rem, 2.5vw, 1.5rem);
  padding: 0;
  list-style: none;
  border: 1px solid var(--c-border);
  border-radius: var(--r-md);
  background: var(--c-surface-2);
}

.order__item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0.85rem;
  border-bottom: 1px solid var(--c-border);
}

.order__item:last-child {
  border-bottom: none;
}

.order__item-main {
  display: grid;
  flex: 1 1 auto;
  min-width: 0;
}

.order__item-name {
  font-size: var(--fs-sm);
  font-weight: 700;
  overflow-wrap: anywhere;
}

.order__item-qty {
  color: var(--c-muted);
  font-size: var(--fs-xs);
}

.order__item-sum {
  flex: 0 0 auto;
  font-size: var(--fs-sm);
  font-weight: 700;
  white-space: nowrap;
}

/* итог и действия */
.order__foot {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem clamp(1rem, 2.5vw, 1.5rem) 1.1rem;
}

.order__total {
  display: grid;
}

.order__total-value {
  font-size: var(--fs-xl);
  font-weight: 800;
  letter-spacing: -0.02em;
  white-space: nowrap;
}

.order__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem 1rem;
}

.order__hint {
  color: var(--c-muted);
  font-size: var(--fs-sm);
}

.order__note {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--c-muted);
  font-size: var(--fs-sm);
  font-weight: 600;
}

.order__note--success {
  color: var(--c-success);
}

.order__note--danger {
  color: var(--c-danger);
}

.order--cancelled .order__items,
.order--cancelled .order__total-value {
  opacity: 0.7;
}

@media (max-width: 640px) {
  .order__foot {
    align-items: stretch;
    flex-direction: column;
  }

  .order__total {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 1rem;
  }

  .order__actions {
    justify-content: flex-start;
  }

  .order__cta {
    width: 100%;
  }
}
</style>
