import { expect, it } from 'vitest'
import { gold, sellPrice, totalPrice } from './economy'
import type { Config, Item, Point } from './types'

const config = { settlements: { camp: { bonus_kind: 'weapon' }, settlement: { bonus_kind: 'armor' }, city: { bonus_kind: 'other' } } } as Config
it('nalicza 10% także dla tanich nabojów i większych ilości, bez obcinania premii', () => {
  const ammo = { kind: 'other', sell: 1 } as Item
  const city = { settlement: 'city' } as Point
  expect(sellPrice(ammo, city, config)).toBe(1.1)
  expect(totalPrice(sellPrice(ammo, city, config), 99)).toBe(108.9)
  expect(sellPrice(ammo, { settlement: 'camp' } as Point, config)).toBe(1)
  expect(gold(108.9)).toBe('108,9')
})
it('przyznaje premię wyłącznie specjalności danej miejscowości', () => {
  const gun = { kind: 'weapon', sell: 60 } as Item
  expect(sellPrice(gun, { settlement: 'camp' } as Point, config)).toBe(66)
  expect(sellPrice(gun, { settlement: 'settlement' } as Point, config)).toBe(60)
})
