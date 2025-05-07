<script setup lang="ts">
import { getAllLiveTournaments } from '@/api/tournament';
import Match from '@/components/Match.vue'
import { onMounted } from 'vue';

onMounted(() => {
  getAllLiveTournaments()
    .then((tournaments) => {
      console.log('Tournaments:', tournaments);
    })
    .catch((error) => {
      console.error('Error fetching tournaments:', error);
    });
});
</script>

<template>
  <div class="my-10 mx-auto text-4xl font-bold">月来会　第１０回　定期弓道大会</div>

  <!-- <Match :shots="data" class="w-1/2 mx-auto" /> -->

  <div class="text-red-500">
    pour la partie client, mettre en place des socket pour automatiquement update le front quand un
    admin update un tournoi. Les sockets devront être créés lorsqu'un client affiche un tournoi en
    cours, un peu comme OGC ou Lishogi quand on regarde un tournoi en live. Aussi, sur la page
    d'accueil il serait bien de lister tout les tournois en cours. Retirer toutes les actions
    d'administration si utilitsateurs lambda
  </div>
</template>
