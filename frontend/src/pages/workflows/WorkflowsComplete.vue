<template>
  <div class="row q-mb-md">
    <q-btn-group push>
      <q-btn push color="primary" glossy label="Active" :to="{ name: 'workflow-dashboard' }" />
      <q-btn push color="secondary" glossy label="Complete" :to="{ name: 'workflows-complete' }" />
      <q-btn push color="primary" glossy label="Deleted" :to="{ name: 'workflows-archived' }"  />
    </q-btn-group>
  </div>
  <div class="row items-center justify-between">
    <div class="text-h5">Complete</div>
    <div>Only the 100 most recently completed workflows are shown.</div>
  </div>
  <WorkflowTable
    :archived="false"
    :complete="true"
    type="all"
    :allowAddDelete="false"
    :workflowsLoaded="workflowsLoaded"
    v-on:retrieve="retrieveWorkflows"
  />
  <!-- TODO: For now we just have one complete page/table -->
  <!-- <router-view /> -->
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import WorkflowTable from 'src/components/workflows/WorkflowTable.vue'
import { useUserStore } from 'src/stores/user'
import { useWorkflowsStore } from 'src/stores/workflows'
import { getCurrentUser } from 'src/utils'

const router = useRouter()
const workflowsStore = useWorkflowsStore()

let workflowsLoaded = ref(false)

function retrieveWorkflows(): void {
  workflowsStore.getWorkflows({archived: false, complete: true})
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
