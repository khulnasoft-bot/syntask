import { SubscriptionOptions } from '@synopkg/vue-compositions'

export function useDashboardSubscriptionOptions(): SubscriptionOptions {
  return {
    interval: 30000,
  }
}
