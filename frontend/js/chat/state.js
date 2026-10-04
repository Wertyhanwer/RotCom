const token = localStorage.getItem('token')
let currentUserId = null
let ws = null
let currentChatUserId = null
let currentChatId = null
let messagesOffset = 0
let isLoadingMessages = false
let chats = []
