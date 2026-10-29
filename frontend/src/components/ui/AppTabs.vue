<script setup lang="ts" generic="T extends string | number">
import AppIcon from './AppIcon.vue'
import type { TabItem } from './types'

const props = withDefaults(
  defineProps<{
    modelValue: T
    items: TabItem<T>[]
    variant?: 'underline' | 'pills'
    ariaLabel?: string
  }>(),
  { variant: 'pills', ariaLabel: undefined },
)

const emit = defineEmits<{ 'update:modelValue': [value: T] }>()

const select = (value: T) => emit('update:modelValue', value)

/* стрелки влево/вправо переключают вкладки */
const onKeydown = (event: KeyboardEvent, index: number) => {
  if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return
  event.preventDefault()
  const delta = event.key === 'ArrowRight' ? 1 : -1
  const next = (index + delta + props.items.length) % props.items.length
  select(props.items[next]!.value)
  const buttons = (event.currentTarget as HTMLElement).parentElement?.querySelectorAll<HTMLElement>('[role="tab"]')
  buttons?.[next]?.focus()
}
</script>

<template>
  <div class="app-tabs" :class="`app-tabs--${variant}`" role="tablist" :aria-label="ariaLabel">
    <button
      v-for="(item, index) in items"
      :key="String(item.value)"
      type="button"
      role="tab"
      class="app-tabs__tab"
      :class="{ 'is-active': item.value === modelValue }"
      :aria-selected="item.value === modelValue"
      :tabindex="item.value === modelValue ? 0 : -1"
      @click="select(item.value)"
      @keydown="onKeydown($event, index)"
    >
      <AppIcon v-if="item.icon" :name="item.icon" :size="16" />
      <span>{{ item.label }}</span>
      <span v-if="item.count !== undefined" class="app-tabs__count">{{ item.count }}</span>
    </button>
  </div>
</template>

<style scoped>
.app-tabs {
  display: flex;
  gap: 0.25rem;
  max-width: 100%;
  overflow-x: auto;
  scrollbar-width: none;
}

.app-tabs::-webkit-scrollbar {
  display: none;
}

.app-tabs__tab {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  flex: 0 0 auto;
  min-height: 40px;
  padding: 0 0.95rem;
  border: none;
  background: transparent;
  color: var(--c-muted);
  font-size: var(--fs-sm);
  font-weight: 700;
  white-space: nowrap;
  transition: background var(--dur) var(--ease), color var(--dur) var(--ease), box-shadow var(--dur) var(--ease);
}

.app-tabs__tab:hover {
  color: var(--c-text);
}

.app-tabs__tab:focus-visible {
  outline: none;
  box-shadow: var(--sh-focus);
}

.app-tabs__count {
  min-width: 1.4rem;
  padding: 0.05rem 0.4rem;
  border-radius: var(--r-full);
  background: var(--c-surface-sunken);
  color: var(--c-text-2);
  font-size: 0.6875rem;
  text-align: center;
}

/* pills: сегментированный переключатель */
.app-tabs--pills {
  display: inline-flex;
  padding: 4px;
  border-radius: var(--r-md);
  background: var(--c-surface-sunken);
}

.app-tabs--pills .app-tabs__tab {
  border-radius: var(--r-sm);
}

.app-tabs--pills .app-tabs__tab.is-active {
  background: var(--c-surface);
  color: var(--c-text);
  box-shadow: var(--sh-sm);
}

.app-tabs--pills .app-tabs__tab.is-active .app-tabs__count {
  background: var(--c-accent-100);
  color: var(--c-brand-800);
}

/* underline: табы с подчёркиванием */
.app-tabs--underline {
  gap: 0.5rem;
  border-bottom: 1px solid var(--c-border);
}

.app-tabs--underline .app-tabs__tab {
  padding: 0 0.25rem;
  margin-bottom: -1px;
  border-bottom: 2px solid transparent;
  border-radius: 0;
}

.app-tabs--underline .app-tabs__tab.is-active {
  color: var(--c-brand-800);
  border-bottom-color: var(--c-accent);
}
</style>
