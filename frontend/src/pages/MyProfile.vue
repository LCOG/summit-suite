<template>
  <q-page class="q-pa-md">
    <p class="text-h5">Update Your Profile</p>
    <form>
      <!-- DISPLAY NAME -->
      <p class="row text-h6 q-mt-lg q-mb-none">Display Name</p>
      <div class="row items-center q-gutter-sm">
        <q-input v-model="displayName" />
      </div>
      
      <p class="row text-h6 q-mt-lg q-mb-none">Email Notifications</p>
      <!-- ALL EMAILS -->
      <p class="row q-mb-none text-bold">All</p>
      <div class="row items-center q-gutter-sm">
        <q-toggle
          v-model="emailOptOutAll"
          color="negative"
          checked-icon="clear"
          unchecked-icon="mail"
          :label="
            emailOptOutAll ? 'Opt out of all email notifications' :
            'Receive email notifications'
          "
          class="text-bold"
        />
      </div>
      <hr/>
      <!-- CREDIT CARD EXPENSE EMAILS -->
      <p class="row q-mb-none text-bold">Credit Card Expenses</p>
      <div class="row items-center q-gutter-sm">
        <q-toggle
          v-model="emailOptOutExpensesAll"
          color="negative"
          checked-icon="clear"
          unchecked-icon="mail"
          :label="
            emailOptOutExpensesAll ?
            'Opt out of all expense email notifications' :
            'Receive expense email notifications'
          "
          class="text-bold"
          :disable="emailOptOutAll"
        />
      </div>
      <!-- PHISH EMAILS -->
      <p class="row q-mb-none text-bold">Phishing/Security</p>
      <div class="row items-center q-gutter-sm">
        <q-toggle
          v-model="emailOptOutPhishAll"
          color="negative"
          checked-icon="clear"
          unchecked-icon="mail"
          :label="
            emailOptOutPhishAll ?
            'Opt out of all phishing/security email notifications' :
            'Receive phishing/security email notifications'
          "
          class="text-bold"
          :disable="emailOptOutAll"
        />
      </div>
      <!-- TIMEOFF EMAILS -->
      <p class="row q-mb-none text-bold">Time Off</p>
      <div class="row items-center q-gutter-sm">
        <q-toggle
          v-model="emailOptOutTimeOffAll"
          color="negative"
          checked-icon="clear"
          unchecked-icon="mail"
          :label="
            emailOptOutTimeOffAll ?
            'Opt out of all time off email notifications' :
            'Receive time off email notifications'
          "
          class="text-bold"
          :disable="emailOptOutAll"
        />
      </div>
      <div class="row items-center q-gutter-sm">
        <q-toggle
          v-model="emailOptOutTimeOffWeekly"
          color="negative"
          checked-icon="clear"
          unchecked-icon="mail"
          :label="
            emailOptOutTimeOffWeekly ?
            'Opt out of weekly time off email notifications' :
            'Receive weekly time off email notifications'
          "
          :disable="emailOptOutAll || emailOptOutTimeOffAll"
        />
      </div>
      <div class="row items-center q-gutter-sm">
        <q-toggle
          v-model="emailOptOutTimeOffDaily"
          color="negative"
          checked-icon="clear"
          unchecked-icon="mail"
          :label="
            emailOptOutTimeOffDaily ?
            'Opt out of daily time off email notifications' :
            'Receive daily time off email notifications'
          "
          :disable="emailOptOutAll || emailOptOutTimeOffAll"
        />
      </div>
      <!-- WORKFLOW EMAILS -->
      <p class="row q-mb-none text-bold">Workflows</p>
      <div class="row items-center q-gutter-sm">
        <q-toggle
          v-model="emailOptOutWorkflowsAll"
          color="negative"
          checked-icon="clear"
          unchecked-icon="mail"
          :label="
            emailOptOutWorkflowsAll ?
            'Opt out of all workflow email notifications' :
            'Receive workflow email notifications'
          "
          class="text-bold"
          :disable="emailOptOutAll"
        />
      </div>
      <div class="row items-center q-gutter-sm">
        <q-toggle
          v-model="emailOptOutWorkflowsTransitions"
          color="negative"
          checked-icon="clear"
          unchecked-icon="mail"
          :label="
            emailOptOutWorkflowsTransitions ?
            'Opt out of employee transition email notifications' :
            'Receive employee transition email notifications'"
          :disable="emailOptOutAll || emailOptOutWorkflowsAll"
        />
      </div>
      <div class="row items-center q-gutter-sm">
        <q-toggle
          v-model="emailOptOutWorkflowsProcesses"
          color="negative"
          checked-icon="clear"
          unchecked-icon="mail"
          :label="
            emailOptOutWorkflowsProcesses ?
            'Opt out of process email notifications' :
            'Receive process email notifications'"
          :disable="emailOptOutAll || emailOptOutWorkflowsAll"
        />
      </div>

      <p class="row text-h6 q-mt-lg q-mb-none">Workflow Display Order</p>
      <q-markup-table style="max-width: 500px;">
        <thead>
          <tr>
            <th class="text-left">Workflow Type</th>
            <th>Display</th>
          </tr>
        </thead>
        <draggable 
          v-model="workflows" 
          tag="tbody"
          group="people" 
          @start="drag=true"
          @end="onEndDrag()"
          item-key="id">
          <template #item="{element}">
            <tr>
              <td class="text-left">{{ element.name }}</td>
              <td class="text-center">
                <q-checkbox v-model="element.display"/>
              </td>
            </tr>
          </template>
        </draggable>
      </q-markup-table>

      <div id="submit-button" class="row items-center q-gutter-sm q-mt-sm">
        <q-btn :disabled="!valuesAreChanged()" @click="submitProfileForm()">
          Submit
        </q-btn>
        <span class="success q-ml-sm q-mt-sm" :hidden="!submitted">
          <strong>Profile Updated.</strong>
        </span>
      </div>
    </form>
  </q-page>
</template>

<style scoped lang="scss">
.q-input {
  width: 300px;
}

.success {
    color: green;
}

#submit-button {
  position: fixed;
  top: 48px;
  right: 20px;

  button:enabled {
    background-color: $accent;
    color: white;
  }
}
</style>

<script setup lang="ts">
import { onMounted, Ref, ref } from 'vue'
import draggable from 'vuedraggable'

import { useUserStore } from 'src/stores/user'
import { usePeopleStore } from 'src/stores/people'
import { EmployeeRetrieve, WorkflowOption } from 'src/types'

const peopleStore = usePeopleStore()
const userStore = useUserStore()

let employeePk = ref('')

let displayNameCurrentVal = ref('')
let displayName = ref('')

let emailOptOutAllCurrentVal = ref(false)
let emailOptOutAll = ref(false)

let emailOptOutExpensesAllCurrentVal = ref(false)
let emailOptOutExpensesAll = ref(false)

let emailOptOutPhishAllCurrentVal = ref(false)
let emailOptOutPhishAll = ref(false)

let emailOptOutTimeOffAllCurrentVal = ref(false)
let emailOptOutTimeOffAll = ref(false)
let emailOptOutTimeOffWeeklyCurrentVal = ref(false)
let emailOptOutTimeOffWeekly = ref(false)
let emailOptOutTimeOffDailyCurrentVal = ref(false)
let emailOptOutTimeOffDaily = ref(false)

let emailOptOutWorkflowsAllCurrentVal = ref(false)
let emailOptOutWorkflowsAll = ref(false)
let emailOptOutWorkflowsTransitionsCurrentVal = ref(false)
let emailOptOutWorkflowsTransitions = ref(false)
let emailOptOutWorkflowsProcessesCurrentVal = ref(false)
let emailOptOutWorkflowsProcesses = ref(false)

let drag = ref(false)
let workflows: Ref<Array<WorkflowOption>> = ref([])
let workflowsCurrentVal: Ref<Array<WorkflowOption>> = ref([])

let submitted = ref(false)

function retrieveProfile(): Promise<EmployeeRetrieve> {
  return new Promise((resolve, reject) => {
    // We cannot guarantee the user has arrived in vuex state immediately,
    // so request it again here
    userStore.simpleUserRequest()
      .then((employee) => {
        employeePk.value = employee.pk.toString()
        displayName.value = employee.name
        displayNameCurrentVal.value = displayName.value
        emailOptOutAll.value = employee.email_opt_out_all
        emailOptOutAllCurrentVal.value = emailOptOutAll.value
        emailOptOutExpensesAll.value = employee.email_opt_out_expenses_all
        emailOptOutExpensesAllCurrentVal.value = emailOptOutExpensesAll.value
        emailOptOutPhishAll.value = employee.email_opt_out_phish_all
        emailOptOutPhishAllCurrentVal.value = emailOptOutPhishAll.value
        emailOptOutTimeOffAll.value = employee.email_opt_out_timeoff_all
        emailOptOutTimeOffAllCurrentVal.value = emailOptOutTimeOffAll.value
        emailOptOutTimeOffWeekly.value = employee.email_opt_out_timeoff_weekly
        emailOptOutTimeOffWeeklyCurrentVal.value = emailOptOutTimeOffWeekly.value
        emailOptOutTimeOffDaily.value = employee.email_opt_out_timeoff_daily
        emailOptOutTimeOffDailyCurrentVal.value = emailOptOutTimeOffDaily.value
        emailOptOutWorkflowsAll.value =
          employee.email_opt_out_workflows_all
        emailOptOutWorkflowsAllCurrentVal.value = emailOptOutWorkflowsAll.value
        emailOptOutWorkflowsTransitions.value =
          employee.email_opt_out_workflows_transitions
        emailOptOutWorkflowsTransitionsCurrentVal.value =
          emailOptOutWorkflowsTransitions.value
        emailOptOutWorkflowsProcesses.value =
          employee.email_opt_out_workflows_processes
        emailOptOutWorkflowsProcessesCurrentVal.value =
          emailOptOutWorkflowsProcesses.value
        workflows.value = employee.workflow_display_options
        workflowsCurrentVal.value = JSON.parse(JSON.stringify(workflows.value))
      })
      .catch(e => {
        console.error('Error getting user from API:', e)
        reject(e)
      })
  })
}

function workflowOptionsAreChanged(): boolean {
  if (workflows.value.length != workflowsCurrentVal.value.length) {
    return true
  }
  for (let i = 0; i < workflows.value.length; i++) {
    if (workflows.value[i].id != workflowsCurrentVal.value[i].id) {
      return true
    }
    if (workflows.value[i].name != workflowsCurrentVal.value[i].name) {
      return true
    }
    if (workflows.value[i].display != workflowsCurrentVal.value[i].display) {
      return true
    }
    if (workflows.value[i].order != workflowsCurrentVal.value[i].order) {
      return true
    }
  }
  return false
}

function valuesAreChanged(): boolean { 
  if (
    displayName.value == displayNameCurrentVal.value &&
    emailOptOutAll.value == emailOptOutAllCurrentVal.value &&
    emailOptOutExpensesAll.value == emailOptOutExpensesAllCurrentVal.value &&
    emailOptOutPhishAll.value == emailOptOutPhishAllCurrentVal.value &&
    emailOptOutTimeOffAll.value == emailOptOutTimeOffAllCurrentVal.value &&
    emailOptOutTimeOffWeekly.value ==
      emailOptOutTimeOffWeeklyCurrentVal.value &&
    emailOptOutTimeOffDaily.value == emailOptOutTimeOffDailyCurrentVal.value &&
    emailOptOutWorkflowsAll.value == emailOptOutWorkflowsAllCurrentVal.value &&
    emailOptOutWorkflowsTransitions.value ==
      emailOptOutWorkflowsTransitionsCurrentVal.value &&
    emailOptOutWorkflowsProcesses.value ==
      emailOptOutWorkflowsProcessesCurrentVal.value &&
    !workflowOptionsAreChanged()
  ) {
    return false
  } else {
    return true
  }
}

function onEndDrag(): void {
  drag.value = false
  // updateServer(workflows)
}

function submitProfileForm(): void {
  peopleStore.updatePartialEmployee(employeePk.value, {
    display_name: displayName.value,
    email_opt_out_all: emailOptOutAll.value,
    email_opt_out_expenses_all: emailOptOutExpensesAll.value,
    email_opt_out_phish_all: emailOptOutPhishAll.value,
    email_opt_out_timeoff_all: emailOptOutTimeOffAll.value,
    email_opt_out_timeoff_weekly: emailOptOutTimeOffWeekly.value,
    email_opt_out_timeoff_daily: emailOptOutTimeOffDaily.value,
    email_opt_out_workflows_all: emailOptOutWorkflowsAll.value,
    email_opt_out_workflows_transitions: emailOptOutWorkflowsTransitions.value,
    email_opt_out_workflows_processes: emailOptOutWorkflowsProcesses.value,
    workflow_display_options: workflows.value
  })
    .then((p) => {
      displayNameCurrentVal.value = p.name
      emailOptOutAllCurrentVal.value = p.email_opt_out_all
      emailOptOutExpensesAllCurrentVal.value = p.email_opt_out_expenses_all
      emailOptOutPhishAllCurrentVal.value = p.email_opt_out_phish_all
      emailOptOutTimeOffAllCurrentVal.value = p.email_opt_out_timeoff_all
      emailOptOutTimeOffWeeklyCurrentVal.value = p.email_opt_out_timeoff_weekly
      emailOptOutTimeOffDailyCurrentVal.value = p.email_opt_out_timeoff_daily
      emailOptOutWorkflowsAllCurrentVal.value = p.email_opt_out_workflows_all
      emailOptOutWorkflowsTransitionsCurrentVal.value =
        p.email_opt_out_workflows_transitions
      emailOptOutWorkflowsProcessesCurrentVal.value =
        p.email_opt_out_workflows_processes
      workflows.value = JSON.parse(JSON.stringify(
        p.workflow_display_options
      ))
      workflowsCurrentVal.value = JSON.parse(JSON.stringify(
        p.workflow_display_options
      ))
      userStore.userRequest()
        .catch(e => {
          console.error('Error getting user from store', e)
        })
      submitted.value = true
      setTimeout(() => submitted.value = false, 3000)
    })
    .catch(e => {
      console.error('Error updating employee profile settings:', e)
    })
}

onMounted(() => { 
  retrieveProfile()
    .catch(e => {
      console.error('Error retrieving Employee profile from API:', e)
    })
})
</script>
