import { DateRangeSelectValue } from '@synopkg/synotask-design'

export type FlowStatsFilter = {
  range: NonNullable<DateRangeSelectValue>,
  flowId: string,

}