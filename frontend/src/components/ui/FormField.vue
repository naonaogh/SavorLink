<script setup lang="ts">
import { computed, useId } from 'vue'

const props = withDefaults(
  defineProps<{
    label: string
    hint?: string
    error?: string
    required?: boolean
    /** id поля; если не задан — генерируется */
    id?: string
  }>(),
  { hint: undefined, error: undefined, required: false, id: undefined },
)

const generatedId = useId()
const fieldId = computed(() => props.id ?? generatedId)
const hintId = computed(() => `${fieldId.value}-hint`)
const errorId = computed(() => `${fieldId.value}-error`)
const describedBy = computed(() =>
  [props.error ? errorId.value : null, props.hint ? hintId.value : null].filter(Boolean).join(' ') || undefined,
)
</script>

<template>
  <div class="form-field" :class="{ 'form-field--invalid': !!error }">
    <label :for="fieldId" class="form-field__label">
      {{ label }}<span v-if="required" class="form-field__req" aria-hidden="true">*</span>
    </label>
    <!-- слот получает атрибуты для связки поля с подписью и подсказкой -->
    <slot :id="fieldId" :described-by="describedBy" :invalid="!!error" />
    <p v-if="error" :id="errorId" class="form-field__error" role="alert">{{ error }}</p>
    <p v-else-if="hint" :id="hintId" class="form-field__hint">{{ hint }}</p>
  </div>
</template>

<style scoped>
.form-field {
  display: grid;
  gap: 0.4rem;
  min-width: 0;
}

.form-field__label {
  font-size: var(--fs-sm);
  font-weight: 700;
  color: var(--c-text-2);
}

.form-field__req {
  margin-left: 0.2rem;
  color: var(--c-danger);
}

.form-field__hint {
  font-size: var(--fs-xs);
  color: var(--c-muted);
}

.form-field__error {
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--c-danger);
}
</style>
