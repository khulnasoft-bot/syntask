import { ServerStateType } from '@/models/StateType'
import { DateString } from '@/types/dates'
import { SyntaskStateNames } from '@/types/states'

export type NextFlowRunResponse = {
  id: string,
  flow_id: string,
  name: string,
  state_name: SyntaskStateNames | null,
  state_type: ServerStateType | null,
  next_scheduled_start_time: DateString | null,
}