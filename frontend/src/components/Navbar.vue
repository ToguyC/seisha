<script setup lang="ts">
import { getTournament } from '@/api/tournament'
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Navlink from './Navlink.vue'

const route = useRoute()
const tournamentId = computed(() => {
  return route.name === 'singleTournament' && route.params.id ? (route.params.id as string) : null
})
const tournamentName = ref<string | null>(null)

watch(
  tournamentId,
  async (id) => {
    if (id) {
      try {
        const response = await getTournament(Number(id))
        tournamentName.value = response.data.name
      } catch (error) {
        console.error('Error fetching tournament:', error)
        tournamentName.value = null
      }
    }
  },
  { immediate: true },
)
</script>

<template>
  <div class="w-full h-16 bg-white border-b border-gray-200">
    <div class="container h-full mx-auto flex items-center">
      <a href="/" class="mr-10">
        <div class="flex justify-center items-center gap-4 text-lg font-bold">
          <img
            src="https://kapowaz.github.io/square-flags/flags/ch.svg"
            width="36"
            class="rounded"
          />
          <div class="leading-5 w-36">Swiss Kyudo Federation</div>
        </div>
      </a>

      <div class="flex gap-8 w-full">
        <div class="grow"></div>
        <div class="font-semibold text-2xl">得点板</div>
        <div class="grow"></div>
        <div class="flex gap-3">
          <div class="pr-3 border-r border-slate-800 text-slate-800">Admin</div>
          <Navlink to="/admin/archers" name="Archers" />
          <Navlink to="/admin/tournaments" name="Tournaments" />
        </div>
      </div>
    </div>
  </div>
</template>
