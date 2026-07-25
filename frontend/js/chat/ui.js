function createMessageEl(content, side) {
  const el = document.createElement('div')
  el.className = `message ${side}`
  el.innerHTML = `<span class="bubble">${content}</span>`
  return el
}

function createCallEl(item) {
  const isOutgoing = item.caller_id === currentUserId
  const answered = item.status === 'answered'

  const icon = answered ? '📞' : '📵'
  let label
  if (answered) {
    label = isOutgoing ? 'Исходящий звонок' : 'Входящий звонок'
  } else {
    label = isOutgoing ? 'Отменённый звонок' : 'Пропущенный звонок'
  }

  const duration = answered && item.duration
    ? `<span class="call-duration">· ${formatDuration(item.duration)}</span>`
    : ''

  const el = document.createElement('div')
  el.className = 'event-call'
  el.innerHTML = `
    <div class="call-bubble ${answered ? 'answered' : 'missed'}">
      <span class="call-icon">${icon}</span>
      <span>${label}</span>
      ${duration}
    </div>
  `
  return el
}

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

function renderHistoryItem(item) {
  const messagesDiv = document.querySelector('.messages')
  const wasAtBottom = messagesDiv.scrollHeight - messagesDiv.scrollTop <= messagesDiv.clientHeight + 50

  let el
  if (item.event_type === 'call') {
    el = createCallEl(item)
  } else {
    const side = item.from_user_id === currentUserId ? 'me' : 'them'
    el = createMessageEl(item.content, side)
  }

  messagesDiv.appendChild(el)
  if (wasAtBottom) messagesDiv.scrollTop = messagesDiv.scrollHeight
}

function addBubble(text, side) {
  const messagesDiv = document.querySelector('.messages')
  const wasAtBottom = messagesDiv.scrollHeight - messagesDiv.scrollTop <= messagesDiv.clientHeight + 50
  const el = createMessageEl(text, side)
  messagesDiv.appendChild(el)
  if (wasAtBottom) messagesDiv.scrollTop = messagesDiv.scrollHeight
}

function renderChatItem(chat) {
  const item = document.createElement('div')
  item.className = 'chat-item'
  item.innerHTML = `
    <span class="chat-item-name">${chat.other_user.username}</span>
    <span class="chat-item-last">${chat.last_message || 'Нет сообщений'}</span>
  `
  item.dataset.userId = chat.other_user.id_
  item.addEventListener('click', () => {
    openChat(chat.id_, chat.other_user.id_, chat.other_user.username)
  })
  return item
}
