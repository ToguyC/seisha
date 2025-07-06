from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import selectinload
from sqlmodel import Session, func, select

from ..api_models import (
    PaginatedTournaments,
    TeamInput,
    TournamentInput,
    TournamentNextStageInput,
)
from ..models.models import (
    Archer,
    ArcherTournamentLink,
    Match,
    Team,
    Tournament,
    TournamentWithEverything,
)
from ..models.constants import TournamentFormat, TournamentStage, TournamentStatus
from ..utils.sqlite import get_session
from ..utils.ws_manager_insance import ws_instance

router = APIRouter()


@router.get("/tournaments/paginate", response_model=PaginatedTournaments)
async def get_tournaments_paginated(
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


@router.get("/tournaments/live", response_model=list[TournamentWithEverything])
async def get_live_tournaments(
    session: Session = Depends(get_session),
):
    tournaments = session.exec(
        select(Tournament)
        .where(Tournament.status == TournamentStatus.LIVE)
        .order_by(Tournament.id.asc())
    ).all()

    return tournaments


@router.get("/tournaments/{tournament_id}", response_model=TournamentWithEverything)
async def get_tournament_by_id(
    tournament_id: int,
    session: Session = Depends(get_session),
):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    return tournament


@router.put("/tournaments/{tournament_id}")
async def update_tournament(
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
    tournament.current_stage = data.current_stage
    tournament.advancing_count = data.advancing_count
    tournament.target_count = data.target_count

    session.commit()
    session.refresh(tournament)
    return tournament


@router.post("/tournaments")
async def post_tournament(
    data: TournamentInput, session: Session = Depends(get_session)
):
    tournament = Tournament(
        name=data.name,
        format=data.format,
        start_date=data.start_date,
        end_date=data.end_date,
        status=data.status,
        target_count=data.target_count,
    )
    session.add(tournament)
    session.commit()
    session.refresh(tournament)
    return tournament


@router.post("/tournaments/{tournament_id}/next-stage")
async def next_stage(
    tournament_id: int,
    data: TournamentNextStageInput,
    session: Session = Depends(get_session),
):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    if tournament.current_stage == TournamentStage.FINALS_TIE_BREAK:
        raise HTTPException(status_code=400, detail="Tournament is already in the finals tie-break stage")

    if tournament.current_stage == TournamentStage.QUALIFIERS:
        if data.tie_breaker_needed:
            tournament.current_stage = TournamentStage.QUALIFIERS_TIE_BREAK
        else:
            tournament.current_stage = TournamentStage.FINALS
    elif tournament.current_stage == TournamentStage.QUALIFIERS_TIE_BREAK:
        tournament.current_stage = TournamentStage.FINALS
    elif tournament.current_stage == TournamentStage.FINALS:
        if data.tie_breaker_needed:
            tournament.current_stage = TournamentStage.FINALS_TIE_BREAK
        else:
            tournament.status = TournamentStatus.FINISHED


@router.post("/tournaments/{tournament_id}/archers/{archer_id}")
async def add_archer_to_tournament(
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
async def add_team_to_tournament(
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


def generate_individual_match(session: Session, tournament: Tournament):
    archer_links = sorted(tournament.archers, key=lambda x: x.number)
    archers = session.exec(
        select(Archer).where(Archer.id.in_([link.archer_id for link in archer_links]))
    ).all()
    target_count = tournament.target_count
    matches = tournament.matches

    matches_per_archer = {
        archer.id: sum(
            1 for match in matches if archer.id in map(lambda x: x.id, match.archers)
        )
        for archer in archers
    }
    most_played_archer = max(matches_per_archer.values())
    archers_left_to_play = [
        archer
        for archer in archers
        if matches_per_archer[archer.id] < most_played_archer
    ]

    if len(archers_left_to_play) == 0:
        new_match_archers = archers[:target_count]
    else:
        new_match_archers = archers_left_to_play[:target_count]

    new_match = Match()
    new_match.tournament = tournament
    new_match.stage = tournament.current_stage
    new_match.archers = new_match_archers

    session.add(new_match)
    session.commit()
    session.refresh(new_match)
    session.refresh(tournament)

    return tournament


def generate_team_match(session: Session, tournament: Tournament):
    teams = sorted(tournament.teams, key=lambda x: x.number)
    target_count = tournament.target_count
    matches = tournament.matches

    team_representantives_links = [team.archers[0] for team in teams]
    team_representantives = session.exec(
        select(Archer).where(
            Archer.id.in_([link.archer_id for link in team_representantives_links])
        )
    ).all()

    matches_per_representative = {
        representative.id: sum(
            1
            for match in matches
            if representative.id in map(lambda x: x.id, match.archers)
        )
        for representative in team_representantives
    }

    most_played_representative = max(matches_per_representative.values())
    teams_left_to_play = [
        team
        for team in teams
        if matches_per_representative[team.archers[0].archer_id]
        < most_played_representative
    ]

    def fill_spots(teams, target_count):
        spots = target_count
        new_match_teams = []

        for team in teams:
            if spots == 0:
                break

            new_match_teams.append(team)
            spots -= len(team.archers)

        return new_match_teams

    if len(teams_left_to_play) == 0:
        new_match_teams = fill_spots(teams, target_count)
    else:
        new_match_teams = fill_spots(teams_left_to_play, target_count)

    new_match_archer_team_links = [
        archer for team in new_match_teams for archer in team.archers
    ]
    new_match_archers = session.exec(
        select(Archer).where(
            Archer.id.in_([link.archer_id for link in new_match_archer_team_links])
        )
    ).all()

    new_match = Match()
    new_match.tournament = tournament
    new_match.stage = tournament.current_stage
    new_match.archers = new_match_archers

    session.add(new_match)
    session.commit()
    session.refresh(new_match)
    session.refresh(tournament)

    return tournament


@router.post(
    "/tournaments/{tournament_id}/matches", response_model=TournamentWithEverything
)
async def add_match_to_tournament(
    tournament_id: int,
    session: Session = Depends(get_session),
):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    match tournament.format:
        case TournamentFormat.INDIVIDUAL:
            tournament = generate_individual_match(session, tournament)
        case TournamentFormat.TEAM:
            tournament = generate_team_match(session, tournament)
        case _:
            raise HTTPException(status_code=400, detail="Invalid tournament format")

    await ws_instance.broadcast("new match")

    return tournament


@router.delete("/tournaments/{tournament_id}/archers/{archer_id}")
async def remove_archer_from_tournament(
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
async def delete_tournament(
    tournament_id: int, session: Session = Depends(get_session)
):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    session.delete(tournament)
    session.commit()
    return {"message": "Tournament deleted"}
