export type Archer = {
  id: number
  name: string
  position: string
  accuracy: number
}

export type Team = {
  id: number
  name: string
  archers: Archer[]
}

export type Match = {
  id: number
  series: []
}

export type Tournament = {
  id: number
  name: string
  start_date: string
  end_date: string
  format: string
  status: string
}

export type TournamentWithRelations = Tournament & {
  archers: Archer[]
  teams: Team[]
  matches: Match[]
}

export type PaginatedResponse<T> = {
  count: number
  total: number
  page: number
  total_pages: number
  limit: number
  data: T[]
}
