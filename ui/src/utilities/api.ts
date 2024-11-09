import { createApi, SyntaskConfig } from '@syntaskhq/syntask-ui-library'
import { createActions } from '@syntaskhq/vue-compositions'
import { InjectionKey } from 'vue'
import { AdminApi } from '@/services/adminApi'
import { CsrfTokenApi, setupCsrfInterceptor } from '@/services/csrfTokenApi'
import { AxiosInstance } from 'axios'



// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export function createSyntaskApi(config: SyntaskConfig) {
  const csrfTokenApi = createActions(new CsrfTokenApi(config))

  function axiosInstanceSetupHook(axiosInstance: AxiosInstance) {
    setupCsrfInterceptor(csrfTokenApi, axiosInstance)
  };

  const workspaceApi = createApi(config, axiosInstanceSetupHook)
  return {
    ...workspaceApi,
    csrf: csrfTokenApi,
    admin: createActions(new AdminApi(config, axiosInstanceSetupHook)),
  }
}

export type CreateSyntaskApi = ReturnType<typeof createSyntaskApi>

export const syntaskApiKey: InjectionKey<CreateSyntaskApi> = Symbol('SyntaskApi')