export type Archer = {
  id: number
  name: string
  position: string
  accuracy: number
}

export type ArcherWithNumber = {
  archer: Archer
  number: number
}

export type Team = {
  id: number
  name: string
  number: number
  archers: ArcherWithNumber[]
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
  archers: ArcherWithNumber[]
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
