from datetime import datetime
from typing import List

from pydantic import BaseModel

from .models.constants import (
    ArcherPosition,
    TournamentStage,
    TournamentStatus,
    MatchFormat,
)
from .models.models import ArcherPublic, TournamentWithArchersAndTeams


class ArrowInput(BaseModel):
    archer_id: int
    tournament_id: int
    shot: int


class MatchArrowInput(BaseModel):
    arrow: int


class MatchEnkinInput(BaseModel):
    place: int


class MatchIzumeParticipantsInput(BaseModel):
    ids: List[int] = []


class ArcherInput(BaseModel):
    name: str
    position: str


class TournamentInput(BaseModel):
    name: str
    format: str
    start_date: datetime
    end_date: datetime
    status: TournamentStatus = TournamentStatus.UPCOMING
    current_stage: TournamentStage = TournamentStage.QUALIFIERS
    advancing_count: int = 8
    qualifiers_round_count: int = 0
    finals_round_count: int = 0
    target_count: int


class TeamInput(BaseModel):
    name: str


class Paginated(BaseModel):
    count: int
    total: int
    page: int
    total_pages: int
    limit: int


class PaginatedTournaments(Paginated):
    data: List[TournamentWithArchersAndTeams]


class PaginatedArcher(Paginated):
    data: List[ArcherPublic]


class ArcherSearchInput(BaseModel):
    name: str = ""
    position: ArcherPosition = ArcherPosition.ZASHA


class AdvancingParticipant(BaseModel):
    id: int
    hit_count: int  # in Enkin, a high hit count means a better place


class TournamentNextStageInput(BaseModel):
    advancing_participants: List[AdvancingParticipant]
    tie_breaker_needed: bool = False


class TournamentTieBreakParticipantsInput(BaseModel):
    stage: TournamentStage
