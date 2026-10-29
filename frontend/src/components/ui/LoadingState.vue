<script setup lang="ts">
withDefaults(
  defineProps<{
    label?: string
    /** spinner — компактный индикатор; skeleton — заглушки строк/карточек */
    variant?: 'spinner' | 'skeleton' | 'cards'
    rows?: number
  }>(),
  { label: 'Загрузка…', variant: 'spinner', rows: 3 },
)
</script>

<template>
  <div class="loading-state" role="status" aria-live="polite" :aria-label="label">
    <template v-if="variant === 'spinner'">
      <span class="loading-state__spinner" aria-hidden="true"></span>
      <span class="loading-state__label">{{ label }}</span>
    </template>

    <div v-else-if="variant === 'cards'" class="loading-state__cards" aria-hidden="true">
      <div v-for="n in rows" :key="n" class="loading-state__card">
        <span class="ui-skeleton" style="height: 120px"></span>
        <span class="ui-skeleton" style="height: 16px; width: 70%"></span>
        <span class="ui-skeleton" style="height: 14px; width: 45%"></span>
      </div>
    </div>

    <div v-else class="loading-state__rows" aria-hidden="true">
      <span v-for="n in rows" :key="n" class="ui-skeleton loading-state__row"></span>
    </div>

    <span v-if="variant !== 'spinner'" class="sr-only">{{ label }}</span>
  </div>
</template>

<style scoped>
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem 1rem;
  color: var(--c-muted);
  font-size: var(--fs-sm);
  font-weight: 600;
}

.loading-state__spinner {
  width: 22px;
  height: 22px;
  border: 2.5px solid var(--c-accent-100);
  border-top-color: var(--c-accent-600);
  border-radius: 50%;
  animation: ls-spin 0.8s linear infinite;
}

@keyframes ls-spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state__rows {
  display: grid;
  gap: 0.75rem;
  width: 100%;
}

.loading-state__row {
  height: 64px;
  border-radius: var(--r-md);
}

.loading-state__cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
  width: 100%;
}

.loading-state__card {
  display: grid;
  gap: 0.6rem;
  padding: 1rem;
  border: 1px solid var(--c-border);
  border-radius: var(--r-lg);
  background: var(--c-surface);
}
</style>
