export enum TournamentStage {
  QUALIFIERS = 'qualifiers',
  TIE_BREAK = 'tie_break',
  FINALS = 'finals',
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

export enum ArcherPosition {
  ZASHA = 'zasha',
  RISSHA = 'rissha',
}

export enum MatchType {
  STANDARD = 'standard',
  EMPEROR = 'emperor',
  ENKIN = 'enkin',
  IZUME = 'izume',
}

export enum HitOutcome {
  MISS = 0,
  HIT = 1,
  ENSURE = 2,
}
