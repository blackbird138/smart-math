import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import router from './router'
import App from './App.vue'
import './style.css'
import 'temml/dist/Temml-Local.css'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { loadFonts } from './plugins/webfontloader'
import vuetify from './plugins/vuetify'

loadFonts()

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

createApp(App)
  .use(pinia)
  .use(router)
  .use(vuetify)
  .mount('#app')
