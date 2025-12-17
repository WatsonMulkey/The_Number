import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'

try {
  console.log('🚀 Starting The Number app...')

  const app = createApp(App)

  // Global error handler
  app.config.errorHandler = (err, instance, info) => {
    console.error('❌ Vue Error:', err)
    console.error('📦 Component:', instance)
    console.error('ℹ️ Info:', info)
  }

  app.use(createPinia())
  console.log('✅ Pinia initialized')

  app.use(router)
  console.log('✅ Router initialized')

  app.use(vuetify)
  console.log('✅ Vuetify initialized')

  app.mount('#app')
  console.log('✅ App mounted successfully!')
} catch (error) {
  console.error('Failed to mount app:', error)

  // SECURITY FIX: Use textContent instead of innerHTML to prevent XSS attacks
  // Error messages could contain malicious scripts if sourced from user input or external data
  const container = document.createElement('div')
  container.style.cssText = 'padding: 20px; font-family: sans-serif; max-width: 600px; margin: 50px auto; border: 2px solid red; border-radius: 8px; background: #fff;'

  const title = document.createElement('h1')
  title.style.color = 'red'
  title.textContent = 'Failed to Load Application'

  const errorPara = document.createElement('p')
  const errorLabel = document.createElement('strong')
  errorLabel.textContent = 'Error: '
  errorPara.appendChild(errorLabel)
  // Use textContent to safely render error message without XSS risk
  errorPara.appendChild(document.createTextNode(error instanceof Error ? error.message : String(error)))

  const helpPara = document.createElement('p')
  helpPara.style.color = '#666'
  helpPara.textContent = 'Check the browser console (F12) for more details.'

  const stackPre = document.createElement('pre')
  stackPre.style.cssText = 'background: #f5f5f5; padding: 10px; border-radius: 4px; overflow: auto;'
  // Use textContent to safely render stack trace without XSS risk
  stackPre.textContent = error instanceof Error ? error.stack || '' : ''

  container.appendChild(title)
  container.appendChild(errorPara)
  container.appendChild(helpPara)
  container.appendChild(stackPre)

  document.body.innerHTML = ''
  document.body.appendChild(container)
}
