import { StateType } from '@/models/StateType'
import { SyntaskStateNames } from '@/types/states'

export type NextFlowRun = {
  id: string,
  flowId: string,
  name: string,
  stateName: SyntaskStateNames | null,
  stateType: StateType | null,
  nextScheduledStartTime: Date | null,
}