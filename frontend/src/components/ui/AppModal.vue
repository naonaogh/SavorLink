<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, useId, watch } from 'vue'
import AppIcon from './AppIcon.vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title: string
    description?: string
    size?: 'sm' | 'md' | 'lg'
    /** Запретить закрытие по фону/Esc (например, во время отправки) */
    persistent?: boolean
  }>(),
  { description: undefined, size: 'md', persistent: false },
)

const emit = defineEmits<{ 'update:open': [value: boolean]; close: [] }>()

const titleId = useId()
const descId = useId()
const dialogRef = ref<HTMLElement | null>(null)
let lastFocused: HTMLElement | null = null

const close = () => {
  if (props.persistent) return
  emit('update:open', false)
  emit('close')
}

const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

const onKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    event.stopPropagation()
    close()
    return
  }
  // удерживаем фокус внутри окна
  if (event.key === 'Tab' && dialogRef.value) {
    const items = Array.from(dialogRef.value.querySelectorAll<HTMLElement>(FOCUSABLE))
    if (items.length === 0) return
    const first = items[0]!
    const last = items[items.length - 1]!
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault()
      last.focus()
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault()
      first.focus()
    }
  }
}

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      lastFocused = document.activeElement as HTMLElement | null
      document.body.style.overflow = 'hidden'
      await nextTick()
      const target =
        dialogRef.value?.querySelector<HTMLElement>('[autofocus]') ??
        dialogRef.value?.querySelector<HTMLElement>('.app-modal__body ' + FOCUSABLE.split(', ').join(', .app-modal__body ')) ??
        dialogRef.value
      target?.focus()
    } else {
      document.body.style.overflow = ''
      lastFocused?.focus?.()
    }
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  if (props.open) document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <Transition name="app-modal">
      <div v-if="open" class="app-modal" @keydown="onKeydown">
        <div class="app-modal__backdrop" aria-hidden="true" @click="close"></div>
        <div
          ref="dialogRef"
          class="app-modal__dialog"
          :class="`app-modal__dialog--${size}`"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
          :aria-describedby="description ? descId : undefined"
          tabindex="-1"
        >
          <header class="app-modal__header">
            <div class="app-modal__titles">
              <h2 :id="titleId" class="app-modal__title">{{ title }}</h2>
              <p v-if="description" :id="descId" class="app-modal__desc">{{ description }}</p>
            </div>
            <button
              v-if="!persistent"
              type="button"
              class="app-modal__close"
              aria-label="Закрыть"
              title="Закрыть"
              @click="close"
            >
              <AppIcon name="x" :size="20" />
            </button>
          </header>

          <div class="app-modal__body">
            <slot />
          </div>

          <footer v-if="$slots.footer" class="app-modal__footer">
            <slot name="footer" />
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.app-modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: 1rem;
}

.app-modal__backdrop {
  position: absolute;
  inset: 0;
  background: rgba(11, 31, 23, 0.45);
  backdrop-filter: blur(2px);
}

.app-modal__dialog {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-height: calc(100dvh - 2rem);
  background: var(--c-surface);
  border-radius: var(--r-xl);
  box-shadow: var(--sh-lg);
  outline: none;
}

.app-modal__dialog--sm {
  max-width: 420px;
}

.app-modal__dialog--md {
  max-width: 560px;
}

.app-modal__dialog--lg {
  max-width: 760px;
}

.app-modal__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.35rem 1.5rem 0.75rem;
}

.app-modal__titles {
  display: grid;
  gap: 0.3rem;
  min-width: 0;
}

.app-modal__title {
  font-size: var(--fs-xl);
}

.app-modal__desc {
  color: var(--c-muted);
  font-size: var(--fs-sm);
}

.app-modal__close {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  margin: -0.25rem -0.5rem 0 0;
  border: none;
  border-radius: var(--r-sm);
  background: transparent;
  color: var(--c-muted);
  transition: background var(--dur) var(--ease), color var(--dur) var(--ease);
}

.app-modal__close:hover {
  background: var(--c-surface-sunken);
  color: var(--c-text);
}

.app-modal__body {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 1.5rem 1.25rem;
}

.app-modal__footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.6rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--c-border);
  background: var(--c-surface-2);
  border-radius: 0 0 var(--r-xl) var(--r-xl);
}

/* анимация */
.app-modal-enter-active,
.app-modal-leave-active {
  transition: opacity 0.18s var(--ease);
}

.app-modal-enter-active .app-modal__dialog,
.app-modal-leave-active .app-modal__dialog {
  transition: transform 0.22s var(--ease);
}

.app-modal-enter-from,
.app-modal-leave-to {
  opacity: 0;
}

.app-modal-enter-from .app-modal__dialog,
.app-modal-leave-to .app-modal__dialog {
  transform: translateY(12px) scale(0.98);
}

@media (max-width: 560px) {
  .app-modal {
    align-items: end;
    padding: 0;
  }

  .app-modal__dialog {
    max-width: none;
    max-height: 92dvh;
    border-radius: var(--r-xl) var(--r-xl) 0 0;
  }

  .app-modal__footer {
    border-radius: 0;
  }

  .app-modal__footer > :deep(*) {
    flex: 1 1 auto;
  }
}
</style>
