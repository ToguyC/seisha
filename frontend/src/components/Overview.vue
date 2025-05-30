<script setup lang="ts">
import type { Archer, ArcherWithNumber, Team, TournamentWithRelations } from '@/models/models'
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
      return '予選'
    case 'finals':
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

const getArcherNumber = (archer: ArcherWithNumber) => {
  if (isIndividual.value) {
    return archer.number
  }

  const team = getArcherTeam(archer.archer)
  return team?.archers.find((a) => a.archer.id === archer.archer.id)?.number || 0
}

const getArchers = () => {
  if (isIndividual.value) {
    return tournament.archers.sort((a, b) => {
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
  let sortedTeams = [...tournament.teams]
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
          :class="{ 'hover:cursor-pointer': isIndividual, 'bg-gray-200': isIndividual && allowSorting }"
          @click="isIndividual && changeSort('id')"
        >
          <div class="w-full flex justify-center items-center gap-2">
            <ArrowDownIcon class="h-5 w-5" v-if="sorting === 'id' && reversed && isIndividual && allowSorting" />
            <ArrowUpIcon class="h-5 w-5" v-if="sorting === 'id' && !reversed && isIndividual && allowSorting" />
            立順
          </div>
        </td>
        <td rowspan="2" class="border w-48">氏名</td>
        <td v-if="!isIndividual" colspan="2" class="border">個人</td>
        <td
          v-if="!isIndividual"
          rowspan="2"
          class="border w-20 hover:cursor-pointer"
          :class="{ 'bg-gray-200': allowSorting }"
          @click="changeSort('hits')"
        >
          <div class="w-full flex justify-center items-center gap-2">
            <ArrowDownIcon class="h-5 w-5" v-if="sorting === 'hits' && reversed && allowSorting" />
            <ArrowUpIcon class="h-5 w-5" v-if="sorting === 'hits' && !reversed && allowSorting" />
            的中
          </div>
        </td>
        <td v-if="!isIndividual" rowspan="2" class="border w-20">割合（％）</td>
      </tr>
      <tr>
        <td
          class="border w-16 hover:cursor-pointer"
          :class="{ 'hover:cursor-pointer': isIndividual, 'bg-gray-200': isIndividual && allowSorting }"
          @click="isIndividual && changeSort('hits')"
        >
          <div class="w-full flex justify-center items-center gap-2">
            <ArrowDownIcon class="h-5 w-5" v-if="sorting === 'hits' && reversed && isIndividual && allowSorting" />
            <ArrowUpIcon class="h-5 w-5" v-if="sorting === 'hits' && !reversed && isIndividual && allowSorting" />
            的中
          </div>
        </td>
        <td class="border w-16">合計</td>
        <td v-if="isIndividual" rowspan="2" class="border w-16">割合（％）</td>
      </tr>
    </thead>
    <tbody class="text-center">
      <tr v-for="archer in getArchers()" :key="archer.archer.id">
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
        <td class="border w-20">{{ archer.archer.name }}</td>
        <td class="border w-16">{{ getHitCount(archer.archer)[0] }}</td>
        <td class="border w-16">{{ getHitCount(archer.archer)[1] }}</td>
        <td v-if="isIndividual" class="border w-16">{{ (getHitCount(archer.archer)[2] * 100).toFixed(1) }}</td>
        <template v-if="!isIndividual && getArcherNumber(archer) === 1">
          <td class="border w-20" :rowspan="getTeamSize(archer.archer)">
            {{ getTeamHitCount(getArcherTeam(archer.archer)!)[0] }} /
            {{ getTeamHitCount(getArcherTeam(archer.archer)!)[1] }}
          </td>
          <td class="border w-20" :rowspan="getTeamSize(archer.archer)">
            {{ (getTeamHitCount(getArcherTeam(archer.archer)!)[2] * 100).toFixed(1) }}
          </td>
        </template>
      </tr>
    </tbody>
  </table>
</template>
