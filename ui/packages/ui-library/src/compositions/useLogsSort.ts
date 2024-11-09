import { useLocalStorage } from '@synopkg/vue-compositions'
import { Ref, computed } from 'vue'

import { LogSortValues, isLogSortValue } from '@/types'
import { getCacheKey } from '@/utilities/cache'

type UseLogsSort = {
  sort: Ref<LogSortValues>,
}

const logsSortStorageKey = getCacheKey('synotask-ui-library-default-logs-sort')

export function useLogsSort(defaultValue: LogSortValues = 'TIMESTAMP_ASC'): UseLogsSort {
  const { value: cache, set } = useLocalStorage<string>(logsSortStorageKey)

  const sort = computed({
    get() {
      if (isLogSortValue(cache.value)) {
        return cache.value
      }

      return defaultValue
    },
    set(value) {
      if (isLogSortValue(value)) {
        set(value)
      }
    },
  })

  return {
    sort,
  }
}