<script setup lang="ts">
import AppButton from './AppButton.vue'
import AppIcon from './AppIcon.vue'

withDefaults(
  defineProps<{
    title?: string
    message?: string
    retryLabel?: string
    retrying?: boolean
    /** Показать кнопку повтора (нужен обработчик @retry) */
    retryable?: boolean
  }>(),
  {
    title: 'Не удалось загрузить данные',
    message: undefined,
    retryLabel: 'Повторить',
    retrying: false,
    retryable: true,
  },
)

defineEmits<{ retry: [] }>()
</script>

<template>
  <div class="error-state" role="alert">
    <AppIcon name="alert-circle" :size="22" class="error-state__icon" />
    <div class="error-state__body">
      <p class="error-state__title">{{ title }}</p>
      <p v-if="message" class="error-state__msg">{{ message }}</p>
      <slot />
    </div>
    <AppButton
      v-if="retryable"
      variant="secondary"
      size="sm"
      icon="refresh"
      :loading="retrying"
      class="error-state__retry"
      @click="$emit('retry')"
    >
      {{ retryLabel }}
    </AppButton>
  </div>
</template>

<style scoped>
.error-state {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  padding: 1rem 1.15rem;
  border: 1px solid rgba(192, 58, 43, 0.25);
  border-radius: var(--r-md);
  background: var(--c-danger-bg);
}

.error-state__icon {
  margin-top: 1px;
  color: var(--c-danger);
}

.error-state__body {
  flex: 1;
  display: grid;
  gap: 0.2rem;
  min-width: 0;
}

.error-state__title {
  font-weight: 700;
  color: var(--c-danger-600);
}

.error-state__msg {
  color: var(--c-text-2);
  font-size: var(--fs-sm);
  overflow-wrap: anywhere;
}

.error-state__retry {
  flex: 0 0 auto;
}

@media (max-width: 520px) {
  .error-state {
    flex-wrap: wrap;
  }

  .error-state__retry {
    margin-left: calc(22px + 0.85rem);
  }
}
</style>
