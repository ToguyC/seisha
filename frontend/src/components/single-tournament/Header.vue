<script setup lang="ts">
import type { Tournament } from '@/models/models'

defineProps<{
  tournament: Tournament
}>()
</script>

<template>
  <div>
    <div class="flex flex-col w-full items-center justify-center mb-10">
      <div class="text-4xl font-bold">{{ tournament.name }}</div>
    </div>

    <table class="w-full">
      <tbody>
        <tr>
          <td class="w-40 font-semibold p-1 bg-gray-200 text-center">Start date</td>
          <td class="px-3">{{ new Date(tournament.start_date).toLocaleDateString() }}</td>
          <td class="w-40 font-semibold p-1 bg-gray-200 text-center">End date</td>
          <td class="px-3">{{ new Date(tournament.end_date).toLocaleDateString() }}</td>
          <td class="w-40 font-semibold p-1 bg-gray-200 text-center">Format</td>
          <td class="px-3">
            <div
              v-if="tournament.format === 'individual'"
              class="bg-emerald-100 text-emerald-700 font-semibold w-12 rounded-sm flex items-center justify-center"
            >
              個人
            </div>
            <div
              v-else
              class="bg-purple-100 text-purple-700 font-semibold w-16 rounded-sm flex items-center justify-center"
            >
              チーム
            </div>
          </td>
          <td class="w-40 font-semibold p-1 bg-gray-200 text-center">Status</td>
          <td class="px-3">
            <div
              v-if="tournament.status === 'upcoming'"
              class="bg-orange-100 text-orange-700 font-semibold w-20 rounded-sm flex items-center justify-center"
            >
              開催前
            </div>
            <div
              v-else-if="tournament.status === 'live'"
              class="bg-amaranth-500 text-white font-semibold w-20 rounded-sm flex items-center justify-center gap-2"
            >
              <div class="w-2 h-2 rounded-full bg-white"></div>
              開催中
            </div>
            <div
              v-else-if="tournament.status === 'finished'"
              class="bg-wedgeblue-100 text-wedgeblue-700 font-semibold w-20 rounded-sm flex items-center justify-center"
            >
              終了
            </div>
            <div
              v-else-if="tournament.status === 'cancelled'"
              class="bg-red-100 text-red-700 font-semibold w-20 rounded-sm flex items-center justify-center"
            >
              中止
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
