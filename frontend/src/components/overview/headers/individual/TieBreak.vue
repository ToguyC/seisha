<script setup lang="ts">
import { TournamentStage } from '@/models/constants'
import type { TournamentWithRelations } from '@/models/models';
import { ArrowDownIcon, ArrowUpIcon } from '@heroicons/vue/16/solid'

const { allowSorting, stage } = defineProps<{
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
</script>

<template>
  <tr>
    <td
      class="border w-10 hover:cursor-pointer"
      :class="{
        'bg-gray-200': allowSorting,
      }"
      @click="changeSort('id')"
    >
      <div class="w-full flex justify-center items-center gap-2">
        <ArrowDownIcon class="h-5 w-5" v-if="sorting === 'id' && reversed && allowSorting" />
        <ArrowUpIcon class="h-5 w-5" v-if="sorting === 'id' && !reversed && allowSorting" />
        立順
      </div>
    </td>
    <td rowspan="2" class="border border-r-4 w-48">氏名</td>
    <td class="border w-10" v-if="stage === TournamentStage.FINALS_TIE_BREAK">射詰</td>
    <td
      class="border w-10 hover:cursor-pointer"
      :class="{
        'bg-gray-200': allowSorting,
      }"
      @click="changeSort('hits')"
      v-if="
        stage === TournamentStage.QUALIFIERS_TIE_BREAK || stage === TournamentStage.FINALS_TIE_BREAK
      "
    >
      <div class="w-full flex justify-center items-center gap-2">
        <ArrowDownIcon class="h-5 w-5" v-if="sorting === 'hits' && reversed && allowSorting" />
        <ArrowUpIcon class="h-5 w-5" v-if="sorting === 'hits' && !reversed && allowSorting" />
        遠近
      </div>
    </td>
    <td v-if="stage !== tournament.current_stage" class="border border-l-4 w-16">格</td>
  </tr>
</template>
