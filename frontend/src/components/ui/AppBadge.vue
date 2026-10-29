<script setup lang="ts">
import AppIcon from './AppIcon.vue'
import type { IconName } from './icons'
import type { StatusTone } from '@/utils/orderStatus'

withDefaults(
  defineProps<{
    tone?: StatusTone | 'accent'
    icon?: IconName
    size?: 'sm' | 'md'
    /** Цветная точка вместо иконки */
    dot?: boolean
  }>(),
  { tone: 'neutral', icon: undefined, size: 'md', dot: false },
)
</script>

<template>
  <span class="app-badge" :class="[`app-badge--${tone}`, `app-badge--${size}`]">
    <span v-if="dot" class="app-badge__dot" aria-hidden="true"></span>
    <AppIcon v-else-if="icon" :name="icon" :size="size === 'sm' ? 12 : 14" :stroke-width="2.4" />
    <slot />
  </span>
</template>

<style scoped>
.app-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  max-width: 100%;
  padding: 0.25rem 0.6rem;
  border-radius: var(--r-full);
  font-size: var(--fs-xs);
  font-weight: 700;
  line-height: 1.3;
  white-space: nowrap;
}

.app-badge--sm {
  padding: 0.15rem 0.5rem;
  font-size: 0.6875rem;
}

.app-badge__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.app-badge--neutral {
  background: var(--c-surface-sunken);
  color: var(--c-text-2);
}

.app-badge--info {
  background: var(--c-info-bg);
  color: var(--c-info);
}

.app-badge--warning {
  background: var(--c-warning-bg);
  color: var(--c-warning);
}

.app-badge--success {
  background: var(--c-success-bg);
  color: var(--c-success);
}

.app-badge--danger {
  background: var(--c-danger-bg);
  color: var(--c-danger);
}

.app-badge--brand {
  background: var(--c-brand-800);
  color: #fff;
}

.app-badge--accent {
  background: var(--c-accent-100);
  color: var(--c-brand-800);
}
</style>
