<script setup lang="ts">
import { RouterView } from 'vue-router'
import Navbar from './components/Navbar.vue';
</script>

<template>
  <div class="app w-full h-screen">
    <Navbar />

    <main>
      <RouterView />
    </main>
  </div>
</template>
