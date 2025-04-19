<script setup lang="ts">
import { ref } from 'vue'
import Modal from '../Modal.vue'
import type { Archer, TournamentWithRelations } from '@/models/models'
import { getAllArchers } from '@/api/archer'
import { HashtagIcon, UserIcon } from '@heroicons/vue/16/solid'

const { tournament } = defineProps<{
  tournament: TournamentWithRelations
}>()

const emit = defineEmits<{
  addArcher: [archerId: number]
}>()

const searchArcherName = ref('')
const showModal = ref(false)
const archersList = ref<Archer[]>([])

const show = () => {
  fetchArchers()
  showModal.value = true
}

const hide = () => {
  showModal.value = false
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

const filterArchers = (archers: Archer[], name: string) => {
  return archers.filter((archer) => {
    return archer.name.toLowerCase().includes(name.toLowerCase())
  })
}

const archerInTournament = (archerId: number) => {
  if (tournament.format === 'team') {
    return tournament.teams.some((team) =>
      team.archers.some((archerWithNumber) => archerWithNumber.archer.id === archerId),
    )
  }
  return tournament.archers.some((archerWithNumber) => archerWithNumber.archer.id === archerId)
}

defineExpose({
  show,
  hide,
})
</script>

<template>
  <Modal v-model="showModal" title="Register an archer">
    <form class="w-full flex flex-col items-center gap-5 pb-4 border-b border-gray-200 h-96">
      <div v-if="archersList.length == 0">loading</div>
      <div v-else class="w-full flex flex-col gap-6">
        <div class="w-full">
          <div class="relative">
            <div class="absolute inset-y-0 start-0 flex items-center ps-2.5 pointer-events-none">
              <UserIcon class="w-5 h-5 text-gray-500" />
            </div>
            <input
              type="text"
              class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5"
              placeholder="Archer's name filter"
              v-model="searchArcherName"
              @input="fetchArchers()"
            />
          </div>
        </div>

        <div class="h-72 overflow-auto">
          <table class="w-full text-sm text-left text-gray-500">
            <thead class="text-xs text-gray-500 uppercase bg-gray-50">
              <tr>
                <th class="px-6 py-3"><HashtagIcon class="w-4 h-4" /></th>
                <th class="px-6 py-3">User</th>
                <th class="px-6 py-3"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                class="border-b border-gray-200 hover:bg-blue-100 hover:text-blue-700 hover:cursor-pointer group"
                v-for="(archer, index) in filterArchers(archersList, searchArcherName)"
                :class="{
                  'bg-gray-300 hover:cursor-not-allowed! hover:bg-gray-300': archerInTournament(
                    archer.id,
                  ),
                }"
                :key="index"
                @click="
                  () => {
                    if (archerInTournament(archer.id)) return

                    emit('addArcher', archer.id)
                    searchArcherName = ''
                    showModal = false
                  }
                "
              >
                <td
                  class="px-6 py-2 w-4 text-gray-900 group-hover:text-blue-700 whitespace-nowrap font-semibold"
                  :class="{
                    'group-hover:text-gray-900!': archerInTournament(archer.id),
                  }"
                >
                  {{ archer.id }}
                </td>
                <th
                  scope="row"
                  class="px-6 py-2 font-medium text-gray-900 group-hover:text-blue-700 whitespace-nowrap"
                  :class="{
                    'group-hover:text-gray-900!': archerInTournament(archer.id),
                  }"
                >
                  {{ archer.name }}
                </th>
                <td class="px-6 py-2 flex justify-end items-center">
                  <div class="hidden group-hover:block" v-if="!archerInTournament(archer.id)">
                    Register
                  </div>
                  <div v-else class="group-hover:text-gray-500">Already register</div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </form>

    <template #footer>
      <div class="wf-full flex justify-between items-center gap-4">
        <button
          class="w-full px-4 py-2 mr-2 text-sm text-gray-900 bg-white border border-gray-200 rounded hover:bg-gray-100 hover:cursor-pointer hover:text-blue-700"
          @click="showModal = false"
        >
          Discard
        </button>
      </div>
    </template>
  </Modal>
</template>
