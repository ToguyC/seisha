from pydantic import BaseModel


class ShotInput(BaseModel):
    shooter_id: int
    tournament_id: int
    shot: int


class TournamentInput(BaseModel):
    name: str


class ShooterInput(BaseModel):
    name: str
