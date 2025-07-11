<script setup lang="ts">
import { MatchArrows, TournamentStage, TournamentType } from '@/models/constants'
import type { TournamentWithRelations } from '@/models/models'
import { ArrowDownIcon, ArrowUpIcon } from '@heroicons/vue/16/solid'
import StandardHeaders from './Standard.vue'
import TieBreakHeaders from './TieBreak.vue'

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
  <StandardHeaders
    v-if="[TournamentStage.QUALIFIERS, TournamentStage.FINALS].includes(stage as TournamentStage)"
    :tournament="tournament"
    :stage="stage"
    :current-stage="tournament.current_stage"
    :allow-sorting="allowSorting"
    :sorting="sorting"
    :reversed="reversed"
    :show-details="showDetails"
    @changeSort="changeSort"
  />
  <TieBreakHeaders
    v-else
    :tournament="tournament"
    :allow-sorting="allowSorting"
    :sorting="sorting"
    :reversed="reversed"
    :stage="stage"
    @changeSort="changeSort"
  />
</template>
