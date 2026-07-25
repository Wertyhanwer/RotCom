const tabs = document.querySelectorAll('.tab')
const formLogin = document.getElementById('form-login')
const formRegister = document.getElementById('form-register')

tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    tabs.forEach(t => t.classList.remove('active'))
    tab.classList.add('active')

    if (tab.textContent === 'Войти') {
      formLogin.classList.add('active')
      formRegister.classList.remove('active')
    } else {
      formRegister.classList.add('active')
      formLogin.classList.remove('active')
    }
  })
})

document.getElementById('form-login').addEventListener('submit', async (e) => {
  e.preventDefault()

  const login = document.getElementById('login-input').value
  const password = document.getElementById('login-password').value

  const response = await fetch(
    `${API}/login/?login=${encodeURIComponent(login)}&password=${encodeURIComponent(password)}`,
    { method: 'POST' }
  )

  const data = await response.json()

  if (response.ok) {
    localStorage.setItem('token', data.access_token)
    window.location.href = '/chat'
  } else {
    console.log('Ошибка:', data.detail)
  }
})

document.getElementById('form-register').addEventListener('submit', async (e) => {
  e.preventDefault()

  const email = document.getElementById('reg-email').value
  const username = document.getElementById('reg-username').value
  const login = document.getElementById('reg-login').value
  const password1 = document.getElementById('reg-password').value
  const password2 = document.getElementById('reg-password2').value

  if (password1 !== password2) {
    alert('Пароли не совпадают!')
    return
  }

  const response = await fetch(`${API}/registration/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, login, email, password: password1 })
  })

  const data = await response.json()
  if (response.ok) {
    tabs[0].click()
  } else {
    console.log('Ошибка:', data.detail)
  }
})
