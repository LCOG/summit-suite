<template>
  <div>
    <div>
      <q-date v-model="dates" range @update:model-value="dateChanged()"/>
      <div class="row items-center q-mt-md q-gutter-md">
        <q-checkbox v-model="showTimes" label="Partial Day" class="q-mt-none" />
        <q-input v-if="showTimes" filled v-model="startTime" mask="time" :rules="['time']">
          <template #append>
            <q-icon name="access_time" class="cursor-pointer">
              <q-popup-proxy
                cover
                transition-show="scale"
                transition-hide="scale"
              >
                <q-time v-model="startTime">
                  <div class="row items-center justify-end">
                    <q-btn v-close-popup label="Close" color="primary" flat />
                  </div>
                </q-time>
              </q-popup-proxy>
            </q-icon>
          </template>
        </q-input>
        <q-input v-if="showTimes" filled v-model="endTime" mask="time" :rules="['time']">
          <template #append>
            <q-icon name="access_time" class="cursor-pointer">
              <q-popup-proxy
                cover
                transition-show="scale"
                transition-hide="scale"
              >
                <q-time v-model="endTime">
                  <div class="row items-center justify-end">
                    <q-btn v-close-popup label="Close" color="primary" flat />
                  </div>
                </q-time>
              </q-popup-proxy>
            </q-icon>
          </template>
        </q-input>
      </div>
      <div v-if="conflictingResponsibilities().length != 0">
        <q-icon color="orange" name="warning" size="xl" class="q-ml-sm" />
        <div>
          <div>
            One or more team members with shared responsibilities will also be
            unavailable:
          </div>
          <ul>
            <li v-for="tor of conflictingResponsibilities()" :key="tor.pk">
              <router-link
                :to="{ name: 'employee-responsibilities',
                params: { pk: tor.pk } }"
              >
                {{ tor.name }}
              </router-link>
              :
              <span v-for="(name, idx) of tor.responsibility_names" :key="idx">
                <span v-if="idx==0">{{ name }}</span>
                <span v-else>, {{ name }}</span>
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <q-input
      v-model="note"
      label="Public Note (visible to team members)"
      class="q-pb-md"
    />
    <q-input
      v-model="privateNote"
      label="Private Note (visible to manager only)"
      class="q-pb-md"
    />
    <q-btn
      color="white"
      text-color="black"
      label="Update"
      :disabled="!formIsFilled()"
      @click="updateTimeOffRequest()"
    />
  </div>
</template>

<script setup lang="ts">

import { onMounted, ref, Ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getRoutePk } from 'src/utils'
import {
  EmployeeConflictingResponsibilities, TimeOffRequestDates,
  TimeOffRequestUpdate
} from 'src/types'
import { useTimeOffStore } from 'src/stores/timeoff'

const route = useRoute()
const router = useRouter()
const timeOffStore = useTimeOffStore()

const pk = getRoutePk(route)
let dates: Ref<TimeOffRequestDates> = ref({'from': '', 'to': ''})
let showTimes = ref(false)
let startTime = ref('08:00')
let endTime = ref('17:00')
let note = ref('')
let privateNote = ref('')

function formIsFilled(): boolean {
  if (!!dates.value) {
    return true
  } else {
    return false
  }
}

// TODO: Do a valuesAreChanged thing like with ReviewNoteDetail so we aren't
// always resetting acknowledgements unnecessarily

function conflictingResponsibilities():
  Array<EmployeeConflictingResponsibilities>
{
  return timeOffStore.conflictingResponsibilities
}

function dateChanged(): void {
  // Check if there are any coworkers out with shared responsibilities
  if (dates.value) {
    timeOffStore.getConflictingResponsibilites({ dates: dates.value })
      .catch(e => {
        console.error('Error getting conflicting responsibilities:', e)
      })
  }
}

function retrieveRequest(): void {
  if (!pk) {
    console.error('No pk provided to retrieve time off request')
    return
  }
  timeOffStore.getCurrentTimeOffRequest(pk)
    .then(() => {
      const tor = timeOffStore.currentTimeOffRequest
      const startDate: string = tor.start_date.toString().split('-').join('/')
      const endDate: string = tor.end_date.toString().split('-').join('/')
      if (startDate == endDate) {
        dates.value = startDate
      } else {
        dates.value = {'from': startDate, 'to': endDate}
      }
      showTimes.value = !!(tor.start_time || tor.end_time)
      startTime.value = tor.start_time ?? '08:00'
      endTime.value = tor.end_time ?? '17:00'
      note.value = tor.note
      privateNote.value = tor.private_note
      dateChanged()
    })
    .catch(e => {
      console.error('Error getting time off request:', e)
    })
}

function updateTimeOffRequest(): void {
  if (!pk) {
    console.error('No pk provided to update time off request')
    return
  }
  let request: TimeOffRequestUpdate = {
    pk: pk, dates: dates.value, note: note.value, privateNote: privateNote.value
  }
  if (showTimes.value) {
    request.startTime = startTime.value
    request.endTime = endTime.value
  } else {
    request.startTime = undefined
    request.endTime = undefined
  }
  timeOffStore.updateTimeOffRequest(request)
    .then(() => {
      router.push({ name: 'timeoff-my-requests'})
        .catch(e => {
          console.error(
            'Error navigating to My Requests page after creating TOR:',
            e
          )
        })
    })
    .catch(e => {
      console.error('Error updating time off request:', e)
    })
}

onMounted(() => {
  retrieveRequest()
})

</script>
