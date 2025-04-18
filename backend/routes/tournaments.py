from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, func, select

from ..api_models import PaginatedTournaments, TeamInput, TournamentInput
from ..models.models import Archer, Team, Tournament, TournamentWithEverything
from ..utils.sqlite import get_session

router = APIRouter()


@router.get("/tournaments/paginate", response_model=PaginatedTournaments)
def get_tournaments_paginated(
    session: Session = Depends(get_session),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
):
    offset = (page - 1) * limit

    total_stmt = select(func.count()).select_from(Tournament)
    total = session.exec(total_stmt).one()

    tournaments_stmt = (
        select(Tournament).offset(offset).limit(limit).order_by(Tournament.id.asc())
    )
    tournaments = session.exec(tournaments_stmt).all()

    total_pages = (total + limit - 1) // limit

    return PaginatedTournaments(
        count=len(tournaments),
        total=total,
        page=page,
        total_pages=total_pages,
        limit=limit,
        data=tournaments,
    )


@router.get("/tournaments/{tournament_id}", response_model=TournamentWithEverything)
def get_tournament_by_id(
    tournament_id: int,
    session: Session = Depends(get_session),
):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    return tournament


@router.put("/tournaments/{tournament_id}")
def update_tournament(
    tournament_id: int,
    data: TournamentInput,
    session: Session = Depends(get_session),
):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    tournament.name = data.name
    tournament.format = data.format
    tournament.start_date = data.start_date
    tournament.end_date = data.end_date
    tournament.status = data.status

    session.commit()
    session.refresh(tournament)
    return tournament


@router.post("/tournaments")
def post_tournament(data: TournamentInput, session: Session = Depends(get_session)):
    tournament = Tournament(
        name=data.name,
        format=data.format,
        start_date=data.start_date,
        end_date=data.end_date,
        status=data.status,
    )
    session.add(tournament)
    session.commit()
    session.refresh(tournament)
    return tournament


@router.post("/tournaments/{tournament_id}/archers/{archer_id}")
def add_archer_to_tournament(
    tournament_id: int,
    archer_id: int,
    session: Session = Depends(get_session),
):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    archer = session.get(Archer, archer_id)
    if not archer:
        raise HTTPException(status_code=404, detail="Archer not found")

    tournament.archers.append(archer)
    session.commit()
    session.refresh(tournament)
    return tournament


@router.post("/tournaments/{tournament_id}/teams")
def add_team_to_tournament(
    data: TeamInput,
    tournament_id: int,
    session: Session = Depends(get_session),
):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    team = Team(name=data.name)
    tournament.teams.append(team)
    session.add(team)
    session.commit()
    session.refresh(tournament)
    return tournament


@router.delete("/tournaments/{tournament_id}/archers/{archer_id}")
def remove_archer_from_tournament(
    tournament_id: int,
    archer_id: int,
    session: Session = Depends(get_session),
):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    archer = session.get(Archer, archer_id)
    if not archer:
        raise HTTPException(status_code=404, detail="Archer not found")

    tournament.archers.remove(archer)
    session.commit()
    return {"message": "Archer removed from tournament"}


@router.delete("/tournaments/{tournament_id}")
def delete_tournament(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    session.delete(tournament)
    session.commit()
    return {"message": "Tournament deleted"}
