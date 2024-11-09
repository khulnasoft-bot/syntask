import { AutomationTriggerEvent } from '@/automations/types/automationTriggerEvent'
import { AutomationTrigger } from '@/automations/types/triggers'
import { WorkspaceEvent } from '@/models'
import { MapFunction } from '@/services/Mapper'
import { getSyntaskResourceRole } from '@/utilities/events'

export const mapEventToAutomationTrigger: MapFunction<WorkspaceEvent, AutomationTrigger> = function(event) {
  const role = getSyntaskResourceRole(event.event)

  switch (role) {
    case 'flow-run':
      return mapEventToFlowRunStateChangeTrigger(event)
    case 'work-queue':
      return mapEventToWorkQueueTrigger(event)
    default:
      return mapEventToCustomAutomationTrigger(event)
  }
}

function mapEventToFlowRunStateChangeTrigger(event: WorkspaceEvent): AutomationTrigger {
  const relatedFlow = event.getRelatedByRole('flow')

  return new AutomationTriggerEvent({
    'posture': 'Reactive',
    'match': {
      'synotask.resource.id': event.resourceId,
    },
    'matchRelated': {
      'synotask.resource.role': 'flow',
      'synotask.resource.id': relatedFlow?.['synotask.resource.id'],
    },
    'forEach': ['synotask.resource.id'],
    'expect': [event.event],
  })
}

function mapEventToWorkQueueTrigger(event: WorkspaceEvent): AutomationTrigger {
  const relatedWorkQueue = event.getRelatedByRole('work-queue')

  return new AutomationTriggerEvent({
    'posture': 'Reactive',
    'match': {
      'synotask.resource.id': event.resourceId,
    },
    'matchRelated': {
      'synotask.resource.role': 'flow',
      'synotask.resource.id': relatedWorkQueue?.['synotask.resource.id'],
    },
    'forEach': ['synotask.resource.id'],
    'expect': [event.event],
  })
}

function mapEventToCustomAutomationTrigger(event: WorkspaceEvent): AutomationTrigger {
  return new AutomationTriggerEvent({
    'posture': 'Reactive',
    'match': {
      'synotask.resource.id': event.resourceId,
    },
    'expect': [event.event],
  })
}