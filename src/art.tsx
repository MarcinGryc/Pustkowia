export function Survivor({ small = false }: { small?: boolean }) {
  return <svg className={small ? 'survivor small' : 'survivor'} viewBox="0 0 400 470" role="img" aria-label="Ocalały w kapturze i masce na tle ruin">
    <defs><linearGradient id="coat" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#687561"/><stop offset=".5" stopColor="#3c493e"/><stop offset="1" stopColor="#242e28"/></linearGradient><linearGradient id="hood" x1="0" x2="1" y2="1"><stop stopColor="#7b856e"/><stop offset="1" stopColor="#303b32"/></linearGradient><radialGradient id="halo"><stop stopColor="#a8d46f" stopOpacity=".16"/><stop offset="1" stopColor="#a8d46f" stopOpacity="0"/></radialGradient></defs>
    <circle cx="200" cy="206" r="184" fill="url(#halo)"/><g fill="none" stroke="#8eab78" opacity=".2"><circle cx="200" cy="202" r="138"/><circle cx="200" cy="202" r="154" strokeDasharray="2 10"/><path d="M200 30v38m0 276v38M28 202h38m268 0h38"/></g>
    <g fill="#303a31" opacity=".6"><path d="M0 395V268h38v-25h22v152m-8 0V301h44v-28h23v122m172 0V275h27v-34h30v154m-2 0V305h54v90"/><path d="m25 268 17-46 4 46m265-13 5-43 8 43"/></g>
    <ellipse cx="202" cy="445" rx="115" ry="14" fill="#101711" opacity=".5"/>
    <path d="m157 323-8 122h42l13-89 10 89h42l-12-122" fill="#262e28"/><path d="m151 433-12 19h54v-18m25 0v18h55l-19-20" fill="#1b211d"/>
    <path d="m151 186-41 24-31 117 27 16 42-77-17 110 71 15 71-15-20-110 36 70 27-18-27-110-40-22" fill="url(#coat)" stroke="#758069" strokeWidth="1.5"/>
    <path d="m158 186 44 44 43-44-13 123h-61Z" fill="#29362d"/><path d="m153 187 49 44-29 34-29-47m106-31-48 44 27 34 29-47" fill="#7c8268"/>
    <path d="m143 167-6-34q3-72 65-77 62 7 65 77l-11 40-24 27h-58Z" fill="url(#hood)" stroke="#7d896e" strokeWidth="2"/>
    <path d="M158 155q-6-68 44-77 47 13 43 77l-20 35h-46Z" fill="#1e2924"/><path d="m160 116 41-19 43 20-10 27h-64Z" fill="#303f36"/><path d="m166 120 30-7-1 22-26 1m35-23 31 8-4 16-26-2" fill="#a8ba83"/><path d="m170 122 19-5m20 1 18 5" stroke="#d4e5ab" strokeWidth="3" opacity=".7"/>
    <path d="m179 143 23-10 24 11 10 30-19 22h-30l-19-22Z" fill="#536052" stroke="#84917b"/><circle cx="202" cy="164" r="15" fill="#222e27" stroke="#7f8c73" strokeWidth="4"/><path d="M192 158h20m-20 6h20m-19 6h18" stroke="#66725d" strokeWidth="2"/><path d="m168 154-14 6 8 24 16-5m58-24 13 5-8 24-14-5" fill="#38473b"/>
    <path d="m143 204 99 152 13-14-96-148Z" fill="#2b3028" stroke="#92937a" strokeWidth="1.5"/><path d="m152 266 27-4 8 34-31 4m70-5 29 2-2 32-31-4" fill="#65705a" stroke="#83896d"/><path d="m135 342 134-2-2 15H135Z" fill="#292d25"/><rect x="190" y="338" width="25" height="21" rx="3" fill="#a4a38a"/><rect x="195" y="342" width="15" height="12" rx="2" fill="#3a4438"/>
    <path d="m87 320-8 25 13 18 15-6 3-27m176-2 2 27 14 8 15-18-8-24" fill="#343f33"/><path d="m202 238 1 95m-51-14-5 15m100-15 5 15M171 364l-6 64m71-64 7 64" stroke="#8e967a" opacity=".45"/>
    <g fill="#9ebc76" opacity=".5"><circle cx="85" cy="155" r="1.5"/><circle cx="313" cy="177" r="2"/><circle cx="308" cy="87" r="1"/><circle cx="106" cy="83" r="2"/><circle cx="59" cy="294" r="1"/></g>
  </svg>
}
export function Wasteland() {
  return <svg className="wasteland" viewBox="0 0 900 220" preserveAspectRatio="xMidYMax slice" aria-hidden="true"><g fill="#536746" opacity=".25"><path d="M0 220V110h35V80h35v140m60 0V90h26V65h49v155m38 0V130h80v90m80 0V60h18V20h7v40h24v160m35 0v-95h44v-30h30v125m78 0V95h27V65h45v155m60 0V120h48v-20h22v120m55 0V70h23v-25h38v175"/><path d="m0 211 180-26 148 19 170-21 180 19 222-23v41H0"/></g><g stroke="#718660" fill="none" opacity=".3"><path d="M80 220V115m0 55-25-22m25 5 20-26m593 93V107m0 58-27-23m27 2 19-26"/><path d="m320 220 4-60h57l6 60m-59-56 49 50m-49 0 49-50"/></g></svg>
}
