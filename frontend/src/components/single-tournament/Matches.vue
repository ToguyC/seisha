<script setup lang="ts">
import { deleteMatch as _deleteMatch } from '@/api/match'
import { postTournamentMatch } from '@/api/tournament'
import type { TournamentWithRelations } from '@/models/models'
import { TrashIcon } from '@heroicons/vue/16/solid'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import { onBeforeUnmount, onMounted, ref } from 'vue'
import Match from '../Match.vue'

const { tournament } = defineProps<{
  tournament: TournamentWithRelations
}>()

const emit = defineEmits<{
  fetchTournament: [tournamentId: number]
}>()

const fetchTournament = () => {
  emit('fetchTournament', tournament.id)
}

const newMatchError = ref(false)
const newMatchErrorMessage = ref('')
const deleteMatchToggle = ref(false)

const generateNextMatch = () => {
  postTournamentMatch(tournament.id)
    .then((res) => {
      fetchTournament()
    })
    .catch((err) => {
      newMatchError.value = true
      newMatchErrorMessage.value = err.response.data.detail

      setTimeout(() => {
        newMatchError.value = false
        newMatchErrorMessage.value = ''
      }, 3000)
    })
}

const matchContainsUnknowns = (matchId: number) => {
  const match = tournament.matches.find((m) => m.id === matchId)
  if (!match) return false

  return match.series.some((s) => {
    const arrows = JSON.parse(s.arrows_raw) as number[]
    return arrows.some((a) => a === 2)
  })
}

const deleteMatch = (matchId: number) => {
  if (!confirm('Are your sure you want to delete this match?')) {
    return
  }

  _deleteMatch(matchId)
    .then((res) => {
      fetchTournament()
      deleteMatchToggle.value = false
    })
    .catch((err) => {
      console.error(err.message)
    })
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.ctrlKey) {
    deleteMatchToggle.value = true
  }
}

const handleKeyup = (event: KeyboardEvent) => {
  if (!event.ctrlKey) {
    deleteMatchToggle.value = false
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  window.addEventListener('keyup', handleKeyup)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('keyup', handleKeyup)
})
</script>

<template>
  <div>
    <div class="text-red-500 font-bold">
      TODO
      <ol class="list-decimal list-inside">
        <li class="my-2">
          Avoir un affichage live de l'ensemble des archers/équipes comme les listes de la page d'un
          tournoi, mais en format tableau comme un match avec le total de flèches par archer et par
          team

          <ul class="list-disc list-inside pl-4">
            <li>
              Créer une route pour afficher en live (comme home) un tournoi (sans nav, utilisé pour
              un embedd)
            </li>
            <li>
              Créer une route pour afficher en live (comme home) que le tableau récap d'un tournoi
              (sans nav, utilisé pour un embedd) - Colones individuel : "numéro", "nom", "total" -
              Colones équipe : "numéro", "nom", "archers - total" (flex-col), "total"
            </li>
          </ul>
        </li>
        <li class="my-2">
          Bouton pour terminer les qualifs et caculer le placement (jap 予選順位) (champs
          "qualifers_place" des tables teams et archertournamentlink)

          <ul class="list-disc list-inside pl-4">
            <li>
              Créer le tableau récapitulatif avec placement et flèches totales (même component que
              le tableau récap du point 1 mais avec un argument "withPlacement" - nécessaire ensuite
              de calculer les rowspans pour les possibles égalités + trié par placement à la place
              des numéro de participant + garder le numéro de participants)
            </li>
            <li>
              Établir la liste des qualifiés et ceux qui doivent être départagé

              <pre>
      1. je groupe tout les participants par leur place aux qualifs
      2. je parcours les groupes, et pour chaque j'effectue la vérification : place_groupe + len(groupe) <= "advancing_count"
      3. si la vérification passe -> set "finalist" = true pour tout les participants à cette place
      4. si la vérification ne passe pas et que je n'ai pas encore mes "advancing_count" finalistes -> ce groupe doit être départager</pre
              >
            </li>
            <li>
              Passer le champs "current_stage" du tournoi à "finals", ou "tie-breaker" si des
              égalités ne permettant pas d'avoir clairement les "advancing_count" meilleurs
            </li>
          </ul>
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
        <li class="my-2">Pouvoir exporter les tableaux récapitulatif des qualifs, finales, et brackets en un seul PDF (avec infos du tournoi en premier page).</li>
      </ol>
    </div>

    <div class="flex items-center justify-between mb-6">
      <div class="text-xl font-bold text-gray-900 capitalize">Matches</div>
      <div class="flex items-center gap-4">
        <div class="text-red-500">{{ newMatchErrorMessage }}</div>
        <div class="relative">
          <div
            class="absolute animate-ping w-full h-full bg-orange-200 top-0 left-0 rounded"
            :class="{
              hidden: !newMatchError,
              block: newMatchError,
            }"
          ></div>
          <button
            class="relative w-30 flex items-center text-sm font-semibold justify-center gap-4 px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 hover:cursor-pointer disabled:cursor-not-allowed"
            :class="{
              '!bg-orange-100 !text-orange-700': newMatchError,
            }"
            :disabled="newMatchError"
            @click="generateNextMatch"
          >
            <span v-if="!newMatchError">Next Match</span>
            <span v-else>Error</span>
          </button>
        </div>
      </div>
    </div>

    <div class="flex flex-col divide-y divide-gray-500">
      <div v-for="match in tournament.matches" class="py-8 gap-4 flex flex-col">
        <div class="w-full flex justify-between items-center">
          <div>
            <div
              v-if="matchContainsUnknowns(match.id)"
              class="flex items-center gap-2 text-orange-500"
            >
              <ExclamationTriangleIcon class="w-5 h-5" /> Unknowns still presents
            </div>
          </div>

          <button
            class="w-20 py-2 flex items-center text-sm font-semibold justify-center bg-red-100 text-red-700 rounded hover:bg-red-200 hover:cursor-pointer"
            @click="deleteMatch(match.id)"
          >
            <TrashIcon class="w-5 h-5" />
          </button>
        </div>

        <Match :match="match" :tournament="tournament" @fetch-tournament="fetchTournament" />
      </div>
    </div>
  </div>
</template>
