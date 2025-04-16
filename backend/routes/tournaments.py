from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, func, select

from ..api_models import PaginatedTournaments, TournamentInput
from ..models.tournament import Tournament
from ..models.with_relationships import TournamentWithArchersAndMatches
from ..utils.sqlite import get_session

router = APIRouter()


@router.get("/tournaments", response_model=PaginatedTournaments)
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


@router.get(
    "/tournaments/{tournament_id}", response_model=TournamentWithArchersAndMatches
)
def get_tournament_by_id(
    tournament_id: int,
    session: Session = Depends(get_session),
):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    return tournament


@router.post("/tournaments")
def post_tournament(data: TournamentInput, session: Session = Depends(get_session)):
    tournament = Tournament(name=data.name, date=data.date)
    session.add(tournament)
    session.commit()
    session.refresh(tournament)
    return tournament


@router.delete("/tournaments/{tournament_id}")
def delete_tournament(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    session.delete(tournament)
    session.commit()
    return {"message": "Tournament deleted"}
