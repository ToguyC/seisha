<script setup lang="ts">
import type { TournamentWithRelations } from '@/models/models';
import { ArrowDownIcon, ArrowUpIcon } from '@heroicons/vue/16/solid';

const { allowSorting } = defineProps<{
  tournament: TournamentWithRelations
  allowSorting: boolean
  sorting: 'id' | 'hits'
  reversed: boolean
  stage: string
  currentStage: string
}>()

const emit = defineEmits<{
  changeSort: [sortBy: 'id' | 'hits']
}>()

const changeSort = (sortBy: 'id' | 'hits') => {
  if (!allowSorting) return
  emit('changeSort', sortBy)
}
</script>

<template>
  <tr>
    <td
      rowspan="2"
      class="border w-20 hover:cursor-pointer"
      :class="{ 'bg-gray-200': allowSorting }"
      @click="changeSort('id')"
    >
      <div class="w-full flex justify-center items-center gap-2">
        <ArrowDownIcon class="h-5 w-5" v-if="sorting === 'id' && reversed && allowSorting" />
        <ArrowUpIcon class="h-5 w-5" v-if="sorting === 'id' && !reversed && allowSorting" />
        立番号
      </div>
    </td>
    <td rowspan="2" class="border w-32">チーム名</td>
    <td rowspan="2" class="border w-14">
      <div class="w-full flex justify-center items-center gap-2">立順</div>
    </td>
    <td rowspan="2" class="border w-48">氏名</td>
    <td class="border w-20">小計</td>
    <td class="border w-16">最大</td>
    <td
      class="border w-16"
      :class="{
        'hover:cursor-pointer bg-gray-200': allowSorting,
      }"
      @click="changeSort('hits')"
    >
      <div class="w-full flex justify-center items-center gap-2">
        <ArrowDownIcon class="h-5 w-5" v-if="sorting === 'hits' && reversed && allowSorting" />
        <ArrowUpIcon class="h-5 w-5" v-if="sorting === 'hits' && !reversed && allowSorting" />
        合計
      </div>
    </td>
    <td v-if="stage !== currentStage" class="border w-16">順位</td>
    <td v-if="stage !== currentStage" class="border w-16">格</td>
  </tr>
</template>
