import { describe, expect, it } from 'vitest'
import { meters, formatDistance, usable } from './geo'
describe('odległości i interakcje', () => {
  it('oblicza odległość na rzeczywistej powierzchni Ziemi', () => { expect(meters({lat:52,lng:21},{lat:52.001,lng:21})).toBeCloseTo(111.19, 1) })
  it('formatuje metry i kilometry po polsku', () => { expect(formatDistance(74.6)).toBe('75 m'); expect(formatDistance(1250)).toBe('1,25 km') })
  it('odrzuca starą lub niedokładną pozycję', () => { const f = {lat:52,lng:21,accuracy:10,timestamp:Date.now()/1000,demo:false}; expect(usable(f,45,50)).toBe(true); expect(usable({...f,accuracy:80},45,50)).toBe(false); expect(usable({...f,timestamp:f.timestamp-60},45,50)).toBe(false) })
})
