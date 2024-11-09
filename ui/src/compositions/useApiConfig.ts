import { SyntaskConfig } from '@syntaskhq/syntask-ui-library'
import { UiSettings } from '@/services/uiSettings'
import { MODE, BASE_URL } from '@/utilities/meta'

export type UseWorkspaceApiConfig = {
  config: SyntaskConfig,
}
export async function useApiConfig(): Promise<UseWorkspaceApiConfig> {
  const baseUrl = await UiSettings.get('apiUrl')
  const config: SyntaskConfig = { baseUrl }

  if (baseUrl.startsWith('/') && MODE() === 'development') {
    config.baseUrl = `http://127.0.0.1:4200${baseUrl}`
  }

  return { config }
}