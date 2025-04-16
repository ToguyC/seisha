import api from './base'

export const getTournaments = async () => {
  const response = await api.get('/match/1')
  return response.data
}
