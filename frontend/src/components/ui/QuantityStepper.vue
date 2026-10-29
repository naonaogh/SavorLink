<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'

const props = withDefaults(
  defineProps<{
    modelValue: number
    min?: number
    max?: number
    step?: number
    unit?: string
    size?: 'sm' | 'md'
    disabled?: boolean
    label?: string
  }>(),
  { min: 1, max: undefined, step: 1, unit: undefined, size: 'md', disabled: false, label: 'Количество' },
)

const emit = defineEmits<{ 'update:modelValue': [value: number] }>()

const clamp = (value: number) => {
  let next = Number.isFinite(value) ? value : props.min
  next = Math.max(props.min, next)
  if (props.max !== undefined) next = Math.min(props.max, next)
  return next
}

const canDecrease = computed(() => !props.disabled && props.modelValue - props.step >= props.min)
const canIncrease = computed(() => !props.disabled && (props.max === undefined || props.modelValue + props.step <= props.max))

const change = (delta: number) => emit('update:modelValue', clamp(props.modelValue + delta))

const onInput = (event: Event) => {
  const raw = (event.target as HTMLInputElement).value
  if (raw === '') return
  emit('update:modelValue', clamp(Number(raw)))
}

const onBlur = (event: Event) => {
  const input = event.target as HTMLInputElement
  input.value = String(clamp(Number(input.value)))
}
</script>

<template>
  <div class="qty" :class="[`qty--${size}`, { 'qty--disabled': disabled }]" role="group" :aria-label="label">
    <button
      type="button"
      class="qty__btn"
      :disabled="!canDecrease"
      :aria-label="`Уменьшить: ${label.toLowerCase()}`"
      @click="change(-step)"
    >
      <AppIcon name="minus" :size="16" />
    </button>
    <label class="qty__field">
      <span class="sr-only">{{ label }}</span>
      <input
        class="qty__input"
        type="number"
        inputmode="numeric"
        :min="min"
        :max="max"
        :step="step"
        :value="modelValue"
        :disabled="disabled"
        @input="onInput"
        @blur="onBlur"
      />
      <span v-if="unit" class="qty__unit" aria-hidden="true">{{ unit }}</span>
    </label>
    <button
      type="button"
      class="qty__btn"
      :disabled="!canIncrease"
      :aria-label="`Увеличить: ${label.toLowerCase()}`"
      @click="change(step)"
    >
      <AppIcon name="plus" :size="16" />
    </button>
  </div>
</template>

<style scoped>
.qty {
  --qty-h: 44px;
  display: inline-flex;
  align-items: stretch;
  height: var(--qty-h);
  border: 1px solid var(--c-border-strong);
  border-radius: var(--r-sm);
  background: var(--c-surface);
  overflow: hidden;
}

.qty:focus-within {
  border-color: var(--c-accent);
  box-shadow: var(--sh-focus);
}

.qty--sm {
  --qty-h: 36px;
}

.qty__btn {
  display: grid;
  place-items: center;
  width: var(--qty-h);
  border: none;
  background: transparent;
  color: var(--c-text-2);
  transition: background var(--dur) var(--ease), color var(--dur) var(--ease);
}

.qty__btn:hover:not(:disabled) {
  background: var(--c-surface-sunken);
  color: var(--c-text);
}

.qty__btn:disabled {
  color: var(--c-placeholder);
  cursor: not-allowed;
}

.qty__field {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  padding: 0 0.25rem;
  border-inline: 1px solid var(--c-border);
}

.qty .qty__input {
  width: 3.25rem;
  min-height: 0;
  height: 100%;
  padding: 0;
  border: none;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  text-align: center;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  -moz-appearance: textfield;
}

.qty .qty__input:focus {
  box-shadow: none;
}

.qty__input::-webkit-outer-spin-button,
.qty__input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.qty__unit {
  padding-right: 0.35rem;
  color: var(--c-muted);
  font-size: var(--fs-sm);
}
</style>
