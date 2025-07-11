<script setup lang="ts">
import { TournamentStage } from '@/models/constants'
import type { TournamentWithRelations } from '@/models/models'
import StandardHeaders from './Standard.vue'
import TieBreaksHeaders from './TieBreak.vue'

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
  <TieBreaksHeaders
    v-else
    :tournament="tournament"
    :allow-sorting="allowSorting"
    :sorting="sorting"
    :reversed="reversed"
    :stage="stage"
    @changeSort="changeSort"
  />
</template>
