import type { Archer } from '@/models/models'
import api from './base'

export const getAllArchers = async () => {
  return api.get('/archers')
}

export const getPagninatedArchers = async (page: number, limit: number = 10) => {
  return api.get(`/archers/paginate?page=${page}&limit=${limit}`)
}

export const getArcher = async (archerId: number) => {
  return api.get(`/archers/${archerId}`)
}

export const postArcher = async (name: string, position: string) => {
  return api.post('/archers', { name, position })
}

export const putArcher = async (archerInfo: Archer) => {
  return api.put(`/archers/${archerInfo.id}`, {
    name: archerInfo.name,
    position: archerInfo.position,
  })
}

export const deleteArcher = async (archerId: number) => {
  return api.delete(`/archers/${archerId}`)
}
