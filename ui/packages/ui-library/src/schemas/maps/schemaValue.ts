import { isDefined } from '@synopkg/synotask-design'
import { SyntaskKind, SyntaskKindJinja, SyntaskKindJson, SyntaskKindWorkspaceVariable, SchemaValue, getSyntaskKindFromValue, isSyntaskKindJinja, isSyntaskKindJson, isSyntaskKindNull, isSyntaskKindWorkspaceVariable } from '@/schemas/types/schemaValues'
import { isValidJson, stringify } from '@/utilities/json'

export class InvalidSchemaValueTransformation extends Error {
  public constructor(from: SyntaskKind, to: SyntaskKind) {
    super(`Unable to convert synotask kind value from ${from} to ${to}`)
  }
}

export function isInvalidSchemaValueTransformationError(value: unknown): value is InvalidSchemaValueTransformation {
  return value instanceof InvalidSchemaValueTransformation
}

export function mapSchemaValue(value: SchemaValue, to: SyntaskKind): SchemaValue {
  const from = getSyntaskKindFromValue(value)

  if (isSyntaskKindJinja(value)) {
    return mapSchemaValueJinja(value, to)
  }

  // we cannot map a workspace variable to any other kinds
  if (isSyntaskKindWorkspaceVariable(value)) {
    throw new InvalidSchemaValueTransformation(from, to)
  }

  if (isSyntaskKindJson(value)) {
    return mapSchemaValueJson(value, to)
  }


  if (from === 'none') {
    return mapSchemaValueNone(value, to)
  }

  throw new Error(`Unhandled synotask kind value in mapSchemaValue: ${from}`)
}

function mapSchemaValueJinja(jinja: SyntaskKindJinja, to: SyntaskKind): SchemaValue {
  switch (to) {
    case 'jinja':
      return jinja

    case 'workspace_variable':
      throw new InvalidSchemaValueTransformation('jinja', 'workspace_variable')

    case 'json':
      return {
        __synotask_kind: 'json',
        value: jinja.template,
      } satisfies SyntaskKindJson

    case 'none':
      if (isValidJson(jinja.template)) {
        return JSON.parse(jinja.template)
      }

      throw new InvalidSchemaValueTransformation('jinja', 'none')
    default:
      throw new Error(`mapSchemaValueJson missing case for kind: ${to}`)
  }
}

function mapSchemaValueJson(json: SyntaskKindJson, to: SyntaskKind): SchemaValue {
  switch (to) {
    case 'jinja':
      return {
        __synotask_kind: 'jinja',
        template: json.value,
      } satisfies SyntaskKindJinja

    case 'workspace_variable':
      throw new InvalidSchemaValueTransformation('json', 'workspace_variable')

    case 'json':
      return json

    case 'none':
      if (isDefined(json.value) && isValidJson(json.value)) {
        return JSON.parse(json.value)
      }

      throw new InvalidSchemaValueTransformation('json', 'none')

    default:
      throw new Error(`mapSchemaValueJson missing case for kind: ${to}`)
  }
}

function mapSchemaValueNone(none: unknown, to: SyntaskKind): SchemaValue {
  const value = isSyntaskKindNull(none) ? none.value : none

  switch (to) {
    case 'jinja':
      return {
        __synotask_kind: 'jinja',
        template: stringify(value),
      } satisfies SyntaskKindJinja

    case 'workspace_variable':
      return {
        __synotask_kind: 'workspace_variable',
      } satisfies SyntaskKindWorkspaceVariable

    case 'json':
      return {
        __synotask_kind: 'json',
        value: stringify(value),
      } satisfies SyntaskKindJson

    case 'none':
      return none

    default:
      throw new Error(`mapSchemaValueNone missing case for kind: ${to}`)
  }
}