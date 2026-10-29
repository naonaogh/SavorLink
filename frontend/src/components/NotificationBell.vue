<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import AppIcon from '@/components/ui/AppIcon.vue'

const props = defineProps<{
  count: number
}>()

const badge = computed(() => (props.count > 9 ? '9+' : String(props.count)))
const ariaLabel = computed(() => `Уведомления: ${props.count}`)
</script>

<template>
  <RouterLink
    to="/cabinet/notifications"
    class="bell"
    :class="{ 'bell--unread': count > 0 }"
    :aria-label="ariaLabel"
    title="Уведомления"
  >
    <AppIcon name="bell" :size="20" />
    <span v-if="count > 0" class="bell__count ui-num" aria-hidden="true">{{ badge }}</span>
  </RouterLink>
</template>

<style scoped>
.bell {
  position: relative;
  display: inline-grid;
  place-items: center;
  flex: 0 0 auto;
  width: 44px;
  height: 44px;
  border: 1px solid var(--c-border-strong);
  border-radius: var(--r-sm);
  background: var(--c-surface);
  color: var(--c-text-2);
  transition:
    border-color var(--dur) var(--ease),
    background var(--dur) var(--ease),
    color var(--dur) var(--ease);
}

.bell:hover {
  border-color: var(--c-muted);
  background: var(--c-surface-2);
  color: var(--c-brand-800);
}

.bell--unread {
  color: var(--c-brand-800);
}

.bell__count {
  position: absolute;
  top: -7px;
  right: -7px;
  min-width: 20px;
  height: 20px;
  padding: 0 5px;
  border: 2px solid var(--c-bg);
  border-radius: var(--r-full);
  background: var(--c-accent);
  color: var(--c-brand-950);
  font-size: 0.625rem;
  font-weight: 800;
  line-height: 16px;
  text-align: center;
}
</style>
