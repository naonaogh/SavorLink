<script setup lang="ts">
import AppButton from './AppButton.vue'
import AppModal from './AppModal.vue'
import { useConfirm } from '@/composables/useConfirm'

const { state, settle } = useConfirm()
</script>

<template>
  <AppModal :open="state.open" :title="state.title" size="sm" @update:open="(value) => !value && settle(false)">
    <p v-if="state.message" class="confirm__msg">{{ state.message }}</p>
    <template #footer>
      <AppButton variant="secondary" @click="settle(false)">{{ state.cancelLabel }}</AppButton>
      <AppButton :variant="state.tone === 'danger' ? 'danger' : 'primary'" autofocus @click="settle(true)">
        {{ state.confirmLabel }}
      </AppButton>
    </template>
  </AppModal>
</template>

<style scoped>
.confirm__msg {
  color: var(--c-text-2);
}
</style>
