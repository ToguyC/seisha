from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel


class MatchBase(SQLModel):
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )


class Match(MatchBase, table=True):
    id: int = Field(default=None, primary_key=True)

    series: List["Series"] = Relationship(back_populates="match")

    tournament_id: int = Field(default=None, foreign_key="tournament.id")
    tournament: Optional["Tournament"] = Relationship(back_populates="matches")


class MatchPublic(MatchBase):
    id: int
