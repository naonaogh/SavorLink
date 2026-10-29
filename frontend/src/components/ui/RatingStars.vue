<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'

const props = withDefaults(
  defineProps<{
    /** Реальная оценка из API (0–5) */
    value: number
    size?: number
    showValue?: boolean
    /** Количество отзывов — показывается в скобках, если передано */
    count?: number
  }>(),
  { size: 16, showValue: false, count: undefined },
)

const rounded = computed(() => Math.round(props.value))
const label = computed(() => `Оценка ${props.value.toFixed(1)} из 5`)
</script>

<template>
  <span class="rating" role="img" :aria-label="label">
    <span class="rating__stars" aria-hidden="true">
      <AppIcon
        v-for="n in 5"
        :key="n"
        name="star"
        :size="size"
        :filled="n <= rounded"
        :stroke-width="1.6"
        :class="n <= rounded ? 'rating__star is-on' : 'rating__star'"
      />
    </span>
    <span v-if="showValue" class="rating__value" aria-hidden="true">{{ value.toFixed(1) }}</span>
    <span v-if="count !== undefined" class="rating__count" aria-hidden="true">({{ count }})</span>
  </span>
</template>

<style scoped>
.rating {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.rating__stars {
  display: inline-flex;
  gap: 1px;
}

.rating__star {
  color: var(--c-border-strong);
}

.rating__star.is-on {
  color: #e0a526;
}

.rating__value {
  font-weight: 800;
  font-size: var(--fs-sm);
  color: var(--c-text);
}

.rating__count {
  color: var(--c-muted);
  font-size: var(--fs-sm);
}
</style>
