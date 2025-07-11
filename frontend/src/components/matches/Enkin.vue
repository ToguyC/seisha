<script setup lang="ts">
import { setEnkinPlace as _setEnkinPlace } from '@/api/match'
import { TournamentFormat, type HitOutcome } from '@/models/constants'
import type { Archer, Match, Team, Tournament } from '@/models/models'
import { computed, ref } from 'vue'

const { tournament, match, getArchers } = defineProps<{
  tournament: Tournament
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

const emit = defineEmits<{
  fetchTournament: [tournamentId: number]
}>()

const fetchTournament = () => {
  emit('fetchTournament', tournament.id)
}

const ranking = ref<Record<number, number>>(
  Object.assign(
    {},
    ...match.archers.map((a) => {
      const arrows_raw = match.series.find((s) => s.archer.id === a.id)?.arrows_raw
      const place = arrows_raw ? JSON.parse(arrows_raw)[0] : -1
      return { [a.id]: place }
    }),
  ),
)

const archersCount = computed(() => {
  return getArchers(match).length
})

const setEnkinPlace = (archer: Archer) => {
  const place = ranking.value[archer.id]

  if (place < 0 || place > archersCount.value) {
    console.warn('Invalid place selected:', place)
    return
  }

  _setEnkinPlace(match.id, archer.id, place)
    .then(() => {
      ranking.value[archer.id] = place
      fetchTournament()
    })
    .catch((error) => {
      console.error('Failed to set enkin place:', error)
    })
}
</script>

<template>
  ENKIN
  <table class="w-full border border-separate border-spacing-0">
    <thead class="text-center">
      <tr>
        <td class="border w-20" v-if="!isIndividual">{{ matchStageName(match) }}<br />立番号</td>
        <td class="border w-32" v-if="!isIndividual">チーム名</td>
        <td class="border w-14">立順</td>
        <td class="border w-48">氏名</td>
        <td class="border w-20">遠近順位</td>
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
        <td class="border w-20 px-4">
          <select
            v-if="!readonly"
            :select-options="ranking[archer.id] >= 0 ? ranking[archer.id] : -1"
            class="w-full"
            name="ranking"
            id="ranking"
            v-model="ranking[archer.id]"
            @change="setEnkinPlace(archer)"
          >
            <option value="-1" disabled>Select Rank</option>
            <option :value="i" v-for="i in archersCount">{{ i }}</option>
          </select>
          <span v-else>{{ ranking[archer.id] >= 0 ? ranking[archer.id] : '-' }}</span>
        </td>
      </tr>
    </tbody>
  </table>
</template>
