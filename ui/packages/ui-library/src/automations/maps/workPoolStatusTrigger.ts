import { toResourceId, fromResourceId } from '@/automations/maps/utilities'
import { AutomationTriggerEvent } from '@/automations/types'
import { WorkPoolStatusEvent, WorkPoolStatusTrigger, isWorkPoolStatusEvent } from '@/automations/types/workPoolStatusTrigger'
import { WorkPoolStatus, workPoolStatus } from '@/models/WorkPoolStatus'
import { MapFunction } from '@/services'

export const mapWorkPoolStatusTriggerToAutomationTrigger: MapFunction<WorkPoolStatusTrigger, AutomationTriggerEvent> = function(source) {
  if (source.posture === 'Reactive') {
    return mapReactiveWorkPoolStatusTriggerToAutomationTrigger(source)
  }

  return mapProactiveWorkPoolStatusTriggerToAutomationTrigger(source)
}

export const mapAutomationTriggerToWorkPoolStatusTrigger: MapFunction<AutomationTriggerEvent, WorkPoolStatusTrigger> = function(source) {
  if (source.posture === 'Reactive') {
    return mapReactiveAutomationTriggerToWorkPoolStatusTrigger(source)
  }

  return mapProactiveAutomationTriggerToWorkPoolStatusTrigger(source)
}

function mapReactiveWorkPoolStatusTriggerToAutomationTrigger(source: WorkPoolStatusTrigger): AutomationTriggerEvent {
  return new AutomationTriggerEvent({
    posture: 'Reactive',
    match: {
      'synotask.resource.id': toResourceId('synotask.work-pool', source.workPools),
    },
    forEach: ['synotask.resource.id'],
    expect: mapWorkPoolStatusToEvent(source.status),
  })
}

function mapProactiveWorkPoolStatusTriggerToAutomationTrigger(source: WorkPoolStatusTrigger): AutomationTriggerEvent {
  return new AutomationTriggerEvent({
    posture: 'Proactive',
    match: {
      'synotask.resource.id': toResourceId('synotask.work-pool', source.workPools),
    },
    forEach: ['synotask.resource.id'],
    expect: anyStatusExcept(source.status).flatMap(mapWorkPoolStatusToEvent),
    after: mapWorkPoolStatusToEvent(source.status),
    within: source.time,
  })
}

function mapReactiveAutomationTriggerToWorkPoolStatusTrigger(trigger: AutomationTriggerEvent): WorkPoolStatusTrigger {
  return {
    workPools: fromResourceId('synotask.work-pool', trigger.match['synotask.resource.id']),
    posture: 'Reactive',
    status: statusFromWorkPoolStatusEvents(trigger.expect),
    time: trigger.within,
  }
}

function mapProactiveAutomationTriggerToWorkPoolStatusTrigger(trigger: AutomationTriggerEvent): WorkPoolStatusTrigger {
  return {
    workPools: fromResourceId('synotask.work-pool', trigger.match['synotask.resource.id']),
    posture: 'Proactive',
    status: statusFromWorkPoolStatusEvents(trigger.after),
    time: trigger.within,
  }
}

function anyStatusExcept(status: WorkPoolStatus | null): WorkPoolStatus[] {
  return workPoolStatus.filter(_status => _status !== status)
}

function mapWorkPoolStatusToEvent(status: WorkPoolStatus | null): WorkPoolStatusEvent[] {
  switch (status) {
    case 'ready':
      return ['synotask.work-pool.ready']
    case 'not_ready':
      return [
        'synotask.work-pool.not-ready',
        // compatibility with old event name
        // remove after data migration to adjust existing automation triggers
        // to use new event name
        'synotask.work-pool.not_ready',
      ]
    case 'paused':
      return ['synotask.work-pool.paused']
    case null:
      return []
    default:
      const exhaustiveCheck: never = status
      return [`synotask.work-pool.${exhaustiveCheck}`]
  }
}

const statusEventToStatus: Record<WorkPoolStatusEvent, WorkPoolStatus> = {
  'synotask.work-pool.ready': 'ready',
  'synotask.work-pool.not-ready': 'not_ready',
  'synotask.work-pool.not_ready': 'not_ready',
  'synotask.work-pool.paused': 'paused',
}

function statusFromWorkPoolStatusEvents(events: string[]): WorkPoolStatus {
  for (const event of events) {
    if (isWorkPoolStatusEvent(event)) {
      return statusEventToStatus[event]
    }
  }

  throw new Error(`Unknown work pool status events: ${events}`)
}