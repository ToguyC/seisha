from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..api_models import TeamInput
from ..models.models import Archer, Team, TeamWithArchers, ArcherTeamLink
from ..utils.sqlite import get_session

router = APIRouter()


@router.get("/teams/{team_id}", response_model=TeamWithArchers)
async def get_team(team_id: int, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.put("/teams/{team_id}")
async def update_team(
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
async def add_archer_to_team(
    team_id: int,
    archer_id: int,
    session: Session = Depends(get_session),
):
    last_entry = session.exec(
        select(ArcherTeamLink)
        .where(ArcherTeamLink.team_id == team_id)
        .order_by(ArcherTeamLink.number.desc())
    ).first()

    archer_team_link = ArcherTeamLink(
        team_id=team_id,
        archer_id=archer_id,
        number=last_entry.number + 1 if last_entry else 1,
    )
    session.add(archer_team_link)
    session.commit()
    return {"message": "Archer added to team"}


@router.delete("/teams/{team_id}/archers/{archer_id}")
async def remove_archer_from_team(
    team_id: int,
    archer_id: int,
    session: Session = Depends(get_session),
):
    archer_team_link = session.get(ArcherTeamLink, (archer_id, team_id))
    if not archer_team_link:
        raise HTTPException(status_code=404, detail="Archer not found in team")
    
    removed_number = archer_team_link.number

    session.delete(archer_team_link)

    # Update the numbers of the remaining archers in the team
    stmt = (
        select(ArcherTeamLink)
        .where(ArcherTeamLink.team_id == team_id, ArcherTeamLink.number > removed_number)
        .order_by(ArcherTeamLink.number.asc())
    )
    links_to_update = session.exec(stmt).all()

    for link in links_to_update:
        link.number -= 1
        session.add(link)

    session.commit()
    
    return {"message": "Archer removed from team"}


@router.delete("/teams/{team_id}")
async def remove_team_from_tournament(
    team_id: int,
    session: Session = Depends(get_session),
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    removed_number = team.number

    session.delete(team)

    stmt = (
        select(Team).where(
            Team.tournament_id == team.tournament_id, Team.number > removed_number
        )
    ).order_by(Team.number.asc())
    teams_to_update = session.exec(stmt).all()

    for team in teams_to_update:
        team.number -= 1
        session.add(team)

    session.commit()
    return {"message": "Team removed"}
