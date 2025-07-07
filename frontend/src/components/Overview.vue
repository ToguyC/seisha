<script setup lang="ts">
import { TournamentFormat, TournamentStage } from '@/models/constants'
import type {
  Archer,
  ArcherWithTournamentData,
  Team,
  TournamentWithRelations,
} from '@/models/models'
import { ArrowDownIcon, ArrowUpIcon } from '@heroicons/vue/16/solid'
import { computed, ref } from 'vue'

const {
  tournament,
  stage,
  allowSorting = true,
} = defineProps<{
  tournament: TournamentWithRelations
  stage: string
  allowSorting?: boolean
}>()

const isIndividual = computed(() => tournament.format === 'individual')
const stageJap = computed(() => {
  switch (stage) {
    case 'qualifers':
    case 'qualifers_tie_break':
      return '予選'
    case 'finals':
    case 'finals_tie_break':
      return '決勝'
    default:
      break
  }
})

const sorting = ref<'id' | 'hits'>('id')
const reversed = ref(false)

const getArcherTeam = (archer: Archer) => {
  return tournament.teams.find((team) => team.archers.some((a) => a.archer.id === archer.id))
}

const getArcherNumber = (archer: ArcherWithTournamentData) => {
  if (isIndividual.value) {
    return archer.number
  }

  const team = getArcherTeam(archer.archer)
  return team?.archers.find((a) => a.archer.id === archer.archer.id)?.number || 0
}

const getArchers = () => {
  const filterParticipants = (p: ArcherWithTournamentData | Team) => {
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

  if (isIndividual.value) {
    return tournament.archers.filter(filterParticipants).sort((a, b) => {
      let compare = 0

      if (sorting.value === 'hits') {
        const ratioA = getHitCount(a.archer)[2]
        const ratioB = getHitCount(b.archer)[2]
        compare = ratioA - ratioB
      } else {
        compare = a.archer.id - b.archer.id
      }

      return reversed.value ? -compare : compare
    })
  }

  // Team tournament sorting
  let sortedTeams = [...tournament.teams].filter(filterParticipants)
  if (sorting.value === 'hits') {
    sortedTeams.sort((a, b) => {
      const ratioA = getTeamHitCount(a)[2]
      const ratioB = getTeamHitCount(b)[2]
      return reversed.value ? ratioB - ratioA : ratioA - ratioB
    })
  } else {
    sortedTeams.sort((a, b) => {
      return reversed.value ? b.number - a.number : a.number - b.number
    })
  }

  // Flatten archers, always sorted by archer number within team
  return sortedTeams.flatMap((team) => {
    return [...team.archers].sort((a, b) => a.number - b.number)
  })
}

const getTeamSize = (archer: Archer) => {
  const team = getArcherTeam(archer)
  return team ? team.archers.length : 1
}

const getHitCount = (archer: Archer) => {
  const allSeries = tournament.matches
    .filter((match) => match.stage === stage)
    .flatMap((match) => match.series)
    .filter((series) => series.archer.id === archer.id)

  const { hits, total } = allSeries.reduce(
    ({ hits, total }, series) => {
      const arrows = JSON.parse(series.arrows_raw) as number[]
      return { hits: hits + arrows.filter((a) => a === 1).length, total: total + arrows.length }
    },
    { hits: 0, total: 0 },
  )

  return [hits, total, hits / total || 0]
}

const getTeamHitCount = (team: Team) => {
  const { hits, total } = team.archers.reduce(
    (acc, a) => {
      const [archerHits, archerTotal] = getHitCount(a.archer)
      acc.hits += archerHits
      acc.total += archerTotal
      return acc
    },
    { hits: 0, total: 0 },
  )

  return [hits, total, hits / total || 0]
}

const changeSort = (newSort: 'id' | 'hits') => {
  if (!allowSorting) return

  if (sorting.value === newSort) {
    reversed.value = !reversed.value
  } else {
    sorting.value = newSort
    reversed.value = newSort === 'hits' // applying the reversed order by default if sorting by hits
  }
}

const getRank = (archer: ArcherWithTournamentData) => {
  const allArchers = getArchers()

  // Get hit counts for all archers
  const archersWithHits = allArchers.map((a) => ({
    archer: a,
    hits: getHitCount(a.archer)[0],
  }))

  // Sort by hits in descending order (highest hits first)
  archersWithHits.sort((a, b) => b.hits - a.hits)

  // Find the target archer's hits
  const targetHits = getHitCount(archer.archer)[0]

  // Calculate rank with proper tie handling
  let rank = 1
  for (let i = 0; i < archersWithHits.length; i++) {
    if (archersWithHits[i].hits > targetHits) {
      rank = i + 2 // +2 because we want the rank after this group
    } else if (archersWithHits[i].hits === targetHits) {
      // Found our target or someone with same hits
      break
    }
  }

  return rank
}

const isQualified = (archer: ArcherWithTournamentData) => {
  if (tournament.format === TournamentFormat.INDIVIDUAL) {
    return stage === TournamentStage.QUALIFIERS && archer.qualifiers_place !== null
  } else if (tournament.format === TournamentFormat.TEAM) {
    const archer_team = getArcherTeam(archer.archer)
    return stage === TournamentStage.QUALIFIERS && archer_team?.qualifiers_place !== null
  }
}

const isTieBreak = (archer: ArcherWithTournamentData) => {
  if (tournament.format === TournamentFormat.INDIVIDUAL) {
    return (
      (stage === TournamentStage.QUALIFIERS && archer.tie_break_qualifiers) ||
      (stage === TournamentStage.FINALS && archer.tie_break_finals)
    )
  } else if (tournament.format === TournamentFormat.TEAM) {
    const archer_team = getArcherTeam(archer.archer)
    return (
      (stage === TournamentStage.QUALIFIERS && archer_team?.tie_break_qualifiers) ||
      (stage === TournamentStage.FINALS && archer_team?.tie_break_finals)
    )
  }
  return false
}
</script>

<template>
  <table class="w-full border border-separate border-spacing-0">
    <thead class="text-center">
      <tr>
        <td
          v-if="!isIndividual"
          rowspan="2"
          class="border w-20 hover:cursor-pointer"
          :class="{ 'bg-gray-200': allowSorting }"
          @click="changeSort('id')"
        >
          <div class="w-full flex justify-center items-center gap-2">
            <ArrowDownIcon class="h-5 w-5" v-if="sorting === 'id' && reversed && allowSorting" />
            <ArrowUpIcon class="h-5 w-5" v-if="sorting === 'id' && !reversed && allowSorting" />
            {{ stageJap }}<br />立番号
          </div>
        </td>
        <td v-if="!isIndividual" rowspan="2" class="border w-32">チーム名</td>
        <td
          rowspan="2"
          class="border w-14"
          :class="{
            'hover:cursor-pointer': isIndividual,
            'bg-gray-200': isIndividual && allowSorting,
          }"
          @click="isIndividual && changeSort('id')"
        >
          <div class="w-full flex justify-center items-center gap-2">
            <ArrowDownIcon
              class="h-5 w-5"
              v-if="sorting === 'id' && reversed && isIndividual && allowSorting"
            />
            <ArrowUpIcon
              class="h-5 w-5"
              v-if="sorting === 'id' && !reversed && isIndividual && allowSorting"
            />
            立順
          </div>
        </td>
        <td rowspan="2" class="border w-48">氏名</td>
        <td v-if="!isIndividual" class="border w-20">小計</td>
        <td
          class="border w-16"
          v-if="isIndividual"
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
        <td class="border w-16">最大</td>
        <td
          class="border w-16"
          v-if="!isIndividual"
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
    </thead>
    <tbody class="text-center">
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
        <td
          v-if="!isIndividual && getArcherNumber(archer) === 1"
          class="border w-20"
          :rowspan="getTeamSize(archer.archer)"
        >
          {{ getArcherTeam(archer.archer)?.number }}
        </td>
        <td
          v-if="!isIndividual && getArcherNumber(archer) === 1"
          class="border w-32"
          :rowspan="getTeamSize(archer.archer)"
        >
          {{ getArcherTeam(archer.archer)?.name }}
        </td>
        <td class="border w-20">{{ getArcherNumber(archer) }}</td>
        <td class="border w-20 text-left pl-4">{{ archer.archer.name }}</td>
        <td class="border w-16">{{ getHitCount(archer.archer)[0] }}</td>
        <td class="border w-16">{{ getHitCount(archer.archer)[1] }}</td>
        <template v-if="!isIndividual && getArcherNumber(archer) === 1">
          <td class="border w-20" :rowspan="getTeamSize(archer.archer)">
            {{ getTeamHitCount(getArcherTeam(archer.archer)!)[0] }} /
            {{ getTeamHitCount(getArcherTeam(archer.archer)!)[1] }}
          </td>
        </template>
        <template v-if="!isIndividual && stage !== tournament.current_stage">
          <td v-if="getArcherNumber(archer) === 1" rowspan="2" class="border w-16">
            {{ getRank(archer) }}位
          </td>
          <td v-if="getArcherNumber(archer) === 1" rowspan="2" class="border w-16">
            <span v-if="isQualified(archer)"> Qualified </span>
            <span v-if="isTieBreak(archer)"> Tie Break </span>
          </td>
        </template>
        <template v-else>
          <td v-if="stage !== tournament.current_stage" class="border w-16">
            {{ getRank(archer) }}位
          </td>
          <td v-if="stage !== tournament.current_stage" class="border w-16">
            <span v-if="isQualified(archer)"> Qualified </span>
            <span v-if="isTieBreak(archer)"> Tie Break </span>
          </td>
        </template>
      </tr>
    </tbody>
  </table>
</template>
