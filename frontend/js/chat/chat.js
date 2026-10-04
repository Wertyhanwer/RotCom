async function refreshChatList() {
  const response = await fetchChats()
  chats = await response.json()

  const chatList = document.getElementById('chat-list')
  chatList.innerHTML = ''
  for (const chat of chats) {
    chatList.appendChild(renderChatItem(chat))
  }
}

async function loadOlderMessages() {
  if (isLoadingMessages || !currentChatId) return
  isLoadingMessages = true

  const response = await fetchHistory(currentChatId, messagesOffset)
  const oldItems = await response.json()
  isLoadingMessages = false

  if (oldItems.length === 0) return
  messagesOffset += 50

  const messagesDiv = document.querySelector('.messages')
  const scrollBefore = messagesDiv.scrollHeight

  // API отдаёт DESC, prepend в том же порядке → старые оказываются выше
  oldItems.forEach(item => {
    const el = item.event_type === 'call'
      ? createCallEl(item)
      : createMessageEl(item.content, item.from_user_id === currentUserId ? 'me' : 'them')
    messagesDiv.prepend(el)
  })

  messagesDiv.scrollTop = messagesDiv.scrollHeight - scrollBefore
}

async function searchUser() {
  const response = await fetchUserByLogin(document.getElementById('search-input').value)

  if (!response.ok) return

  const foundUser = await response.json()
  const foundChat = chats.find(c => c.other_user.id_ === foundUser.id_)

  if (foundChat) {
    openChat(foundChat.id_, foundUser.id_, foundUser.username)
  } else {
    openEmptyChat(foundUser.id_, foundUser.username)
  }
}

function sendMsg() {
  const textField = document.getElementById('msg-input')
  const text = textField.value.trim()
  if (!text) return
  ws.send(JSON.stringify({ event_type: 'message', to_user_id: currentChatUserId, content: text, content_type: 'text' }))
  textField.value = ''
  addBubble(text, 'me')
  refreshChatList()
}

async function logout() {
  // POST ${API}/auth/logout  ← раскомментить когда бэк будет готов
  // await fetch(`${API}/auth/logout`, { method: 'POST', headers: authHeaders() })

  if (ws) ws.close()
  localStorage.removeItem('token')
  window.location.replace('/auth')
}

function bindEvents() {
  document.getElementById('logout-btn').addEventListener('click', logout)
  document.getElementById('msg-send').addEventListener('click', sendMsg)
  document.getElementById('search-btn').addEventListener('click', searchUser)
  document.getElementById('msg-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMsg()
    }
  })
  document.querySelector('.messages').addEventListener('scroll', (e) => {
    if (e.target.scrollTop === 0) loadOlderMessages()
  })
}

async function openChat(chatId, userId, username) {
  currentChatUserId = userId
  currentChatId = chatId
  messagesOffset = 50
  document.querySelector('.message-input').classList.add('visible')
  document.querySelector('.no-chat').textContent = username

  const response = await fetchHistory(chatId, 0)
  const messagesDiv = document.querySelector('.messages')
  messagesDiv.innerHTML = ''

  if (response.ok) {
    const items = await response.json()
    // API отдаёт DESC — разворачиваем чтобы старые были сверху
    if (Array.isArray(items)) {
      ;[...items].reverse().forEach(item => renderHistoryItem(item))
    }
  }
}

function openEmptyChat(userId, username) {
  currentChatUserId = userId
  document.querySelector('.message-input').classList.add('visible')
  document.querySelector('.no-chat').textContent = username
  document.querySelector('.messages').innerHTML = '<div class="empty-chat-hint">Нет сообщений. Напишите первым!</div>'
}

async function init() {
  const meResponse = await fetchMe()

  if (!meResponse.ok) {
    localStorage.removeItem('token')
    window.location.href = '/auth'
    return
  }

  const me = await meResponse.json()
  currentUserId = me.id_

  const chatsResponse = await fetchChats()
  chats = await chatsResponse.json()

  const chatList = document.getElementById('chat-list')
  for (const chat of chats) {
    chatList.appendChild(renderChatItem(chat))
  }
}

if (!localStorage.getItem('token')) {
  window.location.replace('/auth')
} else {
  init()
  bindEvents()
  wsConnect()
}
