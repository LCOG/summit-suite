<!-- Not converted from Quasar 1/Vue 2 -->
<template>
  <q-card class="q-pa-md">
    <q-form @submit.prevent="formSubmit" class="q-gutter-md">
      <table class="full-width mileage-table">
        <thead>
          <tr>
            <td colspan="4" />
            <td colspan="2" class="text-center text-weight-bold">Odometer</td>
            <td />
          </tr>
          <tr class="text-weight-bold">
            <td>
              <q-checkbox :model-value="allChecked" @update:model-value="toggleAll" />
            </td>
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
              <q-checkbox v-model="row.checked" />
            </td>
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
        <q-btn label="Approve all checked" type="submit" color="primary" />
      </div>
    </q-form>
  </q-card>
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
import { computed, ref } from 'vue'
import { Notify } from 'quasar'

interface MileageRequestRow {
  checked: boolean
  date: string
  purpose: string
  subfund: string
  start: string
  finish: string
}

const rows = ref<MileageRequestRow[]>([
  { checked: false, date: '2022/02/22', purpose: 'Portland', subfund: 'Fund A', start: '1005', finish: '1010' },
  { checked: false, date: '2022/02/23', purpose: 'Salem', subfund: 'Fund B', start: '42', finish: '420' },
])

const allChecked = computed(() => rows.value.length > 0 && rows.value.every((row) => row.checked))

function getMileage(row: MileageRequestRow): number {
  const start = Number(row.start || 0)
  const finish = Number(row.finish || 0)
  return finish >= start ? finish - start : 0
}

function toggleAll(checked: boolean): void {
  rows.value.forEach((row) => {
    row.checked = checked
  })
}

function formSubmit(): void {
  const selected = rows.value.filter((row) => row.checked).length
  Notify.create(selected > 0 ? `Approved ${selected} mileage request(s)` : 'No mileage requests selected')
}
</script>
