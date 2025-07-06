from datetime import datetime
from typing import List

from pydantic import BaseModel

from .models.models import (
    TournamentWithArchersAndTeams,
    ArcherPublic,
)
from .models.constants import TournamentStage, TournamentStatus


class ArrowInput(BaseModel):
    archer_id: int
    tournament_id: int
    shot: int


class MatchArrowInput(BaseModel):
    arrow: int


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
    position: str = "zasha"


class TournamentNextStageInput(BaseModel):
    advancing_participants_ids: List[
        int
    ]  # List of IDs of participants advancing to the next stage. Archer's IDs if individual, Team's IDs if team tournament.
    tie_breaker_needed: bool = False
