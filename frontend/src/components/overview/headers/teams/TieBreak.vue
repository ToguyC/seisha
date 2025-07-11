<script setup lang="ts">
import { MatchFormat } from '@/models/constants'
import type { TournamentWithRelations } from '@/models/models'
import { ArrowDownIcon, ArrowUpIcon } from '@heroicons/vue/16/solid'

const { allowSorting, stage, tournament } = defineProps<{
  tournament: TournamentWithRelations
  allowSorting: boolean
  sorting: 'id' | 'hits'
  reversed: boolean
  stage: string
}>()

const emit = defineEmits<{
  changeSort: [sortBy: 'id' | 'hits']
}>()

const changeSort = (sortBy: 'id' | 'hits') => {
  if (!allowSorting) return
  emit('changeSort', sortBy)
}

const getIzumeRounds = () => {
  return tournament.matches
    .filter((match) => match.stage === stage)
    .filter((match) => match.format === MatchFormat.IZUME)
}
</script>

<template>
  <tr>
    <td
      rowspan="2"
      class="border w-10 hover:cursor-pointer"
      :class="{ 'bg-gray-200': allowSorting }"
      @click="changeSort('id')"
    >
      <div class="w-full flex justify-center items-center gap-2">
        <ArrowDownIcon class="h-5 w-5" v-if="sorting === 'id' && reversed && allowSorting" />
        <ArrowUpIcon class="h-5 w-5" v-if="sorting === 'id' && !reversed && allowSorting" />
        立番号
      </div>
    </td>
    <td rowspan="2" class="border">チーム名</td>
    <td rowspan="2" class="border w-10">
      <div class="w-full flex justify-center items-center gap-2">立順</div>
    </td>
    <td rowspan="2" class="border border-r-4">氏名</td>
    <td class="border w-10" v-for="i in Math.max(getIzumeRounds().length * 2, 2)">
      <span v-if="i % 2 === 1">{{ Math.ceil(i / 2) }}回目 射詰</span>
      <span v-else>小計</span>
    </td>
    <td v-if="stage !== tournament.current_stage" class="border border-l-4 w-16">格</td>
  </tr>
</template>
