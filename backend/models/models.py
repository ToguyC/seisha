import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Enum, Field, Relationship, SQLModel


class ArcherTournamentLink(SQLModel, table=True):
    archer_id: int = Field(foreign_key="archer.id", primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id", primary_key=True)
    number: int = Field(nullable=False)
    finalist: bool = Field(default=False)
    qualifers_place: int = Field(nullable=True, default=None)
    finals_place: int = Field(nullable=True, default=None)

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
    position: str = Field(default="zasha")
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


class ArcherWithNumber(SQLModel):
    archer: ArcherPublic
    number: int = Field(nullable=False)


class HitEnum(int, Enum):
    miss = 0
    hit = 1
    ensure = 2


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
    def arrows(self) -> List[HitEnum]:
        return json.loads(self.arrows_raw)

    @arrows.setter
    def arrows(self, value: List[HitEnum]):
        self.arrows_raw = json.dumps(value)


class SeriesPublic(SeriesBase):
    id: int
    arrows_raw: str

    @property
    def arrows(self) -> List[HitEnum]:
        return json.loads(self.arrows_raw)


class MatchBase(SQLModel):
    type: str = Field(default="standard")
    stage: str = Field(default="qualifers")
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
            case "standard":
                finished_series = sum(
                    1 for series in self.series if len(series.arrows) == 4
                )
                any_unknown = any(2 in series.arrows for series in self.series)
                print(any_unknown)
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
    qualifers_place: int = Field(nullable=True, default=None)
    finals_place: int = Field(nullable=True, default=None)

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
    format: str
    current_stage: str = Field(default="qualifers")
    advancing_count: int = Field(nullable=True, default=8)
    target_count: int = Field(default=5)
    status: str = Field(default="upcoming")
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
    archers: List[ArcherWithNumber] = []


class TournamentWithArchers(TournamentPublic):
    archers: List[ArcherPublic] = []


class TournamentWithMatchesAndTeams(TournamentWithArchers):
    teams: List[TeamWithArchers] = []


class TournamentWithArchersAndTeams(TournamentWithMatchesAndTeams):
    archers: List[ArcherWithNumber] = []
    teams: List[TeamWithArchers] = []


class TournamentWithEverything(TournamentPublic):
    matches: List[MatchWithSeries] = []
    teams: List[TeamWithArchers] = []
    archers: List[ArcherWithNumber] = []


class ArcherWithTournaments(ArcherPublic):
    tournaments: List[TournamentPublic] = []
