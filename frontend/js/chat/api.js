function authHeaders() {
  return { 'Authorization': `Bearer ${token}` }
}

async function fetchMe() {
  return fetch(`${API}/users/me`, { headers: authHeaders() })
}

async function fetchChats() {
  return fetch(`${API}/chats/private/`, { headers: authHeaders() })
}

async function fetchMessages(chatId, offset = 0) {
  return fetch(
    `${API}/chats/private/${chatId}/messages?limit=50&offset=${offset}`,
    { headers: authHeaders() }
  )
}

async function fetchUserByLogin(login) {
  return fetch(
    `${API}/users/search?login=${encodeURIComponent(login)}`,
    { headers: authHeaders() }
  )
}
