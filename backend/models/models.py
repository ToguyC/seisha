import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

from .constants import (
    ArcherPosition,
    HitOutcome,
    MatchType,
    TournamentFormat,
    TournamentStage,
    TournamentStatus,
)


class ArcherTournamentLink(SQLModel, table=True):
    archer_id: int = Field(foreign_key="archer.id", primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id", primary_key=True)
    number: int = Field(nullable=False)
    qualifiers_place: int | None = Field(nullable=True, default=None)
    finals_place: int | None = Field(nullable=True, default=None)

    tie_break_qualifiers: bool = Field(
        default=False, description="True if tie-break was needed after qualifiers"
    )
    tie_break_finals: bool = Field(
        default=False, description="True if tie-break was needed after finals"
    )

    archer: "Archer" = Relationship(back_populates="tournaments")
    tournament: "Tournament" = Relationship(back_populates="archers")


class ArcherTeamLink(SQLModel, table=True):
    archer_id: int = Field(foreign_key="archer.id", primary_key=True)
    team_id: int = Field(foreign_key="team.id", primary_key=True)
    number: int = Field(nullable=False)

    archer: "Archer" = Relationship(back_populates="teams")
    team: "Team" = Relationship(back_populates="archers")


class ArcherMatchLink(SQLModel, table=True):
    archer_id: int = Field(foreign_key="archer.id", primary_key=True)
    match_id: int = Field(foreign_key="match.id", primary_key=True)


class ArcherBase(SQLModel):
    name: str
    position: ArcherPosition = Field(default=ArcherPosition.ZASHA)
    accuracy: float = Field(default=0.0)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )


class Archer(ArcherBase, table=True):
    id: int = Field(default=None, primary_key=True)

    series: List["Series"] = Relationship(back_populates="archer", cascade_delete=True)
    tournaments: List["ArcherTournamentLink"] = Relationship(back_populates="archer")
    teams: List["ArcherTeamLink"] = Relationship(back_populates="archer")
    matches: List["Match"] = Relationship(
        back_populates="archers", link_model=ArcherMatchLink
    )


class ArcherPublic(ArcherBase):
    id: int
    name: str
    position: str
    accuracy: float


class ArcherWithTournamentData(SQLModel):
    archer: ArcherPublic
    number: int = Field(nullable=False)
    finalist: bool = Field(default=False)
    qualifiers_place: int | None = Field(nullable=True, default=None)
    finals_place: int | None = Field(nullable=True, default=None)

    tie_break_qualifiers: bool = Field(
        default=False, description="True if tie-break was needed after qualifiers"
    )
    tie_break_finals: bool = Field(
        default=False, description="True if tie-break was needed after finals"
    )


class SeriesBase(SQLModel):
    arrows_raw: str
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )


class Series(SeriesBase, table=True):
    id: int = Field(default=None, primary_key=True)

    archer_id: int = Field(default=None, foreign_key="archer.id")
    archer: Optional[Archer] = Relationship(back_populates="series")

    match_id: int = Field(default=None, foreign_key="match.id")
    match: Optional["Match"] = Relationship(back_populates="series")

    @property
    def arrows(self) -> List[HitOutcome]:
        return json.loads(self.arrows_raw)

    @arrows.setter
    def arrows(self, value: List[HitOutcome]):
        self.arrows_raw = json.dumps(value)


class SeriesPublic(SeriesBase):
    id: int
    arrows_raw: str

    @property
    def arrows(self) -> List[HitOutcome]:
        return json.loads(self.arrows_raw)


class MatchBase(SQLModel):
    type: MatchType = Field(default=MatchType.STANDARD)
    stage: TournamentStage = Field(default=TournamentStage.QUALIFIERS)
    finished: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )


class Match(MatchBase, table=True):
    id: int = Field(default=None, primary_key=True)

    series: List["Series"] = Relationship(back_populates="match", cascade_delete=True)
    archers: List["Archer"] = Relationship(
        back_populates="matches", link_model=ArcherMatchLink
    )

    tournament_id: int = Field(default=None, foreign_key="tournament.id")
    tournament: Optional["Tournament"] = Relationship(back_populates="matches")

    @property
    def verify_finish(self) -> bool:
        match self.type:
            case MatchType.STANDARD | MatchType.EMPEROR:
                arrows_shot = 4 if self.type == MatchType.STANDARD else 2

                finished_series = sum(
                    1 for s in self.series if len(s.arrows) == arrows_shot
                )
                any_unknown = any(HitOutcome.ENSURE in s.arrows for s in self.series)
                return not any_unknown and finished_series == len(self.archers)

        return False


class MatchPublic(MatchBase):
    id: int


class TeamBase(SQLModel):
    name: str
    number: int = Field(nullable=False)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )


class Team(TeamBase, table=True):
    id: int = Field(default=None, primary_key=True)
    finalist: bool = Field(default=False)
    qualifiers_place: int = Field(nullable=True, default=None)
    finals_place: int = Field(nullable=True, default=None)

    tie_break_qualifiers: bool = Field(
        default=False, description="True if tie-break was needed after qualifiers"
    )
    tie_break_finals: bool = Field(
        default=False, description="True if tie-break was needed after finals"
    )

    archers: List["ArcherTeamLink"] = Relationship(
        back_populates="team", cascade_delete=True
    )

    tournament_id: int = Field(default=None, foreign_key="tournament.id")
    tournament: Optional["Tournament"] = Relationship(back_populates="teams")


class TeamPublic(TeamBase):
    id: int
    name: str
    number: int


class TournamentBase(SQLModel):
    name: str
    start_date: datetime
    end_date: datetime
    format: TournamentFormat = Field(default=TournamentFormat.INDIVIDUAL)
    current_stage: TournamentStage = Field(default=TournamentStage.QUALIFIERS)
    advancing_count: int | None = Field(nullable=True, default=8)
    target_count: int = Field(default=5)
    status: TournamentStatus = Field(default=TournamentStatus.UPCOMING)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )


class Tournament(TournamentBase, table=True):
    id: int = Field(default=None, primary_key=True)

    matches: List["Match"] = Relationship(back_populates="tournament")
    archers: List["ArcherTournamentLink"] = Relationship(
        back_populates="tournament", cascade_delete=True
    )
    teams: List["Team"] = Relationship(back_populates="tournament", cascade_delete=True)


class TournamentPublic(TournamentBase):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    format: str
    status: str


class SeriesWithArcher(SeriesPublic):
    archer: ArcherPublic


class MatchWithSeries(MatchPublic):
    series: List[SeriesWithArcher] = []
    archers: List[ArcherPublic] = []


class TeamWithArchers(TeamPublic):
    archers: List[ArcherWithTournamentData] = []


class TournamentWithArchers(TournamentPublic):
    archers: List[ArcherPublic] = []


class TournamentWithMatchesAndTeams(TournamentWithArchers):
    teams: List[TeamWithArchers] = []


class TournamentWithArchersAndTeams(TournamentWithMatchesAndTeams):
    archers: List[ArcherWithTournamentData] = []
    teams: List[TeamWithArchers] = []


class TournamentWithEverything(TournamentPublic):
    matches: List[MatchWithSeries] = []
    teams: List[TeamWithArchers] = []
    archers: List[ArcherWithTournamentData] = []


class ArcherWithTournaments(ArcherPublic):
    tournaments: List[TournamentPublic] = []
