import axios from 'axios'
import { defineStore } from 'pinia'

import { apiURL, handlePromiseError } from 'src/stores/index'
import {
  EmployeeTransition, EmployeeTransitionUpdate, WorkflowInstance
} from 'src/types'

export const useWorkflowsStore = defineStore('workflows', {
  state: () => ({
    currentWorkflowInstance: {} as WorkflowInstance,
    workflowsIncomplete: [] as Array<WorkflowInstance>,
    workflowsComplete: [] as Array<WorkflowInstance>,
    workflowsArchived: [] as Array<WorkflowInstance>,
    workflowOptions: {} as {[key: string]: any}
  }),

  getters: {
    currentEmployeeTransition(state): EmployeeTransition {
      return state.currentWorkflowInstance.transition ||
        {} as EmployeeTransition
    },
    currentPIs: state => {
      const pis = state.currentWorkflowInstance.process_instances || []
      return pis.sort((a, b) => {
        // Sort PIs with action_required first
        return a.action_required == b.action_required ? 0 :
          a.action_required ? -1 : 1
      })
    },
    processInstanceCurrentStepPks: state => {
      const d: {[pk: number]: number} = {}
      if (!state.currentWorkflowInstance.pk) {
        return d
      }
      state.currentWorkflowInstance.process_instances.forEach(pi => {
        if (pi.current_step_instance) {
          d[pi.pk] = pi.current_step_instance.pk
        } else {
          d[pi.pk] = -1
        }
      })
      return d
    },
    workflowOptionsByType: state => (type: string) => {
      if (Object.keys(state.workflowOptions).length === 0) { return [] }
      const options = state.workflowOptions.results.filter((o: {workflow_type: string}) => o.workflow_type == type)
      if (options.length > 0 && options[0].column_sort) {
        const [col, desc] = options[0].column_sort?.split(';')
        return {column: col, descending: desc}
      }
      return {}
    }
  },

  actions: {
    createNewEmployeeOnboarding(): Promise<WorkflowInstance> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/workflowinstance`,
          method: 'POST',
          data: {type: 'employee_onboarding'}
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error creating new employee onboarding workflow instance',
              e
            )
          })
      })
    },
    createNewEmployeeReturning(): Promise<WorkflowInstance> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/workflowinstance`,
          method: 'POST',
          data: {type: 'employee_returning'}
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error creating new employee returning workflow instance',
              e
            )
          })
      })
    },
    createNewEmployeeChanging(): Promise<WorkflowInstance> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/workflowinstance`,
          method: 'POST',
          data: {type: 'employee_changing'}
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error creating new employee changing workflow instance',
              e
            )
          })
      })
    },
    createNewEmployeeExiting(): Promise<WorkflowInstance> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/workflowinstance`,
          method: 'POST',
          data: {type: 'employee_exiting'}
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error creating new employee exiting workflow instance',
              e
            )
          })
      })
    },
    createNewWorkflowInstance(type: string): Promise<WorkflowInstance> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/workflowinstance`,
          method: 'POST',
          data: { type }
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(
              reject, `Error creating new ${ type } workflow instance`, e
            )
          })
      })
    },
    getCurrentWorkflowInstance(pk: string) {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/workflowinstance/${ pk }` })
          .then(resp => {
            this.currentWorkflowInstance = resp.data
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error getting current workflow instance', e
            )
          })
        })
    },
    // All workflow instances, optionally filtered to ongoing/completed
    getWorkflows(data: {archived: boolean, complete: boolean}) {
      let targetUrl: string
      let workflowType: 'workflowsComplete' | 'workflowsIncomplete' |
        'workflowsArchived'
      if (data.archived) {
        targetUrl =
          `${ apiURL }api/v1/workflowinstance?simple=true&archived=true`
        workflowType = 'workflowsArchived'
      } else if (data.complete) {
        targetUrl = `${ apiURL }api/v1/workflowinstance?simple=true` +
          '&archived=false&complete=true'
        workflowType = 'workflowsComplete'
      } else {
        targetUrl = `${ apiURL }api/v1/workflowinstance?simple=true` +
          '&archived=false&complete=false'
        workflowType = 'workflowsIncomplete'
      }
      return new Promise((resolve, reject) => {
        axios({ url: targetUrl })
        .then(resp => {
          this[workflowType] = resp.data.results
          resolve(resp)
        })
        .catch(e => {
          handlePromiseError(
            reject, `Error getting workflows of type ${ workflowType }`, e
          )
        })
      })
    },
    getWorkflowOptions() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/workflowoptions` })
          .then(resp => {
            this.workflowOptions = resp.data
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting workflow options', e)
          })
      })
    },
    completeStepInstance(
      stepInstancePk: number, nextStepPk?: number,
      triggerProcessesPks?: number[]
    ) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/stepinstance/${ stepInstancePk }`,
          data: {
            action: 'complete', stepInstancePk, nextStepPk, triggerProcessesPks
          },
          method: 'PATCH'
        })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error completing current step instance', e
            )
          })
      })
    },
    undoStepInstanceCompletion(
      stepInstancePk: number, nextStepInstancePk?: number
    ) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/stepinstance/${ stepInstancePk }`,
          data: { action: 'undo', stepInstancePk, nextStepInstancePk },
          method: 'PATCH'
        })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error undoing current step instance completion', e
            )
          })
      })
    },
    updateEmployeeTransition(
      pk: string, data: EmployeeTransitionUpdate
    ): Promise<EmployeeTransition> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/employeetransition/${ pk }`,
          data,
          method: 'PUT'
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error updating employee transition', e)
          })
      })
    },
    sendMailboxNotificationEmail(pk: string, data: {
      senderName: string, senderEmail: string, transitionUrl: string
    }): Promise<boolean> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/employeetransition/${ pk }` +
            '/send_mailbox_notification_email',
          data,
          method: 'POST'
        })
          .then(() => {
            resolve(true)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error sending mailbox notification email', e
            )
          })
      })
    },
    sendTransitionToEmailList(pk: string, data: {
      type: 'SDS'|'FI'|'HR'|'STN'|'ASSIGN', reassignTo: string, update: boolean,
      extraMessage: string, senderName: string, senderEmail: string,
      transitionUrl: string
    }): Promise<boolean> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/employeetransition/${ pk }` +
            '/send_transition_to_email_list',
          data,
          method: 'POST'
        })
          .then(() => {
            resolve(true)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error sending employee transition to email list', e
            )
          })
      })
    },
    // Archive/restore is when you want to remove a workflow instance that has
    // perhaps been created by accident. No notifications are generated.
    archiveWorkflowInstance(workflowInstancePk: string) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/workflowinstance/${ workflowInstancePk }`,
          data: {action: 'archive'},
          method: 'PATCH'
        })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error archiving workflow instance', e)
          })
      })
    },
    restoreWorkflowInstance(workflowInstancePk: string) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/workflowinstance/${ workflowInstancePk }`,
          data: {action: 'restore'},
          method: 'PATCH'
        })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error restoring workflow instance', e)
          })
      })
    },
    // Complete/reopen is when you want to manually mark a workflow instance as
    // complete. It is only available to admins and we may want to remove in the future.
    completeWorkflowInstance(workflowInstancePk: string) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/workflowinstance/${ workflowInstancePk }`,
          data: {action: 'complete'},
          method: 'PATCH'
        })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error completing workflow instance', e)
          })
      })
    },
    reopenWorkflowInstance(workflowInstancePk: string) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/workflowinstance/${ workflowInstancePk }`,
          data: {action: 'reopen'},
          method: 'PATCH'
        })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error reopening workflow instance', e)
          })
      })
    },
    // Cancel/reinstate is when you want to cancel a workflow instance that is
    // in progress. It is functionally equivalent to archive/restore, but it is
    // available to all users and generates notifications to stakeholders.
    cancelWorkflowInstance(workflowInstancePk: string, reason: string) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/workflowinstance/${ workflowInstancePk }`,
          data: {action: 'cancel', reason},
          method: 'PATCH'
        })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error cancelling workflow instance', e)
          })
      })
    },
    reinstateWorkflowInstance(workflowInstancePk: string) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${ apiURL }api/v1/workflowinstance/${ workflowInstancePk }`,
          data: {action: 'reinstate'},
          method: 'PATCH'
        })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error reinstating workflow instance', e)
          })
      })
    },
    authLogout() {
      return new Promise((resolve) => {
        this.$reset()
        resolve('Successfully triggered logout')
      })
    }
  }
})
