import type { Match, Series, Tournament } from '@/models/models'
import api from './base'
import type { AxiosResponse } from 'axios'

export const postArrowToMatch = async (
  matchId: number,
  archerId: number,
  state: number,
): Promise<AxiosResponse<Series>> => {
  return api.post(`/matches/${matchId}/archers/${archerId}/arrows`, { arrow: state })
}

export const putArrow = async (
  matchId: number,
  archerId: number,
  arrowId: number,
  arrowState: number,
): Promise<AxiosResponse<Series>> => {
  return api.put(`/matches/${matchId}/archers/${archerId}/arrows/${arrowId}`, { arrow: arrowState })
}

export const getArrow = async (
  matchId: number,
  archerId: number,
  arrowId: number,
): Promise<AxiosResponse<number>> => {
  return api.get(`/matches/${matchId}/archers/${archerId}/arrows/${arrowId}`)
}

export const deleteMatch = async (matchId: number) => {
  return api.delete(`/matches/${matchId}`)
}

export const finishMatch = async (matchId: number) => {
  return api.put(`/matches/${matchId}/finish`)
}
