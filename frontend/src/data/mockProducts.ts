export type Product = {
  id: number
  supplierId: number
  name: string
  description: string
  pricePerKg: number
  unit: string
  stockKg: number
}

export const mockProducts: Product[] = [
  {
    id: 1,
    supplierId: 1,
    name: 'Помидоры черри',
    description: 'Заказ от 3 кг • Собрано сегодня',
    pricePerKg: 179,
    unit: 'кг',
    stockKg: 48,
  },
  {
    id: 2,
    supplierId: 1,
    name: 'Огурцы тепличные',
    description: 'Заказ от 5 кг • Категория «Стандарт»',
    pricePerKg: 129,
    unit: 'кг',
    stockKg: 40,
  },
  {
    id: 3,
    supplierId: 1,
    name: 'Салат Айсберг',
    description: 'Заказ от 4 кг • Охлажденный',
    pricePerKg: 220,
    unit: 'кг',
    stockKg: 18,
  },
  {
    id: 4,
    supplierId: 1,
    name: 'Картофель молодой',
    description: 'Заказ от 10 кг • Фермерский',
    pricePerKg: 65,
    unit: 'кг',
    stockKg: 120,
  },
]
