<template>
  <p-layout-default>
    <template #header>
      <PageHeadingWorkPoolCreate />
    </template>
    <WorkPoolCreateWizard />
  </p-layout-default>
</template>

<script lang="ts" setup>
  import { PageHeadingWorkPoolCreate, WorkPoolCreateWizard } from '@syntaskhq/syntask-ui-library'
  import { usePageTitle } from '@/compositions/usePageTitle'

  usePageTitle('Create Work Pool')
</script>