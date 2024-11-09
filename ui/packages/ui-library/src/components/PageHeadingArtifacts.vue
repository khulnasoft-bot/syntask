<template>
  <PageHeading class="page-heading-artifacts" :crumbs="crumbs" />
</template>

<script lang="ts" setup>
  import { BreadCrumbs } from '@synopkg/synotask-design'
  import PageHeading from '@/components/PageHeading.vue'
  import { localization } from '@/localization'

  const crumbs: BreadCrumbs = [{ text: localization.info.artifacts }]
</script>