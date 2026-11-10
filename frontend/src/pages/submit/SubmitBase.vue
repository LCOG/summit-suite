<template>
<q-page class="q-pa-md">
  <div class="row items-center justify-between">
    <div class="q-my-md">
      <q-btn-group rounded>
        <q-btn
          :to="{ name: 'all-submissions' }"
          unelevated
          rounded
          color="primary"
          icon="book"
          :label="$q.screen.xs ? 'All' : 'All Submissions'"
        />
        <q-btn
          :to="{ name: 'all-approvals' }"
          unelevated
          rounded
          color="primary"
          icon="bookmark_added"
          :label="$q.screen.xs ? 'Approve' : 'All Approvals'"
        >
          <q-badge v-if="numToApprove()" rounded color="red" floating>
            {{ numToApprove() }}
          </q-badge>
        </q-btn>
      </q-btn-group>
      <q-btn-group rounded class="q-ml-sm">
        <q-btn
          :to="{ name: 'mileage-list' }"
          unelevated
          rounded
          color="primary"
          icon="airport_shuttle"
          label="Mileage Reimbursement"
        />
      </q-btn-group>
    </div>
    <q-icon
      name="help"
      color="primary"
      size=48px
      class="cursor-pointer"
      @click="showHelp = true"
    />
  </div>
  <div>
    <router-view />
  </div>
  <q-dialog v-model="showHelp">
    <q-card id="help-dialog">
      <q-card-section class="q-ma-lg">
        <div class="row items-center q-gutter-lg">
          <q-avatar
            icon="credit_card"
            size="60px"
            font-size="36px"
            color="primary"
            text-color="white"
          />
          <div class="text-h6">
            <div v-if="router.currentRoute.value.name == 'submit-expenses'">
              <div>1) Click "Get Started" to start a new month.</div>
              <div>2) Select a credit card statement from the dropdown.</div>
              <div>3) Enter expenses by clicking "New Expense".</div>
              <div>4) Once you're ready, click "Submit for Approval".</div>
            </div>
            <div
              v-else-if="router.currentRoute.value.name == 'approve-expenses'"
            >
              <div>1) Approve or deny all pending expenses.</div>
            </div>
            <div
              v-else-if="router.currentRoute.value.name?.toString()
                .indexOf('director-view-expenses') != -1"
            >
              <div>1) Approve or deny all pending expense months.</div>
              <div>Note: there may be multiple people using the same card!</div>
            </div>
            <div
              v-else-if="router.currentRoute.value.name?.toString()
                .indexOf('fiscal-approve-expenses') != -1"
            >
              <div>1) Each month, upload bank statements.</div>
              <div>2) Approve or deny all pending expense months.</div>
              <div>Note: there may be multiple people using the same card!</div>
            </div>
            <div class="row justify-center">
              <q-btn
                class="q-mt-sm"
                color="primary"
                @click="router.push({ name: 'help-cc-expenses' })"
              >
                More help
              </q-btn>
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</q-page>
</template>

<style lang="scss">
#help-dialog {
  max-width: 700px;
}

.submission-row {
  cursor: pointer;
}
</style>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { usePurchaseStore } from 'src/stores/purchase'
import { useRouter } from 'vue-router'

import { useSubmitStore } from 'src/stores/submit'

const purchaseStore = usePurchaseStore()
const submitStore = useSubmitStore()

const router = useRouter()

let showHelp = ref(false)

function numToApprove(): number {
  return submitStore.numToApprove
}

onMounted(() => {
  purchaseStore.initializeDates()
  purchaseStore.getExpenseMonthLocks()
})

</script>
