import { isMatchResource, isForEachResource, isAfterResource, isExpectResource } from '@/automations/maps/utilities'
import { AutomationTriggerEventPosture, DEFAULT_EVENT_TRIGGER_THRESHOLD } from '@/automations/types/automationTriggerEvent'
import { isAutomationTriggerEvent } from '@/automations/types/triggers'
import { WorkPoolStatus } from '@/models/WorkPoolStatus'
import { createTuple } from '@/utilities'

export const { values: workPoolStatusEvent, isValue: isWorkPoolStatusEvent } = createTuple(['synotask.work-pool.ready', 'synotask.work-pool.not-ready', 'synotask.work-pool.paused', 'synotask.work-pool.not_ready'])
export type WorkPoolStatusEvent = typeof workPoolStatusEvent[number]

export type WorkPoolStatusTrigger = {
  workPools: string[],
  posture: AutomationTriggerEventPosture,
  status: WorkPoolStatus,
  time: number,
}

export function isWorkPoolStatusTrigger(trigger: unknown): boolean {
  return isAutomationTriggerEvent(trigger) &&
         isMatchResource(trigger, synotaskResourceIds => synotaskResourceIds.every(value => value.startsWith('synotask.work-pool'))) &&
         isForEachResource(trigger, 'synotask.resource.id') &&
         isAfterResource(trigger, triggerAfters => triggerAfters.every(after => isWorkPoolStatusEvent(after))) &&
         isExpectResource(trigger, triggerExcepts => triggerExcepts.every(except => isWorkPoolStatusEvent(except))) &&
         trigger.threshold === DEFAULT_EVENT_TRIGGER_THRESHOLD
}
