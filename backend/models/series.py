import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Enum, Field, Relationship, SQLModel

from .archer import Archer


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
