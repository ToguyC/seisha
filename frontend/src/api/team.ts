import type { Team } from '@/models/models'
import api from './base'

export const getTeam = async (teamId: number) => {
  return api.get(`/teams/${teamId}`)
}

export const putTeam = async (teamInfo: Team) => {
  return api.put(`/teams/${teamInfo.id}`, {
    name: teamInfo.name,
  })
}

export const deleteTeam = async (teamId: number) => {
  return api.delete(`/teams/${teamId}`)
}

export const addArcherToTeam = async (teamId: number, archerId: number) => {
  return api.post(`/teams/${teamId}/archers/${archerId}`)
}

export const removeArcherFromTeam = async (teamId: number, archerId: number) => {
  return api.delete(`/teams/${teamId}/archers/${archerId}`)
}
