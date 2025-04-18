<script setup lang="ts">
import Match from '@/components/Match.vue'
import { onMounted } from 'vue'

const data = [
  { num: 21, name: 'Tanguy Cavagna', team: 'KKPLO', arrows: [1, 0, 0, 1] },
  { num: 22, name: 'Alexandre Illi', team: 'KKPLO', arrows: [1, 1, 1, 0] },
  { num: 23, name: 'Pierre Guillot', team: 'KKPLO', arrows: [0, 1, 1, 1] },
  { num: 24, name: 'Carmen Castillo', team: 'KKPLO', arrows: [0, 0, 1, 1] },
  { num: 25, name: 'Sabine Bouron', team: 'KKPLO', arrows: [1, 0, 1, 0] },
]

onMounted(() => {

})
</script>

<template>
  <div class="my-10 mx-auto text-4xl font-bold">月来会　第１０回　定期弓道大会</div>

  <Match :shots="data" class="w-1/2 mx-auto" />

  <div class="text-red-500">pour la partie client, mettre en place des socket pour automatiquement update le front quand un admin update un tournoi. Les sockets devront être créés lorsqu'un client affiche un tournoi en cours, un peu comme OGC ou Lishogi quand on regarde un tournoi en live. Aussi, sur la page d'accueil il serait bien de lister tout les tournois en cours.</div>
</template>
