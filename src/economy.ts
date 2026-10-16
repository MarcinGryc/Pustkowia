import type { Config, Item, Point } from './types'

const goldFormat = new Intl.NumberFormat('pl-PL', { maximumFractionDigits: 1 })
export const gold = (amount: number) => goldFormat.format(amount)
export const settlementInfo = (point: Point, config: Config) => config.settlements[point.settlement || 'settlement']
export const sellPrice = (item: Item, point: Point, config: Config) => item.kind === settlementInfo(point, config).bonus_kind ? Math.round(item.sell * 11) / 10 : item.sell
export const totalPrice = (price: number, quantity: number) => Math.round(price * quantity * 10) / 10
