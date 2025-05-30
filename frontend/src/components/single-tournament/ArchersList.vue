<script setup lang="ts">
import { getAllArchers } from '@/api/archer'
import { deleteTournamentArcher, postTournamentArcher } from '@/api/tournament'
import type { Archer, TournamentWithRelations } from '@/models/models'
import { HashtagIcon, PlusIcon, TrashIcon } from '@heroicons/vue/16/solid'
import { ref, useTemplateRef } from 'vue'
import ArchersModal from './ArchersModal.vue'

const { tournament } = defineProps<{
  tournament: TournamentWithRelations
}>()

const emit = defineEmits<{
  fetchTournament: [tournamentId: number]
}>()

const archersList = ref<Archer[]>([])
const modalRef = useTemplateRef<InstanceType<typeof ArchersModal>>('modalRef')

const showModal = () => {
  modalRef.value?.show()
}

const deleteArcher = (archerId: number) => {
  deleteTournamentArcher(tournament.id, archerId)
    .then(() => {
      emit('fetchTournament', tournament.id)
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const fetchArchers = () => {
  getAllArchers()
    .then((res) => {
      archersList.value = res.data
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const addArcher = (archerId: number) => {
  postTournamentArcher(tournament.id, archerId)
    .then(() => {
      emit('fetchTournament', tournament.id)
    })
    .catch((err) => {
      console.error(err.message)
    })
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div class="text-xl font-bold text-gray-900 capitalize">Archers</div>
      <button
        class="w-20 flex items-center text-sm justify-center gap-4 px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 hover:cursor-pointer"
        @click="
          () => {
            fetchArchers()
            showModal()
          }
        "
      >
        <PlusIcon class="w-6 h-6" />
      </button>
    </div>

    <table class="w-full text-sm text-left rtl:text-right text-gray-500">
      <thead class="text-xs text-gray-500 uppercase bg-gray-50">
        <tr class="font-bold">
          <td class="px-6 py-3 flex gap-2">Number</td>
          <td class="px-6 py-3">Name</td>
          <td class="px-6 py-3"></td>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(archerWithNumber, index) in tournament.archers.sort(
            (a, b) => a.number - b.number,
          )"
          :key="index"
          class="bg-white border-b border-gray-200 hover:bg-gray-50 hover:cursor-pointer group"
        >
          <td class="px-6 py-2 text-center w-4 text-gray-900 whitespace-nowrap font-semibold">
            {{ archerWithNumber.number }}
          </td>
          <td scope="row" class="px-6 py-2 font-medium text-gray-900 whitespace-nowrap">
            {{ archerWithNumber.archer.name }}
          </td>
          <td
            class="p-1 text-right w-10 border-l border-gray-200 group-hover:bg-white"
            @click="$event.stopPropagation()"
          >
            <div class="w-full py-2 flex items-center justify-center gap-2 rounded text-red-700 bg-red-100 hover:bg-red-200">
              <TrashIcon
                class="w-4 h-4 rounded-sm"
                @click="() => deleteArcher(archerWithNumber.archer.id)"
              />
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <ArchersModal :tournament="tournament" @add-archer="addArcher" ref="modalRef" />
  </div>
</template>
