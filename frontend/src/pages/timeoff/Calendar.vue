<template>
<div>
  <div class="q-gutter-md q-mt-md">
    <q-btn @click="setThisWeek()">Today</q-btn>
    <q-btn-group>
      <q-btn color="secondary" icon="west" @click="weekBackward()"/>
      <q-btn color="secondary" icon="east" @click="weekForward()"/>
    </q-btn-group>
  </div>
  <q-spinner-grid
    v-if="!calendarLoaded()"
    class="spinner q-mt-lg"
    color="primary"
    size="xl"
  />
  <div v-else class="q-mt-lg">
    <div v-for="day of teamTimeOff()" :key="day.formattedDate">
      <div class="text-h5">
        <span>{{day.formattedDate}}</span><span v-if="day.isToday"> (Today)</span>
      </div>
      <ul>
        <div v-for="request of day.requests" :key="request.pk">
          <q-icon
            v-if="request.acknowledged==null"
            color="orange"
            name="help"
            size="sm"
          />
          <q-icon
            v-if="request.acknowledged==false"
            color="red"
            name="cancel"
            size="sm"
          />
          <q-icon
            v-if="request.acknowledged && request.acknowledged==true"
            color="green"
            name="check_circle"
            size="sm"
          />
          <router-link
            :to="{
              name: 'employee-responsibilities',
              params: { pk: request.employee_pk }
            }"
          >
            {{ request.employee_name }}
          </router-link>
          {{ timespan(request, day.date) }}
          <q-icon
            v-if="request.conflicts.length != 0"
            color="orange"
            name="warning"
            size="sm"
            class="q-ml-sm"
          >
            <q-tooltip  content-style="font-size: 16px">
              <div>
                One or more team members with shared responsibilities will also
                be unavailable:
              </div>
              <ul>
                <li v-for="employee of request.conflicts" :key="employee.pk">
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
          <span v-if="request.note" class="text-italic">
            - {{ request.note }}
          </span>
        </div>
      </ul>
    </div>
  </div>
</div>
</template>

<script setup lang="ts">

import { onMounted, ref } from 'vue'
import { TimeOffRequestRetrieve } from 'src/types'
import { useTimeOffStore } from 'src/stores/timeoff'
import { readableTime } from 'src/filters'

type TimeOffCalendarData = Array<{
  date: Date, formattedDate: string, isToday: boolean,
  requests: Array<TimeOffRequestRetrieve>
}>

const timeOffStore = useTimeOffStore()

let thisWeekLoaded = ref(false)
let allDatesLoaded = ref(false)

let today = ref(new Date())
let thisWeekMonday = ref(new Date())
let selectedMonday = ref(new Date())

function viewingThisWeek() {
  return selectedMonday.value.getTime() === thisWeekMonday.value.getTime()
}

function calendarLoaded() {
  return (viewingThisWeek() && thisWeekLoaded.value) || allDatesLoaded.value
}

function timespan(request: TimeOffRequestRetrieve, todayDate: Date): string {
  const startDate = new Date(request.start_date.replace(/-/g, '\/'))
  const endDate = new Date(request.end_date.replace(/-/g, '\/'))
  const startTime = request.start_time
  const endTime = request.end_time
  if (!startTime || !endTime) {
    return ''
  }
  const startDay = startDate.setHours(0,0,0,0)
  const endDay = endDate.setHours(0,0,0,0)
  const todayDay = todayDate.setHours(0,0,0,0)

  if (startDay === endDay) {
    return '(Out from ' + readableTime(startTime) + ' - ' + readableTime(endTime) + ')'
  }
  if (startDay < todayDay && todayDay < endDay) {
    return ''
  }
  if (startDay === todayDay) {
    return '(Out starting at ' + readableTime(startTime) + ')'
  }
  if (endDay === todayDay) {
    return '(Out until ' + readableTime(endTime) + ')'
  }
  return ''
}

function teamTimeOff(): TimeOffCalendarData {
  const apiResults = timeOffStore.teamTimeOffRequests
  let sortedTimeOff: TimeOffCalendarData = []
  if (apiResults) {
    for (let i=0; i<5; i++) {
      let d = new Date(selectedMonday.value.getTime() + i*(1000 * 60 * 60 * 24))
      let isToday = d.setHours(0,0,0,0) === today.value.setHours(0,0,0,0)
      sortedTimeOff.push({
        date: d,
        formattedDate: d.toLocaleDateString(
          'en-us', { weekday: 'long', month: 'long', day: 'numeric' }
        ),
        isToday: isToday,
        requests: apiResults.filter(request => {
          const targetDateMS = d.setHours(0,0,0,0)
          const fromDate = new Date(request.start_date)
          const fromTZOffset = fromDate.getTimezoneOffset() * 60000
          const fromDateMS = new Date(fromDate.getTime() + fromTZOffset)
            .setHours(0,0,0,0)
          const toDate = new Date(request.end_date)
          const toTZOffset = toDate.getTimezoneOffset() * 60000
          const toDateMS = new Date(toDate.getTime() + toTZOffset)
            .setHours(0,0,0,0)

          if (fromDateMS <= targetDateMS && targetDateMS <= toDateMS) {
            return true
          } else {
            return false
          }
        })
      })
    }
  }
  return sortedTimeOff
}

function retrieveThisWeekTeamTimeOff(): Promise<void> {
  // Get all team time off for this week
  return new Promise((resolve, reject) => {
    timeOffStore.getTeamTimeOffRequests(thisWeekMonday.value)
      .then(() => {
        thisWeekLoaded.value = true
        resolve()
      })
      .catch(e => {
        console.error('Error retrieving team time off', e)
        reject()
      })
  })
}

function retrieveTeamTimeOff(): void {
  // Get all team time off plus and minus 1 year from today
  timeOffStore.getTeamTimeOffRequests()
    .then(() => {
      allDatesLoaded.value = true
    })
    .catch(e => {
      console.error('Error retrieving team time off', e)
    })
}

function setDates() {
  let prevMonday = new Date()
  prevMonday.setDate(prevMonday.getDate() - (prevMonday.getDay() + 6) % 7)
  thisWeekMonday.value = prevMonday
  selectedMonday.value = prevMonday
}

function setThisWeek() {
  selectedMonday.value = thisWeekMonday.value
}

function weekBackward() {
  selectedMonday.value = new Date(
    selectedMonday.value.getTime() - 7 * (1000 * 60 * 60 * 24)
  )
}

function weekForward() {
  selectedMonday.value = new Date(
    selectedMonday.value.getTime() + 7 * (1000 * 60 * 60 * 24)
  )
}

onMounted(() => {
  setDates()
  retrieveThisWeekTeamTimeOff().then(() => {
    retrieveTeamTimeOff()
  })
})

</script>
