<script setup lang="ts">
import { RouterView } from 'vue-router'
import Navbar from './components/Navbar.vue';
</script>

<template>
  <div class="app w-full h-screen">
    <Navbar />

    <main class="container mx-auto flex flex-col p-4">
      <RouterView />
    </main>
  </div>
</template>
