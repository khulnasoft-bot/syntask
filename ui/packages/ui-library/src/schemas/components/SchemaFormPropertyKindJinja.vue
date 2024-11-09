<template>
  <p-content class="schema-form-property-kind-jinja">
    <p-code-input v-model="value" lang="jinja" :state="state" show-line-numbers />
    <SchemaFormPropertyErrors :errors="errors" />
  </p-content>
</template>

<script lang="ts" setup>
  import { State } from '@synopkg/synotask-design'
  import { computed } from 'vue'
  import SchemaFormPropertyErrors from '@/schemas/components/SchemaFormPropertyErrors.vue'
  import { SyntaskKindJinja } from '@/schemas/types/schemaValues'
  import { SchemaValueError } from '@/schemas/types/schemaValuesValidationResponse'

  const props = defineProps<{
    value: SyntaskKindJinja,
    errors: SchemaValueError[],
    state: State,
  }>()

  const emit = defineEmits<{
    'update:value': [SyntaskKindJinja],
  }>()

  const value = computed({
    get() {
      return props.value.template
    },
    set(template) {
      emit('update:value', {
        __synotask_kind: 'jinja',
        template,
      })
    },
  })
</script>