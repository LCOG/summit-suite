<template>
<div>
  <q-inner-loading :showing="loading">
    <q-spinner color="primary" size="2em" />
  </q-inner-loading>
  <q-btn unelevated rounded color="primary" icon="add" label="Request Reimbursement" @click="navigateToCreate()" />
  <q-table
    :rows="rows"
    row-key="submissionPk"
    :columns="columns"
    :pagination="{ rowsPerPage: 50 }"
    class="q-mt-md"
  >
    <template v-slot:body="props">
      <q-tr :props="props" @click="navigateToDetail(props.row.submissionPk)" class="submission-row">
        <q-td v-for="col in props.cols" :key="col.name" :props="props">
          <span v-if="col.name === 'status'">{{ props.row.statusDisplay }}</span>
          <span v-else-if="col.name === 'travelDates'">{{ props.row.travelDates.split(' - ').map(date => readableDateNEW(date)).join(' - ') }}</span>
          <span v-else-if="col.name === 'totalMiles'">{{ props.row.totalMiles }}</span>
        </q-td>
      </q-tr>
    </template>
  </q-table>
</div>
</template>

<style scoped lang="scss">
</style>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Notify } from 'quasar'
import { useRouter } from 'vue-router'

const router = useRouter()

function navigateToDetail(submissionPk: number): void {
  router.push(`/submit/mileage/${submissionPk}`)
}
function navigateToCreate(): void {
  router.push('/submit/mileage/create')
}

import { readableDateNEW } from 'src/filters'
import { useSubmitStore } from 'src/stores/submit'
import { MileageSubmissionRetrieve } from 'src/types'
import { getCurrentUser } from 'src/utils'

interface MileageRequestListRow {
  submissionPk: number
  status: 'submitted' | 'approved'
  statusDisplay: string
  totalMiles: number
  travelDates: string
}

const columns = [
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'travelDates', label: 'Travel Dates', field: 'travelDates', align: 'left' },
  { name: 'totalMiles', label: 'Miles', field: 'totalMiles', align: 'left' }
]

const submissionsStore = useSubmitStore()
const rows = ref<MileageRequestListRow[]>([])
const loading = ref(false)

function toStatusText(status: 'submitted' | 'approved'): string {
  return status ? status.charAt(0).toUpperCase() + status.slice(1) : ''
}

function mapRows(data: Array<MileageSubmissionRetrieve>): Array<MileageRequestListRow> {
  const mappedRows: Array<MileageRequestListRow> = []
  data.forEach((submission) => {
    const submissionMeta = submission.submission
    if (!submissionMeta) return
    mappedRows.push({
      submissionPk: submission.pk,
      status: submissionMeta.status,
      statusDisplay: toStatusText(submissionMeta.status),
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
