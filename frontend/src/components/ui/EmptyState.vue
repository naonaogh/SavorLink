<script setup lang="ts">
import AppIcon from './AppIcon.vue'
import type { IconName } from './icons'

withDefaults(
  defineProps<{
    title: string
    description?: string
    icon?: IconName
    compact?: boolean
  }>(),
  { description: undefined, icon: 'inbox', compact: false },
)
</script>

<template>
  <div class="empty-state" :class="{ 'empty-state--compact': compact }" role="status">
    <span class="empty-state__icon"><AppIcon :name="icon" :size="compact ? 22 : 28" /></span>
    <p class="empty-state__title">{{ title }}</p>
    <p v-if="description" class="empty-state__desc">{{ description }}</p>
    <div v-if="$slots.default" class="empty-state__actions"><slot /></div>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: clamp(2rem, 6vw, 3.5rem) 1.5rem;
  text-align: center;
  border: 1px dashed var(--c-border-strong);
  border-radius: var(--r-lg);
  background: var(--c-surface-2);
}

.empty-state--compact {
  padding: 1.5rem 1rem;
}

.empty-state__icon {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  margin-bottom: 0.4rem;
  border-radius: var(--r-md);
  background: var(--c-accent-50);
  color: var(--c-accent-700);
}

.empty-state--compact .empty-state__icon {
  width: 44px;
  height: 44px;
}

.empty-state__title {
  font-weight: 800;
  font-size: var(--fs-lg);
}

.empty-state__desc {
  max-width: 420px;
  color: var(--c-muted);
  font-size: var(--fs-sm);
}

.empty-state__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.6rem;
  margin-top: 0.75rem;
}
</style>
