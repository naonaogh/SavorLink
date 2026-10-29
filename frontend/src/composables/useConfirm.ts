import { reactive } from 'vue'

export interface ConfirmOptions {
  title: string
  message?: string
  confirmLabel?: string
  cancelLabel?: string
  /** danger — красная кнопка подтверждения (удаление, отклонение) */
  tone?: 'default' | 'danger'
}

interface ConfirmState extends Required<Omit<ConfirmOptions, 'message'>> {
  open: boolean
  message?: string
}

const state = reactive<ConfirmState>({
  open: false,
  title: '',
  message: undefined,
  confirmLabel: 'Подтвердить',
  cancelLabel: 'Отмена',
  tone: 'default',
})

let resolver: ((value: boolean) => void) | null = null

const settle = (value: boolean) => {
  state.open = false
  resolver?.(value)
  resolver = null
}

/**
 * Диалог подтверждения вместо window.confirm (выводит ConfirmHost в App.vue).
 *   if (!(await confirm({ title: 'Удалить товар?', tone: 'danger' }))) return
 */
export function useConfirm() {
  const confirm = (options: ConfirmOptions) => {
    resolver?.(false)
    Object.assign(state, {
      confirmLabel: 'Подтвердить',
      cancelLabel: 'Отмена',
      tone: 'default',
      message: undefined,
      ...options,
      open: true,
    })
    return new Promise<boolean>((resolve) => {
      resolver = resolve
    })
  }

  return { confirm, state, settle }
}
