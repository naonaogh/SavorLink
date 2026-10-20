import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

/** Значение `?reason=` для страницы входа: гость пытался сделать действие, доступное только после входа. */
export const AUTH_REQUIRED_REASON = 'auth_required'

/**
 * Возвращает функцию-проверку для действий, доступных только авторизованным
 * (корзина, избранное). Если пользователь не вошёл — отправляет его на
 * регистрацию с пояснением и адресом возврата и возвращает false.
 */
export function useRequireAuth() {
  const router = useRouter()
  const route = useRoute()
  const authStore = useAuthStore()

  return (): boolean => {
    if (authStore.token) return true

    router.push({
      path: '/auth',
      query: { mode: 'register', reason: AUTH_REQUIRED_REASON, redirect: route.fullPath },
    })
    return false
  }
}
