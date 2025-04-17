from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..api_models import TeamInput
from ..models.models import Archer, Team
from ..utils.sqlite import get_session

router = APIRouter()


@router.post("/teams")
def create_team(data: TeamInput, session: Session = Depends(get_session)):
    team = Team(name=data.name)
    session.add(team)
    session.commit()
    return team


@router.post("/teams/{team_id}/archers/{archer_id}")
def add_archer_to_team(
    team_id: int,
    archer_id: int,
    session: Session = Depends(get_session),
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Assuming Archer is a model and you have a way to get it
    archer = session.get(Archer, archer_id)
    if not archer:
        raise HTTPException(status_code=404, detail="Archer not found")

    team.archers.append(archer)
    session.commit()
    return team
