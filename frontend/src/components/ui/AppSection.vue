<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string
    description?: string
    /** Без внутренних отступов у тела (для таблиц/списков во всю ширину) */
    flush?: boolean
  }>(),
  { title: undefined, description: undefined, flush: false },
)
</script>

<template>
  <section class="app-section ui-card">
    <header v-if="title || $slots.actions" class="app-section__head">
      <div class="app-section__titles">
        <h2 v-if="title" class="app-section__title">{{ title }}</h2>
        <p v-if="description" class="app-section__desc">{{ description }}</p>
      </div>
      <div v-if="$slots.actions" class="app-section__actions"><slot name="actions" /></div>
    </header>
    <div class="app-section__body" :class="{ 'app-section__body--flush': flush }">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.app-section {
  min-width: 0;
}

.app-section__head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem 1rem;
  padding: 1.1rem clamp(1.1rem, 2.5vw, 1.5rem);
  border-bottom: 1px solid var(--c-border);
}

.app-section__titles {
  display: grid;
  gap: 0.2rem;
  min-width: 0;
}

.app-section__title {
  font-size: var(--fs-lg);
}

.app-section__desc {
  color: var(--c-muted);
  font-size: var(--fs-sm);
}

.app-section__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.app-section__body {
  padding: clamp(1.1rem, 2.5vw, 1.5rem);
}

.app-section__body--flush {
  padding: 0;
}
</style>
