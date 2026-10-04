if (localStorage.getItem('token')) {
  window.location.replace('/chat')
} else {
  window.location.replace('/auth')
}
