<!-- Not converted from Quasar 1/Vue 2 -->
<template>
    <q-inner-loading :showing="loading">
      <q-spinner color="primary" size="2em" />
    </q-inner-loading>
      <table class="full-width mileage-table">
        <thead>
          <tr class="text-weight-bold">
            <td>Submitter</td>
            <td>Status</td>
            <td>Travel Dates</td>
            <td>Total Miles</td>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in rows" :key="index">
            <td>{{ row.submitterName }}</td>
            <td v-html="row.statusDisplay.outerHTML"></td>
            <td>
              {{ row.travelDates.split(' - ').map(date => readableDateNEW(date)).join(' - ') }}
            </td>
            <td>{{ getMileage(row) }}</td>
          </tr>
        </tbody>
      </table>
</template>

<style scoped lang="scss">
.list-card {
  position: relative;
  min-height: 180px;
}

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
  checked: boolean
  submissionPk: number
  status: 'submitted' | 'approved'
  statusDisplay: HTMLElement
  submitterName: string
  travelDates: string
  miles: number
}

const submissionsStore = useSubmitStore()
const rows = ref<MileageRequestListRow[]>([])
const loading = ref(false)
const currentUserPk = ref<number>(-1)

function getMileage(row: MileageRequestListRow): number {
  return row.miles
}

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
      checked: false,
      submissionPk: submission.pk,
      status: submissionMeta.status,
      statusDisplay: toStatusDisplay(submission),
      submitterName: submission.submitter_name,
      travelDates: submission.travel_dates,
      miles: submission.total_miles
    })
  })
  return mappedRows
}

function loadMileageSubmissions(pk: number): void {
  loading.value = true
  submissionsStore.getAllMileageSubsToApprove(pk)
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
    currentUserPk.value = employee.employee_pk
    loadMileageSubmissions(currentUserPk.value)
  })
})
</script>
