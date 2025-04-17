from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

class TeamBase(SQLModel):
    name: str
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )


class Team(TeamBase, table=True):
    id: int = Field(default=None, primary_key=True)

    archers: List["Archer"] = Relationship(back_populates="team")  # type: ignore


class TeamPublic(TeamBase):
    id: int
    name: str
