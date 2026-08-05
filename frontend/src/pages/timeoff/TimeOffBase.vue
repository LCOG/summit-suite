<template>
  <div>
  <q-page class="q-pa-md">
    <div class="text-h4">Time Off</div>
    <div class="q-my-md">
      <q-btn-group rounded>
        <q-btn :to="{ name: 'timeoff-calendar' }" unelevated rounded color="primary" icon="list" label="Calendar" />
        <q-btn :to="{ name: 'timeoff-my-requests' }" unelevated rounded color="primary" icon="calendar_today" :label="$q.screen.xs ? 'Requests' : 'My Requests'" />
        <q-btn v-if="isManager()" :to="{ name: 'timeoff-manage-requests' }" unelevated rounded color="primary" icon="book" :label="$q.screen.xs ? 'Manage' : 'Manage Requests'">
          <q-badge v-if="numUnacknowledgedManagedTimeOffRequests()" rounded color="red" floating>{{ numUnacknowledgedManagedTimeOffRequests() }}</q-badge>
        </q-btn>
      </q-btn-group>  
    </div>
    <router-view :key="$route.path" />
  </q-page>
</div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTimeOffStore } from 'src/stores/timeoff'
import { useUserStore } from 'src/stores/user'
import { getCurrentUser } from 'src/utils'

const router = useRouter()
const timeOffStore = useTimeOffStore()
const userStore = useUserStore()

function isManager() {
  return userStore.isManager
}

function managedTimeOffRequests() {
  return timeOffStore.managedTimeOffRequests
}

function numUnacknowledgedManagedTimeOffRequests(): number {
  const tors = managedTimeOffRequests()
  if (tors) {
    return tors.filter(tor => tor.acknowledged == null).length
  } else {
    return 0
  }
}

function retrieveManagedTimeOffRequests(): void {
  timeOffStore.getManagedTimeOffRequests()
}

onMounted(() => {
  getCurrentUser()
    .then(() => {
      retrieveManagedTimeOffRequests()
    })

})

</script>
