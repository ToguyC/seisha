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
      <div class="text-2xl font-bold mr-20 w-20">得点板</div>

      <div class="flex gap-8 w-full">
        <Navlink to="/" name="Home" />

        <div class="grow"></div>
        <div v-if="tournamentId">
          <div class="bg-gray-300 text-gray-900 px-2 rounded-sm">
            Tournament : {{ tournamentName }}
          </div>
        </div>
        <div class="grow" v-if="tournamentId"></div>
        <div class="flex gap-3">
          <div class="pr-3 border-r border-slate-800 text-slate-800">Admin</div>
          <Navlink to="/admin/archers" name="Archers" />
          <Navlink to="/admin/tournaments" name="Tournaments" />
        </div>
      </div>
    </div>
  </div>
</template>
