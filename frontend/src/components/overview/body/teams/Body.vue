<script setup lang="ts">
import { HitOutcome, TournamentStage } from '@/models/constants'
import type {
  Archer,
  ArcherWithTournamentData,
  Team,
  TournamentWithRelations,
} from '@/models/models'
import { computed } from 'vue'
import Standard from './Standard.vue'
import TieBreak from './TieBreak.vue'

const { tournament, sorting, reversed, stage } = defineProps<{
  tournament: TournamentWithRelations
  sorting: 'id' | 'hits'
  reversed: boolean
  stage: string
  showDetails: boolean
}>()
</script>

<template>
  <Standard
    v-if="[TournamentStage.QUALIFIERS, TournamentStage.FINALS].includes(stage as TournamentStage)"
    :tournament="tournament"
    :stage="stage"
    :sorting="sorting"
    :reversed="reversed"
    :show-details="showDetails"
  />
  <TieBreak
    v-else
    :tournament="tournament"
    :allow-sorting="true"
    :sorting="sorting"
    :reversed="reversed"
    :stage="stage"
  />
</template>
