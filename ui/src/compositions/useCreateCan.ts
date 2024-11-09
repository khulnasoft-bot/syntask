import { Can, createCan, workspacePermissions } from '@syntaskhq/syntask-ui-library'
import { useSubscription } from '@syntaskhq/vue-compositions'
import { computed, Ref } from 'vue'
import { uiSettings } from '@/services/uiSettings'
import { Permission } from '@/utilities/permissions'

type UseCreateCan = {
  can: Can<Permission>,
  pending: Ref<boolean>,
}

export function useCreateCan(): UseCreateCan {
  const flagsSubscription = useSubscription(uiSettings.getFeatureFlags, [])

  const permissions = computed<Permission[]>(() => [
    ...workspacePermissions,
    ...flagsSubscription.response ?? [],
  ])

  const can = createCan(permissions)
  const pending = computed(() => flagsSubscription.loading)

  return {
    can,
    pending,
  }
}