function wsConnect() {
  ws = new WebSocket(`ws://${location.host}/ws/?token=${token}`)

  ws.onopen = () => console.log('WS подключён')

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data)

    if (msg.error) {
      console.log('WS ошибка:', msg.error)
      return
    }

    if (msg.from_user_id !== currentChatUserId) {
      updateChatPreview(msg.from_user_id, msg.content)
      return
    }

    if (msg.from_user_id === currentUserId) return

    if (currentChatId === null) {
      document.querySelector('.messages').innerHTML = ''
    }

    addBubble(msg.content, 'them')

    if (currentChatId === null) {
      setTimeout(refreshChatList, 500)
    }
  }

  ws.onclose = () => console.log('WS отключён')
}
