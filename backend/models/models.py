import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

from .constants import (
    ArcherPosition,
    HitOutcome,
    MatchFormat,
    MatchArrows,
    TournamentFormat,
    TournamentStage,
    TournamentStatus,
    TournamentType,
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
    arrows_raw: str  # JSON string representation of arrows. In Enkin, the first arrow is the position of the archer.

    @property
    def arrows(self) -> List[HitOutcome]:
        return json.loads(self.arrows_raw)


class MatchBase(SQLModel):
    format: MatchFormat = Field(default=MatchFormat.STANDARD)
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
        arrows_shot = MatchArrows[self.format.name].value

        finished_series = sum(1 for s in self.series if len(s.arrows) == arrows_shot)

        if self.format != MatchFormat.ENKIN:
            undeceided = any(HitOutcome.ENSURE in s.arrows for s in self.series)
        else:
            # check whether all archers have shot their first arrow
            first_arrows = [s.arrows[0] if s.arrows else None for s in self.series]

            if len(first_arrows) < len(self.archers):
                undeceided = True
            else:
                # check if all archers have a distinct position
                distinct_first_arrows = set(first_arrows)
                undeceided = len(distinct_first_arrows) < len(self.archers)

        return not undeceided and finished_series == len(self.archers)


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
    qualifiers_place: int | None
    finals_place: int | None
    tie_break_qualifiers: bool
    tie_break_finals: bool


class TournamentBase(SQLModel):
    name: str
    start_date: datetime
    end_date: datetime
    format: TournamentFormat = Field(default=TournamentFormat.INDIVIDUAL)
    type: TournamentType = Field(default=TournamentType.STANDARD)
    current_stage: TournamentStage = Field(default=TournamentStage.QUALIFIERS)
    advancing_count: int | None = Field(nullable=True)
    qualifiers_round_count: int = Field(default=0)
    had_qualifiers_tie_break: bool = Field(default=False)
    finals_round_count: int = Field(default=0)
    had_finals_tie_break: bool = Field(default=False)
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
