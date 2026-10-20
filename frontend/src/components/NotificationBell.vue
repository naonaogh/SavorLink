<script setup lang="ts">
import { NotificationIcon } from '@/assets/icons/png'

defineProps<{
  count: number
}>()
</script>

<template>
  <div class="bell-container" :class="{ 'has-unread': count > 0 }">
    <img :src="NotificationIcon" alt="" class="bell-icon" aria-hidden="true" />
    <div v-if="count > 0" class="badge">
      {{ count > 9 ? '9+' : count }}
    </div>
  </div>
</template>

<style scoped>
.bell-container {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  width: 40px;
  height: 40px;
  border-radius: 0;
  background: #fff;
  border: 1px solid var(--sl-line);
  color: var(--sl-ink);
  transition: border-color 0.2s ease, background 0.2s ease;
}

.bell-container:hover {
  border-color: var(--sl-ink);
}

.has-unread {
  border-color: var(--sl-ink);
}

.bell-icon {
  width: 18px;
  height: 18px;
  object-fit: contain;
  /* цветную png-иконку приводим к монохрому, как в сайдбаре */
  filter: grayscale(1) brightness(0.35);
}

.badge {
  position: absolute;
  top: -1px;
  right: -1px;
  transform: translate(45%, -45%);
  min-width: 1.25rem;
  height: 1.25rem;
  padding: 0 0.3rem;
  display: inline-grid;
  place-items: center;
  border-radius: 0;
  background: var(--sl-lime);
  color: var(--sl-ink);
  border: 1px solid var(--sl-ink);
  font-size: 0.68rem;
  font-weight: 800;
  line-height: 1;
}
</style>
