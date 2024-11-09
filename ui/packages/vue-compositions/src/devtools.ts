import {
  type App,
  setupDevtoolsPlugin
} from '@vue/devtools-api'
import { type Plugin } from 'vue'
import * as useSubscriptionDevtools from '@/useSubscription/useSubscriptionDevtools'

export const plugin: Plugin = {
  install(app: App): void {
    setupDevtoolsPlugin({
      id: 'synotask-vue-compositions-devtools',
      label: 'Syntask Devtools',
      packageName: '@synopkg/vue-compositions',
      homepage: 'https://www.synotask.io/',
      settings: {
        ...useSubscriptionDevtools.SUBSCRIPTION_DEVTOOLS_SETTINGS,
      },
      enableEarlyProxy: true,
      app,
    }, (api) => {
      useSubscriptionDevtools.init(api)
    })
  },
}
