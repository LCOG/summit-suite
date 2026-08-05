<template>
  <div class="row items-center q-mb-md">
    <div class="text-h5">Complete</div>
  </div>
  <WorkflowTable
    :archived="false"
    :complete="true"
    type="all"
    :allowAddDelete="false"
  />
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import WorkflowTable from 'src/components/workflows/WorkflowTable.vue'
import { useWorkflowsStore } from 'src/stores/workflows'
import { getCurrentUser } from 'src/utils'

const router = useRouter()
const workflowsStore = useWorkflowsStore()

let workflowsLoaded = ref(false)

function retrieveWorkflows(): void {
  workflowsStore.getWorkflows({archived: false, complete: false})
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
