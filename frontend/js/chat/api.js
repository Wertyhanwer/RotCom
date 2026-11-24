function authHeaders() {
  return { 'Authorization': `Bearer ${token}` }
}

// Access-токен живёт 30 минут. Получив 401, один раз обмениваем refresh-токен на новую пару
// и повторяем запрос. Одновременные 401 ждут один общий обмен: refresh-токен одноразовый,
// и повторное предъявление уже обменянного токена сервер считает кражей и отзывает все сессии.
let refreshInFlight = null

async function refreshTokens() {
  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) return false
      const response = await fetch(`${API}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
      })
      if (!response.ok) return false
      const data = await response.json()
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      token = data.access_token
      return true
    })().finally(() => { refreshInFlight = null })
  }
  return refreshInFlight
}

async function apiFetch(url, options = {}) {
  const withAuth = () => fetch(url, { ...options, headers: { ...(options.headers || {}), ...authHeaders() } })
  let response = await withAuth()
  if (response.status === 401 && await refreshTokens()) {
    response = await withAuth()
  }
  return response
}

async function fetchMe() {
  return apiFetch(`${API}/users/me`)
}

async function fetchChats() {
  return apiFetch(`${API}/chats/private/`)
}

async function fetchHistory(chatId, before = null) {
  const cursor = before ? `&before=${encodeURIComponent(before)}` : ''
  return apiFetch(`${API}/chats/private/${chatId}/history?limit=50${cursor}`)
}

async function fetchUserByLogin(login) {
  return apiFetch(`${API}/users/search?login=${encodeURIComponent(login)}`)
}
