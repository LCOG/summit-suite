<template>
<q-inner-loading :showing="loading">
  <q-spinner color="primary" size="2em" />
</q-inner-loading>
<q-table
  :rows="rows"
  :loading="loading"
  :columns="[
    { name: 'submissionType', label: 'Type', field: 'submissionType', align: 'left' },
    { name: 'status', label: 'Status', field: 'status', align: 'left' },
    { name: 'date', label: 'Last Updated', field: 'date', align: 'left' }
  ]"
>
  <template v-slot:body="props">
    <q-tr :props="props" @click="navigateToDetail(props.row.submissionPk)" class="submission-row">
      <q-td v-for="col in props.cols" :key="col.name" :props="props">
        <span v-if="col.name === 'submissionType'">{{ props.row.submissionType }}</span>
        <span v-else-if="col.name === 'status'">{{ props.row.statusDisplay }}</span>
        <span v-else-if="col.name === 'date'">{{ readableDateTimeNEW(props.row.date) }}</span>
      </q-td>
    </q-tr>
  </template>
</q-table>
</template>

<style scoped lang="scss">
</style>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Notify } from 'quasar'

import { readableDateTimeNEW } from 'src/filters'
import { useSubmitStore } from 'src/stores/submit'
import { SubmissionRetrieve } from 'src/types'
import { getCurrentUser } from 'src/utils'

interface SubmissionListRow {
  submissionPk: number
  submissionType: string
  status: 'submitted' | 'approved'
  statusDisplay: string
  submitterName: string
  date: string
}

const router = useRouter()
const submissionsStore = useSubmitStore()
const rows = ref<SubmissionListRow[]>([])
const loading = ref(false)

function toStatusText(status: 'submitted' | 'approved'): string {
  return status ? status.charAt(0).toUpperCase() + status.slice(1) : ''
}

function navigateToDetail(submissionPk: number): void {
  router.push(`/submit/mileage/${submissionPk}`)
}

function loadSubmissions(pk: number): void {
  loading.value = true
  submissionsStore.getAllSubsForEmployee(pk)
    .then((result) => {
      rows.value = (result as Array<SubmissionRetrieve>).map((submission) => ({
        submissionPk: submission.pk,
        submissionType: submission.type,
        status: submission.status,
        statusDisplay: toStatusText(submission.status),
        submitterName: submission.submitter_name,
        date: submission.updated_at
      }))
    })
    .catch((e) => {
      console.error('Error loading mileage submissions:', e)
      Notify.create('Unable to load mileage requests')
    })
    .finally(() => {
      loading.value = false
    })
}

onMounted(() => {
  getCurrentUser().then((employee) => {
    loadSubmissions(employee.pk)
  })
})
</script>
