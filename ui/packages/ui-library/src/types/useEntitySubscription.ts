import { Action, UseSubscription } from '@synopkg/vue-compositions'
import { ComputedRef } from 'vue'

export type UseEntitySubscription<T extends Action, PropertyName extends string> = {
  subscription: UseSubscription<T | (() => undefined)>,
} & {
  [ P in PropertyName ]: ComputedRef<UseSubscription<T | (() => undefined)>['response']>
}