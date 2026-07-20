if (!localStorage.getItem('token')) {
  window.location.replace('auth.html')
}