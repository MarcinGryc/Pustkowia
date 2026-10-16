import { useId } from 'react'
import type { Player } from './types'

type Equipment = Player['equipment']
const armorNames: Record<string, string> = { jacket: 'zniszczona kurtka', leather_jacket: 'skórzana kurtka', scrap_armor: 'pancerz ze złomu', bulletproof_vest: 'kamizelka kuloodporna', heavy_armor: 'ciężki pancerz', exoskeleton: 'egzoszkielet' }
const weaponNames: Record<string, string> = { knife: 'zardzewiały nóż', club: 'metalowa pałka', machete: 'maczeta', chainsaw: 'piła mechaniczna', pistol: 'pistolet', revolver: 'rewolwer', ak47: 'kałach' }

/** The same layered SVG is used in the shelter, inventory and combat. */
export function Survivor({ small = false, equipment = { armor: 'scrap_armor', weapon: 'pistol' } }: { small?: boolean; equipment?: Equipment }) {
  const id = useId().replace(/:/g, '')
  const armor = equipment.armor, weapon = equipment.weapon, plated = armor === 'scrap_armor'
  const armored = ['bulletproof_vest', 'heavy_armor', 'exoskeleton'].includes(armor || '')
  const heavy = armor === 'heavy_armor', exo = armor === 'exoskeleton', leather = armor === 'leather_jacket'
  const coat = `coat-${id}`, hood = `hood-${id}`, halo = `halo-${id}`
  return <svg className={small ? 'survivor small' : 'survivor'} viewBox="0 0 400 470" role="img" aria-label={`Ocalały: ${armor ? armorNames[armor] : 'koszulka i bokserki'}, ${weapon ? weaponNames[weapon] : 'bez broni'}`} data-armor={armor || 'none'} data-weapon={weapon || 'none'}>
    <defs><linearGradient id={coat} x1="0" y1="0" x2="1" y2="1"><stop stopColor={armored ? '#52606a' : leather ? '#614532' : plated ? '#687561' : '#8a7556'}/><stop offset=".5" stopColor={armored ? '#2c3840' : leather ? '#332b26' : plated ? '#3c493e' : '#544939'}/><stop offset="1" stopColor="#242e28"/></linearGradient><linearGradient id={hood} x1="0" x2="1" y2="1"><stop stopColor="#7b856e"/><stop offset="1" stopColor="#303b32"/></linearGradient><radialGradient id={halo}><stop stopColor="#a8d46f" stopOpacity=".16"/><stop offset="1" stopColor="#a8d46f" stopOpacity="0"/></radialGradient></defs>
    <circle cx="200" cy="206" r="184" fill={`url(#${halo})`}/><g fill="none" stroke="#8eab78" opacity=".2"><circle cx="200" cy="202" r="138"/><circle cx="200" cy="202" r="154" strokeDasharray="2 10"/><path d="M200 30v38m0 276v38M28 202h38m268 0h38"/></g>
    <g fill="#303a31" opacity=".6"><path d="M0 395V268h38v-25h22v152m-8 0V301h44v-28h23v122m172 0V275h27v-34h30v154m-2 0V305h54v90"/><path d="m25 268 17-46 4 46m265-13 5-43 8 43"/></g>
    <ellipse cx="202" cy="445" rx="115" ry="14" fill="#101711" opacity=".5"/>
    <g data-layer="base">
      <path d="m158 327-6 112h32l19-94 18 94h32l-10-112" fill="#b49475" stroke="#d3b18b" strokeWidth="1.5"/>
      <path d="m157 314-5 62 39 5 12-31 13 31 35-5-8-62Z" fill="#626e68" stroke="#8c9990" strokeWidth="2"/><path d="M155 324h90m-43 3v23m-39-15 4 25m65-25-3 25" stroke="#bcc1a7" opacity=".5"/>
      <path d="m151 438-6 9q17 11 43 2l-4-12m36 1-1 11q28 9 42-3l-10-9" fill="#b49475"/>
      <path d="m136 226-22 7-33 95 11 24 16-12 36-83m117-28 22 7 30 94-11 22-18-13-33-84" fill="#b49475" stroke="#d3b18b" strokeWidth="1.5"/>
      <path d="m153 187-36 23-9 46 34 13 8-19-7 76 59 7 59-7-9-77 10 19 33-14-11-45-35-22-25-6h-46Z" fill="#bbb9a2" stroke="#dfd7b7" strokeWidth="1.5"/>
      <path d="m174 181 4 25q24 20 48 0l4-25" fill="#ae8d6e"/><path d="m174 203q26 28 54 0m-78 113 26 4m49-88-5 73" stroke="#777d6b" fill="none" opacity=".65"/>
      <path d="m165 115 8 56q29 39 57 0l9-56-34-29Z" fill="#bc9c7a" stroke="#d0b18d" strokeWidth="1.5"/>
      <path d="m165 133-8-20q-1-39 45-42 42 5 44 39l-9 25-7-26-25-10-31 12Z" fill="#34372d"/><path d="m175 135 15-2m22 0 16 2" stroke="#34372d" strokeWidth="4"/><path d="m202 137-4 17 7 2m-17 14q14 9 28-1" fill="none" stroke="#7b624c" strokeWidth="2"/><path d="m176 162 7 19 19 10 21-11 6-19-12 12-14 2-15-3Z" fill="#525143" opacity=".8"/>
    </g>
    {armor && <g data-layer={armor}>
      <path d="m157 323-8 122h42l13-89 10 89h42l-12-122" fill="#303a32"/><path d="m151 433-12 19h54v-23m25 0v23h55l-19-23" fill="#1b211d" stroke="#59634f"/>
      <path d="m151 186-41 24-31 117 27 16 42-77-17 110 71 15 71-15-20-110 36 70 27-18-27-110-40-22" fill={`url(#${coat})`} stroke="#8c8b70" strokeWidth="1.5"/>
      <path d="m158 186 44 44 43-44-13 123h-61Z" fill="#29362d"/><path d="m153 187 49 44-29 34-29-47m106-31-48 44 27 34 29-47" fill={plated ? '#7c8268' : '#a68e64'}/>
      <path d="m143 204 99 152 13-14-96-148Z" fill="#2b3028" stroke="#92937a" strokeWidth="1.5"/><path d="m152 266 27-4 8 34-31 4m70-5 29 2-2 32-31-4" fill="#65705a" stroke="#83896d"/><path d="m135 342 134-2-2 15H135Z" fill="#292d25"/><rect x="190" y="338" width="25" height="21" rx="3" fill="#a4a38a"/><rect x="195" y="342" width="15" height="12" rx="2" fill="#3a4438"/>
      <path d="m87 320-8 25 13 18 15-6 3-27m176-2 2 27 14 8 15-18-8-24" fill="#343f33"/><path d="m202 238 1 95m-51-14-5 15m100-15 5 15M171 382l-6 46m71-46 7 46" stroke="#8e967a" opacity=".45"/>
      {armor === 'jacket' && <g stroke="#c7ab7b" opacity=".65"><path d="m115 232 16 5m-9 1 3-9m116 87 17 3m-12-9-2 16m-98 33 15 4m-12-7 4 13"/><path d="m110 261 13 3-7 29-13-4" fill="#504a38"/></g>}
    </g>}
    {leather && <g data-layer="leather-details"><path d="m149 189 38 32-17 21-26-29m104-24-37 32 17 21 27-29" fill="#9b7653" stroke="#d4ae79"/><path d="m111 220 23-11 5 24-25 13m156-37 23 11-3 26-25-13" fill="#3b2b22" stroke="#a8875e"/><path d="m174 249 18 74m-38-48 25-5m55 0 20 5" stroke="#cab68c" strokeWidth="3"/><circle cx="153" cy="207" r="3" fill="#d2c19b"/><circle cx="252" cy="207" r="3" fill="#d2c19b"/></g>}
    {armored && <g data-layer="ballistic-plates"><path d="m153 194 26 10 22 17 24-17 26-10 10 132-59 11-59-11Z" fill={heavy ? '#727775' : exo ? '#5f6957' : '#384d5d'} stroke="#a2aaa0" strokeWidth="2"/><path d="m170 227 32 10 33-10 5 61-38 16-37-16Z" fill={exo ? '#9aa578' : heavy ? '#969a8b' : '#536675'} stroke="#b0b7a0"/><path d="M173 248h58m-57 15h58m-57 15h58" stroke="#25343b" strokeWidth="5"/><path d="m151 298 20-2 4 28-23 2m27-25h20v28h-20m27-28h20v28h-20m27-33 21 2-1 28-23-2" fill="#283a42" stroke="#869384"/></g>}
    {(heavy || exo) && <g data-layer="full-armor"><path d="m146 191-41 16-8 36 46 10 17-31m95-31 42 16 8 36-47 10-17-31" fill={exo ? '#8b9873' : '#858c84'} stroke="#b7c1a4" strokeWidth="3"/><path d="m96 269 30 9-16 50-28-13m195-37 29-9 14 46-28 13m-132 58 35 3-8 51h-32m64-51 34-3 5 54h-32" fill={exo ? '#677954' : '#6f7a75'} stroke="#aebaa0" strokeWidth="2"/><path d="M153 98q5-41 49-42 43 4 48 42l-5 69-20 30h-47l-23-30Z" fill={exo ? '#6d7c58' : '#626e6b'} stroke="#bdc7a9" strokeWidth="3"/><path d="m162 108 39-13 39 13-4 31-35 12-35-12Z" fill="#152c2c" stroke="#8c9e89"/><path d="m170 118 26-6m13 0 23 6" stroke={exo ? '#c6ff83' : '#9fc9b4'} strokeWidth="5"/><path d="m180 162 22-8 20 8-7 22h-27Z" fill="#35463d"/><path d="M192 165h19m-19 7h19" stroke="#95a18a" strokeWidth="3"/></g>}
    {exo && <g data-layer="powered-frame" fill="none" stroke="#c4bd8c" strokeWidth="6"><path d="m103 208-15 12-16 97m226-109 14 12 16 97M151 363l-8 67m112-67 8 67M155 198l-13-13v-33m109 46 13-13v-33"/><g fill="#9be074" stroke="#334a35" strokeWidth="3"><circle cx="88" cy="267" r="8"/><circle cx="313" cy="267" r="8"/><circle cx="151" cy="374" r="8"/><circle cx="256" cy="374" r="8"/><circle cx="201" cy="265" r="12"/></g></g>}
    {plated && <g data-layer="scrap-plates">
      <path d="m143 167-6-34q3-72 65-77 62 7 65 77l-11 40-24 27h-58Z" fill={`url(#${hood})`} stroke="#7d896e" strokeWidth="2"/>
      <path d="M158 155q-6-68 44-77 47 13 43 77l-20 35h-46Z" fill="#1e2924"/><path d="m160 116 41-19 43 20-10 27h-64Z" fill="#303f36"/><path d="m166 120 30-7-1 22-26 1m35-23 31 8-4 16-26-2" fill="#a8ba83"/><path d="m170 122 19-5m20 1 18 5" stroke="#d4e5ab" strokeWidth="3" opacity=".7"/>
      <path d="m179 143 23-10 24 11 10 30-19 22h-30l-19-22Z" fill="#536052" stroke="#84917b"/><circle cx="202" cy="164" r="15" fill="#222e27" stroke="#7f8c73" strokeWidth="4"/><path d="M192 158h20m-20 6h20m-19 6h18" stroke="#66725d" strokeWidth="2"/><path d="m168 154-14 6 8 24 16-5m58-24 13 5-8 24-14-5" fill="#38473b"/>
      <path d="m112 205 34-9 16 34-48 17-12-12Zm146-9 33 9 10 30-12 12-48-17Z" fill="#8c9380" stroke="#bbc0a4" strokeWidth="2"/><path d="m174 233 28 9 30-9 9 65-38 17-38-17Z" fill="#727e6a" stroke="#b0b99c" strokeWidth="2"/><path d="m176 250 26 8 28-9m-54 19 26 8 31-10m-57 19 26 8 33-10" stroke="#3a483c" strokeWidth="4"/>
      <path d="m99 275 27 8-17 41-25-8m191-33 26-8 15 40-25 9" fill="#77816b" stroke="#abb395"/><g fill="#d0c6a0"><circle cx="117" cy="218" r="3"/><circle cx="141" cy="214" r="3"/><circle cx="265" cy="213" r="3"/><circle cx="285" cy="219" r="3"/><circle cx="177" cy="242" r="2"/><circle cx="229" cy="242" r="2"/></g>
    </g>}
    {weapon && <g data-layer={weapon}>
      {weapon === 'knife' && <g transform="translate(92 342) rotate(20)"><path d="M-7 5 0 82 10 56 7 5Z" fill="#bdc5af" stroke="#677463" strokeWidth="2"/><path d="M0 15 3 57" stroke="#e3e4c3"/><path d="M-15 3h30v7h-30Z" fill="#878c72"/><rect x="-6" y="-25" width="13" height="29" rx="3" fill="#6b5037"/><path d="M-5-18H6M-5-10H6" stroke="#ab9167"/></g>}
      {weapon === 'club' && <g transform="translate(93 338) rotate(18)"><path d="M-7-9H7V97H-7Z" fill="#798875" stroke="#bcc2a3" strokeWidth="2"/><path d="M-10 38h20v49h-20Z" fill="#697461"/><path d="m-10 44 20 10m-20 1 20 10m-20 1 20 10m-18-32-9 6m24 10 12-5" stroke="#b8b698" strokeWidth="3"/><path d="M-8-16H8v33H-8Z" fill="#554b38"/><path d="m-7-8 14 4m-14 5 14 4" stroke="#9c916d"/></g>}
      {weapon === 'pistol' && <g transform="translate(93 337) rotate(12)"><path d="M-10-10H58V5H12L7 31H-9L-3 3h-7Z" fill="#7c8979" stroke="#b6bfa5" strokeWidth="2"/><path d="M3 5h24v17H9m9-17v10" fill="none" stroke="#acb29a" strokeWidth="3"/><path d="M-8-15h58v7H-8Z" fill="#414e41"/><rect x="48" y="-11" width="13" height="16" fill="#343f36"/><path d="M-7 8h14L4 28H-10Z" fill="#795b3d"/><path d="M-5 12h9m-11 7h9" stroke="#c0a475"/></g>}
      {['machete', 'chainsaw', 'revolver', 'ak47'].includes(weapon) && <g transform={`translate(${weapon === 'ak47' ? 60 : 74} 315) scale(${weapon === 'ak47' ? 1.7 : 1.3})`} fill="none" stroke="#b4c19b" strokeWidth="1.5" strokeLinejoin="round"><WeaponGlyph item={weapon}/></g>}
      <path d="m83 334 3 16 12 5 11-10-5-12" fill={armor ? '#343f33' : '#bc9c7a'} stroke={armor ? '#788269' : '#d3b18b'}/>
    </g>}
    <g fill="#9ebc76" opacity=".5"><circle cx="85" cy="155" r="1.5"/><circle cx="313" cy="177" r="2"/><circle cx="308" cy="87" r="1"/><circle cx="106" cy="83" r="2"/><circle cx="59" cy="294" r="1"/></g>
  </svg>
}

/** Individual silhouettes keep similarly categorized items visually distinct. */
export function ItemArt({ item, size = 52 }: { item: string; size?: number }) {
  return <svg width={size} height={size} viewBox="0 0 64 64" fill="none" stroke="#b4c19b" strokeWidth="2" strokeLinejoin="round" aria-hidden="true" data-item-art={item}>
    {item === 'knife' && <><path d="m41 7 9-3-2 14-23 27-8-8Z" fill="#a3ae95"/><path d="m25 34 8 8m-17-4-6 7 9 9 7-9" fill="#755f43"/><path d="m13 47 4 4m23-35-14 19" stroke="#dbd4ae"/></>}
    {item === 'club' && <><path d="m33 8 12 5-17 45-10-4Z" fill="#667360"/><path d="m31 8 5-4 15 6-2 7-18-6m-5 12 17 7m-20 0 17 7m-20 0 17 7m-13-24-9 1m26 16 10-2"/><path d="m22 42 10 4-4 12-10-4Z" fill="#806c4d"/></>}
    {item === 'pistol' && <><path d="M8 15h47v14H28l-5 25H9l5-26H8Z" fill="#727e6c"/><path d="M7 11h45v7H7Zm39 7h12v10H46" fill="#3c4b3e"/><path d="M25 29h12v12H25m5-12v7"/><path d="m14 33 12 2-4 17H11Z" fill="#8f6c46"/></>}
    <WeaponGlyph item={item}/>
    {item === 'ammo' && <><path d="M23 23q0-12 9-19 9 7 9 19v31H23Z" fill="#b8a368" stroke="#e0ce93"/><path d="M23 23h18m-18 25h18"/><rect x="20" y="53" width="24" height="7" rx="2" fill="#8b794d"/></>}
    {item === 'grenade' && <><path d="m24 18-6 9-3 23 10 10h17l10-10-4-23-8-9Z" fill="#66784b"/><path d="M22 30h24m-27 11h30m-30 10h30M28 22v35m10-35v35" stroke="#35482d"/><path d="M26 12h13v10H26Z" fill="#a8a685"/><path d="m32 12 11-5 10 18" stroke="#ccc5a0" strokeWidth="4"/><circle cx="22" cy="9" r="6" stroke="#ccc5a0"/></>}
    {item === 'jacket' && <><path d="m23 9-12 8-8 28 10 4 9-22-4 28 15 3 14-3-5-28 9 22 10-4-8-28-12-8" fill="#746344"/><path d="m23 9 9 13 9-13m-9 13v34m-10-18 7 1v8h-9m16-8 7-1 2 9h-9"/><path d="m23 9-5 15 9 4 5-6 5 6 9-4-5-15" fill="#a18a60"/></>}
    {item === 'scrap_armor' && <><path d="m20 8-10 8-6 16 13 5 2 21h27l2-21 12-5-6-16-11-8-11 8Z" fill="#56664f"/><path d="m10 16 10-5 7 12-20 7m37-19-7 12 20 7M22 27l10 4 11-4 2 21-13 7-12-7Z" fill="#909b80"/><path d="m23 35 9 3 10-3m-20 8 10 4 11-4"/><circle cx="14" cy="21" r="2" fill="#d1c398"/><circle cx="50" cy="21" r="2" fill="#d1c398"/></>}
    {item === 'leather_jacket' && <><path d="m23 8-12 8-7 29 10 4 7-21-4 29h30l-4-29 7 21 10-4-7-29-12-8-9 11Z" fill="#68452f" stroke="#bc9769"/><path d="m23 8-4 17 9 3 4-9 5 9 9-3-5-17m-9 13-8 34m-5-19 8 3m11-3 8 3" stroke="#dabf8d"/><circle cx="23" cy="20" r="2" fill="#dfcc9d"/></>}
    {['bulletproof_vest', 'heavy_armor', 'exoskeleton'].includes(item) && <><path d="m19 8-7 10 5 39 15 4 15-4 5-39-7-10-13 9Z" fill={item === 'bulletproof_vest' ? '#435e70' : '#7d8a72'}/><path d="m23 25 9 4 10-4 2 22-12 7-12-7Z" fill="#a1ac91"/><path d="M24 34h16m-17 7h18" stroke="#34463f" strokeWidth="3"/>{item !== 'bulletproof_vest' && <path d="M17 10 6 14 2 30l14 4m31-24 11 4 4 16-14 4" fill="#838e7e"/>}{item === 'exoskeleton' && <g fill="none" stroke="#c9c095" strokeWidth="3"><path d="M8 18 4 50m52-32 4 32M20 56l-3 6m27-6 3 6"/><circle cx="32" cy="39" r="5" fill="#acdf7b"/></g>}</>}
    {item === 'medkit' && <><rect x="8" y="19" width="48" height="37" rx="6" fill="#626c4e"/><path d="M23 19v-7h18v7"/><path d="M28 27h8v8h8v8h-8v8h-8v-8h-8v-8h8Z" fill="#d1b591" stroke="none"/></>}
    {item === 'scrap' && <><path d="m10 20 25-9 9 26-26 10Z" fill="#8e7b53"/><path d="m29 31 19-7 9 28-24 8Z" fill="#586550"/><path d="m14 25 20-7m-17 16 20-7m4 12 10-4m-8 11 9-4"/><circle cx="20" cy="43" r="3"/></>}
    {item === 'electronics' && <><rect x="14" y="12" width="37" height="42" rx="3" fill="#405e45"/><rect x="24" y="24" width="17" height="17" fill="#a0ac83"/><path d="M20 5v7m10-7v7m10-7v7m10 42v6m-10-6v6m-10-6v6M6 22h8m-8 12h8m37-12h8m-8 12h8M19 20h7v-4m15 29h5v5m-27-4h8"/></>}
  </svg>
}

function WeaponGlyph({ item }: { item: string }) {
  if (item === 'machete') return <><path d="m25 38 17-30 14-5-4 19-19 23Z" fill="#b9c2ab"/><path d="m24 35 13 10m-13-6-11 17 8 5 11-18" fill="#806044"/><path d="m33 35 12-19" stroke="#e5e1b8"/></>
  if (item === 'chainsaw') return <><path d="M28 16h26q10 11 0 22H28Z" fill="#9ba58b"/><path d="M33 11h21l7 7v18l-7 7H33m5-30v4m8-4v4m8 0v5m4 5h-5m-1 10v-5m-8 8v-5" strokeWidth="3"/><path d="M5 24h28v24H5Z" fill="#ba8a44"/><path d="M10 24V13h15v11m-2 24v9H10V45m-2-9h12m-12 6h12" stroke="#d8c99b" strokeWidth="3"/></>
  if (item === 'revolver') return <><path d="M8 18h47v10H30L22 54H9l6-24-7-2Z" fill="#828c7d"/><rect x="18" y="16" width="17" height="19" rx="5" fill="#bbc1a8"/><path d="M22 19v12m8-12v12m-2 5h11v9H25m-12-9 11 3-5 13H9" fill="#79583c"/><path d="M48 14v5m-39-6 9 5"/></>
  if (item === 'ak47') return <><path d="M4 24h18l5-5h22v9H31l-4 8H15Z" fill="#566557"/><path d="M46 20h14v5H46m7-8v4M4 24v17l12-6m9-2-3 21 10 2 4-20m-18 0-4 14h8" fill="#8b603a"/><path d="M33 33q10 9 8 22l10-3q0-15-10-23Z" fill="#75826e"/><path d="M28 15h17m-9 5h10" stroke="#c4c6a6"/></>
  return null
}
