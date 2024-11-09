import { CloudConfigMissingParamsError } from '@/models/CloudConfigMissingParamsError'
import { Api, ApiBaseUrl, SyntaskConfig } from '@/services/Api'

export type CloudApiConfig = SyntaskConfig & {
  accountId: string,
  workspaceId: string,
}

export type WorkspaceApiConfig = SyntaskConfig | CloudApiConfig

export function isCloudConfig(config: WorkspaceApiConfig): config is CloudApiConfig {
  return 'accountId' in config && 'workspaceId' in config && 'token' in config
}

const getWorkspaceBaseUrl: ApiBaseUrl = (config) => {
  if (!isCloudConfig(config)) {
    return config.baseUrl
  }

  if (config.accountId && config.workspaceId) {
    return `${config.baseUrl}/accounts/${config.accountId}/workspaces/${config.workspaceId}`
  }

  throw new CloudConfigMissingParamsError()
}

export class WorkspaceApi extends Api<WorkspaceApiConfig> {
  protected override apiBaseUrl = getWorkspaceBaseUrl
}