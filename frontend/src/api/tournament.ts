import api from './base'

export const getTournament = async (tournamentId: number) => {
  return api.get(`/tournaments/${tournamentId}`)
}

export const addTournamentTeam = async (tournamentId: number, name: string) => {
  return api.post(`/tournaments/${tournamentId}/teams/`, {
    name,
  })
}

export const addTournamentArcher = async (tournamentId: number, archerId: number) => {
  return api.post(`/tournaments/${tournamentId}/archers/${archerId}`)
}

export const removeTournamentArcher = async (tournamentId: number, archerId: number) => {
  return api.delete(`/tournaments/${tournamentId}/archers/${archerId}`)
}
