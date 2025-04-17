from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel, Enum

from .many_to_many import ArcherTournamentLink, TeamTournamentLink


class TournamentBase(SQLModel):
    name: str
    date: datetime
    format: str
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


class TournamentPublic(TournamentBase):
    id: int
    name: str
    date: datetime
    format: str
