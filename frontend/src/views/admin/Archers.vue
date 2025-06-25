<script setup lang="ts">
import { deleteArcher, getPagninatedArchers, postArcher, putArcher } from '@/api/archer'
import Breadcrumb from '@/components/Breadcrumb.vue'
import Modal from '@/components/Modal.vue'
import type { Archer, PaginatedResponse } from '@/models/models'
import {
  CheckIcon,
  HashtagIcon,
  MagnifyingGlassIcon,
  PencilSquareIcon,
  PlusIcon,
  TrashIcon,
  UserIcon,
} from '@heroicons/vue/16/solid'
import { computed, onMounted, ref } from 'vue'

const levels = [
  {
    name: 'Admin',
    url: '/',
  },
  {
    name: 'Archers',
    url: '/admin/archers',
  },
]

const pagination = ref<PaginatedResponse<Archer>>({
  count: 0,
  total: 0,
  page: 1,
  total_pages: 0,
  limit: 0,
  data: [],
})

const showModal = ref(false)
const showEditModal = ref(false)
const archerEditInfo = ref<Archer | null>(null)
const newArcherName = ref('')
const newArcherPosition = ref('')
const searchArcherName = ref('')
const searchArcherPosition = ref('none')

const filteredArchers = computed(() => {
  return pagination.value.data.filter(
    (archer) =>
      archer.name.toLowerCase().includes(searchArcherName.value.toLowerCase()) &&
      (searchArcherPosition.value === 'none' ||
        archer.position === searchArcherPosition.value.toLowerCase()),
  )
})

const fetchPage = (page: number) => {
  getPagninatedArchers(page)
    .then((res) => {
      pagination.value = res.data
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const addArcher = (name: string, position: string) => {
  postArcher(name, position)
    .then(() => {
      showModal.value = false
      newArcherName.value = ''
      newArcherPosition.value = ''
      fetchPage(pagination.value.page)
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const editArcher = () => {
  if (!archerEditInfo.value) return

  putArcher(archerEditInfo.value)
    .then(() => {
      showEditModal.value = false
      archerEditInfo.value = null
      fetchPage(pagination.value.page)
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const dropArcher = (id: number) => {
  deleteArcher(id)
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

      <div class="text-xl font-bold text-gray-900">All Archers</div>
    </div>

    <button
      class="flex items-center gap-2 text-white bg-blue-700 hover:cursor-pointer hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5"
      @click="showModal = true"
    >
      <PlusIcon class="w-6 h-6" /> Add new archer
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
        placeholder="Search for users"
        v-model="searchArcherName"
      />
    </div>

    <select
      id="position"
      class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-70 p-2.5"
      v-model="searchArcherPosition"
    >
      <option value="none">Choose position</option>
      <option value="zasha">坐射 (Zasha)</option>
      <option value="rissha">立射 (Rissha)</option>
    </select>
  </form>

  <div class="relative mt-4">
    <table class="w-full text-sm text-left rtl:text-right text-gray-500">
      <thead class="text-xs text-gray-500 uppercase bg-gray-50">
        <tr>
          <th class="px-6 py-3"><HashtagIcon class="w-4 h-4" /></th>
          <th class="px-6 py-3">User</th>
          <th class="px-6 py-3">Shooting position</th>
          <th class="px-6 py-3">Overall accuracy</th>
          <th class="px-6 py-3"></th>
          <th class="px-6 py-3"></th>
        </tr>
      </thead>
      <tbody>
        <tr
          class="bg-white border-b border-gray-200 hover:bg-gray-50 hover:cursor-pointer group"
          v-for="(archer, index) in filteredArchers"
          :key="index"
        >
          <td class="px-6 py-2 w-4 text-gray-900 whitespace-nowrap font-semibold">
            {{ archer.id }}
          </td>
          <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">
            {{ archer.name }}
          </th>
          <td class="px-6 py-2">
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
          </td>
          <td class="px-6 py-2">{{ archer.accuracy }} %</td>
          <td
            class="px-6 py-2 text-right w-24 group-hover:bg-white"
            @click="$event.stopPropagation()"
          >
            <div class="flex items-center justify-end gap-2">
              <PencilSquareIcon
                class="w-6 h-6 hover:text-gray-500 hover:bg-gray-100 rounded-sm p-1"
                @click="
                  () => {
                    archerEditInfo = { ...archer }
                    showEditModal = true
                  }
                "
              />
            </div>
          </td>
          <td
            class="px-6 py-2 text-right w-10 border-l border-gray-200 group-hover:bg-white"
            @click="$event.stopPropagation()"
          >
            <div class="flex items-center justify-end gap-2">
              <TrashIcon
                class="w-6 h-6 text-red-500 hover:text-red-600 hover:bg-red-100 rounded-sm p-1"
                @click="() => dropArcher(archer.id)"
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

  <Modal v-model="showModal" title="Add new archer">
    <form class="w-full flex flex-col items-center gap-5 pb-4 border-b border-gray-200">
      <div class="w-full">
        <label for="archer-name" class="block mb-2 text-gray-900">Archer's name</label>
        <div class="relative">
          <div class="absolute inset-y-0 start-0 flex items-center ps-2.5 pointer-events-none">
            <UserIcon class="w-5 h-5 text-gray-500" />
          </div>
          <input
            type="text"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5"
            placeholder="Archer's name"
            id="archer-name"
            v-model="newArcherName"
          />
        </div>
      </div>

      <div class="w-full">
        <label for="archer-position" class="block mb-2 text-gray-900">Archer's position</label>
        <select
          id="archer-position"
          class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
          v-model="newArcherPosition"
        >
          <option value="zasha">坐射 (Zasha)</option>
          <option value="rissha">立射 (Rissha)</option>
        </select>
      </div>
    </form>

    <template #footer>
      <div class="wf-full flex justify-between items-center gap-4">
        <button
          class="w-1/2 text-sm flex items-center justify-center gap-4 px-4 py-2 text-white bg-blue-700 rounded hover:bg-blue-800 hover:cursor-pointer"
          @click="
            () => {
              addArcher(newArcherName, newArcherPosition)
              showModal = false
            }
          "
        >
          <PlusIcon class="w-6 h-6" /> Add new archer
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

  <Modal v-model="showEditModal" title="Edit archer">
    <form
      class="w-full flex flex-col items-center gap-5 pb-4 border-b border-gray-200"
      v-if="archerEditInfo"
    >
      <div class="w-full">
        <label for="archer-name" class="block mb-2 text-gray-900">Archer's name</label>
        <div class="relative">
          <div class="absolute inset-y-0 start-0 flex items-center ps-2.5 pointer-events-none">
            <UserIcon class="w-5 h-5 text-gray-500" />
          </div>
          <input
            type="text"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5"
            placeholder="Archer's name"
            id="archer-name"
            v-model="archerEditInfo.name"
          />
        </div>
      </div>

      <div class="w-full">
        <label for="archer-position" class="block mb-2 text-gray-900">Archer's position</label>
        <select
          id="archer-position"
          class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
          v-model="archerEditInfo.position"
        >
          <option value="zasha">坐射 (Zasha)</option>
          <option value="rissha">立射 (Rissha)</option>
        </select>
      </div>
    </form>

    <template #footer>
      <div class="wf-full flex justify-between items-center gap-4">
        <button
          class="w-1/2 text-sm flex items-center justify-center gap-4 px-4 py-2 text-white bg-blue-700 rounded hover:bg-blue-800 hover:cursor-pointer"
          @click="
            () => {
              editArcher()
              showEditModal = false
            }
          "
        >
          <CheckIcon class="w-6 h-6" /> Edit archer
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
