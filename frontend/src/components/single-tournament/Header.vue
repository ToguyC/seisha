<script setup lang="ts">
import type { Tournament } from '@/models/models'
import { ref } from 'vue'
import Modal from '../Modal.vue'
import { putTournament } from '@/api/tournament'

const { tournament } = defineProps<{
  tournament: Tournament
}>()

const emit = defineEmits<{
  fetchTournament: [tournamentId: number]
}>()

const showModal = ref(false)

const changeStatus = (status: string) => {
  const editedTournament = {
    ...tournament,
    status: status,
  }
  putTournament(editedTournament)
    .then(() => {
      emit('fetchTournament', tournament.id)
      showModal.value = false
    })
    .catch((error) => {
      console.error('Error updating tournament status:', error)
    })
}
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
          <td class="px-3 py-1 flex justify-between items-center">
            <div
              v-if="tournament.status === 'upcoming'"
              class="p-1 bg-orange-100 text-orange-700 font-semibold w-20 rounded-sm flex items-center justify-center gap-2 hover:bg-orange-200 hover:cursor-pointer"
              @click="showModal = true"
            >
              開催前
            </div>
            <div
              v-else-if="tournament.status === 'live'"
              class="p-1 bg-amaranth-500 text-white font-semibold w-20 rounded-sm flex items-center justify-center gap-2 hover:bg-amaranth-200 hover:cursor-pointer"
              @click="showModal = true"
            >
              <div class="w-2 h-2 rounded-full bg-white"></div>
              開催中
            </div>
            <div
              v-else-if="tournament.status === 'finished'"
              class="p-1 bg-wedgeblue-100 text-wedgeblue-700 font-semibold w-20 rounded-sm flex items-center justify-center hover:bg-wedgeblue-200 hover:cursor-pointer"
              @click="showModal = true"
            >
              終了
            </div>
            <div
              v-else-if="tournament.status === 'cancelled'"
              class="p-1 bg-red-100 text-red-700 font-semibold w-20 rounded-sm flex items-center justify-center hover:bg-red-200 hover:cursor-pointer"
              @click="showModal = true"
            >
              中止
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <Modal v-model="showModal" title="Change status">
      <div class="w-full flex justify-around items-center gap-4">
        <div
          class="w-1/2 flex justify-center items-center gap-4 bg-red-500 rounded-md text-white p-2 uppercase font-semibold hover:bg-red-700 hover:cursor-pointer"
          @click="changeStatus('live')"
          v-if="tournament.status === 'upcoming'"
        >
          <div class="w-4 h-4 rounded-full bg-white"></div>
          Go Live
        </div>
        <div
          class="w-1/2 flex justify-center items-center gap-4 text-white bg-wedgeblue-500 rounded-md p-2 hover:bg-wedgeblue-600 hover:cursor-pointer"
          @click="changeStatus('finished')"
          v-if="tournament.status === 'live'"
        >
          Finish the event
        </div>
        <div
          class="w-1/2 flex justify-center items-center gap-4 text-white bg-gray-500 rounded-md p-2 hover:bg-gray-700 hover:cursor-pointer"
          @click="changeStatus('upcoming')"
          v-if="tournament.status === 'finished' || tournament.status === 'cancelled'"
        >
          Reopen the tournament
        </div>
        <div
          class="w-1/2 flex justify-center items-center gap-4 text-red-500 rounded-md p-2 border border-red-500 hover:bg-red-100 hover:cursor-pointer"
          @click="changeStatus('cancelled')"
        >
          Cancel the tournament
        </div>
      </div>

      <template #footer>
        <div class="wf-full flex justify-between items-center gap-4">
          <button
            class="w-full px-4 py-2 text-sm text-gray-900 bg-white border border-gray-200 rounded hover:bg-gray-100 hover:cursor-pointer hover:text-blue-700"
            @click="showModal = false"
          >
            Discard
          </button>
        </div>
      </template>
    </Modal>
  </div>
</template>
