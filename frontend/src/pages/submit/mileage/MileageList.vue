<template>
<div>
  <q-inner-loading :showing="loading">
    <q-spinner color="primary" size="2em" />
  </q-inner-loading>
  <table class="full-width mileage-table">
    <thead>
      <tr class="text-weight-bold">
        <td>Status</td>
        <td>Travel Dates</td>
        <td>Miles</td>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(row, index) in rows" :key="index">
        <td v-html="row.statusDisplay.outerHTML"></td>
        <td>{{ row.travelDates.split(' - ').map(date => readableDateNEW(date)).join(' - ') }}</td>
        <td>{{ row.totalMiles }}</td>
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

import { readableDateNEW } from 'src/filters'
import { useSubmitStore } from 'src/stores/submit'
import { MileageSubmissionRetrieve } from 'src/types'
import { getCurrentUser } from 'src/utils'

interface MileageRequestListRow {
  submissionPk: number
  status: 'submitted' | 'approved'
  statusDisplay: HTMLElement
  totalMiles: number
  travelDates: string
}

const submissionsStore = useSubmitStore()
const rows = ref<MileageRequestListRow[]>([])
const loading = ref(false)

function toStatusDisplay(submission: MileageSubmissionRetrieve): HTMLElement {
  const el = document.createElement('div')
  if (submission.submission?.status === 'approved') {
    el.textContent = 'Approved'
  } else {
    el.textContent = 'Submitted'
    const link = document.createElement('a')
    link.textContent = '(Edit)'
    link.href = `/submit/mileage/${submission.pk}`
    link.style.marginLeft = '4px'
    el.appendChild(link)
  }
  return el
}

function mapRows(data: Array<MileageSubmissionRetrieve>): Array<MileageRequestListRow> {
  const mappedRows: Array<MileageRequestListRow> = []
  data.forEach((submission) => {
    const submissionMeta = submission.submission
    if (!submissionMeta) return
    mappedRows.push({
      submissionPk: submission.pk,
      status: submissionMeta.status,
      statusDisplay: toStatusDisplay(submission),
      totalMiles: submission.total_miles,
      travelDates: submission.travel_dates
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
