import type { IconName } from '@/components/ui/icons'

/** Статусы заказа из backend (OrderStatus). */
export type OrderStatusCode = 'CREATED' | 'CONFIRMED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'

export type StatusTone = 'neutral' | 'info' | 'warning' | 'success' | 'danger' | 'brand'

export interface OrderStatusMeta {
  label: string
  tone: StatusTone
  icon: IconName
}

type Perspective = 'buyer' | 'supplier'

/** Подписи статусов: покупатель и поставщик видят заказ со своей стороны. */
const STATUS_META: Record<Perspective, Record<OrderStatusCode, OrderStatusMeta>> = {
  buyer: {
    CREATED: { label: 'На рассмотрении', tone: 'warning', icon: 'clock' },
    CONFIRMED: { label: 'Принят в работу', tone: 'info', icon: 'check' },
    IN_PROGRESS: { label: 'В пути', tone: 'brand', icon: 'truck' },
    COMPLETED: { label: 'Доставлен', tone: 'success', icon: 'check-circle' },
    CANCELLED: { label: 'Отклонён поставщиком', tone: 'danger', icon: 'x-circle' },
  },
  supplier: {
    CREATED: { label: 'Новый запрос', tone: 'warning', icon: 'inbox' },
    CONFIRMED: { label: 'Подтверждён', tone: 'info', icon: 'check' },
    IN_PROGRESS: { label: 'В процессе', tone: 'brand', icon: 'truck' },
    COMPLETED: { label: 'Завершён', tone: 'success', icon: 'check-circle' },
    CANCELLED: { label: 'Отклонён', tone: 'danger', icon: 'x-circle' },
  },
}

export const isOrderStatus = (value: string): value is OrderStatusCode =>
  value in STATUS_META.buyer

/** Метаданные статуса; неизвестный код показываем как есть, нейтрально. */
export const getOrderStatus = (status: string, perspective: Perspective = 'buyer'): OrderStatusMeta =>
  isOrderStatus(status)
    ? STATUS_META[perspective][status]
    : { label: status, tone: 'neutral', icon: 'info' }

export const ACTIVE_ORDER_STATUSES: OrderStatusCode[] = ['CREATED', 'CONFIRMED', 'IN_PROGRESS']
export const CLOSED_ORDER_STATUSES: OrderStatusCode[] = ['COMPLETED', 'CANCELLED']
