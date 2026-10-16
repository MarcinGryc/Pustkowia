import type { Fix } from './types'
export function meters(a: { lat: number; lng: number }, b: { lat: number; lng: number }) {
  const rad = Math.PI / 180, dlat = (b.lat - a.lat) * rad, dlng = (b.lng - a.lng) * rad
  const h = Math.sin(dlat / 2) ** 2 + Math.cos(a.lat * rad) * Math.cos(b.lat * rad) * Math.sin(dlng / 2) ** 2
  return 12742000 * Math.asin(Math.min(1, Math.sqrt(h)))
}
export const formatDistance = (m: number) => m < 1000 ? `${Math.round(m)} m` : `${(m / 1000).toFixed(2).replace('.', ',')} km`
export function usable(fix: Fix | null, maxAge: number, maxAccuracy: number) { const age = fix ? Date.now() / 1000 - fix.timestamp : Infinity; return !!fix && age >= -5 && age < maxAge && fix.accuracy > 0 && fix.accuracy <= maxAccuracy }
