<script setup lang="ts">
import { getAllArchers } from '@/api/archer'
import {
  deleteTeam as _deleteTeam,
  deleteArcherFromTeam,
  getTeam,
  postArcherToTeam,
  putTeam,
} from '@/api/team'
import {
  deleteTournamentArcher,
  getTournament,
  postTournamentArcher,
  postTournamentTeam,
} from '@/api/tournament'
import Breadcrumb from '@/components/Breadcrumb.vue'
import Modal from '@/components/Modal.vue'
import type { Archer, Team, TournamentWithRelations } from '@/models/models'
import {
  CheckIcon,
  HashtagIcon,
  PlusIcon,
  TrashIcon,
  UserGroupIcon,
  UserIcon,
} from '@heroicons/vue/16/solid'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const showAddArcherModal = ref(false)
const showAddTeamModal = ref(false)
const showEditTeamModal = ref(false)
const searchArcherName = ref('')
const newTeamName = ref('')
const editTeamInfo = ref<Team | null>(null)
const archersList = ref<Archer[]>([])
const tournament = ref<TournamentWithRelations>({
  id: 0,
  name: '',
  start_date: '',
  end_date: '',
  format: '',
  status: '',
  archers: [],
  teams: [],
  matches: [],
})

const levels = ref([
  {
    name: 'Admin',
    url: '/',
  },
  {
    name: 'Tournaments',
    url: '/admin/tournaments',
  },
])

const fetchTournament = (tournamentId: number) => {
  getTournament(tournamentId)
    .then((res) => {
      tournament.value = res.data

      levels.value = levels.value.filter((level) => level.name !== tournament.value.name)
      levels.value.push({
        name: tournament.value.name,
        url: `/admin/tournaments/${tournamentId}`,
      })
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const addArcher = (archerId: number) => {
  if (tournament.value.format === 'team' && showEditTeamModal.value && editTeamInfo.value) {
    const teamId = editTeamInfo.value.id
    postArcherToTeam(archerId, teamId)
      .then(() => {
        fetchTeam(teamId)
        fetchTournament(tournament.value.id)
      })
      .catch((err) => {
        console.error(err.message)
      })
    return
  }

  postTournamentArcher(archerId, tournament.value.id)
    .then(() => {
      fetchTournament(tournament.value.id)
    })
    .catch((err) => {
      console.error(err.message)
    })
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

const editTeam = () => {
  if (!editTeamInfo.value) return

  putTeam(editTeamInfo.value)
    .then(() => {
      fetchTournament(tournament.value.id)
      showEditTeamModal.value = false
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const deleteArcher = (archerId: number) => {
  deleteTournamentArcher(archerId, tournament.value.id)
    .then(() => {
      fetchTournament(tournament.value.id)
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const removeArcherFromTeam = (archerId: number) => {
  if (!editTeamInfo.value) return

  const teamId = editTeamInfo.value.id
  deleteArcherFromTeam(archerId, teamId)
    .then(() => {
      fetchTeam(teamId)
      fetchTournament(tournament.value.id)
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const deleteTeam = (teamId: number) => {
  _deleteTeam(teamId)
    .then(() => {
      fetchTournament(tournament.value.id)
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
  if (tournament.value.format === 'team') {
    return tournament.value.teams.some((team) =>
      team.archers.some((archer) => archer.id === archerId),
    )
  }
  return tournament.value.archers.some((archer) => archer.id === archerId)
}

const fetchParticipant = () => {
  getAllArchers()
    .then((res) => {
      archersList.value = res.data
    })
    .catch((err) => {
      console.error(err.message)
    })
}

onMounted(() => {
  const tournamentId = route.params.id

  if (tournamentId) {
    fetchTournament(Number(tournamentId))
    fetchParticipant()
  } else {
    console.error('Tournament ID is required')
  }
})
</script>

<template>
  <Breadcrumb :levels="levels"></Breadcrumb>

  <div class="flex flex-col w-full items-center justify-center my-10">
    <div class="text-4xl font-bold">{{ tournament.name }}</div>
  </div>

  <table class="w-full mb-5">
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

  <div class="w-full h-1 border-b border-gray-200 mb-5"></div>

  <div class="flex gap-20">
    <div class="w-1/2">
      <div class="flex items-center justify-between mb-6">
        <div class="text-xl font-bold text-gray-900 capitalize">{{ tournament.format }}</div>
        <button
          class="w-1/4 flex items-center text-sm justify-center gap-4 px-4 py-2 text-white bg-blue-700 rounded hover:bg-blue-800 hover:cursor-pointer"
          @click="
            () => {
              if (tournament.format === 'team') {
                showAddTeamModal = true
              } else {
                showAddArcherModal = true
              }
            }
          "
        >
          <PlusIcon class="w-6 h-6" /> Register
          {{ tournament.format === 'team' ? 'team' : 'archer' }}
        </button>
      </div>

      <div v-if="tournament.format === 'team'" class="flex w-full items-center gap-6">
        <table class="w-full text-sm text-left rtl:text-right text-gray-500">
          <thead class="text-xs text-gray-500 uppercase bg-gray-50">
            <tr class="font-bold">
              <td class="px-6 py-3"><HashtagIcon class="w-4 h-4" /></td>
              <td class="px-6 py-3">Name</td>
              <td class="px-6 py-3">Archers</td>
              <td class="px-6 py-3"></td>
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
      </div>

      <div v-else>
        <table class="w-full text-sm text-left rtl:text-right text-gray-500">
          <thead class="text-xs text-gray-500 uppercase bg-gray-50">
            <tr class="font-bold">
              <td class="px-6 py-3"><HashtagIcon class="w-4 h-4" /></td>
              <td class="px-6 py-3">Name</td>
              <td class="px-6 py-3"></td>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(archer, index) in tournament.archers"
              :key="index"
              class="bg-white border-b border-gray-200 hover:bg-gray-50 hover:cursor-pointer group"
            >
              <td class="px-6 py-2 w-4 text-gray-900 whitespace-nowrap font-semibold">
                {{ archer.id }}
              </td>
              <td scope="row" class="px-6 py-2 font-medium text-gray-900 whitespace-nowrap">
                {{ archer.name }}
              </td>
              <td
                class="px-6 py-2 text-right w-10 border-l border-gray-200 group-hover:bg-white"
                @click="$event.stopPropagation()"
              >
                <div class="flex items-center justify-end gap-2">
                  <TrashIcon
                    class="w-6 h-6 text-red-500 hover:text-red-600 hover:bg-red-100 rounded-sm p-1"
                    @click="() => deleteArcher(archer.id)"
                  />
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="w-1/2">
      <div class="flex items-center justify-between mb-6">
        <div class="text-xl font-bold text-gray-900 capitalize">Matches</div>
        <button
          class="w-1/4 flex items-center text-sm justify-center gap-4 px-4 py-2 text-white bg-blue-700 rounded hover:bg-blue-800 hover:cursor-pointer"
        >
          <PlusIcon class="w-6 h-6" /> Add new match
        </button>
      </div>
    </div>
  </div>

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
          @click="() => (showAddArcherModal = true)"
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
          @click="
            () => {
              postTournamentTeam(tournament.id, newTeamName).then(() => {
                fetchTournament(tournament.id)
                showAddTeamModal = false
              })
            }
          "
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

  <Modal v-model="showAddArcherModal" title="Register an archer">
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
              @input="fetchParticipant()"
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

                    addArcher(archer.id)
                    showAddArcherModal = false
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
          @click="showAddArcherModal = false"
        >
          Discard
        </button>
      </div>
    </template>
  </Modal>
</template>
