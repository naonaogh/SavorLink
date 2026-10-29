<script setup lang="ts">
import { computed } from 'vue'
import type { Order } from '@/stores/shopStore'
import AppAvatar from '@/components/ui/AppAvatar.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import type { IconName } from '@/components/ui/icons'
import { formatDate, formatNumber, formatPrice, pluralize } from '@/utils/format'

/**
 * Карточка заказа в кабинете поставщика.
 * variant="new" — новый запрос (кнопки действий передаются в слот #actions),
 * variant="active" — сделка в работе (статус + подсказка по статусу внизу).
 */
const props = withDefaults(
  defineProps<{
    order: Order
    variant?: 'new' | 'active'
  }>(),
  { variant: 'active' },
)

const buyerName = computed(() => props.order.buyer_enterprise?.short_name || 'Покупатель')
const buyerRegion = computed(() => props.order.buyer_enterprise?.region || 'Регион не указан')
const itemsCount = computed(() => props.order.items.length)

/* подсказка внизу карточки — только по фактическому статусу заказа */
const STATUS_HINTS: Record<string, { text: string; icon: IconName }> = {
  CONFIRMED: { text: 'Заказ подтверждён, остатки на складе списаны', icon: 'check-circle' },
  IN_PROGRESS: { text: 'Заказ в процессе выполнения', icon: 'truck' },
}
const statusHint = computed(() => STATUS_HINTS[props.order.status] ?? null)
</script>

<template>
  <article class="order-card ui-card" :class="{ 'order-card--new': variant === 'new' }">
    <header class="order-card__head">
      <div class="order-card__id">
        <h3 class="order-card__title">Заказ №{{ order.id }}</h3>
        <time class="order-card__date" :datetime="order.created_at">
          <AppIcon name="calendar" :size="14" />
          {{ formatDate(order.created_at, 'datetime') }}
        </time>
      </div>
      <StatusBadge :status="order.status" perspective="supplier" size="sm" />
    </header>

    <div class="order-card__body">
      <div class="order-card__buyer">
        <AppAvatar :name="buyerName" :size="40" tone="neutral" />
        <div class="order-card__buyer-text">
          <span class="order-card__buyer-name">{{ buyerName }}</span>
          <span class="order-card__buyer-region">
            <AppIcon name="map-pin" :size="14" />
            {{ buyerRegion }}
          </span>
        </div>
      </div>

      <div class="order-card__items">
        <p class="order-card__items-label">
          {{ itemsCount }} {{ pluralize(itemsCount, ['позиция', 'позиции', 'позиций']) }}
        </p>
        <ul class="order-card__list">
          <li v-for="item in order.items" :key="item.id" class="order-card__item">
            <span class="order-card__item-name">{{ item.product?.name || 'Товар' }}</span>
            <span class="order-card__item-qty ui-num">{{ formatNumber(item.quantity) }} кг</span>
          </li>
        </ul>
      </div>

      <div class="order-card__total">
        <span class="order-card__total-label">{{ variant === 'new' ? 'К оплате' : 'Сумма' }}</span>
        <span class="order-card__total-value ui-num">{{ formatPrice(order.total_amount) }}</span>
      </div>
    </div>

    <footer v-if="$slots.actions" class="order-card__actions">
      <slot name="actions" />
    </footer>
    <footer v-else-if="statusHint" class="order-card__hint">
      <AppIcon :name="statusHint.icon" :size="16" class="order-card__hint-icon" />
      <span>{{ statusHint.text }}</span>
    </footer>
  </article>
</template>

<style scoped>
.order-card {
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.order-card--new {
  border-color: var(--c-accent-200);
  box-shadow: inset 3px 0 0 var(--c-accent), var(--sh-xs);
}

.order-card__head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem 1rem;
  padding: 1rem 1.25rem 0;
}

.order-card__id {
  display: grid;
  gap: 0.2rem;
  min-width: 0;
}

.order-card__title {
  font-size: var(--fs-md);
  font-weight: 800;
}

.order-card__date {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--c-muted);
  font-size: var(--fs-xs);
  font-weight: 600;
}

.order-card__body {
  flex: 1;
  display: grid;
  align-content: start;
  gap: 1rem;
  padding: 1rem 1.25rem 1.25rem;
}

.order-card__buyer {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.order-card__buyer-text {
  display: grid;
  gap: 0.1rem;
  min-width: 0;
}

.order-card__buyer-name {
  font-weight: 700;
  color: var(--c-text);
  overflow-wrap: anywhere;
}

.order-card__buyer-region {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  color: var(--c-muted);
  font-size: var(--fs-sm);
}

.order-card__items {
  display: grid;
  gap: 0.5rem;
  padding: 0.85rem 1rem;
  border-radius: var(--r-md);
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
}

.order-card__items-label {
  color: var(--c-muted);
  font-size: var(--fs-xs);
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.order-card__list {
  display: grid;
  gap: 0.4rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.order-card__item {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
  font-size: var(--fs-sm);
}

.order-card__item-name {
  min-width: 0;
  color: var(--c-text-2);
  overflow-wrap: anywhere;
}

.order-card__item-qty {
  flex: 0 0 auto;
  font-weight: 700;
  color: var(--c-text);
  white-space: nowrap;
}

.order-card__total {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
}

.order-card__total-label {
  color: var(--c-muted);
  font-size: var(--fs-sm);
  font-weight: 600;
}

.order-card__total-value {
  font-size: var(--fs-xl);
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--c-brand-800);
  white-space: nowrap;
}

.order-card__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--c-border);
  background: var(--c-surface-2);
}

.order-card__actions > :deep(*) {
  flex: 1 1 auto;
}

.order-card__hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 1.25rem;
  border-top: 1px solid var(--c-border);
  background: var(--c-surface-2);
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  font-weight: 600;
}

.order-card__hint-icon {
  flex: 0 0 auto;
  color: var(--c-accent-700);
}

@media (max-width: 560px) {
  .order-card__head,
  .order-card__body,
  .order-card__actions,
  .order-card__hint {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .order-card__actions > :deep(*) {
    flex-basis: 100%;
  }
}
</style>
