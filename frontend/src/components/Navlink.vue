<script setup lang="ts">
const { to, name } = defineProps({
  to: {
    type: String,
    required: true,
  },
  name: String,
})
</script>

<template>
  <RouterLink :to="to" v-slot="{ isActive, navigate }" custom class="hover:cursor-pointer">
    <a
      @click="navigate"
      :class="[
        'font-semibold transition-color border-b-2 duration-100',
        isActive || ($route.fullPath.startsWith(to) && to !== '/')
          ? 'text-amaranth-500 border-amaranth-500'
          : 'text-gray-500 border-white hover:text-amaranth-500 hover:border-amaranth-500',
      ]"
    >
      {{ name }}
    </a>
  </RouterLink>
</template>
