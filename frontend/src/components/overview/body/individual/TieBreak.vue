<script setup lang="ts">
import { HitOutcome, MatchFormat, TournamentStage } from '@/models/constants'
import type { Archer, ArcherWithTournamentData, TournamentWithRelations } from '@/models/models'
import { computed } from 'vue'

const { tournament, sorting, reversed, stage } = defineProps<{
  tournament: TournamentWithRelations
  sorting: 'id' | 'hits'
  reversed: boolean
  stage: string
}>()

const enkinRanks = computed(() => {
  const enkinMatches = tournament.matches.filter(
    (match) =>
      match.stage === TournamentStage.QUALIFIERS_TIE_BREAK ||
      match.stage === TournamentStage.FINALS_TIE_BREAK,
  )

  const enkinRanks = new Map<number, number | undefined>()

  enkinMatches.forEach((match) => {
    match.series.forEach((series) => {
      const archerId = series.archer.id
      const rank = JSON.parse(series.arrows_raw)[0] || undefined
      enkinRanks.set(archerId, rank)
    })
  })

  return enkinRanks
})

const getArchers = () => {
  const filterParticipants = (p: ArcherWithTournamentData) => {
    if (stage === TournamentStage.QUALIFIERS || tournament.advancing_count === null) {
      return true
    } else if (stage === TournamentStage.QUALIFIERS_TIE_BREAK) {
      return p.tie_break_qualifiers
    } else if (stage === TournamentStage.FINALS) {
      return p.qualifiers_place !== null
    } else if (stage === TournamentStage.FINALS_TIE_BREAK) {
      return p.tie_break_finals
    }
    return false
  }

  return tournament.archers.filter(filterParticipants).sort((a, b) => {
    let compare = 0

    if (sorting === 'hits') {
      const ratioA = enkinRanks.value.get(a.archer.id) || 0
      const ratioB = enkinRanks.value.get(b.archer.id) || 0
      compare = ratioA - ratioB
    } else {
      compare = a.archer.id - b.archer.id
    }

    return reversed ? -compare : compare
  })
}

const isQualified = (archer: ArcherWithTournamentData) => {
  return (
    [TournamentStage.QUALIFIERS, TournamentStage.QUALIFIERS_TIE_BREAK].includes(
      stage as TournamentStage,
    ) && archer.qualifiers_place !== null
  )
}

const isTieBreak = (archer: ArcherWithTournamentData) => {
  return (
    (stage === TournamentStage.QUALIFIERS && archer.tie_break_qualifiers) ||
    (stage === TournamentStage.FINALS && archer.tie_break_finals)
  )
}
</script>

<template>
  <tr
    v-for="archer in getArchers()"
    :key="archer.archer.id"
    :class="{
      'bg-emerald-500/50': isQualified(archer),
      'bg-gray-400/50': isTieBreak(archer),
      'bg-amber-400/50': stage === TournamentStage.FINALS && archer.finals_place === 1,
      'bg-slate-400/50': stage === TournamentStage.FINALS && archer.finals_place === 2,
      'bg-amber-800/50': stage === TournamentStage.FINALS && archer.finals_place === 3,
    }"
  >
    <td class="border w-10">{{ archer.number }}</td>
    <td class="border border-r-4 w-20 text-left pl-4">{{ archer.archer.name }}</td>
    <td class="border w-10 font-semibold">
      {{ enkinRanks.get(archer.archer.id) !== undefined ? enkinRanks.get(archer.archer.id) : '-' }}
    </td>
    <td v-if="stage !== tournament.current_stage" class="border border-l-4 w-16">
      <span v-if="isQualified(archer)"> Qualified </span>
      <span v-if="isTieBreak(archer)"> Tie Break </span>
    </td>
  </tr>
</template>
