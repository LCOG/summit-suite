<template>
<div class="q-mt-md">
  <q-table
    flat bordered
    :title="tableTitleDisplay()"
    :rows="selectedMonthExpenses()"
    :columns="columns"
    :dense="$q.screen.lt.lg"
    :grid="$q.screen.lt.md"
    row-key="name"
    binary-state-sort
    :pagination="pagination"
    class="expense-table"
    no-data-label="No expenses entered this month"
  >
    <template v-slot:body="props">
      <q-tr
        :props="props"
        :class="expenseClass(props.row)"
      >
        <q-td
          key="name"
          :props="props"
          style="white-space: normal;"
          :class="!monthLocked() && !monthSubmitted() ? 'editable' : ''"
        >
          {{ props.row.name }}
          <q-popup-edit
            v-if="!monthLocked() && !monthSubmitted()"
            v-model="props.row.name"
            buttons
            v-slot="scope"
            @save="(val: string) =>
              updateExpense(props.row.pk, 'name', val)"
          >
            <q-input
              v-model="scope.value"
              maxlength="255"
              dense
              autofocus
              @keyup.enter="scope.set()"
            />
          </q-popup-edit>
        </q-td>
        <q-td
          key="date"
          :props="props"
          :class="!monthLocked() && !monthSubmitted() ? 'editable' : ''"
        >
          {{ readableDateNEW(props.row.date) }}
          <q-popup-edit
            v-if="!monthLocked() && !monthSubmitted()"
            v-model="props.row.date"
            buttons
            v-slot="scope"
            @save="(val: string) =>
              updateExpense(props.row.pk, 'date', val)"
          >
            <q-input
              type="date"
              v-model="scope.value"
              dense
              autofocus
              @keyup.enter="scope.set()"
            />
          </q-popup-edit>
        </q-td>
        <q-td
          key="vendor"
          :props="props"
          style="white-space: normal;"
          :class="!monthLocked() && !monthSubmitted() ? 'editable' : ''"
        >
          <div class="text-pre-wrap">{{ props.row.vendor }}</div>
          <q-popup-edit
            v-if="!monthLocked() && !monthSubmitted()"
            v-model="props.row.vendor"
            buttons
            v-slot="scope"
            @save="(val: string) =>
              updateExpense(props.row.pk, 'vendor', val)"
          >
            <q-input
              v-model="scope.value"
              maxlength="255"
              dense
              autofocus
              @keyup.enter="scope.set()"
            />
          </q-popup-edit>
        </q-td>
        <q-td
          key="amount"
          :props="props"
          :class="!monthLocked() && !monthSubmitted() ? 'editable' : ''"
        >
          {{ props.row.amount }}
          <q-popup-edit
            v-if="!monthLocked() && !monthSubmitted()"
            v-model="props.row.amount"
            buttons
            v-slot="scope"
            :validate="amountValidation"
            @update:model-value="(val: string) => {
              props.row.amount = cleanedAmount(val)
            }"
            @save="(val: string) => {
              updateExpense(props.row.pk, 'amount', cleanedAmount(val))
            }"
          >
            <div class="row items-center">
              <q-input
                v-model="scope.value"
                dense
                autofocus
                :error="errorAmount"
                :error-message="errorMessageAmount"
                @keyup.enter="scope.set()"
              />
            </div>
          </q-popup-edit>
        </q-td>
        <q-td
          key="gls"
          :props="props"
          :class="!monthLocked() && !monthSubmitted() ? 'editable' : ''"
        >
          <div
            class="text-pre-wrap"
            v-for="gl in props.row.gls"
            :key="props.row.gls.indexOf(gl)"
          >
            <span>{{ gl.code }} (Job: {{ gl.job }}</span>
            <span v-if="gl.activity">, Activity: {{ gl.activity }}</span>
            <span>): ${{ gl.amount }} – {{ gl.approver?.name }}</span>
          </div>
          <q-popup-edit
            v-if="!monthLocked() && !monthSubmitted()"
            v-model="props.row.gls"
            buttons
            persistent
            v-slot="scope"
            :validate="GLValidation"
            @save="(val: Array<GL>) => {
              updateExpense(props.row.pk, 'gls', cleanedGLs(val))
            }"
          >
            <div class="gl-popup-edit">
              <div
                v-for="(gl, idx) in scope.value"
                :key="scope.value.indexOf(gl)"
                class="row items-center"
              >
                <q-input
                  v-model="gl.code"
                  class="q-mr-sm q-pa-none"
                  outlined dense autofocus
                  mask="###-##-####-#####"
                  fill-mask="___-__-____-_____"
                  :rules="[
                    (val: string) => !!val || 'Required',
                  ]"
                />
                <q-input
                  v-model="gl.job"
                  label="Job #" stack-label
                  class="q-mr-sm q-pa-none"
                  outlined dense
                  :rules="[
                    (val: string) => !!val || 'Required or \'None\'',
                  ]"
                />
                <q-input
                  v-model="gl.activity"
                  label="Activity #" stack-label
                  class="q-mr-sm q-pa-none"
                  outlined dense
                  maxlength="7"
                />
                <div class="row q-mr-sm">
                  <div class="gl-dollar-symbol">$</div>
                  <q-input
                    v-model="gl.amount"
                    class="gl-amount q-pa-none"
                    outlined
                    dense
                    :error="errorAmount"
                    :error-message="errorMessageAmount"
                    @keyup.enter="scope.set()"
                    :rules="[
                      (val: string) => !!val || '* Required',
                    ]"
                  />
                </div>
                <EmployeeSelect
                  name="approver"
                  label="Approver"
                  :employee="gl.approver"
                  :useLegalName="true"
                  v-on:input="gl.approver=$event"
                  v-on:clear="gl.approver=emptyEmployee"
                  :readOnly=false
                  :employeeFilterFn="
                    (employee: SimpleEmployeeRetrieve) => {
                      if (employee.is_executive_director) {
                        return employee.is_expense_approver
                      } else {
                        return employee.is_expense_approver &&
                          employee.pk != userStore.profile.employee_pk
                      }
                    }
                  "
                />
                <q-icon
                  name="cancel"
                  size="sm"
                  @click.stop="scope.value.splice(idx, 1)"
                  class="cursor-pointer q-ml-sm"
                />
              </div>
              <div class="row justify-center q-mt-sm">
                <q-btn class="col-6" @click="scope.value.push({
                  code: '', job: '', activity: '', amount: '',
                  approver: emptyEmployee
                })">
                  Add a GL
                </q-btn>
              </div>
            </div>
          </q-popup-edit>
        </q-td>
        <q-td key="receipt" :props="props">
          <div class="row justify-center">
            <DocumentViewer
              v-if="props.row.receipt"
              :documentUrl="props.row.receipt"
              iconButton
              dense
              flat
            />
            <!-- Button to upload file -->
            <q-btn icon="cloud_upload"
              dense
              flat
              :disable="monthLocked() || monthSubmitted()"
            >
              <q-popup-edit
                v-if="!monthSubmitted()"
                v-model="props.row.receipt"
                buttons
                v-slot="scope"
              >
                <FileUploader
                  :file="scope.value"
                  contentTypeAppLabel="purchases"
                  contentTypeModel="expense"
                  :readOnly=false
                  :objectPk="props.row.pk.toString()"
                  allowedFileTypes="image/jpeg,image/png,.pdf"
                  v-on="{
                    'uploaded': (url: string) => {
                      uploadedReceipt(props.row.pk)
                    }
                  }"
                />
                <div class="q-mt-sm">
                  Supported filetypes: JPEG, PNG, PDF
                </div>
              </q-popup-edit>
            </q-btn>
          </div>
        </q-td>
        <q-td key="actions" :props="props">
          <q-btn
            v-if="!monthSubmitted()"
            class="col"
            dense
            flat
            @click="updateExpense(
              props.row.pk, 'repeat', !props.row.repeat
            )"
            :icon="props.row.repeat ? 'repeat_on' : 'repeat'"
          >
            <q-tooltip>
              <div v-if="props.row.repeat">
                Expense will repeat next month
              </div>
              <div v-else>Click to repeat expense next month</div>
            </q-tooltip>
          </q-btn>
          <q-btn
            :disable="monthLocked() || monthSubmitted()"
            class="col"
            dense
            flat
            @click="showDeleteDialog(props.row)"
            icon="delete"
          />
        </q-td>
      </q-tr>
    </template>
    <!-- GRID MODE -->
    <template v-slot:item="props">
      <div class="q-pa-xs col-xs-12 col-sm-6 col-md-4 col-lg-3">
        <q-card
          class="q-py-sm"
          :class="monthSubmitted()?'bg-grey':'cursor-pointer'"
        >
          <q-list dense>
            <q-item v-for="col in props.cols" :key="col.name">
              <div class="q-table__grid-item-row">
                <div class="q-table__grid-item-title">
                  {{ col.label }}
                </div>
                <div
                  class="q-table__grid-item-value"
                  v-if="col.name == 'date'"
                >
                  {{ readableDateNEW(col.value) }}
                </div>
                <div
                  class="q-table__grid-item-value"
                  v-else-if="col.name == 'gls'"
                >
                  <div
                    class="text-pre-wrap"
                    v-for="gl in props.row.gls"
                    :key="props.row.gls.indexOf(gl)"
                  >
                    <span>{{ gl.code }} (Job: {{ gl.job }}</span>
                    <span v-if="gl.activity">, Activity: {{ gl.activity }}</span>
                    <span>): ${{ gl.amount }} –</span>
                    {{ gl.approver?.name }}
                  </div>
                </div>
                <div
                  class="q-table__grid-item-value row"
                  v-else-if="col.name == 'receipt'"
                >
                  <DocumentViewer
                    v-if="col.value"
                    :documentUrl="col.value"
                    iconButton
                    flat
                  />
                  <!-- Button to upload file -->
                  <q-btn icon="cloud_upload"
                    flat
                    :disable="monthLocked() || monthSubmitted()"
                  >
                    <q-popup-edit
                      v-if="!monthSubmitted()"
                      v-model="props.row.receipt"
                      buttons
                      v-slot="scope"
                    >
                      <FileUploader
                        :file="scope.value"
                        contentTypeAppLabel="purchases"
                        contentTypeModel="expense"
                        :readOnly=false
                        :objectPk="props.row.pk.toString()"
                        allowedFileTypes="image/jpeg,image/png,.pdf"
                        v-on="{
                          'uploaded': (url: string) => {
                            retrieveAllMyExpenses()
                          }
                        }"
                      />
                      <div class="q-mt-sm">
                        Supported filetypes: JPEG, PNG, PDF
                      </div>
                    </q-popup-edit>
                  </q-btn>
                </div>
                <div
                  class="q-table__grid-item-value row"
                  v-else-if="col.name == 'actions'"
                >
                <q-btn
                  v-if="!monthSubmitted()"
                  class="col"
                  flat
                  @click="updateExpense(
                    props.row.pk, 'repeat', !props.row.repeat
                  )"
                  :icon="props.row.repeat ? 'repeat_on' : 'repeat'"
                >
                  <q-tooltip>
                    <div v-if="props.row.repeat">
                      Expense will repeat next month
                    </div>
                    <div v-else>Click to repeat expense next month</div>
                  </q-tooltip>
                </q-btn>
                <q-btn
                  :disable="monthLocked() || monthSubmitted()"
                  class="col"
                  flat
                  @click="showDeleteDialog(props.row)"
                  icon="delete"
                />
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
  </q-table>
</div>
</template>

<style scoped lang="scss">

</style>

<script setup lang="ts">
import { onMounted, Ref, ref, watch } from 'vue'
import { useQuasar } from 'quasar'

import DocumentViewer from 'src/components/DocumentViewer.vue'
import EmployeeSelect from 'src/components/EmployeeSelect.vue'
import FileUploader from 'src/components/FileUploader.vue'
import { readableDateNEW, readableDateTime } from 'src/filters'
import { handlePromiseError } from 'src/stores'
import { usePurchaseStore } from 'src/stores/purchase'
import { useUserStore } from 'src/stores/user'
import {
  emptyEmployee, Expense, ExpenseMonth, ExpenseStatement, GL,
  SimpleEmployeeRetrieve
} from 'src/types'

const quasar = useQuasar()
const purchaseStore = usePurchaseStore()
const userStore = useUserStore()

let thisMonthLoaded = ref(false)
let allExpensesLoaded = ref(false)
// SelectedMonth is a q-select option, so it has a label and a value.
let selectedMonth = ref(null) as
  Ref<{label: string, value: ExpenseMonth} | null>

// SelectedStatement is a q-select option, so it has a label and a value.
let selectedStatement = ref(null) as
  Ref<{label: string, value: ExpenseStatement} | null>

let showErrorsDialog = ref(false)
let showSubmitDialog = ref(false)
let submitterNote = ref('')
let showUnsubmitDialog = ref(false)
let showAddExpenseMonthDialog = ref(false)

let deleteDialogVisible = ref(false)
let expensePkToDelete = ref(-1)
let deleteDialogExpenseName = ref('')
let deleteDialogExpenseDate = ref('')

let errorAmount = ref(false)
let errorMessageAmount = ref('')

function viewingThisMonth() {
  return purchaseStore.firstOfSelectedMonth.getTime() ===
    purchaseStore.firstOfThisMonth.getTime()
}

function expensesLoaded() {
  return (viewingThisMonth() && thisMonthLoaded.value) ||
    allExpensesLoaded.value
}

const pagination = {
  rowsPerPage: 50
}

const columns = [
  {
    name: 'name', field: 'name', label: 'Item', required: true, align: 'left',
    sortable: true
  },
  {
    name: 'date', field: 'date', label: 'Date', align: 'center', sortable: true
  },
  {
    name: 'vendor', field: 'vendor', label: 'Vendor', align: 'center',
    sortable: true
  },
  { name: 'amount', field: 'amount', label: 'Amount', align: 'center' },
  {
    name: 'gls', field: 'gls', label: 'GL Codes – Approver', align: 'center',
    sortable: true, style: 'width: 10px'
  },
  { name: 'receipt', field: 'receipt', label: 'Receipt', align: 'center' },
  { name: 'actions', label: 'Actions', align: 'center', field: '' },
]


function tableTitleDisplay(): string {
  let statusText = 'Draft'
  if (purchaseStore.selectedExpenseMonth?.status == 'fiscal_approved') {
    statusText = 'Fiscal Approved - You\'re All Set!'
  } else if (purchaseStore.selectedExpenseMonth?.status == 'fiscal_denied') {
    statusText = 'Fiscal Denied - Correct and Resubmit'
  } else if (
    purchaseStore.selectedExpenseMonth?.status == 'approver_approved'
  ) {
    statusText = 'Approver(s) Approved - Waiting on Fiscal'
  } else if (purchaseStore.selectedExpenseMonth?.status == 'approver_denied') {
    statusText = 'Approver(s) Denied - Correct and Resubmit'
  } else if (purchaseStore.selectedExpenseMonth?.status == 'submitted') {
    statusText = 'Submitted - Waiting on Approver(s)'
  }
  return `${ purchaseStore.monthDisplay } - ${ statusText }`
}

function selectedMonthExpenses(): Expense[] {
  const month = purchaseStore.selectedExpenseMonth
  if (month !== undefined) {
    return month.expenses
  } else {
    return []
  }
}

function selectedMonthStatementsLoaded() {
  return purchaseStore.expenseStatements[purchaseStore.yearInt] &&
    purchaseStore.expenseStatements[purchaseStore.yearInt]
    [purchaseStore.monthInt]
}

function selectedMonthNotes(): Array<{
  type: string, approver: string, date: string, expense?: string, note: string
}> {
  let notes = []
  let em = purchaseStore.selectedExpenseMonth
  if (!em) {
    return []
  }
  let fiscalNote = em?.fiscal_note
  let date = em ? readableDateTime(em?.fiscal_approved_at) : ''
  if (fiscalNote) {
    notes.push({
      type: 'fiscal',
      approver: em.fiscal_approver.name,
      date,
      note: fiscalNote
    })
  }
  for (let exp of selectedMonthExpenses()) {
    for (let gl of exp.gls) {
      let date = readableDateTime(gl.approved_at)
      if (gl.approver && gl.approved_at && !gl.approved) {
        notes.push({
          type: 'approver',
          approver: gl.approver.name,
          date,
          expense: exp.name,
          note: gl.approver_note
        })
      }
    }
  }
  return notes
}

function largeExpense() {
  return selectedMonthExpenses().some(exp => parseFloat(exp.amount) >= 1000)
}

function expensesTotal() {
  return selectedMonthExpenses().reduce(
    (acc, exp) => {
      const amt = exp.amount ? parseFloat(exp.amount) : 0
      return acc + amt
    },
    0
  ).toFixed(2)
}

function selectedStatementTotal() {
  if (!selectedStatement.value) {
    return 0
  }
  return selectedStatement?.value.value.items.reduce(
    (acc, item) => acc + parseFloat(item.amount), 0
  ).toFixed(2)
}

function totalsMatch() {
  return selectedStatementTotal() == expensesTotal()
}

function numExpensesMatch() {
  if (!selectedStatement.value) {
    return true
  }
  return selectedStatement?.value.value.items.length ==
    selectedMonthExpenses().length
}

function expensesMatchStatment(): boolean {
  return numExpensesMatch() && totalsMatch()
}

function monthSubmitted() {
  const em = purchaseStore.selectedExpenseMonth
  if (!em) return false
  return em.status !== 'draft'
}

function expenseApproved(expense: Expense) {
  return expense.status === 'approver_approved'
}

function expenseDenied(expense: Expense) {
  return expense.status === 'approver_denied'
}

function monthApproved() {
  return purchaseStore.selectedExpenseMonth?.status === 'fiscal_approved'
}

function monthDenied() {
  return purchaseStore.selectedExpenseMonth?.status === 'fiscal_denied' ||
    purchaseStore.selectedExpenseMonth?.status === 'director_denied'
}

function expenseClass(expense: Expense) {
  if (!expense) {
    return ''
  }
  if (monthApproved()) {
    return 'bg-green'
  } else if (monthDenied() || expenseDenied(expense)) {
    return 'bg-red'
  } else if (expenseApproved(expense) || monthSubmitted()) {
    return 'bg-grey'
  } else {
    return 'cursor-pointer'
  }
}

function clickAddExpense(): void {
  if (!purchaseStore.selectedExpenseMonth) return
  purchaseStore.createExpense({
    em_pk: purchaseStore.selectedExpenseMonth.pk,
    name: '',
    date: `${ purchaseStore.yearInt }-${ purchaseStore.monthInt }-` +
      `${ purchaseStore.dayInt }`,
    gls: [],
  })
    .then(() => {
      retrieveAllMyExpenses()
    })
    .catch((error) => {
      console.log('Error adding expense', error)
    })
}

function formErrorItems() {
  let errorItems: string[] = []
  for (let exp of selectedMonthExpenses()) {
    if (!exp.name) {
      errorItems.push(`Provide a name for the expense on ${exp.date}`)
    }
    if (!exp.amount || parseFloat(exp.amount) == 0) {
      errorItems.push(
        `Provide an amount for ${exp.name}`
      )
    }
    for (let gl of exp.gls) {
      // gl.code must be of format ###-##-####-#####
      if (!gl.code || !/^(\d{3}-\d{2}-\d{4}-\d{5})$/.test(gl.code)) {
        errorItems.push(
          `Provide a valid GL code for each GL row in ${exp.name}`
        )
      }
      if (!gl.job) {
        errorItems.push(
          `Provide a valid Job number for each GL row in ${exp.name} or enter 'None'`
        )
      }
      if (!gl.amount) {
        errorItems.push(
          `Provide a GL amount for each GL row in ${exp.name}`
        )
      }
      if (!gl.approver || gl.approver?.pk == -1) {
        errorItems.push(`Provide an approver for each GL row in ${exp.name}`)
      }
    }
    const GLsTotal = exp.gls.reduce(
      (acc, gl) => acc + parseFloat(gl.amount), 0
    )
    if (GLsTotal.toFixed(2) !== parseFloat(exp.amount).toFixed(2)) {
      errorItems.push(`GLs for ${exp.name} must add to ${exp.amount}`)
    }
    if (!exp.receipt) {
      errorItems.push(
        `Provide a receipt or appropriate documentation for ${exp.name}`
      )
    }
  }
  return errorItems
}

function formErrors() {
  return formErrorItems().length > 0
}

function canUnsubmitMonth() {
  return monthSubmitted() && !monthApproved()
}

function monthLocked() {
  return purchaseStore.expenseMonthLocked
}

function onSubmitDialog() {
  if (monthLocked() || !purchaseStore.selectedExpenseMonth?.card) {
    return
  }
  purchaseStore.submitExpenseMonth({
    yearInt: purchaseStore.yearInt, monthInt: purchaseStore.monthInt,
    cardPK: purchaseStore.selectedExpenseMonth.card.pk,
    note: submitterNote.value
  })
    .then(() => {
      showSubmitDialog.value = false
      retrieveAllMyExpenses()
      quasar.notify({
        message: 'Sent',
        color: 'positive',
        icon: 'send'
      })
    })
    .catch((error) => {
      console.log('Error submitting expenses', error)
    })
}

function onUnsubmitDialog() {
  if (monthLocked() || !purchaseStore.selectedExpenseMonth?.card) {
    return
  }
  purchaseStore.submitExpenseMonth({
    yearInt: purchaseStore.yearInt, monthInt: purchaseStore.monthInt,
    cardPK: purchaseStore.selectedExpenseMonth.card.pk, unsubmit: true
  })
    .then(() => {
      showUnsubmitDialog.value = false
      retrieveAllMyExpenses()
      quasar.notify({
        message: 'Unsubmitted',
        color: 'positive',
        icon: 'cancel'
      })
    })
    .catch((error) => {
      console.log('Error unsubmitting expenses', error)
    })
}

function onAddExpenseMonthDialog() {
  if (monthLocked()) {
    return
  }
  createExpenseMonth()
    .then(() => {
      showAddExpenseMonthDialog.value = false
    })
    .catch((error) => {
      console.log('Error adding expense month', error)
    })
}

function retrieveRecentExpenseMonths(): Promise<void> {
  return new Promise((resolve, reject) => {
    purchaseStore.getExpenseMonths(
      purchaseStore.firstOfThisMonth.getFullYear(),
      purchaseStore.firstOfThisMonth.getMonth() + 1
    )
      .then(() => {
        thisMonthLoaded.value = true
        resolve()
      })
      .catch((error) => {
        handlePromiseError(reject, 'Error retrieving expenses', error)
        reject()
      })
  })
}

function retrieveAllMyExpenses(): Promise<void> {
  return new Promise((resolve, reject) => {
    purchaseStore.getExpenseMonths()
    .then(() => {
      purchaseStore.updateSelectedExpenseMonth()
      allExpensesLoaded.value = true
      resolve()
    })
    .catch((error) => {
      handlePromiseError(reject, 'Error retrieving expenses', error)
    })
  })
}

function thisMonthExpenseMonths(): Array<ExpenseMonth> {
  return purchaseStore.expenseMonths.filter(em => {
    return em.month === purchaseStore.monthInt &&
      em.year === purchaseStore.yearInt
  })
}

function createExpenseMonth(): Promise<ExpenseMonth> {
  if (monthLocked()) {
    return Promise.reject()
  }
  return new Promise ((resolve, reject) => {
    purchaseStore.createExpenseMonth({
      month: purchaseStore.monthInt,
      year: purchaseStore.yearInt
    })
      .then((em) => {
        retrieveAllMyExpenses().then(() => {
          updateSelectedEMStore(em.pk)
          selectedMonth.value = expenseMonthChoices().find(
            em => em.value.pk === purchaseStore.selectedExpenseMonth?.pk
          ) || null
          resolve(em)
        })
      })
      .catch((error) => {
        handlePromiseError(reject, 'Error creating expense month', error)
        reject()
      })
  })
}

function expenseMonthChoices(): Array<{label: string, value: ExpenseMonth}> {
  return thisMonthExpenseMonths().map(em => {
    return {
      label: em.card ? em.card.display : 'No card selected',
      value: em
    }
  })
}

function updateSelectedEMStore(pk?: number) {
  if (monthLocked()) {
    return
  }
  if (pk) {
    purchaseStore.setSelectedExpenseMonth(pk)
      .then(() => {
        setStatement()
        retrieveAllMyExpenses()
      })
  } else if (selectedMonth.value) {
    purchaseStore.setSelectedExpenseMonth(
      selectedMonth.value.value.pk
    ).then(() => {
      setStatement()
      retrieveAllMyExpenses()
    })
  }
}

function updateExpense(
  pk: number,
  field: 'name' | 'date' | 'vendor' | 'amount' | 'gls' | 'repeat',
  val: string | Array<GL> | boolean
) {
  if (monthLocked()) {
    return
  }
  const exp = purchaseStore.myExpenses.find(exp => exp.pk === pk)
  if (exp) {
    if (field === 'gls') {
      exp.gls = val as Array<GL>
    } else if (field === 'repeat') {
      exp.repeat = val as boolean
    } else {
      exp[field] = val as string
    }
    purchaseStore.updateExpense(exp)
      .catch((error) => {
        console.log('Error updating expense', error)
      })
  }
}

function uploadedReceipt(pk: number) {
  if (monthLocked()) {
    return
  }
  purchaseStore.clearExpenseGLApprovals(pk)
    .then(() => {
      retrieveAllMyExpenses()
    })
}

function showDeleteDialog(expense: Expense): void {
  expensePkToDelete.value = expense.pk
  deleteDialogExpenseName.value = expense.name
  deleteDialogExpenseDate.value = expense.date
  deleteDialogVisible.value = true
}

function deleteExpense(): void {
  if (monthLocked()) {
    return
  }
  purchaseStore.deleteExpense(expensePkToDelete.value)
    .then(() => {
      quasar.notify('Deleted an expense.')
      retrieveAllMyExpenses()
    })
    .catch(e => {
      console.error(e)
    })
}

function retrieveMonthStatements(year: number, month: number): Promise<void> {
  if (
    purchaseStore.expenseStatements[year] &&
    purchaseStore.expenseStatements[year][month]
  ) {
    return Promise.resolve()
  }
  return new Promise((resolve, reject) => {
    purchaseStore.getExpenseStatements(year, month)
      .then(() => {
        resolve()
      })
      .catch((error) => {
        handlePromiseError(reject, 'Error retrieving expense statements', error)
        reject()
      })
  })
}

function thisMonthStatements(): Array<ExpenseStatement> {
  return purchaseStore.expenseStatements[purchaseStore.yearInt] &&
    purchaseStore.expenseStatements[purchaseStore.yearInt]
    [purchaseStore.monthInt]
}

function statementChoices(): Array<{label: string, value: ExpenseStatement}> {
  return thisMonthStatements()?.map(es => {
    // Disable this statement choice if any other expenseMonthChoices have this
    // card selected
    let disable = false
    const cardPk = es.card.pk
    const isCardSelectedElsewhere = expenseMonthChoices().some(
      emChoice =>
      emChoice.value.card &&
      emChoice.value.card.pk === cardPk &&
      (!selectedMonth.value ||
        emChoice.value.pk !== selectedMonth.value.value.pk)
    )
    if (isCardSelectedElsewhere) {
      disable = true
    }
    return {
      label: es.card.display,
      value: es,
      disable
    }
  })
}

function updateSelectedStatement() {
  if (monthLocked()) {
    return
  }
  new Promise((resolve, reject) => {
    const em = purchaseStore.selectedExpenseMonth
    if (!em) {
      reject('Could not update statement because no expense month selected.')
    }
    if (em && selectedStatement.value) {
      purchaseStore.setExpenseMonthCard(
        em.pk, selectedStatement.value.value.card.pk
      ).then(() => {
        resolve(em)
      })
    }
  }).then(() => {
    retrieveAllMyExpenses()
  })
}

function statementSelected(): boolean {
  return selectedStatement.value !== null
}

function setStatement(): void {
  selectedStatement.value = statementChoices()?.find(
    sc => sc.value.card.pk === purchaseStore.selectedExpenseMonth?.card?.pk
  ) || null
}

function setDefaultMonthAndStatement() {
  purchaseStore.setDefaultSelectedExpenseMonth().then(() => {
    selectedMonth.value = expenseMonthChoices().find(
      em => em.value.pk === purchaseStore.selectedExpenseMonth?.pk
    ) || null
    setStatement()
  })
}

function cleanedAmount(val: string): string {
  let cleanedVal = val.replace(/[^0-9-.]/g, '')
  return parseFloat(cleanedVal).toFixed(2).toString()
}

function amountValidation (val: any) {
  if (isNaN(parseFloat(val))) {
    errorAmount.value = true
    errorMessageAmount.value = 'The value must be a number!'
    return false
  }
  errorAmount.value = false
  errorMessageAmount.value = ''
  return true
}

function cleanedGLs(val: Array<GL>) {
  for (let gl of val) {
    if (gl.amount) {
      gl.amount = cleanedAmount(gl.amount)
    }
  }
  return val
}

function GLValidation (val: any) {
  for (let gl of val) {
    if (isNaN(parseFloat(gl.amount))) {
      errorAmount.value = true
      errorMessageAmount.value = 'The value must be a number!'
      return false
    }
  }
  errorAmount.value = false
  errorMessageAmount.value = ''
  return true
}

onMounted(() => {
  retrieveRecentExpenseMonths().then(() => {
    retrieveAllMyExpenses()
    // Don't retrieve statements until we've gotten expenses
    // so we can set selected expense card.
    retrieveMonthStatements(
      purchaseStore.yearInt, purchaseStore.monthInt
    ).then(() => {
      setDefaultMonthAndStatement()
    })
  })
})

watch(() => purchaseStore.monthInt, (first, second) => {
  if (first !== second) {
    setDefaultMonthAndStatement()
  }
})

watch(() => purchaseStore.firstOfSelectedMonth, (newVal) => {
  if (viewingThisMonth()) return // Never do this on pageload
  const year = newVal.getFullYear()
  const month = newVal.getMonth()
  retrieveMonthStatements(year, month + 1).then(() => {
    setDefaultMonthAndStatement()
  })
})

</script>
