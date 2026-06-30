<template>
  <q-page class="q-pa-md" v-if="workflowInstanceLoaded()">
    <div class="row items-center justify-between q-mb-sm">
      <div class="row items-center">
        <div class="text-h4 q-mr-md">{{ wfi().workflow.name }}</div>
        <div class="q-mr-md">
          <div v-if="wfi().cancelled_by_name">
            <span class="text-bold">Cancelled by:</span>
              {{ wfi().cancelled_by_name }}
            <br />
            <span class="text-bold">Reason:</span>
              {{ wfi().cancellation_reason }}
          </div>
          <q-linear-progress
            v-else
            style="width: 100px;"
            rounded size="25px"
            :value="wfi().percent_complete/100"
            color="primary"
          >
            <div class="absolute-full flex flex-center">
              <q-badge
                color="white"
                text-color="primary"
                :label="`${wfi().percent_complete}%`"
              />
            </div>
          </q-linear-progress>
        </div>
      </div>
      <div>
        <q-btn
          v-if="canCompleteWorkflowInstance(wfi())"
          :label="!wfi().complete ? 'Complete': 'Reopen'"
          @click="showCompleteDialog(wfi())"
          :icon="!wfi().complete ? 'check': 'replay'"
        ></q-btn>
        <q-btn
          v-if="canCancelWorkflowInstance(wfi())"
          :label="wfi().active ? 'Cancel': 'Reinstate'"
          @click="showCancelDialog(wfi())"
          :icon="wfi().active ? 'cancel': 'replay'"
        ></q-btn>
      </div>
    </div>
    <q-btn-group push v-if="hasEmployeeTransition()">
      <q-btn
        push
        :color="isSelected('workflow-processes')"
        glossy
        label="Processes"
        :to="{name: 'workflow-processes', params: {pk: wfi().pk}}"
      >
        <q-badge
          v-if="wfi().pis_action_required" color="orange" rounded floating
        />
      </q-btn>
      <q-btn
        push
        :color="isSelected('workflow-transition-form')"
        glossy
        label="Employee Transition Form"
        :to="{name: 'workflow-transition-form', params: {pk: wfi().pk}}"
      >
        <q-badge
          v-if="wfi().transition_action_required"
          color="orange"
          rounded
          floating
        />
      </q-btn>
    </q-btn-group>

    <q-dialog v-model="completeDialogVisible">
      <q-card>
        <q-card-section>
          <div class="row items-center">
            <q-avatar
              icon="insert_chart_outlined"
              color="primary"
              text-color="white"
            />
            <span class="q-ml-sm">
              Are you sure you want to
              <span v-if="!wfi().complete">complete</span>
              <span v-else>reopen</span> this workflow?
            </span>
          </div>
          <div class="row justify-center text-center">
            Position: {{ completeDialogPositionName }}
          </div>
          <div class="row justify-center text-center">
            {{ completeDialogPercentComplete }}% Complete
          </div>
        </q-card-section>

        <q-card-actions class="row justify-around">
          <q-btn flat label="Cancel" color="primary" v-close-popup />
          <q-btn
            v-if="!wfi().complete"
            flat
            label="Yes, complete it"
            color="primary"
            @click="completeWFI()"
            v-close-popup
          />
          <q-btn
            v-else
            flat
            label="Yes, reopen it"
            color="primary"
            @click="reopenWFI()"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="cancelDialogVisible">
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar
            icon="insert_chart_outlined"
            color="primary"
            text-color="white"
          />
          <div class="q-ml-sm">
            <span>
              Are you sure you want to
              <span v-if="wfi().active" class="text-bold">cancel</span>
              <span v-else>reinstate</span> this workflow?
            </span>
            <div>Other stakeholders will be notified.</div>
          </div>
        </q-card-section>

        <q-card-section>
          <q-input
            v-if="wfi().active"
            filled
            type="textarea"
            label="Reason for cancellation"
            v-model="cancelDialogReason"
          />
        </q-card-section>

        <q-card-actions class="row justify-around">
          <q-btn flat label="Cancel" color="primary" v-close-popup />
          <q-btn
            v-if="wfi().active"
            :disable="!cancelDialogReason"
            flat
            label="Yes, cancel it"
            color="primary"
            @click="cancelWFI()"
            v-close-popup
          >
            <q-tooltip v-if="!cancelDialogReason" class="bg-accent">
              Please provide a reason
            </q-tooltip>
          </q-btn>
          <q-btn
            v-else
            flat
            label="Yes, reinstate it"
            color="primary"
            @click="reinstateWFI()"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <router-view :key="$route.path" />
  </q-page>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar'
import { useRoute, useRouter } from 'vue-router'
import { onMounted, ref, watch } from 'vue'

import useEventBus from 'src/eventBus'
import { handlePromiseError } from 'src/stores'
import { useUserStore } from 'src/stores/user'
import { useWorkflowsStore } from 'src/stores/workflows'
import { WorkflowInstance } from 'src/types'
import { getCurrentUser, getRoutePk } from 'src/utils'

const quasar = useQuasar()
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const workflowsStore = useWorkflowsStore()
const bus = useEventBus()

let completeDialogVisible = ref(false)
let completeDialogPositionName = ref('Not Set')
let completeDialogPercentComplete = ref(0)
let cancelDialogVisible = ref(false)
let cancelDialogReason = ref('')

function workflowInstanceLoaded() {
  return workflowsStore.currentWorkflowInstance.pk != null
}

function wfi(): WorkflowInstance {
  return workflowsStore.currentWorkflowInstance
}

function hasEmployeeTransition() {
  if (!wfi().transition) {
    return false
  } else {
    return true
  }
}

function isSelected(currentRouteName: string) {
  if (route.name == currentRouteName) {
    return 'primary'
  } else {
    return 'grey'
  }
}

function retrieveWorkflowInstance() {
  return new Promise((resolve, reject) => {
    const pk = getRoutePk(route)
    if (!pk) {
      handlePromiseError(reject, 'No pk found in route params')
      return
    }
    workflowsStore.getCurrentWorkflowInstance(pk)
    .then(() => {
      const wfInstance: WorkflowInstance =
        workflowsStore.currentWorkflowInstance
      if (!wfInstance) {
        console.log('Workflow instance does not seem to exist. Redirecting...')
        router.push('/')
          .catch(e => {
            console.error(
              'Error navigating to dashboard upon not finding a matching ' +
              'Workflow Instance:',
              e
            )
            reject(e)
          })
        return
      }
      // Trigger ProcessInstanceDetail to get a new current step
      bus.emit('updateProcessInstances', Math.random())
      resolve('Got Workflow Instance')
    })
    .catch(e => {
      console.error('Error retrieving workflow instance:', e)
      reject(e)
    })
  })
}

function userHasWorkflowRoles() {
  return userStore.getEmployeeProfile.workflow_roles.length > 0
}

function canCompleteWorkflowInstance(
  workflowInstance: WorkflowInstance
): boolean {
  if (!workflowInstance.active) {
    return false
  }
  if (
    hasEmployeeTransition() &&
    workflowInstance.transition.assignee !== 'Complete'
  ) {
    // If there is an incomplete employee transition, disallow complete/reopen
    return false
  }
  if (userStore.getEmployeeProfile.is_all_workflows_admin) {
    // If they are an All-Workflows-Admin, allow complete/reopen
    return true
  } else {
    // TODO: What should happen if no role assigned? Only admins? Everyone?
    // Require all steps to have roles?
    return false
  }
}

function canCancelWorkflowInstance(
  workflowInstance: WorkflowInstance
): boolean {
  if (workflowInstance.complete) {
    // Cannot cancel a completed workflow instance
    return false
  }
  if (userStore.getEmployeeProfile.is_all_workflows_admin) {
    // If they are an All-Workflows-Admin, allow cancel/reopen
    return true
  } else {
    // TODO: What should happen if no role assigned? Only admins? Everyone?
    // Require all steps to have roles?
    return false
  }
}

function showCompleteDialog(wfi: WorkflowInstance): void {
  completeDialogPositionName.value = wfi.title_name
  completeDialogPercentComplete.value = wfi.percent_complete
  completeDialogVisible.value = true
}

function showCancelDialog(wfi: WorkflowInstance): void {
  cancelDialogVisible.value = true
}

function completeWFI(): void {
  const pk = getRoutePk(route)
  if (!pk) {
    return
  }
  workflowsStore.completeWorkflowInstance(pk)
    .then(() => {
      quasar.notify('Completed workflow.')
      retrieveWorkflowInstance()
    })
    .catch(e => {
      console.error('Error completing workflow', e)
    })
}

function reopenWFI(): void {
  const pk = getRoutePk(route)
  if (!pk) {
    return
  }
  workflowsStore.reopenWorkflowInstance(pk)
    .then(() => {
      quasar.notify('Reopened workflow.')
      retrieveWorkflowInstance()
    })
    .catch(e => {
      console.error('Error reopening workflow', e)
    })
}

function cancelWFI(): void {
  const pk = getRoutePk(route)
  if (!pk) {
    return
  }
  workflowsStore.cancelWorkflowInstance(pk, cancelDialogReason.value)
    .then(() => {
      quasar.notify('Cancelled workflow.')
      retrieveWorkflowInstance()
    })
    .catch(e => {
      console.error('Error cancelling workflow', e)
    })
}

function reinstateWFI(): void {
  const pk = getRoutePk(route)
  if (!pk) {
    return
  }
  workflowsStore.reinstateWorkflowInstance(pk)
    .then(() => {
      quasar.notify('Reinstated workflow.')
      retrieveWorkflowInstance()
    })
    .catch(e => {
      console.error('Error reinstating workflow', e)
    })
}

onMounted(() => {
  getCurrentUser()
    .then(() => {
      if (!userHasWorkflowRoles()) {
        router.push({ name: 'dashboard' })
      } else {
        retrieveWorkflowInstance()
          .then(() => bus.emit('workflowInstanceRetrieved', Math.random()))
          .catch(() => {
            router.push('/')
              .catch(e => {
                console.error(
                  'Error navigating to dashboard upon not finding a matching ' +
                  'Workflow Instance:',
                  e
                )
              })
          })
      }
    })
    .catch(e => {
      // User not authenticated or an error occurred fetching the user
      console.error(e)
      router.push({ name: 'dashboard' })
    })
})

// We trigger updating the current step instance in WorkflowInstanceDetail when
// we complete a step and reload it.
watch(() => bus.bus.value.get('completedStep'), () => {
  retrieveWorkflowInstance()
    .then(() => bus.emit('workflowInstanceRetrieved', Math.random()))
    .catch(e => {
      console.error('Error retrieving workflow instance:', e)
    })
})

watch(() => bus.bus.value.get('transitionReassigned'), () => {
  // When transition form is assigned, get the workflowinstance again so the
  // form updates. In the case of sending to STN and completing the form,
  // process instances are also created, so we get those as well.
  retrieveWorkflowInstance()
    .then(() => bus.emit('workflowInstanceRetrieved', Math.random()))
    .catch(e => {
      console.error('Error retrieving workflow instance:', e)
    })
})

</script>
