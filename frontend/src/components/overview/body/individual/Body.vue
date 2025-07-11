<script setup lang="ts">
import { TournamentStage } from '@/models/constants'
import type { TournamentWithRelations } from '@/models/models'
import StandardBody from './Standard.vue'
import TieBreakBody from './TieBreak.vue'

const { tournament, sorting, reversed, stage } = defineProps<{
  tournament: TournamentWithRelations
  sorting: 'id' | 'hits'
  reversed: boolean
  stage: string
  showDetails: boolean
}>()
</script>

<template>
  <StandardBody
    v-if="[TournamentStage.QUALIFIERS, TournamentStage.FINALS].includes(stage as TournamentStage)"
    :tournament="tournament"
    :sorting="sorting"
    :reversed="reversed"
    :stage="stage"
    :showDetails="showDetails"
  />
  <TieBreakBody
    v-else
    :tournament="tournament"
    :sorting="sorting"
    :reversed="reversed"
    :stage="stage"
  />
</template>
