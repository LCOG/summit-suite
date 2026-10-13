<!-- Not converted from Quasar 1/Vue 2 -->
<template>
  <q-card class="q-pa-md list-card">
    <q-inner-loading :showing="loading">
      <q-spinner color="primary" size="2em" />
    </q-inner-loading>
    <q-form @submit.prevent="formSubmit" class="q-gutter-md">
      <table class="full-width mileage-table">
        <thead>
          <tr>
            <td colspan="5" />
            <td colspan="2" class="text-center text-weight-bold">Odometer</td>
            <td />
          </tr>
          <tr class="text-weight-bold">
            <td>
              <q-checkbox :model-value="allChecked" @update:model-value="toggleAll" />
            </td>
            <td>Submitter</td>
            <td>Status</td>
            <td>Date</td>
            <td>Purpose/Destination</td>
            <td>Subfund &amp; Contract</td>
            <td>Start</td>
            <td>Finish</td>
            <td>Miles</td>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in rows" :key="index">
            <td>
              <q-checkbox
                v-model="row.checked"
                :disable="row.status !== 'submitted'"
              />
            </td>
            <td>{{ row.submitterName }}</td>
            <td>{{ row.statusDisplay }}</td>
            <td>{{ row.date }}</td>
            <td>{{ row.purpose }}</td>
            <td>{{ row.subfund }}</td>
            <td>{{ row.start }}</td>
            <td>{{ row.finish }}</td>
            <td>{{ getMileage(row) }}</td>
          </tr>
        </tbody>
      </table>

      <div>
        <q-btn
          label="Approve all checked"
          type="submit"
          color="primary"
          :loading="submitting"
          :disable="loading || submitting"
        />
      </div>
    </q-form>
  </q-card>
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
import { computed, onMounted, ref } from 'vue'
import { Notify } from 'quasar'

import { useSubmissionsStore } from 'src/stores/submissions'
import { MileageSubmissionRetrieve } from 'src/types'

interface MileageRequestListRow {
  checked: boolean
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
const submitting = ref(false)

const allChecked = computed(() => {
  const selectableRows = rows.value.filter((row) => row.status === 'submitted')
  return selectableRows.length > 0 && selectableRows.every((row) => row.checked)
})

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
        checked: false,
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

function loadMileageSubmissions(): void {
  loading.value = true
  submissionsStore.getMileageSubmissions()
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

function toggleAll(checked: boolean): void {
  rows.value.forEach((row) => {
    if (row.status !== 'submitted') {
      row.checked = false
      return
    }
    row.checked = checked
  })
}

function formSubmit(): void {
  if (loading.value || submitting.value) {
    return
  }
  const selectedSubmissionPks = Array.from(
    new Set(
      rows.value
        .filter((row) => row.checked && row.status === 'submitted')
        .map((row) => row.submissionPk)
    )
  )
  if (!selectedSubmissionPks.length) {
    Notify.create('No mileage requests selected')
    return
  }
  submitting.value = true
  Promise.all(
    selectedSubmissionPks.map((pk) => submissionsStore.approveMileageSubmission(pk))
  )
    .then(() => {
      Notify.create(`Approved ${selectedSubmissionPks.length} mileage request(s)`)
      loadMileageSubmissions()
    })
    .catch((e) => {
      console.error('Error approving mileage submissions:', e)
      Notify.create('Unable to approve one or more requests')
      loadMileageSubmissions()
    })
    .finally(() => {
      submitting.value = false
    })
}

onMounted(() => {
  loadMileageSubmissions()
})
</script>
