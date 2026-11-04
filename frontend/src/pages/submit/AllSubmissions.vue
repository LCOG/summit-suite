<template>
<div>
  <q-inner-loading :showing="loading">
    <q-spinner color="primary" size="2em" />
  </q-inner-loading>
  <table class="full-width submissions-table">
    <thead>
      <tr class="text-weight-bold">
        <td>Type</td>
        <td>Status</td>
        <td>Last Updated</td>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(row, index) in rows" :key="index">
        <td>{{ row.submissionType }}</td>
        <td v-html="row.statusDisplay.outerHTML"></td>
        <td>{{ readableDateTimeNEW(row.date) }}</td>
      </tr>
    </tbody>
  </table>
</div>
</template>

<style scoped lang="scss">
.submissions-table {
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
  statusDisplay: HTMLElement
  submitterName: string
  date: string
}

const submissionsStore = useSubmissionsStore()
const rows = ref<SubmissionListRow[]>([])
const loading = ref(false)

function toStatusDisplay(submission: SubmissionRetrieve): HTMLElement {
  const el = document.createElement('div')
  if (submission.status === 'approved') {
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

function loadSubmissions(pk: number): void {
  loading.value = true
  submissionsStore.getAllSubsForEmployee(pk)
    .then((result) => {
      rows.value = (result as Array<SubmissionRetrieve>).map((submission) => ({
        submissionPk: submission.pk,
        submissionType: submission.type,
        status: submission.status,
        statusDisplay: toStatusDisplay(submission),
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
