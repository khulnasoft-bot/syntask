import { DateRangeSelectValue } from '@synopkg/synotask-design'

export type WorkspaceDashboardFilter = {
  range: NonNullable<DateRangeSelectValue>,
  tags: string[],
  hideSubflows?: boolean,
}