import { useEffect, useRef, useState } from 'react'
import { api } from './api'
import type { Config, Fix, Player } from './types'

export function useLocation(active: boolean, config: Config | null, player: Player | null, fix: Fix | null, setFix: (f: Fix) => void, update: (p: Player) => void) {
  const [geoError, setGeoError] = useState(''), [retry, setRetry] = useState(0)
  const [demo, setDemo] = useState(false)
  const latest = useRef({ player, fix, update, setFix }); latest.current = { player, fix, update, setFix }
  const seq = useRef(0), lastSent = useRef(0), inFlight = useRef(false)
  useEffect(() => {
    if (!active || !config) return
    let stopped = false, watch: number | undefined
    const send = async (f: Fix, force = false) => {
      if (stopped || document.hidden || inFlight.current || (!force && Date.now() - lastSent.current < 7000)) return
      const e = latest.current.player?.expedition
      if (!e?.active) return
      latest.current.setFix(f)
      if (f.accuracy > config.max_accuracy) { setGeoError(`Słaby sygnał GPS: ±${Math.round(f.accuracy)} m. Poczekaj w otwartej przestrzeni.`); return }
      setGeoError(''); inFlight.current = true; lastSent.current = Date.now()
      seq.current = Math.max(seq.current, e.seq) + 1
      try { const p = await api.action({ action: 'location', expedition_id: e.id, seq: seq.current, fix: f }); if (!stopped) latest.current.update(p) }
      catch (error) { if (!stopped) setGeoError(error instanceof Error ? error.message : 'Nie udało się zapisać pozycji.') }
      finally { inFlight.current = false }
    }
    const success = (position: GeolocationPosition) => {
      if (stopped || document.hidden) return
      const f = { lat: position.coords.latitude, lng: position.coords.longitude, accuracy: position.coords.accuracy, timestamp: position.timestamp / 1000, demo: false }
      latest.current.setFix(f); void send(f)
    }
    const error = (e: GeolocationPositionError) => setGeoError(e.code === 1 ? 'Brak zgody na lokalizację. Włącz ją w ustawieniach witryny i spróbuj ponownie.' : e.code === 2 ? 'GPS jest niedostępny. Sprawdź ustawienia telefonu i połączenie.' : 'Oczekiwanie na GPS trwa zbyt długo. Spróbuj ponownie przy lepszym sygnale.')
    const stop = () => { if (watch !== undefined) navigator.geolocation?.clearWatch(watch); watch = undefined }
    const start = () => {
      stop()
      if (document.hidden) return
      if (demo) {
        const f = latest.current.fix
        void send({ lat: f?.lat ?? 52.2297, lng: f?.lng ?? 21.0122, accuracy: 5, timestamp: Date.now() / 1000, demo: true }, true)
      } else if (!navigator.geolocation) setGeoError('Ta przeglądarka nie obsługuje lokalizacji. Wymagane jest HTTPS lub localhost.')
      else {
        setGeoError(''); lastSent.current = 0
        navigator.geolocation.getCurrentPosition(success, error, { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 })
        watch = navigator.geolocation.watchPosition(success, error, { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 })
      }
    }
    start()
    const visibility = () => document.hidden ? stop() : start()
    document.addEventListener('visibilitychange', visibility)
    const timer = window.setInterval(() => { if (demo && !document.hidden) start() }, 10000)
    return () => { stopped = true; stop(); window.clearInterval(timer); document.removeEventListener('visibilitychange', visibility) }
  }, [active, config, demo, retry])
  return { geoError, demo, setDemo, retry: () => setRetry(r => r + 1) }
}

