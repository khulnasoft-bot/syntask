import { maps as designMaps } from '@syntaskhq/syntask-ui-library'
import { mapFlagResponseToFeatureFlag } from '@/maps/featureFlag'
import { mapSettingsResponseToSettings } from '@/maps/uiSettings'
import { mapCsrfTokenResponseToCsrfToken } from '@/maps/csrfToken'

export const maps = {
  ...designMaps,
  FlagResponse: { FeatureFlag: mapFlagResponseToFeatureFlag },
  SettingsResponse: { Settings: mapSettingsResponseToSettings },
  CsrfTokenResponse: { CsrfToken: mapCsrfTokenResponseToCsrfToken },
}
