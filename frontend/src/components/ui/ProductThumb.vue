<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import { categoryIcon } from '@/utils/category'

const props = withDefaults(
  defineProps<{
    /** Название категории — по нему выбирается иконка */
    category?: string | null
    size?: 'sm' | 'md' | 'lg' | 'fill'
  }>(),
  { category: undefined, size: 'md' },
)

const icon = computed(() => categoryIcon(props.category))

/* мягкие тёплые подложки — своя для каждой группы товаров */
const TINTS: Record<string, string> = {
  carrot: '#fdf0e3',
  apple: '#fdecea',
  beef: '#fbeae6',
  fish: '#e8f1f8',
  milk: '#eef2f7',
  coffee: '#f4ece4',
  'cup-soda': '#fff5df',
  package: '#f1eee7',
}
const tint = computed(() => TINTS[icon.value] ?? TINTS.package)
const iconSize = computed(() => ({ sm: 18, md: 24, lg: 36, fill: 40 })[props.size])
</script>

<template>
  <span class="thumb" :class="`thumb--${size}`" :style="{ background: tint }" aria-hidden="true">
    <AppIcon :name="icon" :size="iconSize" :stroke-width="1.6" />
  </span>
</template>

<style scoped>
.thumb {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: var(--r-md);
  color: var(--c-brand-700);
}

.thumb--sm {
  width: 40px;
  height: 40px;
  border-radius: var(--r-sm);
}

.thumb--md {
  width: 56px;
  height: 56px;
}

.thumb--lg {
  width: 88px;
  height: 88px;
  border-radius: var(--r-lg);
}

.thumb--fill {
  width: 100%;
  aspect-ratio: 16 / 10;
  border-radius: var(--r-md);
}
</style>
