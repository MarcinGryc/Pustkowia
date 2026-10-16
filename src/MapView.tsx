import { useEffect, useRef, useState } from 'react'
import * as maplibregl from 'maplibre-gl'
import { Crosshair, LoaderCircle, LocateFixed, MapPin, Navigation, Radio, Search, Shield, Skull, Sun, X } from 'lucide-react'
import 'maplibre-gl/dist/maplibre-gl.css'
import { formatDistance, meters, usable } from './geo'
import type { Config, Fix, Player, Point } from './types'

type Props = { config: Config; player: Player; fix: Fix | null; setFix: (f: Fix) => void; update: (p: Player) => void; onPoint: (p: Point) => void; onBack: () => void; onSearch: () => Promise<boolean>; busy: boolean; report: (s: string) => void }

export default function MapView({ config, player, fix, setFix, onPoint, onBack, onSearch, busy, report, demo, setDemo, geoError, retry }: Props & { demo: boolean; setDemo: (x: boolean) => void; geoError: string; retry: () => void }) {
  const node = useRef<HTMLDivElement>(null), map = useRef<maplibregl.Map | null>(null), playerMarker = useRef<maplibregl.Marker | null>(null)
  const markers = useRef<maplibregl.Marker[]>([]), centered = useRef(false)
  const [selected, setSelected] = useState<string | null>(null), [mapError, setMapError] = useState(''), [awake, setAwake] = useState(false)
  const [searching, setSearching] = useState(false)
  const [coords, setCoords] = useState({ lat: String(fix?.lat ?? 52.2297), lng: String(fix?.lng ?? 21.0122) })
  const wake = useRef<{ release: () => Promise<void>; addEventListener: (s: string, f: () => void) => void } | null>(null)
  const current = useRef({ demo, setFix }); current.current = { demo, setFix }
  useEffect(() => {
    if (!node.current) return
    let instance: maplibregl.Map
    try {
      instance = new maplibregl.Map({ container: node.current, center: [fix?.lng ?? 21.0122, fix?.lat ?? 52.2297], zoom: 15, attributionControl: { compact: true },
        style: config.map_style || { version: 8, sources: { osm: { type: 'raster', tiles: [config.map_tiles], tileSize: 256, attribution: `<a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">${config.map_attribution.replace(/[<>]/g, '')}</a>` } }, layers: [{ id: 'streets', type: 'raster', source: 'osm', paint: { 'raster-saturation': -.8, 'raster-brightness-max': .42, 'raster-brightness-min': .06 } }] } })
      map.current = instance
      instance.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right')
      instance.on('error', () => setMapError('Nie udało się wczytać części mapy. Sprawdź połączenie lub konfigurację dostawcy. Lista miejsc pozostaje dostępna.'))
      instance.on('click', e => { if (current.current.demo) { current.current.setFix({ lat: e.lngLat.lat, lng: e.lngLat.lng, accuracy: 5, timestamp: Date.now() / 1000, demo: true }); setCoords({ lat: e.lngLat.lat.toFixed(6), lng: e.lngLat.lng.toFixed(6) }) } })
    } catch { setMapError('Nie można uruchomić mapy WebGL. Skorzystaj z listy miejsc poniżej.') }
    return () => { instance?.remove(); map.current = null; playerMarker.current = null; markers.current = []; centered.current = false }
  }, [config])
  useEffect(() => {
    if (!fix || !map.current) return
    if (!playerMarker.current) {
      const el = document.createElement('div'); el.className = 'player-marker'; el.setAttribute('aria-label', 'Twoja pozycja')
      playerMarker.current = new maplibregl.Marker({ element: el }).setLngLat([fix.lng, fix.lat]).addTo(map.current)
    }
    playerMarker.current.setLngLat([fix.lng, fix.lat])
    if (!centered.current) { map.current.jumpTo({ center: [fix.lng, fix.lat] }); centered.current = true }
  }, [fix])
  useEffect(() => {
    if (!map.current) return
    markers.current.forEach(m => m.remove())
    markers.current = player.points.map(p => {
      const el = document.createElement('button'); el.className = `point-marker ${p.type}`; el.textContent = p.type === 'city' ? '⌂' : '☠'; el.setAttribute('aria-label', p.name)
      el.onclick = e => { e.stopPropagation(); setSelected(p.id) }
      return new maplibregl.Marker({ element: el }).setLngLat([p.lng, p.lat]).addTo(map.current!)
    })
  }, [player.points])
  useEffect(() => () => { void wake.current?.release() }, [])
  const toggleWake = async () => {
    if (wake.current) { await wake.current.release(); wake.current = null; setAwake(false); return }
    try {
      const n = navigator as unknown as { wakeLock?: { request: (s: string) => Promise<NonNullable<typeof wake.current>> } }
      if (!n.wakeLock) { report('Ta przeglądarka nie obsługuje utrzymania ekranu.'); return }
      wake.current = await n.wakeLock.request('screen'); setAwake(true); wake.current.addEventListener('release', () => { wake.current = null; setAwake(false) })
    } catch { report('Nie udało się utrzymać ekranu. Wyłącz tryb oszczędzania baterii i spróbuj ponownie.') }
  }
  const fresh = usable(fix, config.location_max_age, config.max_accuracy)
  const p = player.points.find(p => p.id === selected)
  const demoMove = (point: Point) => { setFix({ lat: point.lat, lng: point.lng, accuracy: 5, timestamp: Date.now() / 1000, demo: true }); setCoords({ lat: point.lat.toFixed(6), lng: point.lng.toFixed(6) }) }
  return <>
    <div className="page-title expedition-heading"><div><span className="eyebrow"><span className="live-dot"/> WYPRAWA W TOKU</span><h1>Poza schronieniem<span>.</span></h1><p>Każda droga kryje nową historię.</p></div><button className="button secondary end-expedition" disabled={busy} onClick={onBack}><X size={23}/> Zakończ wyprawę</button></div>
    <section className="search-panel panel"><button className="button primary search-button" disabled={busy || searching || !fresh} onClick={async () => { setSearching(true); try { if (await onSearch()) { setSelected(null); if (fix) map.current?.flyTo({ center: [fix.lng, fix.lat], zoom: 14 }) } } finally { setSearching(false) } }}>{searching ? <LoaderCircle className="spin" size={25}/> : <Search size={25}/>}<span>{searching ? 'SZUKAM…' : 'SZUKAJ'}<small>LOSUJ NOWE LOKALIZACJE</small></span></button><p>{fresh ? 'Nowa okolica? Odkryj 7 nowych miejsc wokół swojej aktualnej pozycji.' : 'Poczekaj na świeżą pozycję GPS, aby wyszukać miejsca w okolicy.'}</p></section>
    <div className="map-layout"><section className="map-panel panel"><div ref={node} className="map-canvas"/><div className="map-tag"><Radio size={15}/>{fix ? `GPS ±${Math.round(fix.accuracy)} m` : 'Szukam sygnału GPS…'}{demo && <b>DEMO</b>}</div><div className="map-controls"><button className="icon-button" title="Wycentruj mapę" aria-label="Wycentruj mapę" onClick={() => { if (fix) map.current?.flyTo({ center: [fix.lng, fix.lat], zoom: 16 }); else retry() }}><LocateFixed size={20}/></button><button className={`icon-button ${awake ? 'active' : ''}`} title="Utrzymaj ekran" aria-label="Utrzymaj ekran" onClick={() => void toggleWake()}><Sun size={20}/></button></div><div className="map-legend"><span><i className="dot green"/>Ty</span><span><i className="dot lime"/>Osada</span><span><i className="dot orange"/>Zagrożenie</span></div></section>
    <aside className="expedition-sidebar"><div className="distance-card panel"><Navigation size={21}/><div><span className="eyebrow">DYSTANS WYPRAWY</span><strong>{formatDistance(player.expedition?.distance ?? 0)}</strong><small>Dzisiaj: {formatDistance(player.today_distance)}</small>{!!player.expedition?.estimated && <small>W tym szacowane: {formatDistance(player.expedition.estimated)}</small>}</div></div>
    {geoError && <div className="notice warning" role="alert">{geoError}<button onClick={retry}>Ponów GPS</button></div>}{!fix && !geoError && <div className="notice">Zezwól na lokalizację w przeglądarce. Pierwsze połączenie z GPS może chwilę potrwać.</div>}{fix && !fresh && <div className="notice warning">Pomiar jest niedokładny lub nieaktualny. Interakcje wymagają świeżego GPS.</div>}{mapError && <div className="notice warning">{mapError}</div>}
    {player.points[0]?.source === 'demonstration' && <div className="notice warning"><b>Świat demonstracyjny</b><br/>Punkty są przykładowe. Nie potwierdzono dojścia — mogą leżeć w niedostępnym miejscu. Nie kieruj się do nich w terenie.</div>}{player.points[0]?.source === 'osm_paths' && <div className="notice">Miejsca przy ścieżkach OSM. Dane nie gwarantują bezpiecznego ani publicznego dojścia. Przestrzegaj oznaczeń w terenie.</div>}
    <div className="section-label">W TWOJEJ OKOLICY <span>{player.points.length} MIEJSC</span></div><div className="places">{!player.points.length && <div className="panel empty"><MapPin/>Czekamy na dokładną lokalizację, aby odkryć okolicę.</div>}{player.points.map(point => {
      const d = fix ? meters(fix, point) : Infinity, cooling = point.cooldown_until > Date.now() / 1000
      return <button className={`place panel ${selected === point.id ? 'selected' : ''}`} key={point.id} onClick={() => setSelected(point.id)}><span className={`place-icon ${point.type}`}>{point.type === 'city' ? <Shield size={20}/> : <Skull size={20}/>}</span><span><small>{point.type === 'city' ? 'BEZPIECZNA OSADA' : 'SPOT POTWORÓW'}</small><b>{point.name}</b><small>{cooling ? `Odnowienie: ${Math.ceil((point.cooldown_until - Date.now() / 1000) / 60)} min` : fresh && d <= config.interaction_radius ? 'W zasięgu interakcji' : 'Poza zasięgiem'}</small></span><span className="place-distance">{fix ? formatDistance(d) : '—'}</span></button>
    })}</div></aside></div>
    <p className="fine-print">Dystans jest przybliżony. Zliczamy pomiary wyłącznie przy widocznej stronie; po przerwie możliwy jest szacowany odcinek w linii prostej. Zablokowany telefon nie oznacza aktywnego śledzenia.</p>
    {config.demo_enabled && <section className="demo-panel panel"><div><span className="eyebrow">NARZĘDZIA DEVELOPERSKIE</span><h3>Pozycja demonstracyjna</h3></div><label className="toggle"><input type="checkbox" checked={demo} onChange={e => setDemo(e.target.checked)}/> Włącz DEMO</label>{demo && <><p>Kliknij mapę, wybierz miejsce albo podaj współrzędne. To pozycja testowa.</p><div className="coordinate-fields"><label>Szerokość<input type="number" step="any" value={coords.lat} onChange={e => setCoords({ ...coords, lat: e.target.value })}/></label><label>Długość<input type="number" step="any" value={coords.lng} onChange={e => setCoords({ ...coords, lng: e.target.value })}/></label><button className="button secondary" onClick={() => { const lat = Number(coords.lat), lng = Number(coords.lng); if (coords.lat && coords.lng && Number.isFinite(lat) && Number.isFinite(lng) && Math.abs(lat) <= 85 && Math.abs(lng) <= 180) { setFix({ lat, lng, accuracy: 5, timestamp: Date.now() / 1000, demo: true }); retry() } else report('Podaj poprawne współrzędne (szerokość do ±85°).') }}>Ustaw pozycję</button></div></>}</section>}
    {p && <div className="modal-backdrop" onClick={() => setSelected(null)}><section className="modal panel" role="dialog" aria-modal="true" aria-label={p.name} onClick={e => e.stopPropagation()}><button className="close icon-button" aria-label="Zamknij" onClick={() => setSelected(null)}><X/></button><div className={`large-place-icon ${p.type}`}>{p.type === 'city' ? <Shield size={34}/> : <Skull size={34}/>}</div><span className="eyebrow">{p.type === 'city' ? 'OSADA' : 'ZAGROŻENIE'}</span><h2>{p.name}</h2><p>{fix ? formatDistance(meters(fix, p)) : 'Brak pozycji'} od Ciebie · zasięg {config.interaction_radius} m</p>{p.cooldown_until > Date.now() / 1000 ? <div className="notice">Odnowienie za {Math.ceil((p.cooldown_until - Date.now() / 1000) / 60)} min</div> : <button className="button primary full" disabled={!fresh || !fix || meters(fix, p) > config.interaction_radius} onClick={() => onPoint(p)}>{p.type === 'city' ? 'Wejdź do osady' : 'Zbadaj miejsce'} <Navigation size={17}/></button>}{demo && <button className="button secondary full" onClick={() => { demoMove(p); retry(); setSelected(null) }}><Crosshair size={17}/> DEMO: ustaw pozycję tutaj</button>}</section></div>}
  </>
}
