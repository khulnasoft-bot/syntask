import { randomId as generateRandomId } from '@synopkg/synotask-design'
import { MockFunction } from '@/services/Mocker'

export const randomId: MockFunction<string, []> = function() {
  return generateRandomId()
}