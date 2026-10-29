/** Форматирование чисел, цен и дат для интерфейса (локаль ru-RU). */

const numberFormat = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 2 })
const priceFormat = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 2, minimumFractionDigits: 0 })

const toNumber = (value: number | string | null | undefined) => {
  const n = typeof value === 'string' ? Number(value) : value
  return typeof n === 'number' && Number.isFinite(n) ? n : null
}

/** 1060 → «1 060» */
export const formatNumber = (value: number | string | null | undefined, fallback = '—') => {
  const n = toNumber(value)
  return n === null ? fallback : numberFormat.format(n)
}

/** 1060 → «1 060 ₽» */
export const formatPrice = (value: number | string | null | undefined, fallback = '—') => {
  const n = toNumber(value)
  return n === null ? fallback : `${priceFormat.format(n)} ₽`
}

type DateStyle = 'short' | 'long' | 'datetime' | 'time'

const dateOptions: Record<DateStyle, Intl.DateTimeFormatOptions> = {
  short: { day: '2-digit', month: '2-digit', year: 'numeric' },
  long: { day: 'numeric', month: 'long', year: 'numeric' },
  datetime: { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' },
  time: { hour: '2-digit', minute: '2-digit' },
}

/** Дата из API → строка; невалидная дата → fallback */
export const formatDate = (value: string | number | Date | null | undefined, style: DateStyle = 'long', fallback = '—') => {
  if (value === null || value === undefined || value === '') return fallback
  const date = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(date.getTime())) return fallback
  return date.toLocaleString('ru-RU', dateOptions[style])
}

/** pluralize(5, ['товар', 'товара', 'товаров']) → «товаров» */
export const pluralize = (n: number, forms: [string, string, string]) => {
  const abs = Math.abs(n)
  const mod10 = abs % 10
  const mod100 = abs % 100
  if (mod10 === 1 && mod100 !== 11) return forms[0]
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return forms[1]
  return forms[2]
}

/** Инициалы для аватара: «Анна Соколова» → «АС», «ООО «Мясной Двор»» → «МД» */
export const initials = (value: string | null | undefined, fallback = '?') => {
  if (!value) return fallback
  const cleaned = value
    .replace(/[«»"'()]/g, ' ')
    .replace(/(^|\s)(ООО|ОАО|ЗАО|ПАО|АО|ИП)(?=\s|$)/gu, ' ')
    .trim()
  const words = cleaned.split(/[\s@._-]+/).filter(Boolean)
  const letters = words.slice(0, 2).map((w) => w[0]?.toUpperCase() ?? '')
  return letters.join('') || fallback
}
