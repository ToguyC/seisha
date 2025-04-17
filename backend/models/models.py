import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Enum, Field, Relationship, SQLModel


class ArcherTournamentLink(SQLModel, table=True):
    archer_id: int = Field(foreign_key="archer.id", primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id", primary_key=True)


class ArcherTeamLink(SQLModel, table=True):
    archer_id: int = Field(foreign_key="archer.id", primary_key=True)
    team_id: int = Field(foreign_key="team.id", primary_key=True)


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

    series: List["Series"] = Relationship(back_populates="archer")  # type: ignore
    tournaments: List["Tournament"] = Relationship(  # type: ignore
        back_populates="archers", link_model=ArcherTournamentLink
    )
    teams: List["Team"] = Relationship(
        back_populates="archers", link_model=ArcherTeamLink
    )


class ArcherPublic(ArcherBase):
    id: int
    name: str
    position: str
    accuracy: float


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
    match: Optional["Match"] = Relationship(back_populates="series")  # type: ignore

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
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )


class Match(MatchBase, table=True):
    id: int = Field(default=None, primary_key=True)

    series: List["Series"] = Relationship(back_populates="match")  # type: ignore

    tournament_id: int = Field(default=None, foreign_key="tournament.id")
    tournament: Optional["Tournament"] = Relationship(back_populates="matches")  # type: ignore


class MatchPublic(MatchBase):
    id: int


class TeamBase(SQLModel):
    name: str
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )


class Team(TeamBase, table=True):
    id: int = Field(default=None, primary_key=True)

    archers: List["Archer"] = Relationship(back_populates="teams", link_model=ArcherTeamLink)  # type: ignore

    tournament_id: int = Field(default=None, foreign_key="tournament.id")
    tournament: Optional["Tournament"] = Relationship(back_populates="teams")  # type: ignore


class TeamPublic(TeamBase):
    id: int
    name: str


class TournamentBase(SQLModel):
    name: str
    start_date: datetime
    end_date: datetime
    format: str
    status: str = Field(default="upcoming")
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )


class Tournament(TournamentBase, table=True):
    id: int = Field(default=None, primary_key=True)

    matches: List["Match"] = Relationship(back_populates="tournament")  # type: ignore
    archers: List["Archer"] = Relationship(  # type: ignore
        back_populates="tournaments", link_model=ArcherTournamentLink
    )
    teams: List["Team"] = Relationship(back_populates="tournament")  # type: ignore


class TournamentPublic(TournamentBase):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    format: str
    status: str


class SeriesWithArcher(SeriesPublic):
    archer: ArcherPublic


class MatchWithSeriesAndArchers(MatchPublic):
    series: List[SeriesWithArcher] = []
    archers: List[ArcherPublic] = []


class TeamsWithArchers(TeamPublic):
    archers: List[ArcherPublic] = []


class TournamentWithArchers(TournamentPublic):
    archers: List[ArcherPublic] = []


class TournamentWithArchersAndMatches(TournamentWithArchers):
    matches: List[MatchWithSeriesAndArchers] = []


class TournamentWithMatchesAndTeams(TournamentWithArchers):
    teams: List[TeamsWithArchers] = []


class TournamentWithEverything(TournamentPublic):
    matches: List[MatchWithSeriesAndArchers] = []
    teams: List[TeamsWithArchers] = []
    archers: List[ArcherPublic] = []


class ArcherWithTournaments(ArcherPublic):
    tournaments: List[TournamentPublic] = []
