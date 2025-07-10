<script setup lang="ts">
import { TournamentFormat, TournamentStage } from '@/models/constants'
import type {
  Archer,
  ArcherWithTournamentData,
  Team,
  TournamentWithRelations,
} from '@/models/models'
import { computed, ref } from 'vue'
import IndividualHeaders from './overview-headers/IndividualHeaders.vue'
import TeamsHeaders from './overview-headers/TeamsHeaders.vue'
import IndividualBody from './overview-body/IndividualBody.vue'
import TeamsBody from './overview-body/TeamsBody.vue'

const {
  tournament,
  stage,
  allowSorting = true,
} = defineProps<{
  tournament: TournamentWithRelations
  stage: string
  allowSorting: boolean
  showDetails: boolean
}>()

const isIndividual = computed(() => tournament.format === 'individual')

const sorting = ref<'id' | 'hits'>('id')
const reversed = ref(false)

const changeSort = (newSort: 'id' | 'hits') => {
  if (!allowSorting) return

  if (sorting.value === newSort) {
    reversed.value = !reversed.value
  } else {
    sorting.value = newSort
    reversed.value = newSort === 'hits' // applying the reversed order by default if sorting by hits
  }
}
</script>

<template>
  <table class="w-full border border-separate border-spacing-0">
    <thead class="text-center">
      <IndividualHeaders
        v-if="isIndividual"
        :tournament="tournament"
        :stage="stage"
        :current-stage="tournament.current_stage"
        :allowSorting="allowSorting"
        :sorting="sorting"
        :reversed="reversed"
        :show-details="showDetails"
        @changeSort="changeSort"
      />
      <TeamsHeaders
        v-else
        :tournament="tournament"
        :stage="stage"
        :current-stage="tournament.current_stage"
        :allowSorting="allowSorting"
        :sorting="sorting"
        :reversed="reversed"
        :show-details="showDetails"
        @changeSort="changeSort"
      />
    </thead>
    <tbody class="text-center">
      <IndividualBody
        v-if="isIndividual"
        :tournament="tournament"
        :stage="stage"
        :sorting="sorting"
        :reversed="reversed"
        :show-details="showDetails"
      />
      <TeamsBody
        v-else
        :tournament="tournament"
        :stage="stage"
        :sorting="sorting"
        :reversed="reversed"
        :show-details="showDetails"
      />
    </tbody>
  </table>
</template>
