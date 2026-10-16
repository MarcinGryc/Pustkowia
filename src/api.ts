import type { ActionData, Config, Player } from './types'
let csrf = ''
export class ApiError extends Error { constructor(message: string, public status: number) { super(message) } }
async function request<T>(path: string, body?: unknown): Promise<T> {
  let response: Response
  try {
    response = await fetch(`/api/${path}`, { credentials: 'same-origin', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf }, ...(body === undefined ? {} : { method: 'POST', body: JSON.stringify(body) }) })
  } catch {
    throw new Error('Brak połączenia z serwerem. Po odzyskaniu łączności sprawdź aktualny stan gry przed następną operacją.')
  }
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new ApiError(data.error || 'Nie udało się połączyć z serwerem.', response.status)
  if (data.csrf) csrf = data.csrf
  return data
}
let queue: Promise<unknown> = Promise.resolve()
export const api = {
  bootstrap: () => request<Config>('bootstrap'),
  me: () => request<{ player: Player; email: string }>('me'),
  auth: (mode: string, email: string, password: string, repeat: string) => request<{ player: Player; email: string }>(mode, { email, password, password_repeat: repeat }),
  logout: () => request('logout', {}),
  action: (data: ActionData): Promise<Player> => {
    const body = { ...data, key: crypto.randomUUID() }
    const work = async () => {
      // Retry only transport failures, always with the same idempotency key.
      try { await request('action', body) } catch (e) {
        if (e instanceof ApiError) throw e
        await request('action', body)
      }
      return (await api.me()).player
    }
    const result = queue.then(work, work)
    queue = result.catch(() => undefined)
    return result
  },
}
