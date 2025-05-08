from datetime import datetime
from typing import List

from pydantic import BaseModel

from .models.models import ArcherWithTournaments, TournamentWithArchersAndTeams, ArcherPublic


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
    status: str = "upcoming"
    current_stage: str = "qualifiers"
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