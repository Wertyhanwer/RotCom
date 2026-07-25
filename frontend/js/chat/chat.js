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

  const response = await fetchMessages(currentChatId, messagesOffset)
  const oldMessages = await response.json()
  isLoadingMessages = false

  if (oldMessages.length === 0) return
  messagesOffset += 50

  const messagesDiv = document.querySelector('.messages')
  const scrollBefore = messagesDiv.scrollHeight

  oldMessages.forEach(msg => {
    const bubble = document.createElement('div')
    bubble.className = `message ${msg.from_user_id === currentUserId ? 'me' : 'them'}`
    bubble.innerHTML = `<span class="bubble">${msg.content}</span>`
    messagesDiv.prepend(bubble)
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
  ws.send(JSON.stringify({ to_user_id: currentChatUserId, content: text }))
  textField.value = ''
  addBubble(text, 'me')
  refreshChatList()
}

function bindEvents() {
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

  const response = await fetchMessages(chatId, 0)
  const messages = await response.json()
  const messagesDiv = document.querySelector('.messages')
  messagesDiv.innerHTML = ''

  messages.forEach(msg => {
    addBubble(msg.content, msg.from_user_id === currentUserId ? 'me' : 'them')
  })
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
    window.location.href = 'auth.html'
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
  window.location.replace('auth.html')
} else {
  init()
  bindEvents()
  wsConnect()
}
