import { useId } from 'react'
import type { Player } from './types'

type Equipment = Player['equipment']
const armorNames: Record<string, string> = { jacket: 'zniszczona kurtka', scrap_armor: 'pancerz ze złomu' }
const weaponNames: Record<string, string> = { knife: 'zardzewiały nóż', club: 'metalowa pałka', pistol: 'pistolet samoróbka' }

/** The same layered SVG is used in the shelter, inventory and combat. */
export function Survivor({ small = false, equipment = { armor: 'scrap_armor', weapon: 'pistol' } }: { small?: boolean; equipment?: Equipment }) {
  const id = useId().replace(/:/g, '')
  const armor = equipment.armor, weapon = equipment.weapon, plated = armor === 'scrap_armor'
  const coat = `coat-${id}`, hood = `hood-${id}`, halo = `halo-${id}`
  return <svg className={small ? 'survivor small' : 'survivor'} viewBox="0 0 400 470" role="img" aria-label={`Ocalały: ${armor ? armorNames[armor] : 'koszulka i bokserki'}, ${weapon ? weaponNames[weapon] : 'bez broni'}`} data-armor={armor || 'none'} data-weapon={weapon || 'none'}>
    <defs><linearGradient id={coat} x1="0" y1="0" x2="1" y2="1"><stop stopColor={plated ? '#687561' : '#8a7556'}/><stop offset=".5" stopColor={plated ? '#3c493e' : '#544939'}/><stop offset="1" stopColor="#242e28"/></linearGradient><linearGradient id={hood} x1="0" x2="1" y2="1"><stop stopColor="#7b856e"/><stop offset="1" stopColor="#303b32"/></linearGradient><radialGradient id={halo}><stop stopColor="#a8d46f" stopOpacity=".16"/><stop offset="1" stopColor="#a8d46f" stopOpacity="0"/></radialGradient></defs>
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
      {!plated && <g stroke="#c7ab7b" opacity=".65"><path d="m115 232 16 5m-9 1 3-9m116 87 17 3m-12-9-2 16m-98 33 15 4m-12-7 4 13"/><path d="m110 261 13 3-7 29-13-4" fill="#504a38"/></g>}
    </g>}
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
    {item === 'jacket' && <><path d="m23 9-12 8-8 28 10 4 9-22-4 28 15 3 14-3-5-28 9 22 10-4-8-28-12-8" fill="#746344"/><path d="m23 9 9 13 9-13m-9 13v34m-10-18 7 1v8h-9m16-8 7-1 2 9h-9"/><path d="m23 9-5 15 9 4 5-6 5 6 9-4-5-15" fill="#a18a60"/></>}
    {item === 'scrap_armor' && <><path d="m20 8-10 8-6 16 13 5 2 21h27l2-21 12-5-6-16-11-8-11 8Z" fill="#56664f"/><path d="m10 16 10-5 7 12-20 7m37-19-7 12 20 7M22 27l10 4 11-4 2 21-13 7-12-7Z" fill="#909b80"/><path d="m23 35 9 3 10-3m-20 8 10 4 11-4"/><circle cx="14" cy="21" r="2" fill="#d1c398"/><circle cx="50" cy="21" r="2" fill="#d1c398"/></>}
    {item === 'medkit' && <><rect x="8" y="19" width="48" height="37" rx="6" fill="#626c4e"/><path d="M23 19v-7h18v7"/><path d="M28 27h8v8h8v8h-8v8h-8v-8h-8v-8h8Z" fill="#d1b591" stroke="none"/></>}
    {item === 'scrap' && <><path d="m10 20 25-9 9 26-26 10Z" fill="#8e7b53"/><path d="m29 31 19-7 9 28-24 8Z" fill="#586550"/><path d="m14 25 20-7m-17 16 20-7m4 12 10-4m-8 11 9-4"/><circle cx="20" cy="43" r="3"/></>}
    {item === 'electronics' && <><rect x="14" y="12" width="37" height="42" rx="3" fill="#405e45"/><rect x="24" y="24" width="17" height="17" fill="#a0ac83"/><path d="M20 5v7m10-7v7m10-7v7m10 42v6m-10-6v6m-10-6v6M6 22h8m-8 12h8m37-12h8m-8 12h8M19 20h7v-4m15 29h5v5m-27-4h8"/></>}
  </svg>
}
