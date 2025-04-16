<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/base'

const route = useRoute()

const tournament = ref({
  id: 0,
  name: '',
  date: '',
  archers: [],
})

onMounted(() => {
  const tournamentId = route.params.id

  api
    .get(`/tournaments/${tournamentId}`)
    .then((res) => {
      tournament.value = res.data
      console.log(res.data)
    })
    .catch((err) => {
      console.error(err.message)
    })
})
</script>

<template>
    {{ tournament }}
</template>
