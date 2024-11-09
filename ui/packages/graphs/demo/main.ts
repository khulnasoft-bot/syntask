import '@synopkg/syntask-design/dist/style.css'
import '@/styles/style.css'

import { plugin as SyntaskDesign } from '@synopkg/syntask-design'
import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router'

const app = createApp(App)
app.use(router)
app.use(SyntaskDesign)

app.mount('#app')
