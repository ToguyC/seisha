<script setup lang="ts">
import { postTournamentMatch } from '@/api/tournament'
import type { Archer, Match as MatchModel, TournamentWithRelations } from '@/models/models'
import { computed } from 'vue'

const { tournament } = defineProps<{
  tournament: TournamentWithRelations
}>()

const isIndividual = computed(() => {
  console.log(tournament)
  return tournament.format === 'individual'
})

const generateNextMatch = () => {
  postTournamentMatch(tournament.id)
    .then((res) => {
      console.log(res.data)
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const getArcherNumber = (archer: Archer) => {
  if (isIndividual.value) {
    return tournament.archers.find((a) => a.archer.id === archer.id)?.number || 0
  }

  const team = getArcherTeam(archer)
  return team?.archers.find((a) => a.archer.id === archer.id)?.number || 0
}

const getArcherSeries = (match: MatchModel, archer: Archer) => {
  return match.series.find((s) => s.archer.id === archer.id)
}

const getArcherTeam = (archer: Archer) => {
  return tournament.teams.find((team) => team.archers.some((a) => a.archer.id === archer.id))
}

const getArchers = (match: MatchModel) => {
  if (isIndividual.value) {
    return match.archers
  }

  // slice() to create a shallow copy of the array, avoiding in-place sorting
  const sortedByNumber = match.archers.slice().sort((a, b) => getArcherNumber(a) - getArcherNumber(b))
  const sortedByTeam = sortedByNumber.sort((a, b) => getArcherTeam(a)!.id - getArcherTeam(b)!.id)
  return sortedByTeam
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div class="text-xl font-bold text-gray-900 capitalize">Matches</div>
      <button
        class="w-30 flex items-center text-sm font-semibold justify-center gap-4 px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 hover:cursor-pointer"
        @click="generateNextMatch"
      >
        Next Match
      </button>
    </div>

    <div class="flex flex-col gap-4">
      <div v-for="match in tournament.matches">
        <table>
          <tbody class="text-center border [&>*]:border [&>*]:text-center">
            <tr class="[&>*]:border">
              <td class="w-20"></td>
              <td class="w-60"></td>
              <td class="w-40" v-if="!isIndividual"></td>
              <td class="w-40" colspan="2">予選一立目</td>
              <td class="w-40" colspan="2">予選二立目</td>
            </tr>
            <tr class="[&>*]:border">
              <td class="">立順</td>
              <td class="">氏名</td>
              <td class="" v-if="!isIndividual">チーム</td>
              <td class="">甲矢</td>
              <td class="">乙矢</td>
              <td class="">甲矢</td>
              <td class="">乙矢</td>
            </tr>

            <tr
              class="[&>*]:border"
              v-if="isIndividual"
              v-for="archer in getArchers(match).sort(
                (a, b) => getArcherNumber(a) - getArcherNumber(b),
              )"
              :key="archer.id"
            >
              <td class="">{{ getArcherNumber(archer) }}</td>
              <td class="">{{ archer.name }}</td>
              <td class="p-1" v-for="arr in JSON.parse(getArcherSeries(match, archer)!.arrows_raw)">
                <span v-if="arr == 1">◯</span>
                <span v-else-if="arr == 2">?</span>
                <span v-else>⨉</span>
              </td>
            </tr>

            <tr
              class="[&>*]:border"
              v-else
              v-for="archer in getArchers(match)"
              :key="'team' + archer.id"
            >
              <td>{{ getArcherNumber(archer) }}</td>
              <td>{{ archer.name }}</td>
              <td>{{ getArcherTeam(archer)?.name }}</td>
              <td class="p-1" v-for="arr in JSON.parse(getArcherSeries(match, archer)!.arrows_raw)">
                <span v-if="arr == 1">◯</span>
                <span v-else-if="arr == 2">?</span>
                <span v-else>⨉</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
