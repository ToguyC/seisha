<script setup lang="ts">
import { HomeIcon } from '@heroicons/vue/16/solid'
import type { PropType } from 'vue'

type Level = {
  name: string
  url: string
}

const { levels } = defineProps({
  levels: {
    type: Array as PropType<Level[]>,
    required: true,
  },
})
</script>

<template>
  <nav class="flex text-gray-700">
    <ol class="inline-flex items-center space-x-1 md:space-x-2 rtl:space-x-reverse">
      <li class="inline-flex items-center">
        <RouterLink
          to="/"
          class="inline-flex items-center text-sm text-gray-700 hover:text-amaranth-600"
          :class="{
            'font-medium': levels.length === 0,
            'font-semibold': levels.length > 0,
          }"
        >
          <HomeIcon class="w-5 h-5 me-2.5"></HomeIcon>
          Home
        </RouterLink>
      </li>
      <li v-for="(level, index) in levels" :key="index">
        <div class="flex items-center">
          <svg
            class="rtl:rotate-180 block w-3 h-3 mx-1 text-gray-400"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 6 10"
          >
            <path
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="m1 9 4-4-4-4"
            />
          </svg>
          <RouterLink
            :to="level.url"
            v-if="index !== levels.length - 1"
            class="ms-1 text-sm font-semibold text-gray-700 hover:text-amaranth-600 md:ms-2"
          >
            {{ level.name }}
          </RouterLink>
          <span v-else class="ms-1 text-sm font-medium text-gray-700 md:ms-2">
            {{ level.name }}
          </span>
        </div>
      </li>
    </ol>
  </nav>
</template>
