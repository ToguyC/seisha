import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel, create_engine, Enum


class HitEnum(int, Enum):
    miss = 0
    hit = 1
    ensure = 2


class Tournament(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )

    matches: List["Match"] = Relationship(back_populates="tournament")


class Match(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )

    series: List["Series"] = Relationship(back_populates="match")

    tournament_id: int = Field(foreign_key="tournament.id")
    tournament: Optional[Tournament] = Relationship(back_populates="matches")


class Archer(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    position: str = Field(default="zasha")
    accuracy: float = Field(default=0.0)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )

    series: List["Series"] = Relationship(back_populates="archer")


class Series(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    arrows_raw: str
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )

    archer_id: int = Field(foreign_key="archer.id")
    archer: Optional[Archer] = Relationship(back_populates="series")

    match_id: int = Field(foreign_key="match.id")
    match: Optional[Match] = Relationship(back_populates="series")

    @property
    def arrows(self) -> List[HitEnum]:
        return json.loads(self.arrows_raw)

    @arrows.setter
    def arrows(self, value: List[HitEnum]):
        self.arrows_raw = json.dumps(value)


def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    sqlite_file_name = "tournament.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    engine = create_engine(sqlite_url)
    create_db_and_tables(engine)
