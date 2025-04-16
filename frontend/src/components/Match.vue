<script setup lang="ts">
import { onMounted, type PropType } from 'vue'

type Shot = {
  num: number
  name: string
  team: string
  arrows: number[]
}

const { shots } = defineProps({
  shots: {
    type: Array as PropType<Shot[]>,
    required: true,
  },
})

onMounted(() => {})
</script>

<template>
  <table class="mx-auto w-1/3">
    <tbody class="text-center border [&>*]:border [&>*]:text-center">
      <tr class="[&>*]:border">
        <td class="w-20"></td>
        <td class="w-60"></td>
        <td class="w-40"></td>
        <td class="w-40" colspan="2">予選一立目</td>
        <td class="w-40" colspan="2">予選二立目</td>
      </tr>
      <tr class="[&>*]:border">
        <td class="">立順</td>
        <td class="">氏名</td>
        <td class="">チーム</td>
        <td class="">甲矢</td>
        <td class="">乙矢</td>
        <td class="">甲矢</td>
        <td class="">乙矢</td>
      </tr>
      <tr class="[&>*]:border" v-for="item in shots" :key="item.num">
        <td class="">{{ item.num }}</td>
        <td class="">{{ item.name }}</td>
        <td class="">{{ item.team }}</td>
        <td class="p-1" v-for="arr in item.arrows">
          <span v-if="arr == 1">◯</span>
          <span v-else-if="arr == 2">?</span>
          <span v-else>⨉</span>
        </td>
      </tr>
    </tbody>
  </table>
</template>
