<script setup lang="ts">
import { computed } from 'vue'
import { initials } from '@/utils/format'

const props = withDefaults(
  defineProps<{
    name?: string | null
    size?: number
    tone?: 'brand' | 'accent' | 'neutral'
  }>(),
  { name: undefined, size: 40, tone: 'brand' },
)

const letters = computed(() => initials(props.name))
</script>

<template>
  <span
    class="app-avatar"
    :class="`app-avatar--${tone}`"
    :style="{ width: `${size}px`, height: `${size}px`, fontSize: `${Math.round(size * 0.36)}px` }"
    aria-hidden="true"
    >{{ letters }}</span
  >
</template>

<style scoped>
.app-avatar {
  display: inline-grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 30%;
  font-weight: 800;
  letter-spacing: 0.02em;
  user-select: none;
}

.app-avatar--brand {
  background: var(--c-brand-800);
  color: var(--c-accent-100);
}

.app-avatar--accent {
  background: var(--c-accent-100);
  color: var(--c-brand-800);
}

.app-avatar--neutral {
  background: var(--c-surface-sunken);
  color: var(--c-text-2);
}
</style>
