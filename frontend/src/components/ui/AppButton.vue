<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, type RouteLocationRaw } from 'vue-router'
import AppIcon from './AppIcon.vue'
import type { IconName } from './icons'

const props = withDefaults(
  defineProps<{
    variant?: 'primary' | 'accent' | 'secondary' | 'ghost' | 'danger' | 'danger-ghost'
    size?: 'sm' | 'md' | 'lg'
    /** Если задан — кнопка становится ссылкой роутера */
    to?: RouteLocationRaw
    type?: 'button' | 'submit' | 'reset'
    icon?: IconName
    iconRight?: IconName
    loading?: boolean
    disabled?: boolean
    block?: boolean
    /** Кнопка только с иконкой: обязательно передайте label */
    iconOnly?: boolean
    label?: string
  }>(),
  {
    variant: 'primary',
    size: 'md',
    to: undefined,
    type: 'button',
    icon: undefined,
    iconRight: undefined,
    loading: false,
    disabled: false,
    block: false,
    iconOnly: false,
    label: undefined,
  },
)

const iconSize = computed(() => (props.size === 'sm' ? 16 : props.size === 'lg' ? 20 : 18))
const isDisabled = computed(() => props.disabled || props.loading)

const classes = computed(() => [
  'app-btn',
  `app-btn--${props.variant}`,
  `app-btn--${props.size}`,
  { 'app-btn--block': props.block, 'app-btn--icon-only': props.iconOnly, 'is-loading': props.loading },
])
</script>

<template>
  <RouterLink
    v-if="to && !isDisabled"
    :to="to"
    :class="classes"
    :aria-label="iconOnly ? label : undefined"
    :title="iconOnly ? label : undefined"
  >
    <AppIcon v-if="icon" :name="icon" :size="iconSize" />
    <span v-if="!iconOnly" class="app-btn__label"><slot>{{ label }}</slot></span>
    <AppIcon v-if="iconRight" :name="iconRight" :size="iconSize" class="app-btn__icon-right" />
  </RouterLink>

  <button
    v-else
    :type="type"
    :class="classes"
    :disabled="isDisabled"
    :aria-busy="loading || undefined"
    :aria-label="iconOnly ? label : undefined"
    :title="iconOnly ? label : undefined"
  >
    <span v-if="loading" class="app-btn__spinner" aria-hidden="true"></span>
    <AppIcon v-else-if="icon" :name="icon" :size="iconSize" />
    <span v-if="!iconOnly" class="app-btn__label"><slot>{{ label }}</slot></span>
    <AppIcon v-if="iconRight && !loading" :name="iconRight" :size="iconSize" class="app-btn__icon-right" />
  </button>
</template>

<style scoped>
.app-btn {
  --btn-h: 44px;
  --btn-px: 1.1rem;

  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: var(--btn-h);
  padding: 0 var(--btn-px);
  border: 1px solid transparent;
  border-radius: var(--r-sm);
  font-size: var(--fs-sm);
  font-weight: 700;
  line-height: 1.2;
  white-space: nowrap;
  text-decoration: none;
  cursor: pointer;
  user-select: none;
  transition:
    background-color var(--dur) var(--ease),
    border-color var(--dur) var(--ease),
    color var(--dur) var(--ease),
    box-shadow var(--dur) var(--ease);
}

.app-btn:focus-visible {
  outline: none;
  box-shadow: var(--sh-focus);
}

.app-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.app-btn.is-loading {
  opacity: 0.8;
  cursor: progress;
}

/* размеры */
.app-btn--sm {
  --btn-h: 36px;
  --btn-px: 0.8rem;
  font-size: 0.8125rem;
  border-radius: var(--r-xs);
}

.app-btn--lg {
  --btn-h: 52px;
  --btn-px: 1.5rem;
  font-size: var(--fs-md);
  border-radius: var(--r-md);
}

.app-btn--block {
  display: flex;
  width: 100%;
}

.app-btn--icon-only {
  width: var(--btn-h);
  padding: 0;
}

/* варианты */
.app-btn--primary {
  background: var(--c-brand-800);
  color: #fff;
}

.app-btn--primary:hover:not(:disabled) {
  background: var(--c-brand-700);
}

.app-btn--accent {
  background: var(--c-accent);
  color: var(--c-brand-950);
}

.app-btn--accent:hover:not(:disabled) {
  background: var(--c-accent-600);
  color: #fff;
}

.app-btn--secondary {
  background: var(--c-surface);
  border-color: var(--c-border-strong);
  color: var(--c-text);
  box-shadow: var(--sh-xs);
}

.app-btn--secondary:hover:not(:disabled) {
  border-color: var(--c-muted);
  background: var(--c-surface-2);
}

.app-btn--ghost {
  background: transparent;
  color: var(--c-text-2);
}

.app-btn--ghost:hover:not(:disabled) {
  background: var(--c-surface-sunken);
  color: var(--c-text);
}

.app-btn--danger {
  background: var(--c-danger);
  color: #fff;
}

.app-btn--danger:hover:not(:disabled) {
  background: var(--c-danger-600);
}

.app-btn--danger-ghost {
  background: transparent;
  color: var(--c-danger);
}

.app-btn--danger-ghost:hover:not(:disabled) {
  background: var(--c-danger-bg);
}

.app-btn__label {
  overflow: hidden;
  text-overflow: ellipsis;
}

.app-btn__icon-right {
  transition: transform var(--dur) var(--ease);
}

.app-btn:hover .app-btn__icon-right {
  transform: translateX(2px);
}

.app-btn__spinner {
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: app-btn-spin 0.7s linear infinite;
}

@keyframes app-btn-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
