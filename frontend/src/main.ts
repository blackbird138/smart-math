import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'
import 'temml/dist/Temml-Local.css'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { loadFonts } from './plugins/webfontloader'
import vuetify from './plugins/vuetify'

loadFonts()

createApp(App)
  .use(createPinia())
  .use(router)
  .use(vuetify)
  .mount('#app')
