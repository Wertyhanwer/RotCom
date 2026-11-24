let token = localStorage.getItem('token')  // обновляется в api.js после refresh
let currentUserId = null
let ws = null
let currentChatUserId = null
let currentChatId = null
let oldestEventId = null  // курсор пагинации: id самого старого загруженного события
let isLoadingMessages = false
let chats = []
