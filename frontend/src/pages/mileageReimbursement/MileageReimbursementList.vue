<template>
<div>
  <q-inner-loading :showing="loading">
    <q-spinner color="primary" size="2em" />
  </q-inner-loading>
  <table class="full-width mileage-table">
    <thead>
      <tr class="text-weight-bold">
        <td>Submitter</td>
        <td>Status</td>
        <td>Date</td>
        <td>Purpose/Destination</td>
        <td>Subfund &amp; Contract</td>
        <td>Miles</td>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(row, index) in rows" :key="index">
        <td>{{ row.submitterName }}</td>
        <td>{{ row.statusDisplay }}</td>
        <td>{{ row.date }}</td>
        <td>{{ row.purpose }}</td>
        <td>{{ row.subfund }}</td>
        <td>{{ getMileage(row) }}</td>
      </tr>
    </tbody>
  </table>
</div>
</template>

<style scoped lang="scss">
.mileage-table {
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

import { useSubmissionsStore } from 'src/stores/submissions'
import { MileageSubmissionRetrieve } from 'src/types'
import { getCurrentUser } from 'src/utils'

interface MileageRequestListRow {
  submissionPk: number
  status: 'submitted' | 'approved'
  statusDisplay: string
  submitterName: string
  date: string
  purpose: string
  subfund: string
  start: number
  finish: number
  miles: number
}

const submissionsStore = useSubmissionsStore()
const rows = ref<MileageRequestListRow[]>([])
const loading = ref(false)


function getMileage(row: MileageRequestListRow): number {
  return row.miles
}

function toStatusDisplay(status: 'submitted' | 'approved'): string {
  return status === 'approved' ? 'Approved' : 'Submitted'
}

function mapRows(data: Array<MileageSubmissionRetrieve>): Array<MileageRequestListRow> {
  const mappedRows: Array<MileageRequestListRow> = []
  data.forEach((submission) => {
    const submissionMeta = submission.submission
    if (!submissionMeta) return
    submission.rows.forEach((row) => {
      mappedRows.push({
        submissionPk: submission.pk,
        status: submissionMeta.status,
        statusDisplay: toStatusDisplay(submissionMeta.status),
        submitterName: submission.submitter_name,
        date: row.date,
        purpose: row.purpose,
        subfund: row.contract_fund,
        start: row.odometer_start,
        finish: row.odometer_finish,
        miles: row.miles
      })
    })
  })
  return mappedRows
}

function loadMileageSubmissions(pk: number): void {
  loading.value = true
  submissionsStore.getAllMileageSubsForEmployee(pk)
    .then((result) => {
      rows.value = mapRows(result as Array<MileageSubmissionRetrieve>)
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
    loadMileageSubmissions(employee.pk)
  })
})
</script>
