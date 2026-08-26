<template>
  <div class="flex flex-center bg-grey-2" style="height: 100vh;">
    <div class="maintenance-container text-center q-pa-xl">
      <q-img
        :src="summitImg"
        alt="Maintenance Illustration"
        contain
        class="q-mb-md"
        style="max-width: 300px;"
      />
      <div class="text-h5 text-weight-bold q-mt-none q-mb-md text-negative">
        Oh no! You clicked a phishing link!
      </div>
      <p class="text-body1 q-mb-md">
        This message was sent by your organization to help you practice spotting
        suspicious emails. No harm done, but this is a good
        reminder to slow down and verify unexpected links before clicking.
      </p>
      <p class="text-body1 q-mb-none">
        If a message looks suspicious in the future, use the Report Phish
        button in Outlook so the security team can review it.
      </p>
    </div>
  </div>
</template>



<script lang="ts">
import { defineComponent } from 'vue'
import summitImg from 'src/assets/summit.png'

export default defineComponent({
  name: 'PhishClickedPage',
  setup() {
    
    return {
      summitImg
    }
  }
})
</script>

<style scoped>
.maintenance-container {
  max-width: 600px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
</style>