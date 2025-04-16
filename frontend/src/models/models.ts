export type Archer = {
  id: number
  name: string
  position: string
  accuracy: number
}

export type Tournament = {
  id: number
  name: string
  date: string
  archers: Archer[]
}
