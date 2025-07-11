import type { Tournament } from '@/models/models'
import api from './base'
import type { MatchFormat } from '@/models/constants'

export const getPaginatedTournaments = async (page: number, limit: number = 10) => {
  return api.get(`/tournaments/paginate?page=${page}&limit=${limit}`)
}

export const getTournament = async (tournamentId: number) => {
  return api.get(`/tournaments/${tournamentId}`)
}

export const getAllLiveTournaments = async () => {
  return api.get('/tournaments/live')
}

export const getTieBreakParticipants = async (tournamentId: number) => {
  return api.get(`/tournaments/${tournamentId}/participants/tie-break`)
}

export const postTournament = async (tournamentInfo: Tournament) => {
  return api.post('/tournaments', tournamentInfo)
}

export const putTournament = async (tournamentInfo: Tournament) => {
  return api.put(`/tournaments/${tournamentInfo.id}`, tournamentInfo)
}

export const deleteTournament = async (tournamentId: number) => {
  return api.delete(`/tournaments/${tournamentId}`)
}

export const postTournamentTeam = async (tournamentId: number, name: string) => {
  return api.post(`/tournaments/${tournamentId}/teams/`, { name })
}

export const postTournamentArcher = async (tournamentId: number, archerId: number) => {
  return api.post(`/tournaments/${tournamentId}/archers/${archerId}`)
}

export const postTournamentMatch = async (tournamentId: number, participants: number[]) => {
  return api.post(`/tournaments/${tournamentId}/matches`, { ids: participants })
}

export const deleteTournamentArcher = async (tournamentId: number, archerId: number) => {
  return api.delete(`/tournaments/${tournamentId}/archers/${archerId}`)
}

export const putTournamentStage = async (
  tournamentId: number,
  advancingParticipants: { id: number; hit_count: number }[],
  tieBreakerNeeded: boolean,
) => {
  return api.put(`/tournaments/${tournamentId}/stage`, {
    advancing_participants: advancingParticipants,
    tie_breaker_needed: tieBreakerNeeded,
  })
}
