import { isDefined } from '@synopkg/synotask-design'
import { MaybeRefOrGetter, toValue } from 'vue'
import { isRecord, isString } from '@/utilities'
import { createTuple } from '@/utilities/tuples'

export type SchemaValue = unknown
export type SchemaValues = Record<string, SchemaValue>

export const { values: synotaskKinds, isValue: isSyntaskKind } = createTuple([
  'none',
  'json',
  'jinja',
  'workspace_variable',
])

export type SyntaskKind = typeof synotaskKinds[number]

export function getSyntaskKindFromValue(source: MaybeRefOrGetter<SchemaValue>): SyntaskKind {
  const value = toValue(source)

  if (isSyntaskKindValue(value)) {
    return value.__synotask_kind
  }

  return 'none'
}

type BaseSyntaskKindValue<
  TKind extends SyntaskKind = SyntaskKind,
  TRest extends Record<string, unknown> = Record<string, unknown>
> = {
  __synotask_kind: TKind,
} & TRest

export type SyntaskKindValue = SyntaskKindNull | SyntaskKindJinja | SyntaskKindJson | SyntaskKindWorkspaceVariable

export function isSyntaskKindValue<T extends SyntaskKind = SyntaskKind>(value: unknown, kind?: T): value is SyntaskKindValue & { __synotask_kind: T } {
  const isKindObject = isRecord(value) && isSyntaskKind(value.__synotask_kind)

  if (!isKindObject) {
    return false
  }

  if (isSyntaskKind(kind)) {
    return value.__synotask_kind === kind
  }

  return true
}

export type SyntaskKindNull = BaseSyntaskKindValue<'none', {
  value: unknown,
}>

export function isSyntaskKindNull(value: unknown): value is SyntaskKindNull {
  return isSyntaskKindValue(value, 'none') && 'value' in value
}

export type SyntaskKindJson = BaseSyntaskKindValue<'json', {
  value?: string,
}>

export function isSyntaskKindJson(value: unknown): value is SyntaskKindJson {
  return isSyntaskKindValue(value, 'json') && (isString(value.value) || !isDefined(value.value))
}

export type SyntaskKindJinja = BaseSyntaskKindValue<'jinja', {
  template?: string,
}>

export function isSyntaskKindJinja(value: unknown): value is SyntaskKindJinja {
  return isSyntaskKindValue(value, 'jinja') && isString(value.template)
}

export type SyntaskKindWorkspaceVariable = BaseSyntaskKindValue<'workspace_variable', {
  variable_name?: string,
}>

export function isSyntaskKindWorkspaceVariable(value: unknown): value is SyntaskKindWorkspaceVariable {
  return isSyntaskKindValue(value, 'workspace_variable') && (isString(value.variable_name) || !isDefined(value.variable_name))
}

export type BlockDocumentReferenceValue = {
  $ref: string,
}

export function isBlockDocumentReferenceValue(value: unknown): value is BlockDocumentReferenceValue {
  return isRecord(value) && isString(value.$ref)
}

export function asBlockDocumentReferenceValue(value: unknown): BlockDocumentReferenceValue | undefined {
  if (isBlockDocumentReferenceValue(value)) {
    return value
  }

  return undefined
}