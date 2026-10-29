<script setup lang="ts">
import { computed } from 'vue'
import AppBadge from './AppBadge.vue'
import { getOrderStatus } from '@/utils/orderStatus'

const props = withDefaults(
  defineProps<{
    status: string
    perspective?: 'buyer' | 'supplier'
    size?: 'sm' | 'md'
  }>(),
  { perspective: 'buyer', size: 'md' },
)

const meta = computed(() => getOrderStatus(props.status, props.perspective))
</script>

<template>
  <AppBadge :tone="meta.tone" :icon="meta.icon" :size="size">{{ meta.label }}</AppBadge>
</template>
