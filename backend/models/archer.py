from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

from .many_to_many import ArcherTournamentLink

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

    
class ArcherPublic(ArcherBase):
    id: int
    name: str
    position: str
    accuracy: float
