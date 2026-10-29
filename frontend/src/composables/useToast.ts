import { reactive } from 'vue'

export type ToastTone = 'success' | 'error' | 'info'

export interface Toast {
  id: number
  tone: ToastTone
  title: string
  message?: string
}

const toasts = reactive<Toast[]>([])
let nextId = 1

const dismiss = (id: number) => {
  const index = toasts.findIndex((t) => t.id === id)
  if (index !== -1) toasts.splice(index, 1)
}

const push = (tone: ToastTone, title: string, message?: string, timeout = 4000) => {
  const id = nextId++
  toasts.push({ id, tone, title, message })
  if (toasts.length > 4) toasts.shift()
  if (timeout > 0) window.setTimeout(() => dismiss(id), timeout)
  return id
}

/** Короткие уведомления об успехе/ошибке действия (выводит ToastHost в App.vue). */
export function useToast() {
  return {
    toasts,
    dismiss,
    success: (title: string, message?: string) => push('success', title, message),
    error: (title: string, message?: string) => push('error', title, message, 6000),
    info: (title: string, message?: string) => push('info', title, message),
  }
}
