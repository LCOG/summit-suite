<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h4">Workflows</div>
      <q-icon
        name="help"
        color="primary"
        size=48px
        class="cursor-pointer"
        @click="router.push({ name: 'help-workflows' })"
      />
    </div>
    <router-view />
  </q-page>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

</script>
