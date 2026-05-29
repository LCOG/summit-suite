<template>
  <q-page class="q-pa-md">
    <p class="text-h4">Organization</p>
    <p class="text-h5">Your Direct Reports</p>
    <EmployeeTable :pk="employeePk"/>
  </q-page>
</template>

<style scoped lang="scss">
.q-input {
  width: 300px;
}

.success {
    color: green;
}
</style>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { useUserStore } from 'src/stores/user'
import { EmployeeRetrieve } from 'src/types'

import EmployeeTable from 'src/components/EmployeeTable.vue'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

let employeePk = ref(-1)

let displayNameCurrentVal = ref('')
let displayName = ref('')

function retrieveProfile(): Promise<EmployeeRetrieve> {
  return new Promise((resolve, reject) => {
    // We cannot guarantee the user has arrived in vuex state immediately, so request it again here
    userStore.simpleUserRequest()
      .then((employee) => {
        employeePk.value = employee.pk
        displayName.value = employee.name
        displayNameCurrentVal.value = displayName.value
        resolve(employee)
      })
      .catch(e => {
        console.error('Error getting user from API:', e)
        reject(e)
      })
  })
}

onMounted(() => { 
  retrieveProfile()
    .then(() => {
      // Redirect to profile page of user
      router.push({ name: 'profile', params: { pk: employeePk.value } })
        .catch(e => {
          console.error('Error navigating to profile page:', e)
        })
    })
    .catch(e => {
      console.error('Error retrieving Employee profile from API:', e)
    })
})
</script>
