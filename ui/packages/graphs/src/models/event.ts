export type RunGraphEventResource = {
  'syntask.resource.id': string,
  'syntask.resource.role'?: string,
  'syntask.resource.name'?: string,
  'syntask.name'?: string,
  'syntask-cloud.name'?: string,
} & Record<string, string | undefined>

export type EventRelatedResource = RunGraphEventResource & {
  'syntask.resource.role': string,
}

export type RunGraphEvent = {
  id: string,
  occurred: Date,
  account: string,
  event: string,
  payload: unknown,
  received: Date,
  related: EventRelatedResource[],
  resource: RunGraphEventResource,
  workspace: string | null,
}