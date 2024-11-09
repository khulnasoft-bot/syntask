import { Can, inject } from '@syntaskhq/syntask-ui-library'
import { Permission, canKey } from '@/utilities/permissions'

export function useCan(): Can<Permission> {
  return inject(canKey)
}
