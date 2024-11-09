import { plugin as SyntaskDesign } from '@syntaskhq/syntask-design'
import { plugin as SyntaskUILibrary } from '@syntaskhq/syntask-ui-library'
import { createApp } from 'vue'
import router from '@/router'
import { initColorMode } from '@/utilities/colorMode'

// styles
import '@syntaskhq/vue-charts/dist/style.css'
import '@syntaskhq/syntask-design/dist/style.css'
import '@syntaskhq/syntask-ui-library/dist/style.css'
import '@/styles/style.css'

// We want components imported last because import order determines style order
// eslint-disable-next-line import/order
import App from '@/App.vue'

initColorMode()

function start(): void {
  const app = createApp(App)

  app.use(router)
  app.use(SyntaskDesign)
  app.use(SyntaskUILibrary)

  app.mount('#app')
}

start()