<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'

const route = useRoute()
</script>

<template>
  <div class="app w-full h-screen">
    <Navbar v-if="!route.name?.toString().includes('embed')" />

    <main
      v-if="!route.name?.toString().includes('embed')"
      class="container mx-auto flex flex-col p-4"
    >
      <RouterView />
    </main>
    <main v-else>
      <RouterView />
    </main>
  </div>
</template>
