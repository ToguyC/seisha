<script setup lang="ts">
import {
  deleteTournament as _deleteTournament,
  getPaginatedTournaments,
  postTournament,
  putTournament,
} from '@/api/tournament'
import Breadcrumb from '@/components/Breadcrumb.vue'
import Modal from '@/components/Modal.vue'
import { dummyTournament } from '@/models/dummy'
import type { PaginatedResponse, Tournament, TournamentWithRelations } from '@/models/models'
import router from '@/router'
import {
  BookmarkIcon,
  CalendarDaysIcon,
  CheckIcon,
  HashtagIcon,
  MagnifyingGlassIcon,
  PencilSquareIcon,
  PlusIcon,
  TrashIcon,
} from '@heroicons/vue/16/solid'
import { onMounted, ref } from 'vue'

const levels = [
  {
    name: 'Admin',
    url: '/',
  },
  {
    name: 'Tournaments',
    url: '/admin/tournaments',
  },
]

const pagination = ref<PaginatedResponse<TournamentWithRelations>>({
  count: 0,
  total: 0,
  page: 1,
  total_pages: 0,
  limit: 0,
  data: [],
})

const showAddModal = ref(false)
const showEditModal = ref(false)

const newTournamentInfo = ref<Tournament>(dummyTournament)
const editTournamentInfo = ref<Tournament>(dummyTournament)

const fetchPage = (page: number) => {
  getPaginatedTournaments(page)
    .then((res) => {
      pagination.value = res.data
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const addTournament = () => {
  postTournament(newTournamentInfo.value)
    .then(() => {
      showAddModal.value = false
      fetchPage(pagination.value.page)
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const editTournament = () => {
  putTournament(editTournamentInfo.value)
    .then(() => {
      showEditModal.value = false
      fetchPage(pagination.value.page)
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const deleteTournament = (id: number) => {
  _deleteTournament(id)
    .then(() => {
      fetchPage(pagination.value.page)
    })
    .catch((err) => {
      console.error(err.message)
    })
}

onMounted(() => {
  fetchPage(1)
})
</script>

<template>
  <div class="flex justify-between items-center mb-6">
    <div class="flex flex-col gap-4">
      <Breadcrumb :levels="levels"></Breadcrumb>

      <div class="text-xl font-bold text-gray-900">All Tournaments</div>
    </div>

    <button
      class="flex items-center gap-2 text-white bg-blue-700 hover:cursor-pointer hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5"
      @click="showAddModal = true"
    >
      <PlusIcon class="w-6 h-6" /> Add new tournament
    </button>
  </div>

  <form class="w-full flex items-center gap-5 pb-4 border-b border-gray-200">
    <div class="relative">
      <div class="absolute inset-y-0 start-0 flex items-center ps-2.5 pointer-events-none">
        <MagnifyingGlassIcon class="w-5 h-5 text-gray-500" />
      </div>
      <input
        type="text"
        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-70 ps-10 p-2.5"
        placeholder="Search for tournament"
      />
    </div>
  </form>

  <div class="relative mt-4">
    <table class="w-full text-sm text-left rtl:text-right text-gray-500">
      <thead class="text-xs text-gray-500 uppercase bg-gray-50">
        <tr>
          <th class="px-6 py-3"><HashtagIcon class="w-4 h-4" /></th>
          <th class="px-6 py-3">Name</th>
          <th class="px-6 py-3">Participant count</th>
          <th class="px-6 py-3">Date</th>
          <th class="px-6 py-3">Matos</th>
          <th class="px-6 py-3">Format</th>
          <th class="px-6 py-3">Status</th>
          <th class="px-6 py-3"></th>
          <th class="px-6 py-3"></th>
        </tr>
      </thead>
      <tbody>
        <tr
          class="bg-white border-b border-gray-200 hover:bg-gray-50 hover:cursor-pointer group"
          v-for="(tournament, index) in pagination.data"
          :key="index"
          @click="() => router.push(`/admin/tournaments/${tournament.id}`)"
        >
          <td class="px-6 py-4 w-4 text-gray-900 whitespace-nowrap font-semibold">
            {{ tournament.id }}
          </td>
          <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">
            {{ tournament.name }}
          </th>
          <td class="px-6 py-4">
            <div v-if="tournament.format === 'individual'">{{ tournament.archers.length }}</div>
            <div v-else>
              {{ tournament.teams.length }} ({{
                tournament.teams.reduce((acc, team) => acc + team.archers.length, 0)
              }})
            </div>
          </td>
          <td v-if="tournament.start_date !== tournament.end_date" class="px-6 py-4">
            {{ new Date(tournament.start_date).toLocaleDateString() }} -
            {{ new Date(tournament.end_date).toLocaleDateString() }}
          </td>
          <td v-else class="px-6 py-4">
            {{ new Date(tournament.start_date).toLocaleDateString() }}
          </td>
          <td class="px-6 py-4">{{ tournament.target_count }}</td>
          <td class="px-6 py-4">
            <div
              v-if="tournament.format === 'individual'"
              class="bg-emerald-100 text-emerald-700 font-semibold w-10 rounded-sm flex items-center justify-center"
            >
              個人
            </div>
            <div
              v-else
              class="bg-purple-100 text-purple-700 font-semibold w-12 rounded-sm flex items-center justify-center"
            >
              チーム
            </div>
          </td>
          <td class="px-6 py-4">
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
          <td
            class="px-6 py-4 text-right w-16 group-hover:bg-white"
            @click="$event.stopPropagation()"
          >
            <div class="flex items-center justify-end gap-2">
              <PencilSquareIcon
                class="w-6 h-6 hover:text-gray-500 hover:bg-gray-100 rounded-sm p-1"
                @click="
                  () => {
                    editTournamentInfo = { ...tournament }
                    showEditModal = true
                  }
                "
              />
            </div>
          </td>
          <td
            class="px-6 py-4 text-right w-10 border-l border-gray-200 group-hover:bg-white"
            @click="$event.stopPropagation()"
          >
            <div class="flex items-center justify-end gap-2">
              <TrashIcon
                class="w-6 h-6 text-red-500 hover:text-red-600 hover:bg-red-100 rounded-sm p-1"
                @click="() => deleteTournament(tournament.id)"
              />
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <nav
      class="flex items-center flex-column flex-wrap md:flex-row justify-between pt-4"
      aria-label="Table navigation"
    >
      <span class="text-sm font-normal text-gray-500 mb-4 md:mb-0 block w-full md:inline md:w-auto">
        Showing
        <span class="font-semibold text-gray-900">{{
          Math.min(pagination.limit, pagination.total)
        }}</span>
        of
        <span class="font-semibold text-gray-900">{{ pagination.total }}</span>
      </span>

      <ul class="inline-flex -space-x-px rtl:space-x-reverse text-sm h-8">
        <li>
          <button
            @click="fetchPage(pagination.page - 1)"
            :disabled="pagination.page === 1"
            class="flex items-center justify-center px-3 h-8 ms-0 leading-tight text-gray-500 bg-white border border-gray-300 rounded-s-lg hover:bg-gray-100 hover:text-gray-700 disabled:opacity-50"
          >
            Previous
          </button>
        </li>

        <li v-for="n in pagination.total_pages" :key="n">
          <button
            @click="fetchPage(n)"
            :class="[
              'flex items-center justify-center px-3 h-8 leading-tight border border-gray-300 hover:cursor-pointer',
              pagination.page === n
                ? 'text-blue-600 bg-blue-50 hover:bg-blue-100 hover:text-blue-700'
                : 'text-gray-500 bg-white hover:bg-gray-100 hover:text-gray-700',
            ]"
          >
            {{ n }}
          </button>
        </li>

        <li>
          <button
            @click="fetchPage(pagination.page + 1)"
            :disabled="pagination.page === pagination.total_pages"
            class="flex items-center justify-center px-3 h-8 leading-tight text-gray-500 bg-white border border-gray-300 rounded-e-lg hover:bg-gray-100 hover:text-gray-700 disabled:opacity-50"
          >
            Next
          </button>
        </li>
      </ul>
    </nav>
  </div>

  <Modal v-model="showAddModal" title="Add new tournament">
    <form class="w-full flex flex-col items-center gap-5 pb-4 border-b border-gray-200">
      <div class="w-full">
        <label for="tournament-name" class="block mb-2 text-gray-900">Name</label>
        <div class="relative">
          <div class="absolute inset-y-0 start-0 flex items-center ps-2.5 pointer-events-none">
            <BookmarkIcon class="w-5 h-5 text-gray-500" />
          </div>
          <input
            type="text"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5"
            placeholder="Tournament's name"
            id="tournament-name"
            v-model="newTournamentInfo.name"
          />
        </div>
      </div>

      <div class="w-full flex gap-5">
        <div class="w-1/2">
          <label for="archer-position" class="block mb-2 text-gray-900">Format</label>
          <select
            id="archer-position"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
            v-model="newTournamentInfo.format"
          >
            <option value="individual">Individual</option>
            <option value="team">Team</option>
          </select>
        </div>
        <div class="w-1/2">
          <label for="tournament-matos" class="block mb-2 text-gray-900">Matos count</label>
          <div class="relative">
            <div class="absolute inset-y-0 start-0 flex items-center ps-2.5 pointer-events-none">
              <div class="flex items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 573 573"
                  class="w-5 h-5 fill-gray-500"
                >
                  <path
                    d="M286.5 175C348.08 175 398 224.92 398 286.5C398 348.08 348.08 398 286.5 398C224.92 398 175 348.08 175 286.5C175 224.92 224.92 175 286.5 175ZM286.5 231C255.848 231 231 255.848 231 286.5C231 317.152 255.848 342 286.5 342C317.152 342 342 317.152 342 286.5C342 255.848 317.152 231 286.5 231Z"
                  />
                  <path
                    d="M286.5 105C386.74 105 468 186.26 468 286.5C468 386.74 386.74 468 286.5 468C186.26 468 105 386.74 105 286.5C105 186.26 186.26 105 286.5 105ZM286.5 128C198.963 128 128 198.963 128 286.5C128 374.037 198.963 445 286.5 445C374.037 445 445 374.037 445 286.5C445 198.963 374.037 128 286.5 128Z"
                  />
                  <path
                    d="M286.5 0C444.73 0 573 128.27 573 286.5C573 444.73 444.73 573 286.5 573C128.27 573 0 444.73 0 286.5C0 128.27 128.27 0 286.5 0ZM286.5 59C160.855 59 59 160.855 59 286.5C59 412.145 160.855 514 286.5 514C412.145 514 514 412.145 514 286.5C514 160.855 412.145 59 286.5 59Z"
                  />
                </svg>
              </div>
            </div>
            <input
              type="number"
              id="tournament-matos"
              class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5"
              v-model="newTournamentInfo.target_count"
            />
          </div>
        </div>
      </div>

      <div class="w-full">
        <label for="tournament-date" class="block mb-2 text-gray-900">Start date</label>
        <div class="relative">
          <div class="absolute inset-y-0 start-0 flex items-center ps-2.5 pointer-events-none">
            <CalendarDaysIcon class="w-5 h-5 text-gray-500" />
          </div>
          <input
            type="date"
            id="tournament-date"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5"
            v-model="newTournamentInfo.start_date"
          />
        </div>
      </div>

      <div class="w-full">
        <label for="tournament-date" class="block mb-2 text-gray-900">End date</label>
        <div class="relative">
          <div class="absolute inset-y-0 start-0 flex items-center ps-2.5 pointer-events-none">
            <CalendarDaysIcon class="w-5 h-5 text-gray-500" />
          </div>
          <input
            type="date"
            id="tournament-date"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5"
            v-model="newTournamentInfo.end_date"
          />
        </div>
      </div>
    </form>

    <template #footer>
      <div class="wf-full flex justify-between items-center gap-4">
        <button
          class="w-1/2 flex items-center text-sm justify-center gap-4 px-4 py-2 text-white bg-blue-700 rounded hover:bg-blue-800 hover:cursor-pointer"
          @click="
            () => {
              addTournament()
              showAddModal = false
            }
          "
        >
          <PlusIcon class="w-6 h-6" /> Add new tournament
        </button>
        <button
          class="w-1/2 px-4 py-2 mr-2 text-sm text-gray-900 bg-white border border-gray-200 rounded hover:bg-gray-100 hover:cursor-pointer hover:text-blue-700"
          @click="showAddModal = false"
        >
          Discard
        </button>
      </div>
    </template>
  </Modal>

  <Modal v-model="showEditModal" title="Edit tournament">
    <form class="w-full flex flex-col items-center gap-5 pb-4 border-b border-gray-200">
      <div class="w-full">
        <label for="tournament-name" class="block mb-2 text-gray-900">Name</label>
        <div class="relative">
          <div class="absolute inset-y-0 start-0 flex items-center ps-2.5 pointer-events-none">
            <BookmarkIcon class="w-5 h-5 text-gray-500" />
          </div>
          <input
            type="text"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5"
            placeholder="Tournament's name"
            id="tournament-name"
            v-model="editTournamentInfo.name"
          />
        </div>
      </div>

      <div class="w-full flex gap-5">
        <div class="w-1/2">
          <label for="archer-position" class="block mb-2 text-gray-900">Format</label>
          <select
            id="archer-position"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
            v-model="editTournamentInfo.format"
          >
            <option value="individual">Individual</option>
            <option value="team">Team</option>
          </select>
        </div>
        <div class="w-1/2">
          <label for="tournament-matos" class="block mb-2 text-gray-900">Matos count</label>
          <div class="relative">
            <div class="absolute inset-y-0 start-0 flex items-center ps-2.5 pointer-events-none">
              <div class="flex items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 573 573"
                  class="w-5 h-5 fill-gray-500"
                >
                  <path
                    d="M286.5 175C348.08 175 398 224.92 398 286.5C398 348.08 348.08 398 286.5 398C224.92 398 175 348.08 175 286.5C175 224.92 224.92 175 286.5 175ZM286.5 231C255.848 231 231 255.848 231 286.5C231 317.152 255.848 342 286.5 342C317.152 342 342 317.152 342 286.5C342 255.848 317.152 231 286.5 231Z"
                  />
                  <path
                    d="M286.5 105C386.74 105 468 186.26 468 286.5C468 386.74 386.74 468 286.5 468C186.26 468 105 386.74 105 286.5C105 186.26 186.26 105 286.5 105ZM286.5 128C198.963 128 128 198.963 128 286.5C128 374.037 198.963 445 286.5 445C374.037 445 445 374.037 445 286.5C445 198.963 374.037 128 286.5 128Z"
                  />
                  <path
                    d="M286.5 0C444.73 0 573 128.27 573 286.5C573 444.73 444.73 573 286.5 573C128.27 573 0 444.73 0 286.5C0 128.27 128.27 0 286.5 0ZM286.5 59C160.855 59 59 160.855 59 286.5C59 412.145 160.855 514 286.5 514C412.145 514 514 412.145 514 286.5C514 160.855 412.145 59 286.5 59Z"
                  />
                </svg>
              </div>
            </div>
            <input
              type="number"
              id="tournament-matos"
              class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5"
              v-model="editTournamentInfo.target_count"
            />
          </div>
        </div>
      </div>

      <div class="w-full">
        <label for="tournament-date" class="block mb-2 text-gray-900">Start date</label>
        <div class="relative">
          <div class="absolute inset-y-0 start-0 flex items-center ps-2.5 pointer-events-none">
            <CalendarDaysIcon class="w-5 h-5 text-gray-500" />
          </div>
          <input
            type="date"
            id="tournament-date"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5"
            v-model="editTournamentInfo.start_date"
          />
        </div>
      </div>

      <div class="w-full">
        <label for="tournament-date" class="block mb-2 text-gray-900">End date</label>
        <div class="relative">
          <div class="absolute inset-y-0 start-0 flex items-center ps-2.5 pointer-events-none">
            <CalendarDaysIcon class="w-5 h-5 text-gray-500" />
          </div>
          <input
            type="date"
            id="tournament-date"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5"
            v-model="editTournamentInfo.end_date"
          />
        </div>
      </div>
    </form>

    <template #footer>
      <div class="wf-full flex justify-between items-center gap-4">
        <button
          class="w-1/2 flex items-center text-sm justify-center gap-4 px-4 py-2 text-white bg-blue-700 rounded hover:bg-blue-800 hover:cursor-pointer"
          @click="
            () => {
              editTournament()
              showEditModal = false
            }
          "
        >
          <CheckIcon class="w-6 h-6" /> Edit tournament
        </button>
        <button
          class="w-1/2 px-4 py-2 mr-2 text-sm text-gray-900 bg-white border border-gray-200 rounded hover:bg-gray-100 hover:cursor-pointer hover:text-blue-700"
          @click="showEditModal = false"
        >
          Discard
        </button>
      </div>
    </template>
  </Modal>
</template>
