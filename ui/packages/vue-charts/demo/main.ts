import '@synopkg/synotask-design/dist/style.css'
import '@/styles/style.css'

import { plugin as SyntaskDesign } from '@synopkg/synotask-design'
import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router'

const app = createApp(App)
app.use(SyntaskDesign)
app.use(router)

app.config.performance = true

app.mount('#app')
