<template>
  <div>
    <q-table
      :dense="$q.screen.lt.sm"
      :rows="myTimeOffRequests()"
      :columns="columns"
      :pagination="tablePagination"
      row-key="pk"
    >
      <template v-slot:header-cell-acknowledged="props">
        <q-th :props="props">
          <div v-if="$q.screen.gt.xs">{{ props.col.label }}</div>
          <div v-if="$q.screen.lt.sm"><q-icon name="thumb_up" size="1.5em" /></div>
        </q-th>
      </template>
      <template v-slot:body-cell-dates="props">
        <q-td key="dates" :props="props" :data-past="props.row.past">
          <div>{{ displayRequestDate(props.row) }}</div>
        </q-td>
      </template>
      <template v-slot:body-cell-notes="props">
        <q-td key="notes" :props="props">
          <span v-if="props.row.note && !props.row.private_note">{{ props.row.note }}</span>
          <span v-if="!props.row.note && props.row.private_note"><span class="text-bold">Private:</span> {{ props.row.private_note }}</span>
          <span v-if="props.row.note && props.row.private_note"><span class="text-bold">Public:</span> {{ props.row.note }} / <span class="text-bold">Private:</span> {{ props.row.private_note }}</span>
        </q-td>
      </template>
      <template v-slot:body-cell-acknowledged="props">
        <q-td :props="props">
          <div v-if="props.row.conflicts.length != 0">
            <q-icon color="orange" name="warning" size="md">
              <q-tooltip content-style="font-size: 16px">
                <div v-if="props.row.acknowledged==null" class="q-mb-sm row items-center">
                  <q-icon v-if="props.row.acknowledged==null" color="orange" name="help" size="lg" class="q-mr-sm" />
                  <div>Your manager has not responded to this request.</div>
                </div>
                <div v-if="props.row.acknowledged==false" class="q-mb-sm row items-center">
                  <q-icon v-if="props.row.acknowledged==false" color="red" name="cancel" size="lg" class="q-mr-sm" />
                  <div>Your manager has indicated an issue with this request.</div>
                </div>
                <div v-if="props.row.acknowledged && props.row.acknowledged==true" class="q-mb-sm row items-center">
                  <q-icon v-if="props.row.acknowledged && props.row.acknowledged==true" color="green" name="check_circle" size="lg" class="q-mr-sm" />
                  <div>Your manager has acknowledged this request.</div>
                </div>
                <div>One or more team members with shared responsibilities will also be unavailable:</div>
                <ul>
                  <li v-for="employee of props.row.conflicts" :key="employee.pk">
                    {{ employee.name }}: <span v-for="(name, idx) of employee.responsibility_names" :key="idx"><span v-if="idx==0">{{ name }}</span><span v-else>, {{ name }}</span></span>
                  </li>
                </ul>
              </q-tooltip>
            </q-icon>
          </div>
          <div v-else>
            <q-icon v-if="props.row.acknowledged==null" color="orange" name="help" size="lg">
              <q-tooltip content-style="font-size: 16px">
                Your manager has not responded to this request.
              </q-tooltip>
            </q-icon>
            <q-icon v-if="props.row.acknowledged==false" color="red" name="cancel" size="lg">
              <q-tooltip content-style="font-size: 16px">
                Your manager has indicated an issue with this request.
              </q-tooltip>
            </q-icon>
            <q-icon v-if="props.row.acknowledged && props.row.acknowledged==true" color="green" name="check_circle" size="lg">
              <q-tooltip content-style="font-size: 16px">
                Your manager has acknowledged this request.
              </q-tooltip>
            </q-icon>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn dense round flat color="grey" class="edit-request" @click="editRequest(props)" icon="edit"></q-btn>
          <q-btn dense round flat color="grey" class="delete-request" @click="showDeleteDialog(props)" icon="delete"></q-btn>
        </q-td>
      </template>
      <template v-slot:bottom-row>
        <q-tr @click="clickMakeRequest()" class="cursor-pointer">
          <q-td colspan="100%">
            <q-icon name="add" size="md" class="q-pr-sm"/>Request Time Off
          </q-td>
        </q-tr>
      </template>
    </q-table>

    <q-dialog v-model="deleteDialogVisible">
      <q-card>
        <q-card-section>
          <div class="row items-center">
            <q-avatar icon="insert_chart_outlined" color="primary" text-color="white" />
            <span class="q-ml-sm">Are you sure you want to delete this request?</span>
          </div>
          <div class="row justify-center text-center">{{ deleteDialogDatesText }}</div>
          <div class="row justify-center text-center">{{ deleteDialogNoteText }}</div>
        </q-card-section>

        <q-card-actions class="row justify-around">
          <q-btn flat label="Cancel" color="primary" v-close-popup />
          <q-btn flat label="Yes, delete it" color="primary" @click="deleteRow()" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<style lang="scss">

.q-table {
  .table-note {
    white-space: normal;
  }
}

tr:has(> td[data-past="true"]) {
  background-color: lightgray;
}

</style>

<script setup lang="ts">

import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { QTableProps, useQuasar } from 'quasar'

import { readableDateNEW, readableDateTimeNEW, readableTime } from 'src/filters'
import { useTimeOffStore } from 'src/stores/timeoff'
import { TimeOffRequestRetrieve } from 'src/types'

const quasar = useQuasar()
const router = useRouter()
const timeOffStore = useTimeOffStore()

interface QuasarTimeOffRequestTableRowClickActionProps {
  row: TimeOffRequestRetrieve
}

const columns: QTableProps['columns'] = [
  { name: 'dates', label: 'Dates', field: 'start_date', sortable: true, align: 'center' },
  { name: 'notes', label: 'Note', field: 'notes', align: 'center', classes: 'table-note' },
  { name: 'acknowledged', label: 'Acknowledged', field: 'approved', align: 'center' },
  { name: 'actions', label: 'Actions', field: null }
]

const tablePagination = {
  sortBy: 'dates',
  descending: true,
  rowsPerPage: 10
}

let deleteDialogVisible = ref(false)
let deleteDialogDatesText = ref('')
let deleteDialogNoteText = ref('')
let rowPkToDelete = ref('')

function displayDateTime(date: string, time: string | undefined): string {
  if (time) {
    return readableDateTimeNEW(`${date} ${time}`)
  }
  return readableDateNEW(date)
}

function displayRequestDate(row: TimeOffRequestRetrieve): string {
  if (row.start_date === row.end_date) {
    if (!!row.start_time && !!row.end_time) {
      return `${readableDateNEW(row.start_date.toString())}
        ${readableTime(row.start_time)} - ${readableTime(row.end_time)}`
    } else {
      return readableDateNEW(row.start_date.toString())
    }
  } else {
    return `${displayDateTime(row.start_date.toString(), row.start_time)} -
      ${displayDateTime(row.end_date.toString(), row.end_time)}`
  }
}

function myTimeOffRequests() {
  return timeOffStore.myTimeOffRequests
}

function retrieveMyTimeOffRequests(): void {
  timeOffStore.getMyTimeOffRequests()
    .catch(e => {
      console.error('Error retrieving my upcoming time off requests', e)
    })
}

function editRequest(props: QuasarTimeOffRequestTableRowClickActionProps): void {
  const rowPk = props.row.pk.toString()
  router.push({ name: 'timeoff-request-detail', params: { pk: rowPk }})
    .catch(e => {
      console.error('Error navigating to time off request detail:', e)
    })
}

function showDeleteDialog(props: QuasarTimeOffRequestTableRowClickActionProps): void {
  rowPkToDelete.value = props.row.pk.toString()
  deleteDialogDatesText.value = `${props.row.start_date.toString()} - ${props.row.end_date.toString()}`
  deleteDialogNoteText.value = props.row.note
  deleteDialogVisible.value = true
}

function deleteRow(): void {
  timeOffStore.deleteTimeOffRequest(rowPkToDelete.value)
    .then(() => {
      quasar.notify('Deleted a time off request.')
      retrieveMyTimeOffRequests()
    })
    .catch(e => {
      console.error('Error deleting time off request', e)
    })
}

function clickMakeRequest(): void {
  router.push({'name': 'timeoff-new-request'})
    .catch(e => {
      console.error('Error navigating to new request page', e)
    })
}

onMounted(() => {
  retrieveMyTimeOffRequests()
})

</script>
