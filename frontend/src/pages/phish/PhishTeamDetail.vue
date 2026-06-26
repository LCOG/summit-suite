<template>
<q-page class="q-pa-md">
  <q-spinner-grid
    v-if="loading"
    class="spinner q-mt-lg"
    color="primary"
    size="xl"
  />
  
  <div v-else>
    <!-- Header with back button -->
    <div class="row items-center q-mb-md">
      <q-btn 
        flat 
        dense 
        round 
        icon="arrow_back" 
        @click="goBack"
        class="q-mr-md"
      >
        <q-tooltip>Back to Team List</q-tooltip>
      </q-btn>
      <div class="text-h4">{{ teamMember?.employeeName }}</div>
    </div>

    <!-- Main info cards -->
    <div class="row q-col-gutter-md q-mb-md">
      <!-- Profile card -->
      <div class="col-xs-12 col-sm-6 col-md-4">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-h6 q-mb-md">Profile</div>
            
            <div class="q-mb-sm">
              <div class="text-caption text-grey-7">Employee Name</div>
              <div class="text-body1">{{ teamMember?.employeeName }}</div>
            </div>

            <div class="q-mb-sm">
              <div class="text-caption text-grey-7">Risk Level</div>
              <q-select
                v-model="teamMember.riskLevel"
                :options="riskLevelOptions"
                @update:model-value="
                  phishStore.updateEmployeeRiskLevel(teamMember.pk, $event.name)
                "
                outlined
                dense
                class="q-mt-xs"
              >
                <template v-slot:selected>
                  <q-badge 
                    v-if="teamMember.riskLevel.name"
                    :color="teamMember.riskLevel.color" 
                    :label="teamMember.riskLevel.name"
                  />
                </template>
                <template v-slot:option="scope">
                  <q-item v-bind="scope.itemProps">
                    <q-item-section>
                      <q-badge 
                        :color="scope.opt.color" 
                        :label="scope.opt.name"
                      />
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
            </div>

            <div>
              <div class="text-caption text-grey-7 q-mb-xs">Groups</div>
              <q-select
                v-model="teamMember.groups"
                :options="groupOptions"
                option-label="name"
                @update:model-value="phishStore.updateEmployeeGroups(
                  teamMember.pk, $event.map(g => g.name)
                )"
                multiple
                outlined
                dense
                use-chips
                new-value-mode="add-unique"
              >
                <template v-slot:selected-item="scope">
                  <q-chip
                    removable
                    @remove="scope.removeAtIndex(scope.index)"
                    :tabindex="scope.tabindex"
                    :color="scope.opt.color"
                    size="sm"
                  >
                    {{ scope.opt.name }}
                  </q-chip>
                </template>
              </q-select>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Statistics cards -->
      <div class="col-xs-12 col-sm-6 col-md-8">
        <div class="row q-col-gutter-md">
          <div class="col-xs-6 col-sm-6 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-caption text-grey-7">Organic Reports</div>
                <div class="text-h5 text-primary">{{ organicReports().length }}</div>
                <div class="text-caption">Total reports made</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-xs-6 col-sm-6 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-caption text-grey-7">Synthetic Phishes</div>
                <div class="text-h5 text-orange">{{ phishAssignmentsReported }} / {{ phishAssignments().length }}</div>
                <div class="text-caption">Reported / Received</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-xs-6 col-sm-6 col-md-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-caption text-grey-7">Educational Resources</div>
                <div class="text-h5 text-green">{{ trainingAssignmentsCompleted }} / {{ trainingAssignments().length }}</div>
                <div class="text-caption">Completed / Assigned</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs for detailed views -->
    <q-card flat bordered>
      <q-tabs
        v-model="activeTab"
        dense
        class="text-grey"
        active-color="primary"
        indicator-color="primary"
        align="left"
      >
        <q-tab name="organic" label="Organic Reports" />
        <q-tab name="synthetic" label="Synthetic Phishes" />
        <q-tab name="resources" label="Educational Resources" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="activeTab" animated>
        <!-- Organic Reports Tab -->
        <q-tab-panel name="organic">
          <div class="text-h6 q-mb-md">Organic Reports</div>
          
          <q-table
            :rows="organicReports()"
            :columns="organicReportColumns"
            row-key="pk"
            flat
            :pagination="{ rowsPerPage: 10 }"
          >
            <template v-slot:body-cell-created_at="props">
              <q-td :props="props">
                {{ formatDate(props.value) }}
              </q-td>
            </template>

            <template v-slot:body-cell-status="props">
              <q-td :props="props">
                <q-badge 
                  class="text-body2"  
                  :label="(() => {
                    switch (props.value) {
                      case 'reported':
                        return 'Pending Review'
                      case 'phish':
                        return 'Confirmed Phish'
                      case 'not_phish':
                        return 'Valid Email'
                      case 'training':
                        return 'Training Needed'
                      default:
                        return 'Unknown'
                    }
                  })()"
                  :color="(() => {
                    switch (props.value) {
                      case 'reported':
                        return 'grey'
                      case 'phish':
                        return 'negative'
                      case 'not_phish':
                        return 'positive'
                      case 'training':
                        return 'warning'
                      default:
                        return 'grey'
                    }
                  })()"
                  :text-color="(() => {
                    switch (props.value) {
                      case 'reported':
                        return 'black'
                      case 'phish':
                        return 'white'
                      case 'not_phish':
                        return 'black'
                      case 'training':
                        return 'black'
                      default:
                        return 'black'
                    }
                  })()"
                />
              </q-td>
            </template>
            
            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn 
                  flat 
                  dense 
                  round 
                  icon="visibility" 
                  @click="viewReportDetails(props.row)"
                >
                  <q-tooltip>View Details</q-tooltip>
                </q-btn>
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <!-- Synthetic Phishes Tab -->
        <q-tab-panel name="synthetic">
          <div class="text-h6 q-mb-md">Synthetic Phishing Tests</div>
          
          <!-- Send New Synthetic Phish -->
          <q-card flat bordered class="q-mb-md">
            <q-card-section class="row items-center q-gutter-md">
              <div class="text-subtitle2">Send New:</div>
              <phish-template-select
                :label="'Select Template'"
                :read-only="false"
                @input="template => selectedPhishTemplate = template"
                style="width: 250px;"
              />
              <q-btn 
                label="Send Test Phish"
                color="primary"
                unelevated
                :disable="!selectedPhishTemplate"
                @click="createPhishAssignment()"
              />
            </q-card-section>
          </q-card>

          <!-- Synthetic Phishes Sent -->
          <q-table
            :rows="phishAssignments()"
            :columns="syntheticTestColumns"
            row-key="id"
            flat
            :pagination="{ rowsPerPage: 10 }"
          >
            <template v-slot:body-cell-clicked="props">
              <q-td :props="props">
                <q-icon 
                  :name="props.value ? 'check_circle' : 'cancel'" 
                  :color="props.value ? 'positive' : 'negative'"
                  size="sm"
                />
              </q-td>
            </template>  
            <template v-slot:body-cell-reported="props">
              <q-td :props="props">
                <q-icon 
                  :name="props.value ? 'check_circle' : 'cancel'" 
                  :color="props.value ? 'positive' : 'negative'"
                  size="sm"
                />
              </q-td>
            </template>

            <template v-slot:body-cell-sentAt="props">
              <q-td :props="props">
                {{ formatDate(props.value) }}
              </q-td>
            </template>

            <template v-slot:body-cell-reportedAt="props">
              <q-td :props="props">
                {{ props.value ? formatDate(props.value) : '-' }}
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <!-- Educational Resources Tab -->
        <q-tab-panel name="resources">
          <div class="text-h6 q-mb-md">Educational Resources</div>
          
          <!-- Assign new Training  -->
          <q-card flat bordered class="q-mb-md">
            <q-card-section class="row items-center q-gutter-md">
              <div class="text-subtitle2">Assign New:</div>
              <training-template-select
                :label="'Select Training Module'"
                :read-only="false"
                @input="template => selectedTrainingTemplate = template"
                style="width: 250px;"
              />
              <q-btn 
                label="Assign Training"
                color="primary"
                unelevated
                :disable="!selectedTrainingTemplate"
                @click="createTrainingAssignment()"
              />
            </q-card-section>
          </q-card>

          <phish-training-assignments-table
            :training-assignments="trainingAssignments()"
            :admin="true"
            @reassign="reassignResource"
          />
        </q-tab-panel>
      </q-tab-panels>
    </q-card>

    <!-- Report details dialog -->
    <q-dialog v-model="showReportDialog">
      <q-card style="min-width: 50vw; max-width: 90vw;">
        <q-card-section class="row">
          <div class="col">
            <div class="text-h6">Report Details</div>
            <div class="text-subtitle2">
              Employee: {{ selectedReport?.employee?.name || '' }} — Submitted:
              {{ selectedReport?.created_at ? formatDate(selectedReport.created_at) : '' }}
            </div>
            <div
              v-if="selectedReport?.additional_info"
              class="text-body2 q-mt-sm"
            >
              <span class="text-bold">Message from User:</span>
              <span class="text-italic">"{{ selectedReport.additional_info }}"</span>
            </div>
          </div>
          <q-toggle
            class="col col-3"
            v-model="showRawJson"
            label="Show raw JSON"
            color="primary"
            dense
          />
        </q-card-section>

        <q-separator />

        <q-card-section>
          <!-- <div class="text-subtitle2 q-mb-sm">Report Type</div>
          <q-badge 
            :label="selectedReport?.organic ? 'Organic' : 'Synthetic'" 
            :color="selectedReport?.organic ? 'primary' : 'orange'"
          /> -->
          <phish-report-message-viewer
            :message="selectedReport?.message ?? null"
            :show-raw-json="showRawJson"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Close" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</q-page>
</template>

<script setup lang="ts">
import { ref, Ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import PhishReportMessageViewer from
  'src/components/phish/PhishReportMessageViewer.vue'
import PhishTemplateSelect from 'src/components/phish/PhishTemplateSelect.vue'
import TrainingTemplateSelect from 
  'src/components/phish/TrainingTemplateSelect.vue'
import PhishTrainingAssignmentsTable from 
  'src/components/phish/PhishTrainingAssignmentsTable.vue'
import { usePhishStore } from 'src/stores/phish'
import { usePeopleStore } from 'src/stores/people'
import {
  PhishReport, SyntheticPhishTemplate, TrainingTemplate, TrainingAssignment
} from 'src/types'
import { QTableProps } from 'quasar'

const router = useRouter()
const route = useRoute()
const phishStore = usePhishStore()
const peopleStore = usePeopleStore()

const loading = ref(false)
const activeTab = ref('organic')
const showReportDialog = ref(false)
const showRawJson = ref(false)
const selectedReport = ref<PhishReport | null>(null)
const selectedPhishTemplate = ref<SyntheticPhishTemplate | null>(null)
const selectedTrainingTemplate = ref<TrainingTemplate | null>(null)

const riskLevelOptions = ref([]) as Ref<{name: string, color: string}[]>
const groupOptions = ref([]) as Ref<{name: string, color: string}[]>

interface TeamMember {
  pk: number
  employeeName: string
  riskLevel: {name: string, color: string}
  groups: {name: string, color: string}[]
}

const teamMember = ref<TeamMember>({
  pk: Number(route.params.id),
  employeeName: 'Loading...',
  riskLevel: {name: '', color: ''},
  groups: [] as {name: string, color: string}[]
})

const organicReportColumns: QTableProps['columns'] = [
  {
    name: 'created_at',
    label: 'Date',
    field: 'created_at',
    align: 'left',
    sortable: true
  },
  {
    name: 'status',
    label: 'Status',
    field: 'status',
    align: 'center',
    sortable: true
  },
  {
    name: 'actions',
    label: 'Actions',
    field: '',
    align: 'center'
  }
]

const syntheticTestColumns: QTableProps['columns'] = [
  {
    name: 'testName',
    label: 'Test Name',
    field: 'template_name',
    align: 'left'
  },
  {
    name: 'sentAt',
    label: 'Sent Date',
    field: 'sent_at',
    align: 'left',
    sortable: true
  },
  {
    name: 'clicked',
    label: 'Clicked',
    field: 'clicked',
    align: 'center',
    sortable: true
  },
  {
    name: 'reported',
    label: 'Reported',
    field: 'reported_at',
    align: 'center',
    sortable: true
  },
  {
    name: 'reportedAt',
    label: 'Reported Date',
    field: 'reported_at',
    align: 'left'
  }
]

function organicReports() {
  return phishStore.phishReports[teamMember.value.pk] || []
}

function phishAssignments() {
  return phishStore.phishAssignments[teamMember.value.pk] || []
}

const phishAssignmentsReported = computed(() => 
  phishAssignments().filter(phish => phish.reported).length
)

function trainingAssignments() {
  return phishStore.trainingAssignments[teamMember.value.pk] || []
}

const trainingAssignmentsCompleted = computed(() =>
  trainingAssignments().filter(assignment => assignment.completed).length
)

function formatDate(date: Date | string): string {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function loadTeamMemberData() {
  loading.value = true
  try {
    const employeePk = Number(route.params.pk)
    
    peopleStore.getSimpleEmployeeDetail({pk: employeePk}).then(member => {
      teamMember.value = {
        pk: member.pk,
        employeeName: member.name,
        riskLevel: {name: '', color: ''},
        groups: []
      }
    })

    // Load employee phish data
    await phishStore.getPhishDataForEmployee(employeePk).then(data => {
      riskLevelOptions.value = data.org_risk_profiles.map(
        profile => ({ name: profile.name, color: profile.color })
      )
      groupOptions.value = data.org_groups.map(
        group => ({ name: group.name, color: group.color })
      )
      teamMember.value.riskLevel =
        data.risk_profiles[0] || {name: '', color: ''}
      teamMember.value.groups = data.groups.map(
        group => ({name: group.name, color: group.color})
      )
    })

    // Load all reports for this employee
    await phishStore.getReportsForEmployee(employeePk)
    await phishStore.getPhishAssignmentsForEmployee(employeePk)
    await phishStore.getTrainingAssignmentsForEmployee(employeePk)
    
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/phish/admin/team')
}

function viewReportDetails(report: PhishReport) {
  selectedReport.value = report
  showRawJson.value = false
  showReportDialog.value = true
}

function reassignResource(assignment: TrainingAssignment) {
  console.log('Reassigning training:', assignment)
  // TODO: API call to mark training reassigned
  // After API call succeeds, refresh the training assignments
  loadTeamMemberData()
}

function createPhishAssignment() {
  if (!selectedPhishTemplate.value) {
    console.error('No template selected for synthetic phish')
    return
  }
  phishStore.createPhishAssignment(
    teamMember.value.pk, selectedPhishTemplate.value.pk
  )
    .then(() => {
      // Refresh synthetic tests list after sending
      loadTeamMemberData()
    })
    .catch((e) => {
      console.error('Error sending synthetic phish:', e)
    })
}

function createTrainingAssignment() {
  if (!selectedTrainingTemplate.value) {
    console.error('No template selected for training assignment')
    return
  }
  phishStore.createTrainingAssignment(
    teamMember.value.pk, selectedTrainingTemplate.value.pk
  )
    .then(() => {
      // Refresh educational resources list after assigning
      loadTeamMemberData()
    })
    .catch((e) => {
      console.error('Error assigning training:', e)
    })
}

onMounted(() => {
  loadTeamMemberData()
})
</script>
