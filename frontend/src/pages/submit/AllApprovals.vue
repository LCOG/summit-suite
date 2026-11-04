<!-- Not converted from Quasar 1/Vue 2 -->
<template>
  <div>
    <q-inner-loading :showing="loading">
      <q-spinner color="primary" size="2em" />
    </q-inner-loading>
    <table class="full-width submission-table">
      <thead>
        <tr class="text-weight-bold">
          <td>Type</td>
          <td>Submitter</td>
          <td>Status</td>
          <td>Submitted</td>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in rows" :key="index">
          <td>{{ row.submissionType }}</td>
          <td>{{ row.submitterName }}</td>
          <td>{{ row.statusDisplay }}</td>
          <td>{{ readableDateTimeNEW(row.createdAt) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped lang="scss">
.list-card {
  position: relative;
  min-height: 180px;
}

.submission-table {
  border-collapse: collapse;

  thead,
  tbody {
    td {
      border: 1px solid rgba(0, 0, 0, 0.12);
      padding: 8px 10px;
    }
  }

  thead td {
    font-weight: 600;
  }
}
</style>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Notify } from 'quasar'

import { readableDateTimeNEW } from 'src/filters'
import { useSubmissionsStore } from 'src/stores/submissions'
import { SubmissionRetrieve } from 'src/types'
import { getCurrentUser } from 'src/utils'

interface SubmissionListRow {
  submissionPk: number
  submissionType: string
  status: 'submitted' | 'approved'
  statusDisplay: string
  submitterName: string
  createdAt: string
}

const submissionsStore = useSubmissionsStore()
const rows = ref<SubmissionListRow[]>([])
const loading = ref(false)
const currentUserPk = ref<number>(-1)

function toStatusDisplay(status: 'submitted' | 'approved'): string {
  return status === 'approved' ? 'Approved' : 'Submitted'
}

function mapRows(data: Array<SubmissionRetrieve>): Array<SubmissionListRow> {
  const mappedRows: Array<SubmissionListRow> = []
  data.forEach((submission) => {
    mappedRows.push({
      submissionPk: submission.pk,
      submissionType: submission.type,
      status: submission.status,
      statusDisplay: toStatusDisplay(submission.status),
      submitterName: submission.submitter_name,
      createdAt: submission.created_at,
    })
  })
  return mappedRows
}

function loadSubmissions(pk: number): void {
  loading.value = true
  submissionsStore.getAllSubsToApprove(pk)
    .then((result) => {
      rows.value = mapRows(result as Array<SubmissionRetrieve>)
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
    currentUserPk.value = employee.pk
    loadSubmissions(currentUserPk.value)
  })
})
</script>
