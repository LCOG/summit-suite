<!-- Not converted from Quasar 1/Vue 2 -->
<template>
<q-inner-loading :showing="loading">
  <q-spinner color="primary" size="2em" />
</q-inner-loading>
<q-table
  :rows="rows"
  row-key="submissionPk"
  :columns="[
    { name: 'submissionType', label: 'Type', field: 'submissionType', align: 'left' },
    { name: 'submitterName', label: 'Submitter', field: 'submitterName', align: 'left' },
    { name: 'status', label: 'Status', field: 'status', align: 'left' },
    { name: 'createdAt', label: 'Submitted', field: 'createdAt', align: 'left' }
  ]"
  :pagination="{ rowsPerPage: 50 }"
>
  <template v-slot:body="props">
    <q-tr :props="props" @click="navigateToDetail(props.row.submissionPk)" class="submission-row">
      <q-td v-for="col in props.cols" :key="col.name" :props="props">
        <span v-if="col.name === 'status'" v-html="props.row.statusDisplay.outerHTML"></span>
        <span v-else-if="col.name === 'submissionType'">{{ props.row.submissionType }}</span>
        <span v-else-if="col.name === 'submitterName'">{{ props.row.submitterName }}</span>
        <span v-else-if="col.name === 'createdAt'">{{ readableDateTimeNEW(props.row.createdAt) }}</span>
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
import { useSubmitStore } from 'src/stores/submit'
import { SubmissionRetrieve } from 'src/types'
import { getCurrentUser } from 'src/utils'

interface SubmissionListRow {
  submissionPk: number
  submissionType: string
  status: 'submitted' | 'approved'
  statusDisplay: HTMLElement
  submitterName: string
  createdAt: string
}

const submissionsStore = useSubmitStore()
const rows = ref<SubmissionListRow[]>([])
const loading = ref(false)
const currentUserPk = ref<number>(-1)

function toStatusDisplay(submission: SubmissionRetrieve): HTMLElement {
  const el = document.createElement('div')
  if (submission.status === 'approved') {
    el.textContent = 'Approved'
  } else {
    el.textContent = 'Submitted'
    const link = document.createElement('a')
    link.textContent = '(Approve)'
    link.href = '/submit/mileage/approve'
    link.style.marginLeft = '4px'
    el.appendChild(link)
  }
  return el
}

function mapRows(data: Array<SubmissionRetrieve>): Array<SubmissionListRow> {
  const mappedRows: Array<SubmissionListRow> = []
  data.forEach((submission) => {
    mappedRows.push({
      submissionPk: submission.pk,
      submissionType: submission.type,
      status: submission.status,
      statusDisplay: toStatusDisplay(submission),
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

function navigateToDetail(submissionPk: number): void {
  window.location.href = `/submit/mileage/${submissionPk}`
}

onMounted(() => {
  getCurrentUser().then((employee) => {
    currentUserPk.value = employee.pk
    loadSubmissions(currentUserPk.value)
  })
})
</script>
