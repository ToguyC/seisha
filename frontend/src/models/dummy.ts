import { TournamentFormat, TournamentStage, TournamentStatus } from './constants'
import type { TournamentWithRelations } from './models'

export const dummyTournamentWithRelations: TournamentWithRelations = {
  id: 0,
  name: '',
  start_date: '',
  end_date: '',
  format: TournamentFormat.INDIVIDUAL,
  status: TournamentStatus.UPCOMING,
  advancing_count: 0,
  qualifiers_round_count: 0,
  finals_round_count: 0,
  current_stage: TournamentStage.QUALIFIERS,
  created_at: '',
  updated_at: '',
  target_count: 0,
  archers: [],
  teams: [],
  matches: [],
}

export const dummyTournament: Omit<TournamentWithRelations, 'archers' | 'teams' | 'matches'> = {
  ...dummyTournamentWithRelations,
}
