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
  console.error('💥 Failed to mount app:', error)
  document.body.innerHTML = `
    <div style="padding: 20px; font-family: sans-serif; max-width: 600px; margin: 50px auto; border: 2px solid red; border-radius: 8px; background: #fff;">
      <h1 style="color: red;">❌ Failed to Load Application</h1>
      <p><strong>Error:</strong> ${error instanceof Error ? error.message : String(error)}</p>
      <p style="color: #666;">Check the browser console (F12) for more details.</p>
      <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; overflow: auto;">${error instanceof Error ? error.stack : ''}</pre>
    </div>
  `
}
