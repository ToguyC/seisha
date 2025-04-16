from pydantic import BaseModel


class ArrowInput(BaseModel):
    archer_id: int
    tournament_id: int
    shot: int


class ArcherInput(BaseModel):
    name: str
    position: str
