<script setup lang="ts">
import api from '@/api/base'
import Breadcrumb from '@/components/Breadcrumb.vue'
import Modal from '@/components/Modal.vue'
import type { Tournament } from '@/models/models'
import router from '@/router'
import {
  BookmarkIcon,
  CalendarDaysIcon,
  EyeIcon,
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

const pagination = ref<{
  count: number
  total: number
  page: number
  total_pages: number
  limit: number
  data: Tournament[]
}>({
  count: 0,
  total: 0,
  page: 1,
  total_pages: 0,
  limit: 0,
  data: [],
})

const showModal = ref(false)
const newTournamentName = ref('')
const newTournamentStartDate = ref('')
const newTournamentEndDate = ref('')
const newTournamentFormat = ref('')

const fetchPage = (page: number) => {
  api
    .get(`/tournaments?page=${page}`)
    .then((res) => {
      pagination.value = res.data
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const addTournament = (name: string, format: string, start_date: string, end_date: string) => {
  api
    .post('/tournaments', {
      name,
      format,
      start_date,
      end_date,
    })
    .then((res) => {
      showModal.value = false
      fetchPage(pagination.value.page)
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const deleteTournament = (id: number) => {
  api
    .delete(`/tournaments/${id}`)
    .then((res) => {
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
      @click="showModal = true"
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
          <td class="px-6 py-4">
            {{ new Date(tournament.start_date).toLocaleDateString() }} -
            {{ new Date(tournament.end_date).toLocaleDateString() }}
          </td>
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
            <div class="flex items-center gap-4">
              <div
                v-if="tournament.status === 'upcoming'"
                class="w-2 h-2 bg-orange-400 rounded-full"
              ></div>
              <div
                v-if="tournament.status === 'live'"
                class="w-2 h-2 bg-amaranth-500 rounded-full"
              ></div>
              <div
                v-if="tournament.status === 'finished'"
                class="w-2 h-2 bg-wedgeblue-500 rounded-full"
              ></div>
              <div v-if="tournament.status === 'cancelled'" class="w-4 h-4">
                <PlusIcon class="w-full h-full rotate-45 text-amaranth-500" />
              </div>
              <div class="uppercase">{{ tournament.status }}</div>
            </div>
          </td>
          <td
            class="px-6 py-4 text-right w-16 group-hover:bg-white"
            @click="$event.stopPropagation()"
          >
            <div class="flex items-center justify-end gap-2">
              <PencilSquareIcon
                class="w-6 h-6 hover:text-gray-500 hover:bg-gray-100 rounded-sm p-1"
                @click="() => console.log('Edit icon clicked')"
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

  <Modal v-model="showModal" title="Add new tournament">
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
            v-model="newTournamentName"
          />
        </div>
      </div>

      <div class="w-full">
        <label for="archer-position" class="block mb-2 text-gray-900">Format</label>
        <select
          id="archer-position"
          class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
          v-model="newTournamentFormat"
        >
          <option value="individual">Individual</option>
          <option value="team">Team</option>
        </select>
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
            v-model="newTournamentStartDate"
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
            v-model="newTournamentEndDate"
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
              addTournament(
                newTournamentName,
                newTournamentFormat,
                newTournamentStartDate,
                newTournamentEndDate,
              )
              showModal = false
            }
          "
        >
          <PlusIcon class="w-6 h-6" /> Add new tournament
        </button>
        <button
          class="w-1/2 px-4 py-2 mr-2 text-sm text-gray-900 bg-white border border-gray-200 rounded hover:bg-gray-100 hover:cursor-pointer hover:text-blue-700"
          @click="showModal = false"
        >
          Discard
        </button>
      </div>
    </template>
  </Modal>
</template>
