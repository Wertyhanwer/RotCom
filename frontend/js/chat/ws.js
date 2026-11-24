let wsAuthRetried = false

function wsConnect() {
  // токен не кладём в URL: адрес WebSocket-рукопожатия попадает в логи nginx.
  // Он уходит первым сообщением сразу после открытия соединения.
  ws = new WebSocket(`ws://${location.host}/ws/`)

  ws.onopen = () => {
    ws.send(JSON.stringify({ type: 'auth', token }))
  }

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data)

    if (msg.type === 'auth_ok') {
      wsAuthRetried = false
      console.log('WS подключён')
      return
    }

    if (msg.error) {
      console.log('WS ошибка:', msg.error)
      return
    }

    const senderId = msg.event_type === 'call' ? msg.caller_id : msg.from_user_id

    if (Number(senderId) !== Number(currentChatUserId)) {
      refreshChatList()
      return
    }

    if (Number(senderId) === Number(currentUserId)) return

    if (currentChatId === null) {
      document.querySelector('.messages').innerHTML = ''
      currentChatId = msg.chat_id
    }

    // WS присылает событие в том же формате, что и /history
    renderHistoryItem(msg)

    refreshChatList()
  }

  ws.onclose = async (event) => {
    console.log('WS отключён')
    // 1008 — сервер не принял токен (чаще всего истёк access-токен): обновляем пару и
    // переподключаемся один раз; не получилось — сессия закончилась, на страницу входа
    if (event.code === 1008 && !wsAuthRetried) {
      wsAuthRetried = true
      if (await refreshTokens()) {
        wsConnect()
      } else {
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
        window.location.replace('/auth')
      }
    }
  }
}
