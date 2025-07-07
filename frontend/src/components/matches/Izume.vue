<script setup lang="ts">
import { MatchArrows, type HitOutcome } from '@/models/constants'
import type { Archer, Match, Team, TournamentWithRelations } from '@/models/models'
import { ref } from 'vue'
import ArrowIndicator from '@/components/matches/ArrowIndicator.vue'
import NewArrow from '@/components/matches/NewArrow.vue'

const { getArcherSeriesArrows } = defineProps<{
  match: Match
  isIndividual: boolean
  readonly: boolean
  matchStageName: (match: Match) => string | undefined
  getArchers: (match: Match) => Archer[]
  getTeamSize: (archer: Archer) => number
  getArcherNumber: (archer: Archer) => number
  getArcherTeam: (archer: Archer) => Team | undefined
  getArcherSeriesArrows: (match: Match, archer: Archer) => HitOutcome[]
  setArrowOutcome: (match: Match, archer: Archer, arrowIndex: number, outcome: HitOutcome) => void
  getTotalArrows: (match: Match, team: Team, archer: Archer) => number
  getTotalUnkowns: (match: Match, team: Team, archer: Archer) => number
  shotArrow: (match: Match, archer: Archer, outcome: HitOutcome) => void
}>()

const mouseHoverArrow = ref<{ match: number; archer: number; arrow: number } | null>(null)

const remainingArrows = (match: Match, archer: Archer) => {
  const seriesArrows = getArcherSeriesArrows(match, archer)
  const maxArrows = MatchArrows.IZUME

  return maxArrows - seriesArrows.length
}
</script>

<template>
  <table class="w-full border border-separate border-spacing-0">
    <thead class="text-center">
      <tr>
        <td class="border w-20" v-if="!isIndividual">
          {{ matchStageName(match) }}<br />立番号
        </td>
        <td class="border w-32"  v-if="!isIndividual">チーム名</td>
        <td class="border w-14" >立順</td>
        <td class="border w-48" >氏名</td>
        <td class="border w-20">甲矢</td>
      </tr>
    </thead>
    <tbody class="text-center">
      <tr v-for="(archer, shajoPlace) in getArchers(match)" :key="archer.id">
        <td
          class="border w-20"
          :rowspan="getTeamSize(archer)"
          v-if="!isIndividual && getArcherNumber(archer) === 1"
        >
          {{ getArcherTeam(archer)?.number }}
        </td>
        <td
          class="border w-32"
          :rowspan="getTeamSize(archer)"
          v-if="!isIndividual && getArcherNumber(archer) === 1"
        >
          {{ getArcherTeam(archer)?.name }}
        </td>
        <td class="border w-14">{{ shajoPlace + 1 }}</td>
        <td class="border w-48 text-left pl-4">{{ archer.name }}</td>
        <td
          class="border w-20"
          v-for="(outcome, i) in getArcherSeriesArrows(match, archer)"
          @mouseenter="mouseHoverArrow = { match: match.id, archer: archer.id, arrow: i }"
          @mouseleave="mouseHoverArrow = null"
        >
          <ArrowIndicator
            :match="match"
            :archer="archer"
            :arrowNumber="i"
            :outcome="outcome"
            :readonly="readonly"
            :mouseHoverArrow="mouseHoverArrow"
            @setArrowOutcome="setArrowOutcome"
          ></ArrowIndicator>
        </td>
        <td class="border w-20" v-if="!readonly && remainingArrows(match, archer) > 0">
          <NewArrow :match="match" :archer="archer" @shotArrow="shotArrow"></NewArrow>
        </td>
        <td
          class="border w-20"
          v-if="remainingArrows(match, archer) > 0"
          v-for="_ in remainingArrows(match, archer) - (readonly ? 0 : 1)"
        ></td>
      </tr>
    </tbody>
  </table>
</template>
