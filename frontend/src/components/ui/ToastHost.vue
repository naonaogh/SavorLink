<script setup lang="ts">
import AppIcon from './AppIcon.vue'
import { useToast } from '@/composables/useToast'

const { toasts, dismiss } = useToast()

const ICONS = { success: 'check-circle', error: 'alert-circle', info: 'info' } as const
</script>

<template>
  <div class="toast-host" aria-live="polite" aria-atomic="false">
    <TransitionGroup name="toast">
      <div v-for="toast in toasts" :key="toast.id" class="toast" :class="`toast--${toast.tone}`" role="status">
        <AppIcon :name="ICONS[toast.tone]" :size="20" class="toast__icon" />
        <div class="toast__body">
          <p class="toast__title">{{ toast.title }}</p>
          <p v-if="toast.message" class="toast__msg">{{ toast.message }}</p>
        </div>
        <button type="button" class="toast__close" aria-label="Закрыть уведомление" @click="dismiss(toast.id)">
          <AppIcon name="x" :size="16" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-host {
  position: fixed;
  right: 1rem;
  bottom: 1rem;
  z-index: 1100;
  display: grid;
  gap: 0.6rem;
  width: min(380px, calc(100vw - 2rem));
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.85rem 0.85rem 0.85rem 1rem;
  border: 1px solid var(--c-border);
  border-left-width: 4px;
  border-radius: var(--r-md);
  background: var(--c-surface);
  box-shadow: var(--sh-lg);
  pointer-events: auto;
}

.toast--success {
  border-left-color: var(--c-accent);
}

.toast--success .toast__icon {
  color: var(--c-success);
}

.toast--error {
  border-left-color: var(--c-danger);
}

.toast--error .toast__icon {
  color: var(--c-danger);
}

.toast--info {
  border-left-color: var(--c-info);
}

.toast--info .toast__icon {
  color: var(--c-info);
}

.toast__body {
  flex: 1;
  min-width: 0;
}

.toast__title {
  font-weight: 700;
  font-size: var(--fs-sm);
}

.toast__msg {
  margin-top: 0.15rem;
  color: var(--c-muted);
  font-size: var(--fs-sm);
  overflow-wrap: anywhere;
}

.toast__close {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: var(--r-xs);
  background: transparent;
  color: var(--c-muted);
}

.toast__close:hover {
  background: var(--c-surface-sunken);
  color: var(--c-text);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.2s var(--ease), transform 0.2s var(--ease);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@media (max-width: 560px) {
  .toast-host {
    right: 0.75rem;
    left: 0.75rem;
    bottom: 0.75rem;
    width: auto;
  }
}
</style>
