<template>
  <q-page class="q-pa-md">
    <div class="text-h4">Mileage Reimbursement</div>
    <div class="q-my-md">
      <q-btn-group rounded>
        <q-btn
          :to="{ name: 'mileage-create' }"
          unelevated
          rounded
          color="primary"
          icon="directions_car"
          :label="$q.screen.xs ? 'Submit' : 'Request Reimbursement'"
        />
        <q-btn
          :to="{ name: 'mileage-list' }"
          unelevated
          rounded
          color="primary"
          icon="list"
          :label="$q.screen.xs ? 'List' : 'My Requests'"
        />
        <q-btn
          :to="{ name: 'mileage-approve' }"
          unelevated
          rounded
          color="primary"
          icon="check"
          :label="$q.screen.xs ? 'Approve' : 'Approve Requests'"
        >
          <q-badge v-if="numMileageToApprove()" rounded color="red" floating>
            {{ numMileageToApprove() }}
          </q-badge>
        </q-btn>
      </q-btn-group>
    </div>
    <router-view :key="$route.path" />
  </q-page>
</template>

<script setup lang="ts">
import { useSubmitStore } from 'src/stores/submit'

const submitStore = useSubmitStore()

function numMileageToApprove(): number {
  return submitStore.numMileageToApprove
}
</script>
