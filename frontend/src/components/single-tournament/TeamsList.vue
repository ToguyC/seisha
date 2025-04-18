<script setup lang="ts">
import {
  deleteTeam as _deleteTeam,
  deleteArcherFromTeam,
  getTeam,
  postArcherToTeam,
  putTeam,
} from '@/api/team'
import { postTournamentTeam } from '@/api/tournament'
import type { Team, TournamentWithRelations } from '@/models/models'
import { CheckIcon, HashtagIcon, PlusIcon, TrashIcon, UserGroupIcon } from '@heroicons/vue/16/solid'
import { ref, useTemplateRef } from 'vue'
import Modal from '../Modal.vue'
import ArchersModal from './ArchersModal.vue'

const { tournament } = defineProps<{
  tournament: TournamentWithRelations
}>()

const emit = defineEmits<{
  fetchTournament: [tournamentId: number]
}>()

const showAddTeamModal = ref(false)
const showEditTeamModal = ref(false)
const newTeamName = ref('')
const editTeamInfo = ref<Team | null>(null)

const modalRef = useTemplateRef<InstanceType<typeof ArchersModal>>('modalRef')

const showArchersModal = () => {
  modalRef.value?.show()
}

const fetchTeam = (teamId: number) => {
  getTeam(teamId)
    .then((res) => {
      editTeamInfo.value = res.data
      showEditTeamModal.value = true
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const addTeam = () => {
  if (!newTeamName.value) return

  postTournamentTeam(tournament.id, newTeamName.value)
    .then(() => {
      emit('fetchTournament', tournament.id)
      showAddTeamModal.value = false
      newTeamName.value = ''
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const deleteTeam = (teamId: number) => {
  _deleteTeam(teamId)
    .then(() => {
      emit('fetchTournament', tournament.id)
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const editTeam = () => {
  if (!editTeamInfo.value) return

  putTeam(editTeamInfo.value)
    .then(() => {
      emit('fetchTournament', tournament.id)
      showEditTeamModal.value = false
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const addArcher = (archerId: number) => {
  if (tournament.format === 'team' && showEditTeamModal.value && editTeamInfo.value) {
    const teamId = editTeamInfo.value.id
    postArcherToTeam(teamId, archerId)
      .then(() => {
        fetchTeam(teamId)
        emit('fetchTournament', tournament.id)
      })
      .catch((err) => {
        console.error(err.message)
      })
    return
  }
}

const removeArcherFromTeam = (archerId: number) => {
  if (!editTeamInfo.value) return

  const teamId = editTeamInfo.value.id
  deleteArcherFromTeam(teamId, archerId)
    .then(() => {
      fetchTeam(teamId)
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
      <div class="text-xl font-bold text-gray-900 capitalize">Teams</div>
      <button
        class="w-20 flex items-center text-sm justify-center gap-4 px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 hover:cursor-pointer"
        @click="() => (showAddTeamModal = true)"
      >
        <PlusIcon class="w-6 h-6" />
      </button>
    </div>

    <table class="w-full text-sm text-left rtl:text-right text-gray-500">
      <thead class="text-xs text-gray-500 uppercase bg-gray-50">
        <tr class="font-bold">
          <td class="px-6 py-3"><HashtagIcon class="w-4 h-4" /></td>
          <td class="px-6 py-3">Name</td>
          <td class="px-6 py-3">Archers</td>
          <td class="px-6 py-3"></td>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(team, index) in tournament.teams"
          :key="index"
          class="bg-white border-b border-gray-200 hover:bg-gray-50 hover:cursor-pointer group"
          @click="
            () => {
              fetchTeam(team.id)
              showEditTeamModal = true
            }
          "
        >
          <td class="px-6 py-2 w-4 text-gray-900 whitespace-nowrap font-semibold">
            {{ team.id }}
          </td>
          <td scope="row" class="px-6 py-2 font-medium text-gray-900 whitespace-nowrap">
            {{ team.name }}
          </td>

          <td class="px-6 py-2 w-full flex flex-col items-start gap-2 text-gray-900 capitalize">
            <div
              v-for="(archer, idx) in team.archers"
              :key="idx"
              class="w-full flex items-center justify-between gap-2"
            >
              {{ archer.name }}
              <div
                v-if="archer.position === 'zasha'"
                class="bg-blue-100 text-blue-800 text-xs rounded-sm w-10 flex items-center justify-center"
              >
                坐射
              </div>
              <div
                v-else
                class="bg-red-100 text-red-800 text-xs rounded-sm w-10 flex items-center justify-center"
              >
                立射
              </div>
            </div>
          </td>
          <td
            class="px-6 py-2 text-right w-10 border-l border-gray-200 group-hover:bg-white"
            @click="$event.stopPropagation()"
          >
            <div class="flex items-center justify-end gap-2">
              <TrashIcon
                class="w-6 h-6 text-red-500 hover:text-red-600 hover:bg-red-100 rounded-sm p-1"
                @click="() => deleteTeam(team.id)"
              />
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <Modal v-model="showAddTeamModal" title="Register a team">
      <form class="w-full flex flex-col items-center gap-5 pb-4 border-b border-gray-200">
        <div class="w-full flex flex-col gap-2">
          <div class="w-full flex items-center justify-between gap-2">
            <div class="relative w-full">
              <div class="absolute inset-y-0 start-0 flex items-center ps-2.5 pointer-events-none">
                <UserGroupIcon class="w-5 h-5 text-gray-500" />
              </div>
              <input
                type="text"
                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5"
                placeholder="Team's name"
                v-model="newTeamName"
              />
            </div>
          </div>
        </div>
      </form>

      <template #footer>
        <div class="wf-full flex justify-between items-center gap-4">
          <button
            class="w-1/2 flex items-center text-sm justify-center gap-4 px-4 py-2 text-white bg-blue-700 rounded hover:bg-blue-800 hover:cursor-pointer"
            @click="addTeam()"
          >
            <PlusIcon class="w-6 h-6" /> Register team
          </button>
          <button
            class="w-1/2 px-4 py-2 mr-2 text-sm text-gray-900 bg-white border border-gray-200 rounded hover:bg-gray-100 hover:cursor-pointer hover:text-blue-700"
            @click="showAddTeamModal = false"
          >
            Discard
          </button>
        </div>
      </template>
    </Modal>

    <Modal v-model="showEditTeamModal" title="Edit a team" v-if="editTeamInfo">
      <form class="w-full flex flex-col items-center gap-5 pb-4 border-b border-gray-200">
        <div class="w-full flex flex-col gap-2">
          <div class="w-full flex items-center justify-between gap-2">
            <div class="relative w-full">
              <div class="absolute inset-y-0 start-0 flex items-center ps-2.5 pointer-events-none">
                <UserGroupIcon class="w-5 h-5 text-gray-500" />
              </div>
              <input
                type="text"
                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5"
                placeholder="Team's name"
                v-model="editTeamInfo.name"
              />
            </div>
          </div>
        </div>

        <div class="w-full">
          <div
            v-for="(archer, index) in editTeamInfo.archers"
            :key="index"
            class="w-full flex items-center justify-between p-2"
          >
            {{ archer.name }}
            <TrashIcon
              class="w-6 h-6 text-red-500 hover:text-red-600 hover:bg-red-100 hover:cursor-pointer rounded-sm p-1"
              @click="() => removeArcherFromTeam(archer.id)"
            />
          </div>
          <div
            class="bg-blue-100 text-blue-700 rounded-lg p-2 flex justify-center items-center gap-2 hover:cursor-pointer hover:bg-blue-200"
            @click="() => showArchersModal()"
          >
            <PlusIcon class="w-5 h-5" /> Register archer
          </div>
        </div>
      </form>

      <template #footer>
        <div class="wf-full flex justify-between items-center gap-4">
          <button
            class="w-1/2 flex items-center text-sm justify-center gap-4 px-4 py-2 text-white bg-blue-700 rounded hover:bg-blue-800 hover:cursor-pointer"
            @click="
              () => {
                editTeam()
                showEditTeamModal = false
              }
            "
          >
            <CheckIcon class="w-6 h-6" /> Edit team's name
          </button>
          <button
            class="w-1/2 px-4 py-2 mr-2 text-sm text-gray-900 bg-white border border-gray-200 rounded hover:bg-gray-100 hover:cursor-pointer hover:text-blue-700"
            @click="showEditTeamModal = false"
          >
            Discard
          </button>
        </div>
      </template>
    </Modal>

    <ArchersModal :tournament="tournament" @add-archer="addArcher" ref="modalRef" />
  </div>
</template>
