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
      <div v-if="touchedCalendar && conflictingResponsibilities().length != 0">
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
      label="Create"
      :disabled="!formIsFilled()"
      @click="createTimeOffRequest()"
    />
  </div>
</template>

<script setup lang="ts">

import { ref, Ref } from 'vue'
import { useRouter } from 'vue-router'

import { useQuasar } from 'quasar'
import {
  EmployeeConflictingResponsibilities, TimeOffRequestCreate, TimeOffRequestDates
} from 'src/types'
import { useTimeOffStore } from 'src/stores/timeoff'

const quasar = useQuasar()
const router = useRouter()
const timeOffStore = useTimeOffStore()

const newRequestMessages = [
  'Good for you! You deserve a break.',
  'Rest does not need to be earned, and we\'re glad you\'re taking it.',
  'Ditch the grind. Relax!',
  'You need rest. You deserve rest.',
  'Your team appreciates you! Come back refreshed.',
]

let touchedCalendar = ref(false)
let dates: Ref<TimeOffRequestDates> = ref({'from': '', 'to': ''})
let showTimes = ref(false)
let startTime = ref('08:00')
let endTime = ref('17:00')
let note = ref('')
let privateNote = ref('')

function formIsFilled(): boolean {
  if (
    dates.value &&
    (typeof dates.value != 'string' && dates.value.from != '') ||
    (typeof dates.value == 'string' && dates.value != '')
  ) {
    return true
  } else {
    return false
  }
}

function conflictingResponsibilities():
  Array<EmployeeConflictingResponsibilities>
{
  return timeOffStore.conflictingResponsibilities
}

function dateChanged(): void {
  // Check if there are any coworkers out with shared responsibilities
  touchedCalendar.value = true
  if (dates.value) {
    timeOffStore.getConflictingResponsibilites({ dates: dates.value })
      .catch(e => {
        console.error('Error getting conflicting responsibilities:', e)
      })
  }
}

function randomChoice(array: Array<string>) {
  return array[Math.floor(Math.random() * array.length)]
}

function createTimeOffRequest(): void {
  if (typeof dates.value != 'string' && dates.value.from == '') {
    return
  }
  let request: TimeOffRequestCreate = {
    dates: dates.value, note: note.value, privateNote: privateNote.value
  }
  if (showTimes.value) {
    request.startTime = startTime.value
    request.endTime = endTime.value
  }
  timeOffStore.createTimeOffRequest(request)
    .then(() => {
      quasar.notify(
        `Time off successfully recorded. ${randomChoice(newRequestMessages)}`
      )
      router.push({ name: 'timeoff-my-requests'})
        .catch(e => {
          console.error(
            'Error navigating to My Requests page after creating time off',
            'request:',
            e
          )
        })
    })
    .catch(e => {
      console.error('Error creating time off request:', e)
    })
}

</script>
