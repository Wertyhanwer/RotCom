function authHeaders() {
  return { 'Authorization': `Bearer ${token}` }
}

async function fetchMe() {
  return fetch(`${API}/users/me`, { headers: authHeaders() })
}

async function fetchChats() {
  return fetch(`${API}/chats/private/`, { headers: authHeaders() })
}

async function fetchHistory(chatId, before = null) {
  const cursor = before ? `&before=${encodeURIComponent(before)}` : ''
  return fetch(
    `${API}/chats/private/${chatId}/history?limit=50${cursor}`,
    { headers: authHeaders() }
  )
}

async function fetchUserByLogin(login) {
  return fetch(
    `${API}/users/search?login=${encodeURIComponent(login)}`,
    { headers: authHeaders() }
  )
}
