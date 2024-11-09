import { DateRangeSelectAroundUnit, isDateRangeSelectAroundUnit } from '@synopkg/synotask-design'
import { RouteParam, InvalidRouteParamValue } from '@synopkg/vue-compositions'
import { LocationQueryValue } from 'vue-router'

export class DateRangeSelectAroundUnitParam extends RouteParam<DateRangeSelectAroundUnit> {
  protected override parse(value: LocationQueryValue): DateRangeSelectAroundUnit {
    if (isDateRangeSelectAroundUnit(value)) {
      return value
    }

    throw new InvalidRouteParamValue()
  }

  protected override format(value: DateRangeSelectAroundUnit): LocationQueryValue {
    if (isDateRangeSelectAroundUnit(value)) {
      return value
    }

    throw new InvalidRouteParamValue()
  }
}