<script lang="ts">
  import { defineComponent } from 'vue'

  export default defineComponent({
    name: 'App',
  })
</script>

<template>
  <v-app
    :class="{
      'hide-required-markers': $route.name === 'login',
    }"
  >
    <router-view />
  </v-app>
</template>

<style>
.v-input[required] .v-field-label::after,
.v-input:has([required]) .v-field-label::after {
  content: ' *';
  color: rgb(var(--v-theme-error));
}

.hide-required-markers .v-input[required] .v-field-label::after,
.hide-required-markers .v-input:has([required]) .v-field-label::after {
  content: none;
}
</style>