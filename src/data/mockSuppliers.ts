export type Supplier = {
  id: number
  name: string
  rating: number
  reviews: number
  company: string
  locations: string
  since: string
  minOrder: string
  delivery: string
  description: string
}

export const mockSuppliers: Supplier[] = [
  {
    id: 1,
    name: 'ООО "Оазис"',
    rating: 4.8,
    reviews: 312,
    company: 'ООО "Оазис"',
    locations: 'Москва, Санкт‑Петербург, Казань',
    since: '2015 года',
    minOrder: 'от 50 000 ₽',
    delivery: '1–3 дня по Москве, 5–14 дней по России',
    description: 'Оптовые поставки продуктов питания по всей России с 2015 года.',
  },
  {
    id: 2,
    name: 'Fresh Market',
    rating: 4.6,
    reviews: 198,
    company: 'Fresh Market',
    locations: 'Краснодар, Ростов‑на‑Дону',
    since: '2018 года',
    minOrder: 'от 30 000 ₽',
    delivery: '2–5 дней по России',
    description: 'Свежие овощи и фрукты, ежедневные поставки.',
  },
  {
    id: 3,
    name: 'Мясной Дом',
    rating: 4.7,
    reviews: 154,
    company: 'Мясной Дом',
    locations: 'Москва, МО',
    since: '2012 года',
    minOrder: 'от 70 000 ₽',
    delivery: '1–4 дня по Москве и области',
    description: 'Охлажденное и фермерское мясо для ресторанов.',
  },
  {
    id: 4,
    name: 'Морепродукты 24',
    rating: 4.5,
    reviews: 87,
    company: 'Морепродукты 24',
    locations: 'Санкт‑Петербург',
    since: '2019 года',
    minOrder: 'от 40 000 ₽',
    delivery: '2–6 дней по России',
    description: 'Морепродукты из проверенных хозяйств.',
  },
]

