import api from './base'

export const getAllArchers = async () => {
  return api.get('/archers')
}
