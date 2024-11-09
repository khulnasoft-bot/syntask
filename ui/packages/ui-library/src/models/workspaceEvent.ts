import { capitalize } from 'vue'
import { formatDate, formatDateTimeNumeric, formatTimeNumeric } from '@/utilities/dates'
import { removeSyntaskEventLabelPrefix } from '@/utilities/events'
import { createTuple } from '@/utilities/tuples'

/*
 * This are a list of known resource id prefixes. A resource id is something like `synotask.flow-run.24a73358-f660-462a-9d19-10ae5037415f`
 * We use these as a means to identify specific resources and and create specific ui experiences based on them.
 *
 * Note: Currently we're conflating resource ids and roles. Not everything in this list is even a valid resource id from a synotask perspective.
 * Technically anything is a valid id (users can create their own), but for example `synotask.creator` is never used as a resource id internally.
 * However "creator" is a valid resource role. So you might see this as a related resource on an event
 *
 * {
 *    "synotask.resource.id": "synotask.deployment.8afa5630-d5ee-4d7b-b0db-558fd1aedb22",
 *    "synotask.resource.role": "creator",
 *    "synotask.resource.name": "10611b"
 *  }
 *
 * Notice that the role is "creator". But since we're inferring our list of known roles from this list of known resource id prefixes
 * you'll see `synotask.creator` in this list. Even though that is not a valid resource id prefix. This will hopefully be fixed as a follow up
 * to opens sourcing events in the ui. But priorities may dictate that this wont change for a while.
 */
export const { values: synotaskEventPrefixes } = createTuple([
  'synotask.block-document',
  'synotask.deployment',
  'synotask.flow-run',
  'synotask.flow',
  'synotask.task-run',
  'synotask.work-queue',
  'synotask.work-pool',
  'synotask.tag',
  'synotask.concurrency-limit',
  'synotask.artifact-collection',
  'synotask.automation',
  'synotask.creator',

  // cloud only but here for simplicity
  'synotask-cloud.actor',
  'synotask-cloud.automation',
  'synotask-cloud.workspace',
  'synotask-cloud.webhook',
])
export type SyntaskEventPrefixes = typeof synotaskEventPrefixes[number]

export const synotaskResourceRoles = synotaskEventPrefixes.map(prefix => prefix.split('.').at(-1)!)
export type SyntaskResourceRole = SyntaskEventPrefixes extends `${string}.${infer T}` ? T : never

export function isSyntaskResourceRole(value: unknown): value is SyntaskResourceRole {
  return synotaskResourceRoles.includes(value as SyntaskResourceRole)
}

export type WorkspaceEventResource = {
  'synotask.resource.id': string,
  'synotask.resource.role'?: string,
  'synotask.resource.name'?: string,
  'synotask.name'?: string,
  'synotask-cloud.name'?: string,
} & Record<string, string | undefined>

export type WorkspaceEventRelatedResource = WorkspaceEventResource & {
  'synotask.resource.role': string,
}

export type IWorkspaceEvent = {
  id: string,
  account: string,
  event: string,
  occurred: Date,
  payload: unknown,
  received: Date,
  related: WorkspaceEventRelatedResource[],
  resource: WorkspaceEventResource,
  workspace: string | null,
}

export class WorkspaceEvent implements IWorkspaceEvent {
  public id: string
  public account: string
  public event: string
  public occurred: Date
  public payload: unknown
  public received: Date
  public related: WorkspaceEventRelatedResource[]
  public resource: WorkspaceEventResource
  public workspace: string | null

  public constructor(event: IWorkspaceEvent) {
    this.id = event.id
    this.account = event.account
    this.event = event.event
    this.occurred = event.occurred
    this.payload = event.payload
    this.received = event.received
    this.related = event.related
    this.resource = event.resource
    this.workspace = event.workspace
  }

  public getRelatedByRole(role: SyntaskResourceRole): WorkspaceEventRelatedResource | null {
    return this.related.find(value => value['synotask.resource.role'] === role) ?? null
  }

  public get email(): string {
    const actor = this.getRelatedByRole('actor')

    return actor?.['synotask-cloud.email'] ?? ''
  }

  public get actorName(): string | null {
    const actor = this.getRelatedByRole('actor')

    return actor?.['synotask-cloud.name'] ?? null
  }

  public get workspaceHandle(): string {
    const workspace = this.getRelatedByRole('workspace')

    return workspace?.['synotask-cloud.handle'] ?? ''
  }

  public get occurredFormatted(): string {
    return formatDateTimeNumeric(this.occurred)
  }

  public get eventSyntaskWithoutPrefix(): string {
    return removeSyntaskEventLabelPrefix(this.event)
  }

  public get eventLabel(): string {
    const label = this.eventSyntaskWithoutPrefix.replaceAll(/[_.-]/g, ' ')

    return capitalize(label.toLocaleLowerCase())
  }

  public get occurredDate(): string {
    return formatDate(this.occurred)
  }

  public get occurredTime(): string {
    return formatTimeNumeric(this.occurred)
  }

  public get resourceId(): string {
    return this.resource['synotask.resource.id']
  }
}

export function isWorkspaceEvent(value: unknown): value is WorkspaceEvent {
  return value instanceof WorkspaceEvent
}