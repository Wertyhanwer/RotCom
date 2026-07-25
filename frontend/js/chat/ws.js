function wsConnect() {
  ws = new WebSocket(`ws://${location.host}/ws/?token=${token}`)

  ws.onopen = () => console.log('WS подключён')

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data)

    if (msg.error) {
      console.log('WS ошибка:', msg.error)
      return
    }

    const senderId = msg.event_type === 'call' ? msg.caller_id : msg.from_user_id

    if (senderId !== currentChatUserId) {
      refreshChatList()
      return
    }

    if (senderId === currentUserId) return

    if (currentChatId === null) {
      document.querySelector('.messages').innerHTML = ''
    }

    if (msg.event_type === 'call') {
      renderHistoryItem(msg)
    } else {
      addBubble(msg.content, 'them')
    }

    refreshChatList()
  }

  ws.onclose = () => console.log('WS отключён')
}
