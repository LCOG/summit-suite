<template>
  <q-item
    clickable
    :to="link"
    :id="id"
  >
    <q-item-section
      v-if="icon"
      avatar
    >
      <q-icon :name="icon" />
    </q-item-section>

    <q-item-section>
      <q-item-label>{{ title }}</q-item-label>
    </q-item-section>
  </q-item>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'NavLink',
  props: {
    title: {
      type: String,
      required: true
    },
    link: {
      type: String,
      required: false,
      default: '#'
    },
    icon: {
      type: String,
      required: false,
      default: ''
    },
    id: {
      type: String,
      required: false
    }
  }
})
</script>
