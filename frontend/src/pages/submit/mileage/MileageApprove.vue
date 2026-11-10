<template>
<q-inner-loading :showing="loading">
  <q-spinner color="primary" size="2em" />
</q-inner-loading>
<q-table
  :rows="rows"
  row-key="submissionPk"
  :columns="[
    { name: 'submitterName', label: 'Submitter', field: 'submitterName', align: 'left' },
    { name: 'status', label: 'Status', field: 'status', align: 'left' },
    { name: 'travelDates', label: 'Travel Dates', field: 'travelDates', align: 'left' },
    { name: 'miles', label: 'Total Miles', field: 'miles', align: 'left' }
  ]"
  :pagination="{ rowsPerPage: 50 }"
>
  <template v-slot:body="props">
    <q-tr :props="props" @click="navigateToDetail(props.row.submissionPk)" class="submission-row">
      <q-td v-for="col in props.cols" :key="col.name" :props="props">
        <span v-if="col.name === 'status'">{{ props.row.statusDisplay }}</span>
        <span v-else-if="col.name === 'travelDates'">{{ props.row.travelDates.split(' - ').map(date => readableDateNEW(date)).join(' - ') }}</span>
        <span v-else-if="col.name === 'miles'">{{ props.row.miles }}</span>
        <span v-else-if="col.name === 'submitterName'">{{ props.row.submitterName }}</span>
      </q-td>
    </q-tr>
  </template>
</q-table>
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
import { useRouter } from 'vue-router'
import { Notify } from 'quasar'

import { readableDateNEW } from 'src/filters'
import { useSubmitStore } from 'src/stores/submit'
import { MileageSubmissionRetrieve } from 'src/types'
import { getCurrentUser } from 'src/utils'

interface MileageRequestListRow {
  checked: boolean
  submissionPk: number
  status: 'submitted' | 'approved'
  statusDisplay: string
  submitterName: string
  travelDates: string
  miles: number
}

const router = useRouter()
const submissionsStore = useSubmitStore()
const rows = ref<MileageRequestListRow[]>([])
const loading = ref(false)
const currentUserPk = ref<number>(-1)

function toStatusText(status: 'submitted' | 'approved'): string {
  return status ? status.charAt(0).toUpperCase() + status.slice(1) : ''
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
      statusDisplay: toStatusText(submissionMeta.status),
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

function navigateToDetail(submissionPk: number): void {
  router.push(`/submit/mileage/${submissionPk}`)
}

onMounted(() => {
  getCurrentUser().then((employee) => {
    currentUserPk.value = employee.employee_pk
    loadMileageSubmissions(currentUserPk.value)
  })
})
</script>
