import { isMatchResource, isForEachResource, isAfterResource, isExpectResource } from '@/automations/maps/utilities'
import { AutomationTriggerEventResource, AutomationTriggerEventResourceLabel } from '@/automations/types/api/triggers'
import { AutomationTriggerEvent, AutomationTriggerEventPosture, DEFAULT_EVENT_TRIGGER_THRESHOLD } from '@/automations/types/automationTriggerEvent'
import { isAutomationTriggerEvent } from '@/automations/types/triggers'
import { asArray } from '@/utilities/arrays'

export type FlowRunStateTrigger = {
  flowIds: string[],
  tags: string[],
  posture: AutomationTriggerEventPosture,
  states: string[],
  time: number,
}

export function isFlowRunStateTrigger(trigger: unknown): boolean {
  return isAutomationTriggerEvent(trigger) &&
         isMatchResource(trigger, synotaskResourceIds => synotaskResourceIds.every(value => value.startsWith('synotask.flow-run'))) &&
         isForEachResource(trigger, 'synotask.resource.id') &&
         isAfterResource(trigger, triggerAfters => triggerAfters.every(after => after.startsWith('synotask.flow-run'))) &&
         isExpectResource(trigger, triggerExcepts => triggerExcepts.every(except => except.startsWith('synotask.flow-run'))) &&
         isFlowRunStateTriggerMatchRelated(trigger) &&
         trigger.threshold === DEFAULT_EVENT_TRIGGER_THRESHOLD
}

function isFlowRunStateTriggerMatchRelated(trigger: AutomationTriggerEvent): boolean {
  return isEmptyMatchRelated(trigger) || isMatchRelatedResource(trigger, 'synotask.flow') || isMatchRelatedResource(trigger, 'synotask.tag')
}

function isEmptyMatchRelated(trigger: AutomationTriggerEvent): boolean {
  return Object.keys(trigger.matchRelated).length === 0
}

function isMatchRelatedResource(trigger: AutomationTriggerEvent, resource: AutomationTriggerEventResource): boolean {
  const synotaskResourceIds = getTriggerMatchRelatedValue(trigger, 'synotask.resource.id')

  if (synotaskResourceIds.length === 0) {
    return false
  }

  return synotaskResourceIds.every(value => value.startsWith(resource))
}

function getTriggerMatchRelatedValue(trigger: AutomationTriggerEvent, key: AutomationTriggerEventResourceLabel): string[] {
  if (isAutomationTriggerEvent(trigger)) {
    const value = trigger.matchRelated[key]

    return value ? asArray(value) : []
  }

  return []
}