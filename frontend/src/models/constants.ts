export enum TournamentStage {
  QUALIFIERS = 'qualifiers',
  QUALIFIERS_TIE_BREAK = 'qualifiers_tie_break',
  FINALS = 'finals',
  FINALS_TIE_BREAK = 'finals_tie_break',
}

export enum TournamentStageName {
  qualifiers = 'Qualifiers',
  qualifiers_tie_break = 'Qualifiers Tie Break',
  finals = 'Finals',
  finals_tie_break = 'Finals Tie Break',
}

export enum TournamentStatus {
  UPCOMING = 'upcoming',
  LIVE = 'live',
  FINISHED = 'finished',
  CANCELLED = 'cancelled',
}

export enum TournamentFormat {
  INDIVIDUAL = 'individual',
  TEAM = 'team',
}

export enum TournamentType {
  STANDARD = 'standard',
  EMPEROR = 'emperor',
}

export enum ArcherPosition {
  ZASHA = 'zasha',
  RISSHA = 'rissha',
}

export enum MatchFormat {
  STANDARD = 'standard',
  ENKIN = 'enkin',
  IZUME = 'izume',
}

export enum MatchArrows {
  STANDARD = 4,
  EMPEROR = 2,
  ENKIN = 1,
  IZUME = 1,
}

export enum HitOutcome {
  MISS = 0,
  HIT = 1,
  ENSURE = 2,
}
