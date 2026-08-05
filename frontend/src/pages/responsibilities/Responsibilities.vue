<template>
  <q-page class="q-pa-md">
    <div class="q-mb-md row justify-between q-gutter-y-sm">
      <div class="q-gutter-x-sm">
        <q-btn :to="{ name: 'all-responsibilities' }" unelevated rounded color="primary" icon="visibility" label="View All" />
        <q-btn :to="{ name: 'orphaned-responsibilities' }" unelevated rounded color="primary" icon="visibility_off" label="View Orphaned" />
        <q-btn :to="{ name: 'all-tags' }" unelevated rounded color="primary" icon="tag" label="View Tags" />
      </div>
      <div>
        <q-btn unelevated rounded color="primary" icon="add" label="Add" @click="addDialogVisible=true" />
      </div>
    </div>
    <router-view :key="$route.path" />

    <!-- ADD RESPONSIBILITY DIALOG -->
    <q-dialog v-model="addDialogVisible">
      <q-card>
        <q-card-section>
          <q-form
            @submit="onAddFormSubmit"
            @reset="clearAddForm"
            class="q-gutter-sm"
          >
            <div class="text-h5">Add a Responsibility</div>
            <q-input
              filled
              v-model="addFormName"
              label="Name"
            />
            <q-input
              filled
              v-model="addFormDescription"
              label="Description"
            />
            <q-input
              filled
              v-model="addFormLink"
              label="Link"
            />
            <div>Tags</div>
            <q-chip v-for="tag of addFormTags" :key="addFormTags.indexOf(tag)" removable @remove="addFormRemoveTag(addFormTags.indexOf(tag))" color="secondary" text-color="white">{{ tag.name }}</q-chip>
            <div class="row justify-between">
              <q-select :model-value="addFormNewTag" @input-value="setNewAddTagName" :options="tags()" option-value="pk" option-label="name" label="Add Tag" use-input hide-selected fill-input input-debounce="500" @filter="tagFilterFn">
                <template v-slot:no-option>
                  <q-item>
                    <q-item-section class="text-grey">
                      No results
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
              <q-btn label="Add" color="primary" :disable="!addFormNewTag" @click="addFormAddTag()"/>
            </div>
            <q-select v-model="addFormPrimaryEmployee" :options="employees()" option-value="pk" option-label="name" label="Primary Employee" use-input hide-selected fill-input input-debounce="500" @filter="filterFn">
              <template v-slot:no-option>
                <q-item>
                  <q-item-section class="text-grey">
                    No results
                  </q-item-section>
                </q-item>
              </template>
              <template v-if="addFormPrimaryEmployee.name" v-slot:append>
                <q-icon name="cancel" @click.stop="addFormPrimaryEmployee = emptyEmployee" class="cursor-pointer" />
              </template>
            </q-select>
            <q-select v-model="addFormSecondaryEmployee" :options="employees()" option-value="pk" option-label="name" label="Secondary Employee"  use-input hide-selected fill-input input-debounce="500" @filter="filterFn">
              <template v-slot:no-option>
                <q-item>
                  <q-item-section class="text-grey">
                    No results
                  </q-item-section>
                </q-item>
              </template>
              <template v-if="addFormSecondaryEmployee.name" v-slot:append>
                <q-icon name="cancel" @click.stop="addFormSecondaryEmployee = emptyEmployee" class="cursor-pointer" />
              </template>
            </q-select>
            <div>
              <q-btn label="Submit" type="submit" color="primary" :disable="!addFormName"/>
              <q-btn label="Reset" type="reset" color="primary" flat class="q-ml-sm" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- EDIT RESPONSIBILITY DIALOG -->
    <q-dialog v-model="editDialogVisible">
      <q-card>
        <q-card-section>
          <q-form
            @submit="onEditFormSubmit"
            class="q-gutter-sm"
          >
            <div class="text-h5">Edit Responsibility</div>
            <q-input
              filled
              v-model="editFormName"
              label="Name"
            />
            <q-input
              filled
              v-model="editFormDescription"
              label="Description"
            />
            <q-input
              filled
              v-model="editFormLink"
              label="Link"
            />
            <div>Tags</div>
            <q-chip v-for="tag of editFormTags" :key="editFormTags.indexOf(tag)" removable @remove="editFormRemoveTag(editFormTags.indexOf(tag))" color="secondary" text-color="white">{{ tag.name }}</q-chip>
            <div class="row justify-between">
              <q-select :model-value="editFormNewTag" @input-value="setNewEditTagName" :options="tags()" option-value="pk" option-label="name" label="Add Tag" use-input hide-selected fill-input input-debounce="500" @filter="tagFilterFn">
                <template v-slot:no-option>
                  <q-item>
                    <q-item-section class="text-grey">
                      No results
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
              <q-btn label="Add" color="primary" :disable="!editFormNewTag" @click="editFormAddTag()"/>
            </div>
            <q-select v-model="editFormPrimaryEmployee" :options="employees()" option-value="pk" option-label="name" label="Primary Employee" use-input hide-selected fill-input input-debounce="500" @filter="filterFn">
              <template v-slot:no-option>
                <q-item>
                  <q-item-section class="text-grey">
                    No results
                  </q-item-section>
                </q-item>
              </template>
              <template v-if="editFormPrimaryEmployee.name" v-slot:append>
                <q-icon name="cancel" @click.stop="editFormPrimaryEmployee = emptyEmployee" class="cursor-pointer" />
              </template>
            </q-select>
            <q-select v-model="editFormSecondaryEmployee" :options="employees()" option-value="pk" option-label="name" label="Secondary Employee"  use-input hide-selected fill-input input-debounce="500" @filter="filterFn">
              <template v-slot:no-option>
                <q-item>
                  <q-item-section class="text-grey">
                    No results
                  </q-item-section>
                </q-item>
              </template>
              <template v-if="editFormSecondaryEmployee.name" v-slot:append>
                <q-icon name="cancel" @click.stop="editFormSecondaryEmployee = emptyEmployee" class="cursor-pointer" />
              </template>
            </q-select>
            <div>
              <q-btn label="Submit" type="submit" color="primary" :disable="!editFormName"/>
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- DELETE RESPONSIBILITY DIALOG -->
    <q-dialog v-model="deleteDialogVisible">
      <q-card>
        <q-card-section>
          <div class="row items-center">
            <q-avatar icon="list" color="primary" text-color="white" />
            <span class="q-ml-sm">Are you sure you want to delete this responsibility?</span>
          </div>
          <div class="row justify-center text-center">{{ deleteDialogResponsibilityName }}</div>
        </q-card-section>

        <q-card-actions class="row justify-around">
          <q-btn flat label="Cancel" color="primary" v-close-popup />
          <q-btn flat label="Yes, delete it" color="primary" @click="deleteRow()" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- EDIT TAG DIALOG -->
    <q-dialog v-model="editTagDialogVisible">
      <q-card>
        <q-card-section>
          <q-form
            @submit="onTagEditFormSubmit"
            class="q-gutter-sm"
          >
            <div class="text-h5">Edit Tag</div>
            <q-input
              filled
              v-model="editTagFormName"
              label="Name"
            />
            <div>
              <q-btn label="Submit" type="submit" color="primary" :disable="!editTagFormName"/>
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- DELETE TAG DIALOG -->
    <q-dialog v-model="deleteTagDialogVisible">
      <q-card>
        <q-card-section>
          <div class="row items-center">
            <q-avatar icon="list" color="primary" text-color="white" />
            <span class="q-ml-sm">Are you sure you want to delete this tag?</span>
          </div>
          <div class="row justify-center text-center">{{ deleteTagDialogName }}</div>
        </q-card-section>

        <q-card-actions class="row justify-around">
          <q-btn flat label="Cancel" color="primary" v-close-popup />
          <q-btn flat label="Yes, delete it" color="primary" @click="deleteTag()" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref, Ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar, QSelect } from 'quasar'

import { getCurrentUser, getRoutePk } from 'src/utils'
import {
  Responsibility, ResponsibilityTagRetrieve, SimpleEmployeeRetrieve,
  SimpleResponsibilityTagRetrieve 
} from 'src/types'

import useEventBus from 'src/eventBus'
import { useResponsibilityStore } from 'src/stores/responsibility'
import { usePeopleStore } from 'src/stores/people'

const quasar = useQuasar()
const route = useRoute()
const router = useRouter()
const { bus } = useEventBus()
const responsibilityStore = useResponsibilityStore()
const peopleStore = usePeopleStore()

const emptyEmployee = {name: '', pk: -1}

let addDialogVisible = ref(false)
let addFormName = ref('')
let addFormDescription = ref('')
let addFormLink = ref('')
let addFormTags: Ref<Array<{'name': string}>> = ref([])
let addFormNewTag = ref('')
let addFormPrimaryEmployee = ref(emptyEmployee)
let addFormSecondaryEmployee = ref(emptyEmployee)

let editDialogVisible = ref(false)
let pkToEdit = ref(-1)
let editFormName = ref('')
let editFormDescription = ref('')
let editFormLink = ref('')
let editFormTags: Ref<Array<ResponsibilityTagRetrieve>> = ref([])
let editFormNewTag = ref('')
let editFormPrimaryEmployee = ref(emptyEmployee)
let editFormSecondaryEmployee = ref(emptyEmployee)

let deleteDialogVisible = ref(false)
let deleteDialogResponsibilityName = ref('')
let rowPkToDelete = ref('')

let editTagDialogVisible = ref(false)
let tagPkToEdit = ref(-1)
let editTagFormName = ref('')

let deleteTagDialogVisible = ref(false)
let deleteTagDialogName = ref('')
let tagPkToDelete = ref('')

let needle = ref('') // For filtering employee list
let tagNeedle = ref('') // For filtering tag list

///////////////
// EMPLOYEES //
///////////////
function employees(): Array<SimpleEmployeeRetrieve> {    
  const employees = peopleStore.simpleEmployeeList
  return employees.filter((employee) => {
    return employee.name.toLowerCase().indexOf(needle.value) != -1
  })
}

function retrieveSimpleEmployeeList(): void {
  peopleStore.getSimpleEmployeeList()
    .catch(e => {
      console.error('Error retrieving simple employee list', e)
    })
}

function filterFn (val: string, update: (callbackFn: () => void, afterFn?: (ref: QSelect) => void) => void) {
  update(() => {
    needle.value = val.toLowerCase()
  })
}

//////////
// TAGS //
//////////
function tags(): Array<SimpleResponsibilityTagRetrieve> {    
  const tags = responsibilityStore.simpleTagList
  return tags.filter((tag) => {
    return tag.name.toLowerCase().indexOf(tagNeedle.value) != -1
  })
}

function retrieveSimpleTagList(): void {
  responsibilityStore.getSimpleTagList()
}

function tagFilterFn (val: string, update: (callbackFn: () => void, afterFn?: (ref: QSelect) => void) => void) {
  update(() => {
    tagNeedle.value = val.toLowerCase()
  })
}

function setNewEditTagName(val: string) {
  editFormNewTag.value = val
}

//////////////
// ADD FORM //
//////////////
function setNewAddTagName(val: string) {
  addFormNewTag.value = val
}

function addFormAddTag(): void {
  addFormTags.value.push({'name': addFormNewTag.value})
  addFormNewTag.value = ''
}

function addFormRemoveTag(tagIndex: number): void {
  addFormTags.value.splice(tagIndex, 1)
}

function clearAddForm() {
  addFormName.value = ''
  addFormDescription.value = ''
  addFormLink.value = ''
  addFormNewTag.value = ''
  addFormTags.value = []
  addFormPrimaryEmployee.value = emptyEmployee
  addFormSecondaryEmployee.value = emptyEmployee
}

function onAddFormSubmit () {
  createResponsibility()
    .then(() => {
      updateResponsibiliyLists()
      retrieveSimpleTagList()
      addDialogVisible.value = false
      quasar.notify('Created responsibility')
      clearAddForm()
    })
    .catch(e => {
      console.error('Error creating Responsibility:', e)
    })
  }

function createResponsibility() {
  return new Promise((resolve, reject) => {
    responsibilityStore.createResponsibility({
      name: addFormName.value,
      description: addFormDescription.value,
      link: addFormLink.value,
      tags: addFormTags.value,
      primary_employee: addFormPrimaryEmployee.value.pk,
      secondary_employee: addFormSecondaryEmployee.value.pk
    })
      .then(() => {
        resolve('Created responsibility')
      })
      .catch(e => {
        console.error('Error creating Responsibility:', e)
        reject(e)
      })
  })
}

///////////////
// EDIT FORM //
///////////////

function openEditDialog(row: Responsibility) {
  pkToEdit.value = row.pk
  editFormName.value = row.name
  editFormDescription.value = row.description
  editFormLink.value = row.link
  editFormTags.value = row.tags
  if (row.primary_employee_pk && row.primary_employee_name) {
    editFormPrimaryEmployee.value = { pk: row.primary_employee_pk, name: row.primary_employee_name}
  }
  if (row.secondary_employee_pk && row.secondary_employee_name) {
    editFormSecondaryEmployee.value = { pk: row.secondary_employee_pk, name: row.secondary_employee_name}
  }
  editDialogVisible.value = true
}

function editFormAddTag(): void {
  let newTags = [...editFormTags.value]
  newTags.push({'name': editFormNewTag.value})
  editFormTags.value = newTags
  editFormNewTag.value = ''
}

function editFormRemoveTag(tagIndex: number): void {
  let newTags = [...editFormTags.value]
  newTags.splice(tagIndex, 1)
  editFormTags.value = newTags
}

function clearEditForm() {
  pkToEdit.value = -1
  editFormName.value = ''
  editFormDescription.value = ''
  editFormLink.value = ''
  editFormTags.value = []
  editFormNewTag.value = ''
  editFormPrimaryEmployee.value = emptyEmployee
  editFormSecondaryEmployee.value = emptyEmployee
}

function onEditFormSubmit () {
  editResponsibility()
    .then(() => {
      updateResponsibiliyLists()
      retrieveSimpleTagList()
      editDialogVisible.value = false
      quasar.notify('Updated responsibility')
      clearEditForm()
    })
    .catch(e => {
      console.error('Error updating Responsibility:', e)
    })
}

function editResponsibility() {
  return new Promise((resolve, reject) => {
    responsibilityStore.updateResponsibility(pkToEdit.value.toString(), {
      name: editFormName.value,
      description: editFormDescription.value,
      link: editFormLink.value,
      tags: editFormTags.value,
      primary_employee: editFormPrimaryEmployee.value.pk,
      secondary_employee: editFormSecondaryEmployee.value.pk
    })
      .then(() => {
        resolve('Updated')
      })
      .catch(e => {
        console.error('Error updating Responsibility:', e)
        reject(e)
      })
  })
}

////////////////////////////////
// DELETE RESPONSIBILITY FORM //
////////////////////////////////

function openDeleteDialog(row: Responsibility) {
  rowPkToDelete.value = row.pk.toString()
  deleteDialogResponsibilityName.value = row.name
  deleteDialogVisible.value = true
}

function deleteRow(): void {
  responsibilityStore.deleteResponsibility(rowPkToDelete.value)
    .then(() => {
      updateResponsibiliyLists()
      quasar.notify('Deleted a responsibility.')
    })
    .catch(e => {
      console.error('Error deleting responsibility', e)
    })
}

///////////////////
// EDIT TAG FORM //
///////////////////

function openTagEditDialog(tag: ResponsibilityTagRetrieve) {
  if (tag.pk) {
    tagPkToEdit.value = tag.pk
    editTagFormName.value = tag.name
    editTagDialogVisible.value = true
  }
}

function clearTagEditForm() {
  tagPkToEdit.value = -1
  editTagFormName.value = ''
}

function onTagEditFormSubmit () {
  editTag()
    .then(() => {
      updateTagLists()
      editTagDialogVisible.value = false
      quasar.notify('Updated tag')
      clearTagEditForm()
    })
    .catch(e => {
      console.error('Error updating Tag:', e)
    })
}

function editTag() {
  return new Promise((resolve, reject) => {
    responsibilityStore.updateTag(tagPkToEdit.value.toString(), {
      name: editTagFormName.value,
    })
      .then(() => {
        resolve('Updated')
      })
      .catch(e => {
        console.error('Error updating Tag:', e)
        reject(e)
      })
  })
}

/////////////////////
// DELETE TAG FORM //
/////////////////////

function openDeleteTagDialog(row: ResponsibilityTagRetrieve) {
  if (row.pk) {
    tagPkToDelete.value = row.pk.toString()
    deleteTagDialogName.value = row.name
    deleteTagDialogVisible.value = true
  }
}

function deleteTag(): void {
  responsibilityStore.deleteTag(tagPkToDelete.value)
    .then(() => {
      updateTagLists()
      quasar.notify('Deleted a tag.')
    })
    .catch(e => {
      console.error('Error deleting tag', e)
    })
}

///////////////
// SET STATE //
///////////////

// Update the various responsibility lists in Vuex
function updateResponsibiliyLists(): void {
  retrieveAllResponsibilites()
  retrieveOrphanedResponsibilites()
  const pk = getRoutePk(route)
  if (pk) {
    retrieveEmployeeResponsibilites(pk)
    retrieveEmployeeSecondaryResponsibilites(pk)
  }
}

// Update the various tag lists in Vuex
function updateTagLists(): void {
  retrieveAllTags()
  retrieveSimpleTagList()
}

// Update All Tags Table
function retrieveAllTags(): void {
  responsibilityStore.getAllTags()
    .catch(e => {
      console.error('Error retrieving tags', e)
    })
}

// Update All Responsibilities Table
function retrieveAllResponsibilites(): void {
  responsibilityStore.getAllResponsibilities()
    .catch(e => {
      console.error('Error retrieving responsibilities', e)
    })
}

// Update Orphaned Responsibilities Table
function retrieveOrphanedResponsibilites(): void {
  responsibilityStore.getOrphanedResponsibilities()
    .catch(e => {
      console.error('Error retrieving orphaned responsibilities', e)
    })
}

// Update Employee Responsibilities Table
function retrieveEmployeeResponsibilites(employeePk: string): void {
  responsibilityStore.getEmployeePrimaryResponsibilities({pk: employeePk})
    .catch(e => {
      console.error('Error retrieving employee responsibilities', e)
    })
}

// Update Employee Secondary Responsibilities Table
function retrieveEmployeeSecondaryResponsibilites(employeePk: string): void {
  responsibilityStore.getEmployeeSecondaryResponsibilities({pk: employeePk})
    .catch(e => {
      console.error('Error retrieving employee secondary responsibilities', e)
    })
}

// We trigger opening the edit and delete dialogs in AllResponsibilities,
// EmployeeResponsibilites, or OrphanedResponsibilities
watch(() => bus.value.get('emitOpenEditDialog'), (row: Responsibility) => {
  openEditDialog(row)
})
watch(() => bus.value.get('emitOpenDeleteDialog'), (row: Responsibility) => {
  openDeleteDialog(row)
})
watch(() => bus.value.get('emitOpenEditTagDialog'), (row: ResponsibilityTagRetrieve) => {
  openTagEditDialog(row)
})
watch(() => bus.value.get('emitOpenDeleteTagDialog'), (row: ResponsibilityTagRetrieve) => {
  openDeleteTagDialog(row)
})

onMounted(() => {
  getCurrentUser()
    .then(() => {
      if (!employees().length) {
        retrieveSimpleEmployeeList()
        retrieveSimpleTagList()
      }
    })
})
</script>
