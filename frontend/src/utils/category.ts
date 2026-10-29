import type { IconName } from '@/components/ui/icons'

/**
 * Иконка категории товара по её названию.
 * У товаров в backend нет фотографий, поэтому вместо выдуманных фото
 * показываем аккуратную иконку категории.
 */
const RULES: { test: RegExp; icon: IconName }[] = [
  { test: /овощ|зелен|салат/i, icon: 'carrot' },
  { test: /фрукт|ягод/i, icon: 'apple' },
  { test: /мяс|птиц|колбас/i, icon: 'beef' },
  { test: /рыб|море/i, icon: 'fish' },
  { test: /молоч|сыр|молок/i, icon: 'milk' },
  { test: /кофе|чай/i, icon: 'coffee' },
  { test: /напит|сок|вод/i, icon: 'cup-soda' },
]

export const categoryIcon = (name: string | null | undefined): IconName => {
  if (!name) return 'package'
  return RULES.find((rule) => rule.test.test(name))?.icon ?? 'package'
}
