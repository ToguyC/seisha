export type Archer = {
  id: number
  name: string
  position: string
  accuracy: number
}

export type ArcherWithNumber = {
  archer: Archer
  number: number
  finalist: boolean
  qualifers_place: number
  finals_place: number
}

export type Team = {
  id: number
  name: string
  number: number
  finalist: boolean
  qualifers_place: number
  finals_place: number
  archers: ArcherWithNumber[]
}

export type Series = {
  id: number
  arrows_raw: string
  archer: Archer
}

export type Match = {
  id: number
  type: string
  finished: boolean
  stage: string
  series: Series[]
  archers: Archer[]
  created_at: string
  updated_at: string
}

export type Tournament = {
  id: number
  name: string
  start_date: string
  end_date: string
  format: string
  status: string
  current_stage: string
  advancing_count: number
  target_count: number
  created_at: string
  updated_at: string
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
