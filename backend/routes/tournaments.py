from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import selectinload
from sqlmodel import Session, func, select

from ..api_models import PaginatedTournaments, TeamInput, TournamentInput
from ..models.models import (
    Archer,
    ArcherTournamentLink,
    Team,
    Tournament,
    TournamentWithEverything,
)
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
    last_entry = session.exec(
        select(ArcherTournamentLink)
        .where(ArcherTournamentLink.tournament_id == tournament_id)
        .order_by(ArcherTournamentLink.number.desc())
    ).first()

    archer_tournament_link = ArcherTournamentLink(
        tournament_id=tournament_id,
        archer_id=archer_id,
        number=last_entry.number + 1 if last_entry else 1,
    )
    session.add(archer_tournament_link)
    session.commit()
    return {"message": "Archer added to tournament"}


@router.post("/tournaments/{tournament_id}/teams")
def add_team_to_tournament(
    data: TeamInput,
    tournament_id: int,
    session: Session = Depends(get_session),
):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    last_entry = session.exec(
        select(Team)
        .where(Team.tournament_id == tournament_id)
        .order_by(Team.number.desc())
    ).first()
    team_number = last_entry.number + 1 if last_entry else 1

    team = Team(name=data.name, number=team_number)
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
    archer_tournament_link = session.get(
        ArcherTournamentLink, (archer_id, tournament_id)
    )
    if not archer_tournament_link:
        raise HTTPException(status_code=404, detail="Archer not found in tournament")

    removed_number = archer_tournament_link.number

    session.delete(archer_tournament_link)

    # Shift numbers of the remaining archers
    stmt = (
        select(ArcherTournamentLink)
        .where(
            ArcherTournamentLink.tournament_id == tournament_id,
            ArcherTournamentLink.number > removed_number,
        )
        .order_by(ArcherTournamentLink.number.asc())
    )
    links_to_update = session.exec(stmt).all()

    for link in links_to_update:
        link.number -= 1
        session.add(link)

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
