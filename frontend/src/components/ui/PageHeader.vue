<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'
import AppButton from './AppButton.vue'

withDefaults(
  defineProps<{
    title: string
    eyebrow?: string
    description?: string
    /** Ссылка «назад» над заголовком */
    backTo?: RouteLocationRaw
    backLabel?: string
  }>(),
  { eyebrow: undefined, description: undefined, backTo: undefined, backLabel: 'Назад' },
)
</script>

<template>
  <header class="page-header">
    <AppButton v-if="backTo" :to="backTo" variant="ghost" size="sm" icon="arrow-left" class="page-header__back">
      {{ backLabel }}
    </AppButton>

    <div class="page-header__row">
      <div class="page-header__text">
        <p v-if="eyebrow" class="ui-eyebrow">{{ eyebrow }}</p>
        <h1 class="page-header__title">{{ title }}</h1>
        <p v-if="description" class="page-header__desc">{{ description }}</p>
        <slot />
      </div>
      <div v-if="$slots.actions" class="page-header__actions">
        <slot name="actions" />
      </div>
    </div>
  </header>
</template>

<style scoped>
.page-header {
  display: grid;
  gap: 0.75rem;
}

.page-header__back {
  justify-self: start;
  margin-left: -0.6rem;
}

.page-header__row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem 1.5rem;
}

.page-header__text {
  display: grid;
  gap: 0.4rem;
  min-width: 0;
  max-width: 760px;
}

.page-header__title {
  font-size: var(--fs-3xl);
  overflow-wrap: anywhere;
}

.page-header__desc {
  color: var(--c-muted);
  font-size: var(--fs-md);
}

.page-header__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

@media (max-width: 640px) {
  .page-header__actions {
    width: 100%;
  }

  .page-header__actions > :deep(*) {
    flex: 1 1 auto;
  }
}
</style>
