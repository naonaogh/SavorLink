import type { IconName } from './icons'

export interface TabItem<V extends string | number = string> {
  value: V
  label: string
  count?: number
  icon?: IconName
}
