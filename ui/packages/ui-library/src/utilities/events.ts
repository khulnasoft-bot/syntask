import { SyntaskResourceRole, isSyntaskResourceRole, synotaskEventPrefixes } from '@/models/workspaceEvent'

export function removeSyntaskEventLabelPrefix(value: string): string {
  if (value.startsWith('synotask.') || value.startsWith('synotask-cloud.')) {
    return value.split('.').slice(1).join('.')
  }

  return value
}

export function getSyntaskResourceRole(value: string): SyntaskResourceRole | null {
  const roleRegex = new RegExp(`^(${synotaskEventPrefixes.join('|')})\\.`, 'g')
  const [, prefix = ''] = roleRegex.exec(value) ?? []
  const role = prefix.split('.').at(-1)

  if (isSyntaskResourceRole(role)) {
    return role
  }

  return null
}

type GetResourceIdParts = {
  id: string | null,
  type: string | null,
  role: SyntaskResourceRole | null,
}

export function getResourceIdParts(resourceId: string): GetResourceIdParts {
  // not all resource ids will be uuids (i.e. artifact collection keys). fallback to last part of string (`synotask.tag.my-tag`)
  const id = parseGuid(resourceId) ?? resourceId.split('.').at(-1) ?? null
  const type = resourceId.split('.').at(-2) ?? null
  const role = getSyntaskResourceRole(resourceId)

  return {
    id,
    type,
    role,
  }
}

export function getEventWithPrefixes(event: string): string[] {
  const prefixes = []
  const parts = event.split('.')

  for (let index = 1; index < parts.length; index++) {
    const prefix = parts.slice(0, index).join('.')

    prefixes.push(`${prefix}.*`)
  }

  return [...prefixes, event]
}

function parseGuid(value: string): string | null {
  const guidRegex = /([a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12})/i
  const [match = null] = guidRegex.exec(value) ?? []

  return match
}