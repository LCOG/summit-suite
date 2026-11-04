<!-- Not converted from Quasar 1/Vue 2 -->
<template>
  <q-card class="q-pa-md">
    <q-form @submit.prevent="formSubmit" @reset.prevent="formReset" class="q-gutter-md">
      <table class="full-width mileage-table">
        <thead>
          <tr>
            <td colspan="3" />
            <td colspan="2" class="text-center text-weight-bold">Odometer</td>
            <td />
          </tr>
          <tr class="text-weight-bold">
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
              <q-input v-model="row.date" filled type="date" />
            </td>
            <td>
              <q-input v-model="row.purpose" outlined />
            </td>
            <td>
              <q-input v-model="row.subfund" outlined />
            </td>
            <td>
              <q-input v-model="row.start" outlined type="number" min="0" />
            </td>
            <td>
              <q-input v-model="row.finish" outlined type="number" min="0" />
            </td>
            <td>
              {{ getRowMiles(row) }}
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="4" />
            <td class="text-right text-weight-bold">Total Miles:</td>
            <td class="text-weight-bold">{{ totalMiles }}</td>
          </tr>
          <tr>
            <td colspan="4" />
            <td class="text-right text-weight-bold">x $0.585</td>
            <td class="text-weight-bold">${{ (totalMiles * 0.585).toFixed(2) }}</td>
          </tr>
        </tfoot>
      </table>

      <div class="row items-center q-gutter-sm">
        <q-btn unelevated rounded color="primary" icon="add" label="Add Row" @click="addRow" />
      </div>

      <div>
        <div class="text-subtitle1 q-mb-sm">
          By clicking "{{ isUpdateMode ? 'Update' : 'Submit' }}" below, I certify that all the expenses listed above are true and correct and were incurred on official {{ organizationName }} business.
        </div>
        <div class="q-gutter-sm">
          <q-btn
            :label="isUpdateMode ? 'Update' : 'Submit'"
            type="submit"
            color="primary"
            :loading="submitting"
            :disable="submitting"
          />
          <q-btn label="Reset" type="reset" color="primary" flat :disable="submitting" />
        </div>
      </div>
    </q-form>
  </q-card>
</template>

<style scoped lang="scss">
.mileage-table {
  border-collapse: collapse;

  thead,
  tfoot,
  tbody {
    td {
      border: 1px solid rgba(0, 0, 0, 0.12);
      padding: 8px 10px;
      vertical-align: top;
    }
  }

  thead td {
    font-weight: 600;
  }
}
</style>

<script setup lang="ts">

import { computed, ref, watch } from 'vue'
import { Notify } from 'quasar'
import { useRoute, useRouter } from 'vue-router'

import { useSubmissionsStore } from 'src/stores/submissions'
import { useUserStore } from 'src/stores/user'
import { MileageSubmissionRetrieve } from 'src/types'

interface MileageRow {
  date: string
  purpose: string
  subfund: string
  start: string
  finish: string
}

const emptyRow: MileageRow = {
  date: '',
  purpose: '',
  subfund: '',
  start: '',
  finish: ''
}

const props = defineProps<{ pk?: number | string | null }>()
const route = useRoute()
const router = useRouter()
const submissionsStore = useSubmissionsStore()
const userStore = useUserStore()

const organizationName = computed(() => userStore.getEmployeeProfile?.organization?.name ?? '')

const rows = ref<MileageRow[]>([{ ...emptyRow }])
const reimbursementRate = 0.585
const submitting = ref(false)

const submissionPk = computed<number | null>(() => {
  const rawPk = props.pk ?? route.params.pk
  if (rawPk === undefined || rawPk === null || rawPk === '') {
    return null
  }

  const parsed = Number(rawPk)
  return Number.isFinite(parsed) ? parsed : null
})

const isUpdateMode = computed(() => submissionPk.value !== null)

function getRowMiles(row: MileageRow): number {
  const start = Number(row.start || 0)
  const finish = Number(row.finish || 0)

  if (start > 0 && finish >= start) {
    return finish - start
  }

  return 0
}

const totalMiles = computed(() => {
  return rows.value.reduce((total, row) => total + getRowMiles(row), 0)
})

function hasAtLeastOneValidRow(): boolean {
  return rows.value.some((row) => {
    const start = Number(row.start)
    const finish = Number(row.finish)
    return (
      !!row.date &&
      !!row.purpose.trim() &&
      !!row.subfund.trim() &&
      Number.isFinite(start) &&
      Number.isFinite(finish) &&
      start >= 0 &&
      finish >= start
    )
  })
}

function allRowsValid(): boolean {
  return rows.value.every((row) => {
    const start = Number(row.start)
    const finish = Number(row.finish)
    return (
      !!row.date &&
      !!row.purpose.trim() &&
      !!row.subfund.trim() &&
      Number.isFinite(start) &&
      Number.isFinite(finish) &&
      start >= 0 &&
      finish >= start
    )
  })
}

function addRow(): void {
  rows.value.push({ ...emptyRow })
}

function rowFromApi(row: any): MileageRow {
  return {
    date: row.date ?? '',
    purpose: row.purpose ?? '',
    subfund: row.contract_fund ?? '',
    start: row.odometer_start !== undefined && row.odometer_start !== null ? String(row.odometer_start) : '',
    finish: row.odometer_finish !== undefined && row.odometer_finish !== null ? String(row.odometer_finish) : ''
  }
}

function formPayload() {
  return {
    reimbursement_rate: reimbursementRate.toFixed(3),
    rows: rows.value.map((row, index) => ({
      row_order: index,
      date: row.date,
      purpose: row.purpose.trim(),
      contract_fund: row.subfund.trim(),
      odometer_start: Number(row.start),
      odometer_finish: Number(row.finish)
    }))
  }
}

async function loadMileageSubmission(pk: number): Promise<void> {
  try {
    const submission = await submissionsStore.getMileageSubmission(pk) as MileageSubmissionRetrieve
    rows.value = submission.rows.map(rowFromApi)
  } catch (e) {
    console.error('Error loading mileage submission:', e)
    Notify.create('Unable to load mileage request')
  }
}

watch(
  submissionPk,
  (pk) => {
    if (pk === null) {
      rows.value = [{ ...emptyRow }]
      return
    }

    void loadMileageSubmission(pk)
  },
  { immediate: true }
)

function formSubmit(): void {
  if (submitting.value) {
    return
  }
  if (!hasAtLeastOneValidRow()) {
    Notify.create('Please enter at least one complete mileage row')
    return
  }
  if (!allRowsValid()) {
    Notify.create('Please complete all rows before submitting')
    return
  }

  submitting.value = true

  const payload = formPayload()

  const request = isUpdateMode.value && submissionPk.value !== null
    ? submissionsStore.updateMileageSubmission(submissionPk.value, payload)
    : submissionsStore.createMileageSubmission(payload)

  request
    .then(() => {
      Notify.create(
        isUpdateMode.value ? 'Mileage reimbursement updated' : 'Mileage reimbursement submitted'
      )
      router.push({ name: 'mileage-list' }).catch((e) => {
        console.error('Error navigating to mileage reimbursement list:', e)
      })
    })
    .catch((e) => {
      console.error('Error saving mileage reimbursement submission:', e)
      Notify.create(
        isUpdateMode.value ? 'Unable to update mileage reimbursement' : 'Unable to submit mileage reimbursement'
      )
    })
    .finally(() => {
      submitting.value = false
    })
}

function formReset(): void {
  if (isUpdateMode.value && submissionPk.value !== null) {
    void loadMileageSubmission(submissionPk.value)
    return
  }

  rows.value = [{ ...emptyRow }]
}
</script>
