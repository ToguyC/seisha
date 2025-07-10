import type { ArcherPosition, MatchFormat, TournamentFormat, TournamentStage, TournamentStatus, TournamentType } from "./constants"

export type Archer = {
  id: number
  name: string
  position: ArcherPosition
  accuracy: number
}

export type ArcherWithTournamentData = {
  archer: Archer
  number: number
  qualifiers_place: number | null
  finals_place: number | null
  tie_break_qualifiers: boolean
  tie_break_finals: boolean
}

export type Team = {
  id: number
  name: string
  number: number
  qualifiers_place: number | null
  finals_place: number | null
  tie_break_qualifiers: boolean
  tie_break_finals: boolean
  archers: ArcherWithTournamentData[]
}

export type Series = {
  id: number
  arrows_raw: string
  archer: Archer
}

export type Match = {
  id: number
  format: MatchFormat
  finished: boolean
  stage: TournamentStage
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
  format: TournamentFormat
  type: TournamentType
  status: TournamentStatus
  current_stage: TournamentStage
  advancing_count: number | null
  qualifiers_round_count: number
  finals_round_count: number
  target_count: number
  created_at: string
  updated_at: string
}

export type TournamentWithRelations = Tournament & {
  archers: ArcherWithTournamentData[]
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
