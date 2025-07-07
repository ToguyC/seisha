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

      <div class="text-3xl">
        Point 1 à faire et ensuite modifier l'overview pour virer le nombre de flèches max possible.
        A la place, mettre le nombre de flèches max calculé basé sur le format et le nombre de
        tours, entre parenthèse à côté du total de touché
      </div>

      <ol class="list-decimal list-inside">
        <li class="my-2">
          Tester de mettre dans le modèle de tournoi un champ "nb round qualif", "nb round finale"
          et "current round" pour pouvoir mieux gérer les matches. Ca implique d'avoir aussi un
          champ "round" dans le modèle de match pour savoir à quel tour on est. Le "current round"
          serait reset lors du passage en phase finale.
        </li>
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
          Faire un onglet dans les pages de tournoi pour voir le détail des différentes phases. Ca
          comprend de faire :

          <ul class="list-disc list-inside pl-4">
            <li>Un onglet "Details" dans le menu de navigation (participants, qualifiers, etc)</li>
            <li>
              Un affichage des différentes phases du tournoi (qualifiers, tie-break, finals, etc)
              les uns au dessus des autres
            </li>
            <li>
              Afficher un tableau récapitulatif plus détaillé (pour chaque archer, afficher le
              détail de chaque flèche tirée avec le sous-total par match, et le total final à la
              fin) c.f.
              <a
                class="underline text-blue-700"
                href="https://www.ikyf.org/worldtaikai2024/assets/img/Tournament_record_The_4th_World_Kyudo_Taikai(Aichi-Nagoya)2024.pdf"
                >la coupe du monde</a
              >
            </li>
          </ul>
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
          <div class="text-xl font-semibold">
            <RouterLink
              :to="`/admin/tournaments/${tournament.id}`"
              class="hover:text-amaranth-600"
              >{{ tournament.name }}</RouterLink
            >
          </div>

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
            <p class="text-xl">No ongoing matches</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
