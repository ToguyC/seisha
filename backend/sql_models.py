import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel, create_engine, Enum


class Tournament(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )

    series: List["Series"] = Relationship(back_populates="tournament")


class Shooter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )

    series: List["Series"] = Relationship(back_populates="shooter")


class HitEnum(int, Enum):
    miss = 0
    hit = 1
    ensure = 2


class Series(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    shots_raw: str
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )

    shooter_id: int = Field(foreign_key="shooter.id")
    shooter: Optional[Shooter] = Relationship(back_populates="series")

    tournament_id: int = Field(foreign_key="tournament.id")
    tournament: Optional[Tournament] = Relationship(back_populates="series")

    @property
    def shots(self) -> List[HitEnum]:
        return json.loads(self.shots_raw)

    @shots.setter
    def shots(self, value: List[HitEnum]):
        self.shots_raw = json.dumps(value)


def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    sqlite_file_name = "tournament.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    engine = create_engine(sqlite_url)
    create_db_and_tables(engine)
