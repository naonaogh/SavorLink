<script setup lang="ts">
import { computed } from 'vue'
import { icons, type IconName } from './icons'

const props = withDefaults(
  defineProps<{
    name: IconName
    size?: number | string
    strokeWidth?: number
    /** Заливка контура (например, «закрашенное» сердце избранного) */
    filled?: boolean
    /** Подпись для скринридера; без неё иконка декоративная */
    label?: string
  }>(),
  { size: 20, strokeWidth: 2, filled: false, label: undefined },
)

const markup = computed(() => icons[props.name])
const dimension = computed(() => (typeof props.size === 'number' ? `${props.size}px` : props.size))
</script>

<template>
  <!-- v-html: только статичная разметка из icons.ts -->
  <svg
    class="app-icon"
    viewBox="0 0 24 24"
    :width="dimension"
    :height="dimension"
    :fill="filled ? 'currentColor' : 'none'"
    stroke="currentColor"
    :stroke-width="strokeWidth"
    stroke-linecap="round"
    stroke-linejoin="round"
    :role="label ? 'img' : undefined"
    :aria-label="label"
    :aria-hidden="label ? undefined : 'true'"
    focusable="false"
    v-html="markup"
  />
</template>

<style scoped>
.app-icon {
  flex: 0 0 auto;
  display: inline-block;
  vertical-align: middle;
}
</style>
