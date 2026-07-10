<template>
  <div class="row">
    <q-btn-group push>
      <q-btn
        name="workflows-active-button"
        push
        color="secondary"
        glossy
        label="Active"
        :to="{ name: 'workflow-dashboard' }"
      />
      <q-btn
        name="workflows-complete-button"
        push
        color="primary"
        glossy
        label="Complete"
        :to="{ name: 'workflows-complete' }"
      />
      <q-btn
        name="workflows-deleted-button"
        push
        color="primary"
        glossy
        label="Deleted"
        :to="{ name: 'workflows-archived' }"
      />
    </q-btn-group>
  </div>

  <div v-for="type of userWorkflowTypes()" :key="type.id">
    <div class="row items-center q-mb-sm q-mt-md">
      <q-avatar
        :icon="type.icon"
        color="primary"
        text-color="white"
        font-size="22px"
        class="q-mr-sm"
        size="md"
      />
      <div class="text-h5">{{ type.name }}</div>
    </div>
    <WorkflowTable
      :archived="false"
      :complete="false"
      :type="type.type ? type.type : ''"
      :allowAddDelete="true"
      :workflowsLoaded="workflowsLoaded"
      :employeePk="userStore.getEmployeeProfile.employee_pk"
      :sortOptions="workflowsStore.workflowOptionsByType(type.type ? type.type : '')"
      v-on:retrieve="retrieveWorkflows"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import WorkflowTable from 'src/components/workflows/WorkflowTable.vue'
import { useUserStore } from 'src/stores/user'
import { useWorkflowsStore } from 'src/stores/workflows'
import { getCurrentUser } from 'src/utils'

const router = useRouter()
const userStore = useUserStore()
const workflowsStore = useWorkflowsStore()

let workflowsLoaded = ref(false)

function userHasWorkflowRoles() {
  return userStore.getEmployeeProfile.workflow_roles.length > 0
}

function userWorkflowTypes() {
  return userStore.getEmployeeProfile.workflow_display_options.filter(
    (option) => option.display
  )
}

function retrieveWorkflows(): void {
  Promise.all([
    workflowsStore.getWorkflows({archived: false, complete: false}),
    workflowsStore.getWorkflowOptions()
  ])
    .then(() => {
      workflowsLoaded.value = true
    })
    .catch(e => {
      console.error('Error retrieving incomplete workflows:', e)
    })
}

onMounted(() => {
  getCurrentUser()
    .then(() => {
      if (!userHasWorkflowRoles()) {
        router.push({ name: 'dashboard' })
      } else {
        retrieveWorkflows()
      }
    })
    .catch(e => {
      // User not authenticated or an error occurred fetching the user
      console.error(e)
      router.push({ name: 'dashboard' })
    })
})

</script>
