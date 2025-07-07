from enum import Enum

class HitOutcome(int, Enum):
    MISS = 0
    HIT = 1
    ENSURE = 2

class TournamentStage(str, Enum):
    QUALIFIERS = "qualifiers"
    QUALIFIERS_TIE_BREAK = "qualifiers_tie_break"
    FINALS = "finals"
    FINALS_TIE_BREAK = "finals_tie_break"


class TournamentStatus(str, Enum):
    UPCOMING = "upcoming"
    LIVE = "live"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class TournamentFormat(str, Enum):
    INDIVIDUAL = "individual"
    TEAM = "team"


class ArcherPosition(str, Enum):
    ZASHA = "zasha"
    RISSHA = "rissha"


class MatchFormat(str, Enum):
    STANDARD = "standard"
    EMPEROR = "emperor"
    ENKIN = "enkin"
    IZUME = "izume"

class MatchArrows(int, Enum):
    STANDARD = 4
    EMPEROR = 2
    ENKIN = 1
    IZUME = 1