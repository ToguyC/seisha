<script setup lang="ts">
import { HitOutcome } from '@/models/constants'
import type { Archer, Match } from '@/models/models'

const { readonly, mouseHoverArrow } = defineProps<{
  match: Match
  archer: Archer
  arrowNumber: number
  outcome: HitOutcome
  readonly: boolean
  mouseHoverArrow: { match: number; archer: number; arrow: number } | null
}>()

const emit = defineEmits<{
  setArrowOutcome: [match: Match, archer: Archer, arrowIndex: number, outcome: HitOutcome]
}>()

const setArrowOutcome = (match: Match, archer: Archer, arrowIndex: number, outcome: HitOutcome) => {
  emit('setArrowOutcome', match, archer, arrowIndex, outcome)
}

const isMouseHoveringCell = (match: Match, archer: Archer, arrowIndex: number) => {
  return (
    !readonly &&
    mouseHoverArrow !== null &&
    mouseHoverArrow.match === match.id &&
    mouseHoverArrow.archer === archer.id &&
    mouseHoverArrow.arrow === arrowIndex
  )
}

const arrowCycleUI = (arrowState: HitOutcome) => {
  switch (arrowState) {
    case HitOutcome.MISS:
      return '⨉'
    case HitOutcome.HIT:
      return '◯'
    case HitOutcome.ENSURE:
      return '?'
  }
}
</script>

<template>
  <div class="w-full h-full">
    <div
      class="flex bg-orange-100 text-orange-700 font-semibold hover:cursor-pointer"
      v-if="isMouseHoveringCell(match, archer, arrowNumber)"
    >
      <div
        class="w-1/2 hover:bg-orange-200 hover:text-orange-800 hover:font-bold"
        :class="{ hidden: outcome === HitOutcome.MISS }"
        @click="setArrowOutcome(match, archer, arrowNumber, HitOutcome.MISS)"
      >
        ⨉
      </div>
      <div
        class="w-1/2 hover:bg-orange-200 hover:text-orange-800 hover:font-bold"
        :class="{ hidden: outcome === HitOutcome.HIT }"
        @click="setArrowOutcome(match, archer, arrowNumber, HitOutcome.HIT)"
      >
        ◯
      </div>
      <div
        class="w-1/2 hover:bg-orange-200 hover:text-orange-800 hover:font-bold"
        :class="{ hidden: outcome === HitOutcome.ENSURE }"
        @click="setArrowOutcome(match, archer, arrowNumber, HitOutcome.ENSURE)"
      >
        ?
      </div>
    </div>
    <div v-else class="flex justify-center items-center">{{ arrowCycleUI(outcome) }}</div>
  </div>
</template>
