from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..api_models import TeamInput
from ..models.models import Archer, Team, TeamWithArchers
from ..utils.sqlite import get_session

router = APIRouter()


@router.get("/teams/{team_id}", response_model=TeamWithArchers)
def get_team(team_id: int, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post("/teams")
def create_team(data: TeamInput, session: Session = Depends(get_session)):
    team = Team(name=data.name)
    session.add(team)
    session.commit()
    return team


@router.put("/teams/{team_id}")
def update_team(
    team_id: int,
    data: TeamInput,
    session: Session = Depends(get_session),
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    team.name = data.name
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


@router.delete("/teams/{team_id}/archers/{archer_id}")
def remove_archer_from_team(
    team_id: int,
    archer_id: int,
    session: Session = Depends(get_session),
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    archer = session.get(Archer, archer_id)
    if not archer:
        raise HTTPException(status_code=404, detail="Archer not found")

    if archer in team.archers:
        team.archers.remove(archer)
        session.commit()
        return {"message": "Archer removed from team"}
    else:
        raise HTTPException(status_code=404, detail="Archer not in this team")


@router.delete("/teams/{team_id}")
def remove_team_from_tournament(
    team_id: int,
    session: Session = Depends(get_session),
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    session.delete(team)
    session.commit()
    return {"message": "Team removed"}
