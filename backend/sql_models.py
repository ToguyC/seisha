import json
from typing import List, Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class Tournament(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    series: List["Series"] = Relationship(back_populates="tournament")


class Shooter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    series: List["Series"] = Relationship(back_populates="shooter")


class Series(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    shots_raw: str

    shooter_id: int = Field(foreign_key="shooter.id")
    shooter: Optional[Shooter] = Relationship(back_populates="series")

    tournament_id: int = Field(foreign_key="tournament.id")
    tournament: Optional[Tournament] = Relationship(back_populates="series")

    @property
    def shots(self) -> List[int]:
        return json.loads(self.shots_raw)

    @shots.setter
    def shots(self, value: List[int]):
        self.shots_raw = json.dumps(value)


def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    sqlite_file_name = "tournament.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    engine = create_engine(sqlite_url)
    create_db_and_tables(engine)
