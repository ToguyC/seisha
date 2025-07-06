<script setup lang="ts">
import { getAllLiveTournaments } from '@/api/tournament'
import Match from '@/components/Match.vue'
import type { TournamentWithRelations, Match as MatchModel } from '@/models/models'
import { ws } from '@/plugins/sockets'
import { onMounted, ref } from 'vue'

const liveTournaments = ref<TournamentWithRelations[]>([])
const lastMatch = ref<MatchModel | null>(null)

const getUnfinishedMatches = (tournament: TournamentWithRelations) => {
  return tournament.matches.filter((m) => !m.finished)
}

const getLastMatch = (tournament: TournamentWithRelations) => {
  const matches = tournament.matches
  return matches.length > 0 ? matches[matches.length - 1] : null
}

const fetchLiveTournaments = () => {
  getAllLiveTournaments()
    .then((res) => {
      liveTournaments.value = res.data
    })
    .catch((error) => {
      console.error('Error fetching tournaments:', error)
    })
}

onMounted(() => {
  ws.onmessage = (ev: MessageEvent) => {
    const data = JSON.parse(ev.data)

    if (['new arrow', 'new match', 'arrow update', 'match finished'].includes(data.event)) {
      fetchLiveTournaments()
    }
  }

  fetchLiveTournaments()
})
</script>

<template>
  <div>
    <div class="text-red-500 font-bold">
      TODO
      <ol class="list-decimal list-inside">
        <li class="my-2">
          Si tie-break. La création de ces matchs ne doit prendre en compte que les participants à
          départager.

          <ul class="list-disc list-inside pl-4">
            <li>
              Si individuel : créer un match mort-subite (nombre de flèches inconnu). Si après un
              certain nombre de flèches il y a toujours égalité, faire un match enkin (1 seule
              flèche par archer).
            </li>
            <li>
              Si équipe : créer un match simple. Si après un certain nombre de flèches il y a
              toujours égalité, faire un match enkin (1 seule flèche par archer). L'archer avec la
              flèche la plus proche du centre faire remporter son équipe.
            </li>
          </ul>

          À ce moment, il est nécessaire de pouvoir choisir le type de match à créer (mort-subite ou
          enkin).
        </li>
        <li class="my-2">
          Bouton pour terminer le tie-break si il y a eu, et assigner les places des finalistes
          restantes.
        </li>
        <li class="my-2">
          Phase finale en élimination directe.

          <ul class="list-disc list-inside pl-4">
            <li>
              Générer l'ordre de rencontre du bracket comme étant : 1er vs dernier, 2ème vs
              avant-dernier, etc
            </li>
            <li>La création d'un match simple se fait maintenant sur cet ordre.</li>
            <li>
              Après chaque match, le gagnant est déterminé par le nombre de flèches marquées. En cas
              d'égalité, le match est prolongé par un match mort-subite (nombre de flèches inconnu).
              Si après un certain nombre de flèches il y a toujours égalité, faire un match enkin (1
              seule flèche par archer). L'archer avec la flèche la plus proche du centre faire
              remporter son équipe.
            </li>
            <li>
              Assigner les places des participants perdants basée sur le nombre de flèches marquées
              sur ce round.
            </li>
            <li>
              Recommencer les matchs à éliminations directe en matchant comme un bracket, jusqu'à ce
              qu'il n'en reste qu'1. Pas de match pour la 3ème place, les participants en
              demi-finale sont 3ème.
            </li>
          </ul>
        </li>
        <li class="my-2">Avoir un affichage en brackets pour la phase finale.</li>
        <li class="my-2">Avoir un tableau récapitulatif de la phase finale.</li>
        <li class="my-2">
          Pouvoir exporter les tableaux récapitulatif des qualifs, finales, et brackets en un seul
          PDF (avec infos du tournoi en premier page).
        </li>
      </ol>
    </div>
    <div class="w-full flex flex-col items-center justify-center gap-6">
      <div class="text-3xl font-bold uppercase">Live tournaments</div>

      <div class="flex flex-col divide-y divide-gray-500">
        <div class="py-10 flex flex-col gap-4" v-for="tournament in liveTournaments">
          <div class="text-xl font-semibold">{{ tournament.name }}</div>

          <Match
            v-for="match of getUnfinishedMatches(tournament)"
            :match="match"
            :tournament="tournament"
            :readonly="true"
            :key="match.id"
          />
          <div
            class="flex flex-col justify-center items-center gap-4"
            v-if="getUnfinishedMatches(tournament).length === 0"
          >
            <p class="text-xl">Last played match</p>
            <Match
              v-if="lastMatch = getLastMatch(tournament)"
              :match="lastMatch"
              :tournament="tournament"
              :readonly="true"
              :key="getLastMatch(tournament)?.id"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
