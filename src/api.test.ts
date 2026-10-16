import { afterEach, expect, it, vi } from 'vitest'
import { api } from './api'
afterEach(() => vi.unstubAllGlobals())
it('ponawia przerwaną operację z tym samym kluczem, a potem pobiera świeży stan', async () => {
  const fetchMock = vi.fn().mockRejectedValueOnce(new TypeError('network')).mockResolvedValueOnce(new Response(JSON.stringify({ok:true}))).mockResolvedValueOnce(new Response(JSON.stringify({player:{gold:75}})))
  vi.stubGlobal('fetch', fetchMock)
  const p = await api.action({action:'buy', item:'medkit', quantity:1})
  expect(p.gold).toBe(75)
  const first = JSON.parse(fetchMock.mock.calls[0][1].body)
  const retry = JSON.parse(fetchMock.mock.calls[1][1].body)
  expect(first.key).toBeTruthy()
  expect(retry).toEqual(first)
  expect(fetchMock.mock.calls[2][0]).toBe('/api/me')
})
it('pokazuje polski komunikat przy błędzie sieci', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
  await expect(api.bootstrap()).rejects.toThrow('Brak połączenia z serwerem')
})
