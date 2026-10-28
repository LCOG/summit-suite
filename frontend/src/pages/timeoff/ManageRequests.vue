<template>
  <div>
    <q-table
      :dense="$q.screen.lt.sm"
      :rows="managedTimeOffRequests()"
      :columns="columns"
      :pagination="tablePagination"
      row-key="pk"
    >
      <template v-slot:body-cell-dates="props">
        <q-td key="dates" :props="props">
          <div v-if="$q.screen.gt.xs">
            {{ startDateTime(props.row) }} - {{ endDateTime(props.row) }}
          </div>
          <div v-if="$q.screen.xs">
            <div>{{ startDateTime(props.row) }}</div>
            <div>{{ endDateTime(props.row) }}</div>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-notes="props">
        <q-td key="notes" :props="props">
          <span v-if="props.row.note && !props.row.private_note">
            {{ props.row.note }}
          </span>
          <span v-if="!props.row.note && props.row.private_note">
            <span class="text-bold">Private:</span> {{ props.row.private_note }}
          </span>
          <span v-if="props.row.note && props.row.private_note">
            <span class="text-bold">Public:</span>
            {{ props.row.note }} /
            <span class="text-bold">Private:</span>
            {{ props.row.private_note }}
          </span>
        </q-td>
      </template>
      <template v-slot:body-cell-acknowledge="props">
        <q-td key="acknowledge" :props="props" class="row justify-center items-center">
          <q-btn
            dense round color="red" icon="close"
            :outline="props.row.acknowledged == null ||
              props.row.acknowledged == true"
            :disable="!canAcknowledge || props.row.acknowledged == false"
            class="q-mr-sm"
            @click="acknowledgeRequest(props.row.pk, false)"
          />
          <q-btn
            dense round color="green" icon="check"
            :outline="props.row.acknowledged == null ||
              props.row.acknowledged == false"
            :disable="!canAcknowledge || props.row.acknowledged == true"
            @click="acknowledgeRequest(props.row.pk, true)"
          />
          <div v-if="props.row.conflicts.length != 0" class="q-ml-sm">
            <q-icon color="orange" name="warning" size="md">
              <q-tooltip content-style="font-size: 16px">
                <div>
                  One or more team members with shared responsibilities will
                  also be unavailable:
                </div>
                <ul>
                  <li
                    v-for="employee of props.row.conflicts"
                    :key="employee.pk"
                  >
                    {{ employee.name }}:
                    <span
                      v-for="(name, idx) of employee.responsibility_names"
                      :key="idx"
                    >
                      <span v-if="idx==0">{{ name }}</span>
                      <span v-else>, {{ name }}</span>
                    </span>
                  </li>
                </ul>
              </q-tooltip>
            </q-icon>
          </div>
        </q-td>
      </template>
      <!-- GRID MODE -->
      <template v-slot:item="props">
        <div
          class="q-pa-xs col-xs-12 col-sm-6 col-md-4 col-lg-3
            grid-style-transition"
        >
          <q-card class="q-py-sm">
            <q-list dense>
              <q-item v-for="col in props.cols" :key="col.name">
                <div class="q-table__grid-item-row">
                  <div class="q-table__grid-item-title">{{ col.label }}</div>
                  <div
                    v-if="col.name == 'notes'"
                    class="q-table__grid-item-value"
                  >
                    <span v-if="props.row.note && !props.row.private_note">
                      {{ props.row.note }}
                    </span>
                    <span v-if="!props.row.note && props.row.private_note">
                      <span class="text-bold">Private:</span>
                      {{ props.row.private_note }}
                    </span>
                    <span v-if="props.row.note && props.row.private_note">
                      <span class="text-bold">Public:</span>
                      {{ props.row.note }} /
                      <span class="text-bold">Private:</span>
                      {{ props.row.private_note }}
                    </span>
                  </div>
                  <div
                    v-else-if="col.name != 'acknowledge'"
                    class="q-table__grid-item-value"
                  >
                    {{ col.value }}
                  </div>
                  <div class="q-table__grid-item-value row q-gutter-sm" v-else>
                    <q-btn
                      dense round color="red" icon="close"
                      :outline="props.row.acknowledged == null ||
                        props.row.acknowledged == true"
                      :disable="!canAcknowledge ||
                        props.row.acknowledged == false"
                      class="q-mr-sm"
                      @click="acknowledgeRequest(props.row.pk, false)"
                    />
                    <q-btn
                      dense round color="green" icon="check"
                      :outline="props.row.acknowledged == null ||
                        props.row.acknowledged == false"
                      :disable="!canAcknowledge ||
                        props.row.acknowledged == true"
                      @click="acknowledgeRequest(props.row.pk, true)"
                    />
                    <div v-if="props.row.conflicts.length != 0" class="q-ml-sm">
                      <q-icon color="orange" name="warning" size="md">
                        <q-tooltip content-style="font-size: 16px">
                          <div>
                            One or more team members with shared
                            responsibilities will also be unavailable:
                          </div>
                          <ul>
                            <li
                              v-for="employee of props.row.conflicts"
                              :key="employee.pk"
                            >
                              {{ employee.name }}:
                              <span
                                v-for="(name, idx) of
                                  employee.responsibility_names"
                                :key="idx"
                              >
                                <span v-if="idx==0">{{ name }}</span>
                                <span v-else>, {{ name }}</span>
                              </span>
                            </li>
                          </ul>
                        </q-tooltip>
                      </q-icon>
                    </div>
                  </div>
                </div>
              </q-item>
            </q-list>
          </q-card>
        </div>
      </template>
    </q-table>
  </div>
</template>

<style lang="scss">
@media only screen and (max-width: 1600px) {
  .q-table td {
    white-space: normal;
  }
}
</style>

<script setup lang="ts">

import { ref } from 'vue'
import { QTableProps } from 'quasar'
import { readableDateNEW, readableDateTimeNEW } from 'src/filters'
import { useTimeOffStore } from 'src/stores/timeoff'
import { TimeOffRequestRetrieve } from 'src/types'

const timeOffStore = useTimeOffStore()

const columns: QTableProps['columns'] = [
  {
    name: 'employee', label: 'Employee', field: 'employee_name', sortable: true,
    align: 'center'
  },
  {
    name: 'dates', label: 'Dates', field: 'start_date', sortable: true,
    align: 'center'
  },
  { name: 'notes', label: 'Notes', field: 'notes', align: 'center' },
  {
    name: 'acknowledge', label: 'Acknowledge?', field: 'acknowledged',
    align: 'center'
  },
]

const tablePagination = {
  sortBy: 'dates',
  descending: true,
  rowsPerPage: 10
}

const canAcknowledge = ref(true)

function displayDateTime(date: string, time: string | undefined): string {
  if (time) {
    // return `${date} ${time}`
    return readableDateTimeNEW(`${date} ${time}`)
  }
  return readableDateNEW(date)
}

function startDateTime(row: TimeOffRequestRetrieve): string {
  return displayDateTime(row.start_date.toString(), row.start_time)
}

function endDateTime(row: TimeOffRequestRetrieve): string {
  return displayDateTime(row.end_date.toString(), row.end_time)
}

function managedTimeOffRequests() {
  return timeOffStore.managedTimeOffRequests
}

function retrieveManagedTimeOffRequests(): void {
  timeOffStore.getManagedTimeOffRequests()
    .catch(e => {
      console.error('Error retrieving my upcoming time off requests', e)
    })
}

function acknowledgeRequest(pk: number, acknowledged: boolean): void {
  canAcknowledge.value = false
  setTimeout(() => {
    canAcknowledge.value = true
  }, 1500)
  timeOffStore.acknowledgeTimeOffRequest({pk, acknowledged})
    .then(() => {
      // TODO: Get just the one we changed, not all of them
      retrieveManagedTimeOffRequests()
    })
    .catch(e => {
      console.error('Error acknowledging time off request', e)
    })
}

</script>
