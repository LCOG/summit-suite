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
          By clicking "Submit" below, I certify that all the expenses listed above are true and correct and were incurred on official LCOG business.
        </div>
        <div class="q-gutter-sm">
          <q-btn
            label="Submit"
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
import { computed, ref } from 'vue'
import { Notify } from 'quasar'
import { useRouter } from 'vue-router'

import { useSubmissionsStore } from 'src/stores/submissions'

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

const rows = ref<MileageRow[]>([{ ...emptyRow }])
const router = useRouter()
const submissionsStore = useSubmissionsStore()
const reimbursementRate = 0.585
const certificationStatement = 'By clicking "Submit" below, I certify that all the expenses listed above are true and correct and were incurred on official LCOG business.'
const submitting = ref(false)

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
  submissionsStore.createMileageSubmission({
    certification_statement: certificationStatement,
    reimbursement_rate: reimbursementRate.toFixed(3),
    rows: rows.value.map((row, index) => ({
      row_order: index,
      date: row.date,
      purpose: row.purpose.trim(),
      contract_fund: row.subfund.trim(),
      odometer_start: Number(row.start),
      odometer_finish: Number(row.finish)
    }))
  })
    .then(() => {
      Notify.create('Mileage reimbursement submitted')
      formReset()
      router.push({ name: 'mileage-reimbursement-list' })
        .catch(e => {
          console.error('Error navigating to mileage reimbursement list:', e)
        })
    })
    .catch(e => {
      console.error('Error creating mileage reimbursement submission:', e)
      Notify.create('Unable to submit mileage reimbursement')
    })
    .finally(() => {
      submitting.value = false
    })
}

function formReset(): void {
  rows.value = [{ ...emptyRow }]
}
</script>
