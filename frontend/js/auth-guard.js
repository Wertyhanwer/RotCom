if (localStorage.getItem('token')) {
  window.location.replace('chat.html')
} else {
  window.location.replace('auth.html')
}
