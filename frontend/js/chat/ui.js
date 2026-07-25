function addBubble(text, side) {
  const messagesDiv = document.querySelector('.messages')
  const wasAtBottom = messagesDiv.scrollHeight - messagesDiv.scrollTop <= messagesDiv.clientHeight + 50

  const bubble = document.createElement('div')
  bubble.className = `message ${side}`
  bubble.innerHTML = `<span class="bubble">${text}</span>`
  messagesDiv.appendChild(bubble)

  if (wasAtBottom) messagesDiv.scrollTop = messagesDiv.scrollHeight
}

function updateChatPreview(fromUserId, content) {
  document.querySelectorAll('.chat-item').forEach(item => {
    if (item.dataset.userId == fromUserId) {
      item.querySelector('.chat-item-last').textContent = content
    }
  })
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
