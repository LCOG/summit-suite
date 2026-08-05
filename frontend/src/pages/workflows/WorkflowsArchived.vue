<template>
  <div class="row q-mb-md">
    <q-btn-group push>
      <q-btn push color="primary" glossy label="Active" :to="{ name: 'workflow-dashboard' }" />
      <q-btn push color="primary" glossy label="Complete" :to="{ name: 'workflows-complete' }" />
      <q-btn push color="secondary" glossy label="Deleted" :to="{ name: 'workflows-archived' }"  />
    </q-btn-group>
  </div>
  <div class="row items-center justify-between">
    <div class="text-h5">Deleted</div>
    <div>Only the 100 most recently created workflows are shown.</div>
  </div>
  <WorkflowTable
    :archived="true"
    :complete="false"
    type="all"
    :allowAddDelete="false"
    :workflowsLoaded="workflowsLoaded"
    v-on:retrieve="retrieveWorkflows"
  />
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

function retrieveWorkflows(): void {
  workflowsStore.getWorkflows({archived: true, complete: false})
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
      retrieveWorkflows()
    })
    .catch(e => {
      // User not authenticated or an error occurred fetching the user
      console.error(e)
      router.push({ name: 'dashboard' })
    })
})

</script>
