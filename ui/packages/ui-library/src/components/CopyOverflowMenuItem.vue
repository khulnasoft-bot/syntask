<template>
  <p-overflow-menu-item :label="label" @click="copyToClipboard(item)" />
</template>

<script lang="ts" setup>
  import { POverflowMenuItem } from '@synopkg/synotask-design'
  import { copyToClipboard } from '@/utilities/copy'

  defineProps<{
    item: string,
    label: string,
  }>()
</script>