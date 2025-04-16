<script setup lang="ts">
import Navlink from './Navlink.vue'
</script>

<template>
  <div class="w-full h-16 bg-white border-b border-gray-200">
    <div class="container h-full mx-auto flex items-center">
      <div class="text-2xl font-bold mr-20">得点板</div>

      <div class="flex gap-8">
        <Navlink to="/" name="Home" />

        <div class="flex gap-3">
          <div class="pr-3 border-r border-slate-800 text-slate-800">Admin</div>
          <Navlink to="/admin/archers" name="Archers" />
          <Navlink to="/admin/tournaments" name="Tournaments" />
        </div>
      </div>
    </div>
  </div>
</template>
