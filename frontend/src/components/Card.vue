<script setup lang="ts">
defineProps<{
  tag?: 'div' | 'article' | 'section'
}>()
</script>

<template>
  <component
    :is="tag ?? 'div'"
    class="card"
  >
    <slot />
  </component>
</template>

<style scoped>
.card {
  background: rgba(45, 90, 58, 0.4);
  backdrop-filter: blur(12px);
  border-radius: 1rem;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
