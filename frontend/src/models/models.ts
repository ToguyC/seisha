export type Archer = {
  id: number
  name: string
  position: string
  accuracy: number
}

export type Tournament = {
  id: number
  name: string
  start_date: string
  end_date: string
  format: string
  status: string
  archers: Archer[]
}
