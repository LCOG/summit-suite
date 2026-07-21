<template>
<div class="q-py-sm">
  <q-spinner-grid
      v-if="!workflowsLoaded"
      class="spinner q-mt-lg"
      color="primary"
      size="xl"
    />
  <q-table
    v-else
    :rows="workflows()"
    :columns="columns()"
    :filter=tableFilter
    :filter-method=tableFilterMethod
    :grid="$q.screen.lt.md"
    no-data-label="Nothing to show"
    row-key="name"
    :rows-per-page-options="[0]"
    v-bind:class="'workflowtable-' + props.type"
    v-model:pagination="pagination"
  >
    <template v-slot:top-right>
      <q-input
        borderless
        dense
        clearable
        debounce="300"
        v-model="tableFilter"
        placeholder="Search"
      >
        <template v-slot:prepend>
          <q-icon name="search">
            <q-tooltip>
              Type to search on Name, Description, Tag name, or Employee Name
            </q-tooltip>
          </q-icon>
        </template>
      </q-input>
    </template>
    <template v-slot:body-cell-createdBy="props">
      <q-td key="createdBy" :props="props">
        {{ props.row.created_by?.display_name }}
      </q-td>
    </template>
    <template v-slot:body-cell-createdAt="props">
      <q-td key="createdAt" :props="props">
        {{ readableDate(props.row.started_at) }}
      </q-td>
    </template>
    <template v-slot:body-cell-submitted="props">
      <q-td key="submitted" :props="props">
        {{ submittedDisplay(props.row) }}
      </q-td>
    </template>
    <template v-slot:body-cell-transitionDate="props">
      <q-td key="transitionDate" :props="props">
        {{ readableDate(props.row.transition_date) }}
      </q-td>
    </template>
    <template v-slot:body-cell-completed="props">
      <q-td key="completed" :props="props">
        {{ readableDate(props.row.completed_at) }}
      </q-td>
    </template>
    <template v-slot:body-cell-status="props">
      <q-td key="status" :props="props">
        <q-linear-progress
          v-if="isInteger(props.row.status)"
          rounded size="25px"
          :value="props.row.percent_complete/100"
          color="primary"
        >
          <div class="absolute-full flex flex-center">
            <q-badge
              color="white"
              text-color="primary"
              :label="`${props.row.percent_complete}%`"
            />
          </div>
        </q-linear-progress>
        <div v-else>Assigned to: {{ props.row.status }}</div>
      </q-td>
    </template>
    <template v-slot:body-cell-actions="props">
      <q-td key="actions" :props="props">
        <q-btn
          class="col"
          dense
          round
          flat
          :color="props.row.pis_action_required ? 'orange' : 'grey'"
          @click="editWorkflowInstance(props.row)"
          icon="play_arrow"
        >
          <q-tooltip :delay="400">
            View progress
          </q-tooltip>
        </q-btn>
        <q-btn
          v-if="workflowHasTransition(props.row) && canViewTransition()"
          class="col"
          dense
          round
          flat
          :color="props.row.transition_action_required ? 'orange' : 'grey'"
          @click="editTransitionForm(props.row)"
          icon="assignment"
        >
          <q-tooltip :delay="400">
            View form
          </q-tooltip>
        </q-btn>
        <q-btn
          v-if="!archived && canArchiveWorkflowInstance(props.row)"
          class="col"
          dense
          round
          flat
          color="grey"
          @click="showArchiveDialog(props.row)"
          icon="delete"
        >
          <q-tooltip :delay="400">
            Delete workflow
          </q-tooltip>
        </q-btn>
        <q-btn
          v-if="archived && canArchiveWorkflowInstance(props.row)"
          class="col"
          dense
          round
          flat
          color="grey"
          @click="showArchiveDialog(props.row)"
          icon="restore_from_trash"
        >
          <q-tooltip :delay="400">
            Restore workflow
          </q-tooltip>
        </q-btn>
        <q-icon
          v-if="!archived && !complete && props.row.employee_action_required"
          color="orange"
          name="warning"
          size="md"
        >
          <q-tooltip content-style="font-size: 16px">
            <div>Your action is required</div>
          </q-tooltip>
        </q-icon>
      </q-td>
    </template>
    <!-- GRID MODE -->
    <template v-slot:item="props">
      <div class="q-pa-xs col-xs-12 col-sm-6 col-md-4 col-lg-3">
        <q-card class="q-py-sm">
          <q-list dense>
            <q-item v-for="col in props.cols" :key="col.name">
              <div class="q-table__grid-item-row">
                <div class="q-table__grid-item-title">{{ col.label }}</div>
                <div
                  class="q-table__grid-item-value"
                  v-if="col.name == 'createdBy'"
                >
                  {{ col.value?.display_name }}
                </div>
                <div
                  class="q-table__grid-item-value"
                  v-else-if="col.name == 'transitionDate'"
                >
                  {{ readableDate(props.row.transition_date) }}
                </div>
                <div
                  class="q-table__grid-item-value"
                  v-else-if="col.name == 'createdAt'"
                >
                  {{ readableDate(props.row.started_at) }}
                </div>
                <div
                  class="q-table__grid-item-value"
                  v-else-if="col.name == 'submitted'"
                >
                  {{ submittedDisplay(props.row) }}
                </div>
                <div
                  class="q-table__grid-item-value"
                  v-else-if="col.name == 'status'"
                >
                  <q-linear-progress
                    v-if="isInteger(props.row.status)"
                    rounded size="25px"
                    :value="props.row.percent_complete/100"
                    color="primary"
                  >
                    <div class="absolute-full flex flex-center">
                      <q-badge
                        color="white"
                        text-color="primary"
                        :label="`${props.row.percent_complete}%`"
                      />
                    </div>
                  </q-linear-progress>
                  <div v-else>Assigned to: {{ props.row.status }}</div>
                </div>
                <div
                  class="q-table__grid-item-value"
                  v-else-if="col.name == 'completed'"
                >
                  {{ readableDate(props.row.completed_at) }}
                </div>
                <div
                  class="q-table__grid-item-value row q-gutter-sm items-center
                    justify-around"
                  v-else-if="col.label == 'Actions'"
                >
                  <q-btn
                    dense
                    round
                    flat
                    :color="props.row.pis_action_required ? 'orange' : 'grey'"
                    @click="editWorkflowInstance(props.row)"
                    icon="play_arrow"
                  >
                    <q-tooltip>
                      View progress
                    </q-tooltip>
                  </q-btn>
                  <q-btn
                    v-if="workflowHasTransition(props.row) &&
                      canViewTransition()"
                    dense
                    round
                    flat
                    :color="
                      props.row.transition_action_required ? 'orange' : 'grey'
                    "
                    @click="editTransitionForm(props.row)"
                    icon="assignment"
                  >
                    <q-tooltip :delay="400">
                      View form
                    </q-tooltip>
                  </q-btn>
                  <q-btn
                    v-if="!archived && canArchiveWorkflowInstance(props.row)"
                    dense
                    round
                    flat
                    color="grey"
                    @click="showArchiveDialog(props.row)"
                    icon="delete"
                  >
                    <q-tooltip :delay="400">
                      Delete workflow
                    </q-tooltip>
                  </q-btn>
                  <q-btn
                    v-if="archived && canArchiveWorkflowInstance(props.row)"
                    dense
                    round
                    flat
                    color="grey"
                    @click="showArchiveDialog(props.row)"
                    icon="restore_from_trash"
                  >
                    <q-tooltip :delay="400">
                      Restore workflow
                    </q-tooltip>
                  </q-btn>
                  <q-icon
                    v-if="!archived && !complete &&
                      props.row.employee_action_required"
                    color="orange"
                    name="warning"
                    size="md"
                  >
                    <q-tooltip content-style="font-size: 16px">
                      <div>Your action is required</div>
                    </q-tooltip>
                  </q-icon>
                </div>
                
                <div class="q-table__grid-item-value" v-else>
                  {{ col.value }}
                </div>
              </div>
            </q-item>
          </q-list>
        </q-card>
      </div>
    </template>
    <template v-slot:bottom-row v-if="props.allowAddDelete">
      <q-tr @click="clickAddWorkflow()" class="cursor-pointer row-add-new">
        <q-td colspan="100%">
          <q-icon name="add" size="md" class="q-pr-sm"/>New Workflow
        </q-td>
      </q-tr>
    </template>
  </q-table>

  <q-dialog v-model="archiveDialogVisible">
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
            <span v-if="!archived">delete</span>
            <span v-else>restore</span>
            this workflow?
          </span>
        </div>
        <div class="row justify-center text-center">
          Position: {{ archiveDialogPositionName }}
        </div>
        <div class="row justify-center text-center">
          {{ archiveDialogPercentComplete }}% Complete
        </div>
      </q-card-section>

      <q-card-actions class="row justify-around">
        <q-btn flat label="Cancel" color="primary" v-close-popup />
        <q-btn
          v-if="!archived"
          flat
          label="Yes, delete it"
          color="primary"
          @click="archiveRow()"
          v-close-popup
        />
        <q-btn
          v-else
          flat
          label="Yes, restore it"
          color="primary"
          @click="restoreRow()"
          v-close-popup
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <q-dialog v-model="newWorkflowDialogVisible">
    <q-card>
      <q-card-section>
        <div class="row items-center">
          <q-avatar
            icon="add_circle_outline"
            color="primary"
            text-color="white"
          />
          <span class="q-ml-sm">
            Are you sure you want to start a new workflow?
          </span>
        </div>
      </q-card-section>

      <q-card-actions class="row justify-around">
        <q-btn flat label="Cancel" color="primary" v-close-popup />
        <q-btn
          flat
          label="Yes, start it"
          color="primary"
          @click="startNewWorkflow()"
          v-close-popup
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</div>
</template>

<style lang="scss">
.q-table tbody td.td-status {
    min-width: 135px;
    white-space: normal;
}
.q-table tbody td.wide-actions {
    min-width: 200px;
    white-space: normal;
}
.q-table__bottom {
  display: none !important;
}
.q-table__grid-item-row {
  width: 100%;

}
</style>

<script setup lang="ts">
import { QTableProps, useQuasar } from 'quasar'
import { ref, Ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { WorkflowInstanceSimple } from 'src/types'

import { readableDate } from 'src/filters'
import { usePeopleStore } from 'src/stores/people'
import { useUserStore } from 'src/stores/user'
import { useWorkflowsStore } from 'src/stores/workflows'
import { isInteger } from 'src/utils'

const quasar = useQuasar()
const router = useRouter()
const peopleStore = usePeopleStore()
const userStore = useUserStore()
const workflowsStore = useWorkflowsStore()

let archiveDialogVisible = ref(false)
let archiveDialogPositionName = ref('Not Set')
let archiveDialogPercentComplete = ref(0)
let rowPkToArchive = ref('')
let newWorkflowDialogVisible = ref(false)

const pagination = ref({}) as Ref<QTableProps['pagination']>

type WorkflowTableSortOptions = {
  column?: string
  descending?: boolean | string
}

const props = defineProps<{
  archived: boolean,
  complete: boolean,
  type: string,
  allowAddDelete: boolean,
  workflowsLoaded: boolean,
  employeePk?: number,
  sortOptions?: WorkflowTableSortOptions
  // TODO: Move action required into the table as a column
  // actionRequired?: boolean,
}>()

const emit = defineEmits<{
  (e: 'retrieve'): void
}>()

const activeColumns: QTableProps['columns'] = [
  {
    name: 'createdBy',
    label: 'Created By',
    align: 'center',
    field: 'created_by'
  },
  { 
    name: 'createdAt',
    align: 'center',
    label: 'Created',
    field: 'created_at',
    sortable: true
  },
  {
    name: 'status',
    align: 'center',
    label: 'Status',
    field: 'status',
    sortable: true
  },
  { name: 'actions', label: 'Actions', align: 'center', field: '' },
]

const archivedColumns: QTableProps['columns'] = [
  { name: 'type', label: 'Type', align: 'center', field: 'workflow_name'},
  {
    name: 'createdAt',
    align: 'center',
    label: 'Created',
    field: 'created_at',
    sortable: true
  },
  {
    name: 'status',
    align: 'center',
    label: 'Status',
    field: 'status',
    sortable: true
  },
  { name: 'actions', label: 'Actions', align: 'center', field: '' },
]

const completedColumns: QTableProps['columns'] = [
  { name: 'type', label: 'Type', align: 'center', field: 'workflow_name'},
  {
    name: 'createdAt',
    align: 'center',
    label: 'Created',
    field: 'created_at',
    sortable: true
  },
  {
    name: 'status',
    align: 'center',
    label: 'Status',
    field: 'status',
    sortable: true
  },
  {
    name: 'completed',
    align: 'center',
    label: 'Completed',
    field: 'completed_at',
    sortable: true
  },
  { name: 'actions', label: 'Actions', align: 'center', field: '' },
]

const activeTransitionColumns: QTableProps['columns'] = [
  { name: 'position', label: 'Position', align: 'center', field: 'title_name' },
  { name: 'name', label: 'Name', align: 'center', field: 'employee_name' },
  { 
    name: 'submitted',
    align: 'center',
    label: 'Submitted',
    field: 'submitted',
    sortable: true
  },
  {
    name: 'transitionDate',
    align: 'center',
    label: 'Transition Date',
    field: 'transition_date',
    sortable: true
  },
  {
    name: 'status',
    align: 'center',
    label: 'Status',
    field: 'status',
    sortable: true
  },
  { name: 'actions', label: 'Actions', align: 'center', field: '' },
]

const archivedTransitionColumns: QTableProps['columns'] = [
  { name: 'type', label: 'Type', align: 'center', field: 'workflow_name'},
  { name: 'position', label: 'Position', align: 'center', field: 'title_name' },
  {
    name: 'submitted',
    align: 'center',
    label: 'Submitted',
    field: 'submitted',
    sortable: true
  },
  {
    name: 'status',
    align: 'center',
    label: 'Status',
    field: 'status',
    sortable: true
  },
  { name: 'actions', label: 'Actions', align: 'center', field: '' },
]

const completedTransitionColumns: QTableProps['columns'] = [
  { name: 'type', label: 'Type', align: 'center', field: 'workflow_name'},
  { name: 'position', label: 'Position', align: 'center', field: 'title_name' },
  {
    name: 'submitted',
    align: 'center',
    label: 'Submitted',
    field: 'submitted',
    sortable: true
  },
  {
    name: 'status',
    align: 'center',
    label: 'Status',
    field: 'status',
    sortable: true
  },
  {
    name: 'completed',
    align: 'center',
    label: 'Completed',
    field: 'completed_at',
    sortable: true
  },
  { name: 'actions', label: 'Actions', align: 'center', field: '' },
]

function columns() {
  if ([
    'employee-new', 'employee-return', 'employee-name-change',
    'employee-change', 'employee-exit'
  ].includes(props.type)) {
    if (props.archived) {
      return archivedTransitionColumns
    } else if (props.complete) {
      return completedTransitionColumns
    }
    return activeTransitionColumns 
  } else {
    if (props.archived) {
      return archivedColumns
    } else if (props.complete) {
      return completedColumns
    }
    return activeColumns
  }
}

function normalizeDescending(value: WorkflowTableSortOptions['descending']): boolean {
  if (typeof value == 'boolean') {
    return value
  }
  if (typeof value == 'string') {
    return value.toLowerCase() == 'true'
  }
  return false
}

function applyStoredSortOptions(): void {
  const column = props.sortOptions?.column
  if (!column) {
    return
  }

  const tableColumns = columns() || []
  const targetColumn = tableColumns.find((col) => col.name == column)
  if (!targetColumn || !targetColumn.sortable) {
    return
  }

  pagination.value = {
    ...pagination.value,
    sortBy: column,
    descending: normalizeDescending(props.sortOptions?.descending)
  }
}

let tableFilter = ref('')

function tableFilterMethod(rows: readonly any[], term: string) {
  const tableRows = rows as WorkflowInstanceSimple[]
  const searchTerm = term ? term.toLowerCase() : ''
  const filteredRows = tableRows.filter(
    (row) => {
      if (searchTerm == '') {
          // If no search term, return all rows
          return true
      } else {
          const matchCriteria: Array<boolean> = []
          // Filter by name
          if (row.employee_name) {
            const nameMatches = row.employee_name.toLowerCase()
              .includes(searchTerm)
            matchCriteria.push(nameMatches)
          }
          // Filter by position
          if (row.title_name) {
            const positionMatches = row.title_name.toLowerCase()
              .includes(searchTerm)
            matchCriteria.push(positionMatches)
          }
          // Filter by workflow name if we're searching complete or deleted WFs
          if (props.complete || props.archived) {
            if (row.workflow_name) {
              const workflowNameMatches = row.workflow_name.toLowerCase()
                .includes(searchTerm)
              matchCriteria.push(workflowNameMatches)
            }
          }
          // If any criteria match, return the row
          if (matchCriteria.some(c => !!c)) {
              return true
          }
          // Assume row doesn't match
          return false
      }
    })
  return filteredRows
}

function workflows(): Array<WorkflowInstanceSimple> {
  let workflows: Array<WorkflowInstanceSimple> = []
  if (props.archived) {
    workflows = workflowsStore.workflowsArchived
  } else if (props.complete) {
    workflows = workflowsStore.workflowsComplete
  } else {
    workflows = workflowsStore.workflowsIncomplete
  }
  return workflows.filter(
    (wf) => {
      if (props.type == 'all') {
        return true
      } else {
        // Filter by workflow type
        if (props.type == wf.workflow_type) {
          return true
        } else {
          // Assume workflow doesn't match
          return false 
        }
      }
    }
  )
}

function submittedDisplay(row: WorkflowInstanceSimple): string {
  if (row.transition_date_submitted) {
    return `${ readableDate(row.transition_date_submitted) } - 
      ${ row.transition_submitter }`
  } else {
    return 'Not submitted'
  }
}

function editWorkflowInstance(workflowInstance: WorkflowInstanceSimple): void {
  const rowPk = workflowInstance.pk.toString()
  router.push({name: 'workflow-processes', params: {pk: rowPk}})
    .catch(e => {
      console.error('Error navigating to workflow instance detail:', e)
    })
}

function workflowHasTransition(
  workflowInstance: WorkflowInstanceSimple
): boolean {
  if (workflowInstance.transition_type) {
    return true
  } else {
    return false
  }
}

// TODO
function canViewTransition(): boolean {
  return true
}

function editTransitionForm(workflowInstance: WorkflowInstanceSimple) {
  const rowPk = workflowInstance.pk.toString()
  router.push({name: 'workflow-transition-form', params: {pk: rowPk}} )
    .catch(e => {
      console.error('Error navigating to workflow transition form:', e)
    })
}

function canArchiveWorkflowInstance(
  workflowInstance: WorkflowInstanceSimple
): boolean {
  if (workflowInstance.complete || workflowInstance.completed_at) {
    return false
  }
  if (userStore.getEmployeeProfile.is_all_workflows_admin) {
    // If they are an All-Workflows-Admin, allow archive
    return true
  } else if (workflowInstance.workflow_role_pk) {
    // If they are an admin of the workflow, allow archive
    return userStore.getEmployeeProfile.workflow_roles
      .indexOf(workflowInstance.workflow_role_pk) != -1
  } else {
    // TODO: What should happen if no role assigned?
    // Only admins? Everyone? Require all steps to have roles?
    return false
  }
}

function showArchiveDialog(row: WorkflowInstanceSimple): void {
  rowPkToArchive.value = row.pk.toString()
  archiveDialogPositionName.value = row.title_name
  archiveDialogPercentComplete.value = row.percent_complete
  archiveDialogVisible.value = true
}

function archiveRow(): void {
  workflowsStore.archiveWorkflowInstance(rowPkToArchive.value)
    .then(() => {
      quasar.notify('Deleted a workflow.')
      emit('retrieve')
    })
    .catch(e => {
      console.error('Error deleting workflow', e)
    })
}

function restoreRow(): void {
  workflowsStore.restoreWorkflowInstance(rowPkToArchive.value)
    .then(() => {
      quasar.notify('Restored a workflow.')
      emit('retrieve')
    })
    .catch(e => {
      console.error('Error restoring workflow', e)
    })
}

function clickAddWorkflow(): void {
  newWorkflowDialogVisible.value = true
}

function startNewWorkflow(): void {
  workflowsStore.createNewWorkflowInstance(props.type)
    .then((wfi) => {
      if (!!wfi.transition) {
        navigateToWorkflowTransitionForm(wfi.pk)
      } else {
        navigateToWorkflowProcesses(wfi.pk)
      }
    })
    .catch(e => {
      console.error(
        `Error creating a new ${ props.type } workflow instance`, e
      )
    })
}

function navigateToWorkflowTransitionForm(pk: number): void {
  router.push({name: 'workflow-transition-form', params: {pk: pk.toString()}})
    .catch(e => {
      console.error('Error navigating to workflow transition form:', e)
    })
}

function navigateToWorkflowProcesses(pk: number): void {
  router.push({name: 'workflow-processes', params: {pk: pk.toString()}})
    .catch(e => {
      console.error('Error navigating to workflow processes:', e)
    })
}

watch(
  [() => pagination.value?.sortBy, () => pagination.value?.descending],
  ([sortBy, descending], [oldSortBy, oldDescending]) => {
    if (oldSortBy === undefined) {
      return // Page init
    }
    const savedSortBy = props.sortOptions?.column
    const savedDescending = normalizeDescending(props.sortOptions?.descending)
    if (savedSortBy == sortBy && savedDescending == descending) {
      return // No change from stored sort options
    }
    let clearSort = false
    if (!sortBy) {
      clearSort = true
    }
    peopleStore.updatePartialEmployee(
      props.employeePk.toString(),
      {workflow_table_sort: [props.type, sortBy, descending, clearSort]}
    )
  }
)

watch(
  () => props.sortOptions,
  () => {
    applyStoredSortOptions()
  },
  { immediate: true, deep: true }
)
</script>
