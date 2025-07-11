<script setup lang="ts">
import { MatchArrows, TournamentStage, TournamentType } from '@/models/constants';
import type { TournamentWithRelations } from '@/models/models';
import { ArrowDownIcon, ArrowUpIcon } from '@heroicons/vue/16/solid';

const { allowSorting, stage, tournament } = defineProps<{
  tournament: TournamentWithRelations
  allowSorting: boolean
  sorting: 'id' | 'hits'
  reversed: boolean
  stage: string
  showDetails: boolean
}>()

const emit = defineEmits<{
  changeSort: [sortBy: 'id' | 'hits']
}>()

const changeSort = (sortBy: 'id' | 'hits') => {
  if (!allowSorting) return
  emit('changeSort', sortBy)
}

const getMatchArrowsFromTournamentType = (type: TournamentType) => {
  return MatchArrows[
    Object.keys(TournamentType)[
      Object.values(TournamentType).indexOf(type)
    ] as keyof typeof MatchArrows
  ]
}

const getRounds = () => {
  if (stage === TournamentStage.QUALIFIERS) {
    return tournament.qualifiers_round_count
  } else if (stage === TournamentStage.FINALS) {
    return tournament.finals_round_count
  }

  return 0
}
</script>

<template>
  <tr>
    <td
      rowspan="2"
      class="border w-16 hover:cursor-pointer"
      :class="{ 'bg-gray-200': allowSorting }"
      @click="changeSort('id')"
    >
      <div class="w-full flex justify-center items-center gap-2">
        <ArrowDownIcon class="h-5 w-5" v-if="sorting === 'id' && reversed && allowSorting" />
        <ArrowUpIcon class="h-5 w-5" v-if="sorting === 'id' && !reversed && allowSorting" />
        立番号
      </div>
    </td>
    <td rowspan="2" class="border w-20">チーム名</td>
    <td rowspan="2" class="border w-14">
      <div class="w-full flex justify-center items-center gap-2">立順</div>
    </td>
    <td rowspan="2" class="border border-r-4 w-48">氏名</td>
    <td
      v-for="i in getRounds() * (showDetails ? 2 : 1)"
      class="border"
      :class="{
        'border-r-4': true,
      }"
      :colspan="i % 2 == 1 && showDetails ? getMatchArrowsFromTournamentType(tournament.type) : 1"
    >
      <span v-if="i % 2 == 1 && showDetails"> {{ i }}回目 </span>
      <span v-else>小計</span>
    </td>
    <td class="border w-20">小計</td>
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
    <td v-if="stage !== tournament.current_stage" class="border w-16">順位</td>
    <td v-if="stage !== tournament.current_stage" class="border w-16">格</td>
  </tr>
</template>
