<!-- Not converted from Quasar 1/Vue 2 -->
<template>
  <q-page class="q-pa-md">
    <div class="text-h4">Mileage Reimbursement</div>
    <div class="q-my-md">
      <q-btn-group rounded>
        <q-btn
          :to="{ name: 'mileage-reimbursement-create' }"
          unelevated
          rounded
          color="primary"
          icon="directions_car"
          label="Request Reimbursement"
        />
        <q-btn
          :to="{ name: 'mileage-reimbursement-list' }"
          unelevated
          rounded
          color="primary"
          icon="list"
          label="View Requests"
        />
      </q-btn-group>
    </div>
    <router-view :key="$route.path" />
  </q-page>
</template>

<script setup lang="ts">
</script>
