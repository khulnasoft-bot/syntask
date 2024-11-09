import { inject } from '@syntaskhq/syntask-ui-library'
import { CreateSyntaskApi, syntaskApiKey } from '@/utilities/api'

export function useSyntaskApi(): CreateSyntaskApi {
  return inject(syntaskApiKey)
}