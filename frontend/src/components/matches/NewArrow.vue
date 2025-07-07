<script setup lang="ts">
import { HitOutcome } from '@/models/constants'
import type { Archer, Match } from '@/models/models'

defineProps<{
  match: Match
  archer: Archer
}>()

const emit = defineEmits<{
  shotArrow: [match: Match, archer: Archer, outcome: HitOutcome]
}>()

const shotArrow = (match: Match, archer: Archer, outcome: HitOutcome) => {
  emit('shotArrow', match, archer, outcome)
}
</script>

<template>
  <div
    class="w-full h-full flex items-center bg-blue-100 text-blue-700 font-semibold hover:cursor-pointer"
  >
    <div
      class="w-1/3 hover:text-blue-800 hover:bg-blue-200 hover:font-bold"
      @click="shotArrow(match, archer, HitOutcome.MISS)"
    >
      ⨉
    </div>
    <div
      class="w-1/3 hover:text-blue-800 hover:bg-blue-200 hover:font-bold"
      @click="shotArrow(match, archer, HitOutcome.HIT)"
    >
      ◯
    </div>
    <div
      class="w-1/3 hover:text-blue-800 hover:bg-blue-200 hover:font-bold"
      @click="shotArrow(match, archer, HitOutcome.ENSURE)"
    >
      ?
    </div>
  </div>
</template>
