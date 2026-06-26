<template>
<q-page class="q-pa-md">
  <div class="text-h4 q-mb-md">Assignments</div>

  <q-card flat bordered>
    <q-tabs
      v-model="activeTab"
      dense
      class="text-grey"
      active-color="primary"
      indicator-color="primary"
      align="left"
    >
      <q-tab name="phish" label="Phish Assignments" />
      <q-tab name="training" label="Training Assignments" />
    </q-tabs>

    <q-separator />

    <q-tab-panels v-model="activeTab" animated>
      <q-tab-panel name="phish">
        <div class="text-h6 q-mb-md">Phish Assignments</div>
        <q-card flat bordered class="q-mb-md">
          <q-card-section class="row q-col-gutter-sm items-end">
            <div class="col-12 col-md-4">
              <q-select
                v-model="selectedPhishTemplate"
                :options="phishTemplateOptions"
                option-label="label"
                option-value="value"
                emit-value
                map-options
                label="Phish Template"
                outlined
                dense
              />
            </div>
            <div class="col-12 col-md-3">
              <q-select
                v-model="selectedPhishGroup"
                :options="groupOptions"
                option-label="name"
                option-value="name"
                emit-value
                map-options
                label="Phish Group"
                outlined
                dense
                clearable
                @update:model-value="onPhishGroupSelect"
              />
            </div>
            <div class="col-12 col-md-3">
              <q-select
                v-model="selectedPhishRiskProfile"
                :options="riskProfileOptions"
                option-label="name"
                option-value="name"
                emit-value
                map-options
                label="Risk Profile"
                outlined
                dense
                clearable
                @update:model-value="onPhishRiskSelect"
              />
            </div>
            <div class="col-12 col-md-2">
              <q-btn
                color="primary"
                label="Assign"
                class="full-width"
                :disable="disablePhishAssign"
                :loading="savingPhishAssignments"
                @click="assignPhishTemplate"
              />
            </div>
          </q-card-section>
        </q-card>

        <q-table
          :rows="phishTemplates"
          :columns="phishColumns"
          row-key="pk"
          flat
          :loading="loading"
          @row-click="(_, row) => selectedPhishTemplate = row.pk"
        >
          <template v-slot:body-cell-active="props">
            <q-td :props="props">
              <q-icon
                :name="props.value ? 'check_circle' : 'cancel'"
                :color="props.value ? 'positive' : 'negative'"
              />
            </q-td>
          </template>
        </q-table>
      </q-tab-panel>

      <q-tab-panel name="training">
        <div class="text-h6 q-mb-md">Training Assignments</div>
        <q-card flat bordered class="q-mb-md">
          <q-card-section class="row q-col-gutter-sm items-end">
            <div class="col-12 col-md-4">
              <q-select
                v-model="selectedTrainingTemplate"
                :options="trainingTemplateOptions"
                option-label="label"
                option-value="value"
                emit-value
                map-options
                label="Training Template"
                outlined
                dense
              />
            </div>
            <div class="col-12 col-md-3">
              <q-select
                v-model="selectedTrainingGroup"
                :options="groupOptions"
                option-label="name"
                option-value="name"
                emit-value
                map-options
                label="Phish Group"
                outlined
                dense
                clearable
                @update:model-value="onTrainingGroupSelect"
              />
            </div>
            <div class="col-12 col-md-3">
              <q-select
                v-model="selectedTrainingRiskProfile"
                :options="riskProfileOptions"
                option-label="name"
                option-value="name"
                emit-value
                map-options
                label="Risk Profile"
                outlined
                dense
                clearable
                @update:model-value="onTrainingRiskSelect"
              />
            </div>
            <div class="col-12 col-md-2">
              <q-btn
                color="primary"
                label="Assign"
                class="full-width"
                :disable="disableTrainingAssign"
                :loading="savingTrainingAssignments"
                @click="assignTrainingTemplate"
              />
            </div>
          </q-card-section>
        </q-card>

        <q-table
          :rows="trainingTemplates"
          :columns="trainingColumns"
          row-key="pk"
          flat
          :loading="loading"
          @row-click="(_, row) => selectedTrainingTemplate = row.pk"
        >
          <template v-slot:body-cell-active="props">
            <q-td :props="props">
              <q-icon
                :name="props.value ? 'check_circle' : 'cancel'"
                :color="props.value ? 'positive' : 'negative'"
              />
            </q-td>
          </template>
        </q-table>
      </q-tab-panel>
    </q-tab-panels>
  </q-card>
</q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { QTableProps, useQuasar } from 'quasar'

import { usePhishStore } from 'src/stores/phish'

const $q = useQuasar()
const phishStore = usePhishStore()

const activeTab = ref('phish')
const loading = ref(false)
const savingPhishAssignments = ref(false)
const savingTrainingAssignments = ref(false)

const selectedPhishTemplate = ref<number | null>(null)
const selectedTrainingTemplate = ref<number | null>(null)
const selectedPhishGroup = ref<string | null>(null)
const selectedPhishRiskProfile = ref<string | null>(null)
const selectedTrainingGroup = ref<string | null>(null)
const selectedTrainingRiskProfile = ref<string | null>(null)

const phishColumns: QTableProps['columns'] = [
  {
    name: 'name',
    label: 'Template Name',
    field: 'name',
    align: 'left',
    sortable: true
  },
  {
    name: 'version',
    label: 'Version',
    field: 'version',
    align: 'center',
    sortable: true
  },
  {
    name: 'difficulty',
    label: 'Difficulty',
    field: 'difficulty',
    align: 'center',
    sortable: true
  },
  {
    name: 'active',
    label: 'Active',
    field: 'active',
    align: 'center',
    sortable: true
  }
]

const trainingColumns: QTableProps['columns'] = [
  {
    name: 'name',
    label: 'Template Name',
    field: 'name',
    align: 'left',
    sortable: true
  },
  {
    name: 'version',
    label: 'Version',
    field: 'version',
    align: 'center',
    sortable: true
  },
  {
    name: 'active',
    label: 'Active',
    field: 'active',
    align: 'center',
    sortable: true
  }
]

const phishTemplates = computed(() => {
  return [...phishStore.phishTemplates].sort((a, b) => {
    if (a.name === b.name) {
      return b.version - a.version
    }
    return a.name.localeCompare(b.name)
  })
})

const trainingTemplates = computed(() => {
  return [...phishStore.trainingTemplates].sort((a, b) => {
    if (a.name === b.name) {
      return b.version - a.version
    }
    return a.name.localeCompare(b.name)
  })
})

const groupOptions = computed(() => {
  return [...phishStore.assignmentTargets.groups].sort((a, b) => {
    if (a.order === b.order) {
      return a.name.localeCompare(b.name)
    }
    return a.order - b.order
  })
})

const riskProfileOptions = computed(() => {
  return [...phishStore.assignmentTargets.riskProfiles].sort((a, b) => {
    if (a.order === b.order) {
      return a.name.localeCompare(b.name)
    }
    return a.order - b.order
  })
})

const phishTemplateOptions = computed(() => {
  return phishTemplates.value.map(template => ({
    label: `${ template.name } (v${ template.version })`,
    value: template.pk
  }))
})

const trainingTemplateOptions = computed(() => {
  return trainingTemplates.value.map(template => ({
    label: `${ template.name } (v${ template.version })`,
    value: template.pk
  }))
})

const disablePhishAssign = computed(() => {
  const hasTarget =
    !!selectedPhishGroup.value || !!selectedPhishRiskProfile.value
  const hasSingleTarget =
    !(selectedPhishGroup.value && selectedPhishRiskProfile.value)
  return !selectedPhishTemplate.value || !hasTarget || !hasSingleTarget
})

const disableTrainingAssign = computed(() => {
  const hasTarget = !!selectedTrainingGroup.value ||
    !!selectedTrainingRiskProfile.value
  const hasSingleTarget = !(
    selectedTrainingGroup.value && selectedTrainingRiskProfile.value
  )
  return !selectedTrainingTemplate.value || !hasTarget || !hasSingleTarget
})

function onPhishGroupSelect(value: string | null) {
  if (value) {
    selectedPhishRiskProfile.value = null
  }
}

function onPhishRiskSelect(value: string | null) {
  if (value) {
    selectedPhishGroup.value = null
  }
}

function onTrainingGroupSelect(value: string | null) {
  if (value) {
    selectedTrainingRiskProfile.value = null
  }
}

function onTrainingRiskSelect(value: string | null) {
  if (value) {
    selectedTrainingGroup.value = null
  }
}

async function loadPageData() {
  loading.value = true
  try {
    await Promise.all([
      phishStore.getPhishTemplates(),
      phishStore.getTrainingTemplates(),
      phishStore.getAssignmentTargets()
    ])
  } finally {
    loading.value = false
  }
}

async function assignPhishTemplate() {
  if (disablePhishAssign.value || !selectedPhishTemplate.value) {
    return
  }

  const targetType = selectedPhishGroup.value ? 'group' : 'risk_profile'
  const targetValue = selectedPhishGroup.value || selectedPhishRiskProfile.value
  if (!targetValue) {
    return
  }

  savingPhishAssignments.value = true
  try {
    const result = await phishStore.createPhishAssignmentsForTarget(
      selectedPhishTemplate.value,
      targetType,
      targetValue
    )
    $q.notify({
      type: 'positive',
      message: `Assigned phish template to ${ result.createdCount } employee(s)`
    })
  } finally {
    savingPhishAssignments.value = false
    selectedPhishTemplate.value = null
    selectedPhishGroup.value = null
    selectedPhishRiskProfile.value = null
  }
}

async function assignTrainingTemplate() {
  if (disableTrainingAssign.value || !selectedTrainingTemplate.value) {
    return
  }

  const targetType = selectedTrainingGroup.value ? 'group' : 'risk_profile'
  const targetValue = selectedTrainingGroup.value ||
    selectedTrainingRiskProfile.value
  if (!targetValue) {
    return
  }

  savingTrainingAssignments.value = true
  try {
    const result = await phishStore.createTrainingAssignmentsForTarget(
      selectedTrainingTemplate.value,
      targetType,
      targetValue
    )
    $q.notify({
      type: 'positive',
      message:
        `Assigned training template to ${ result.createdCount } employee(s)`
    })
  } finally {
    savingTrainingAssignments.value = false
    selectedTrainingTemplate.value = null
    selectedTrainingGroup.value = null
    selectedTrainingRiskProfile.value = null
  }
}

onMounted(() => {
  loadPageData()
})
</script>