from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, func, select

from ..api_models import (
    PaginatedTournaments,
    TeamInput,
    TournamentInput,
    TournamentNextStageInput,
    TournamentTieBreakFormatInput,
)
from ..models.constants import (
    TournamentFormat,
    TournamentStage,
    TournamentStatus,
    MatchFormat,
)
from ..models.models import (
    Archer,
    ArcherTournamentLink,
    Match,
    Team,
    Tournament,
    TournamentWithEverything,
)
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
        advancing_count=data.advancing_count,
    )
    session.add(tournament)
    session.commit()
    session.refresh(tournament)
    return tournament


@router.post("/tournaments/{tournament_id}/stage")
async def next_stage(
    tournament_id: int,
    data: TournamentNextStageInput,
    session: Session = Depends(get_session),
):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    if tournament.current_stage == TournamentStage.FINALS_TIE_BREAK:
        raise HTTPException(
            status_code=400,
            detail="Tournament is already in the finals tie-break stage",
        )

    sorted_participants = sorted(
        data.advancing_participants, key=lambda x: x.hit_count, reverse=True
    )
    least_hit_count = sorted_participants[-1].hit_count
    tie_break_participants = (
        [
            participant
            for participant in sorted_participants
            if participant.hit_count == least_hit_count
        ]
        if data.tie_breaker_needed
        else []
    )
    advancing_participants = (
        [
            participant
            for participant in sorted_participants
            if participant.hit_count > least_hit_count
        ]
        if data.tie_breaker_needed
        else sorted_participants
    )

    # Update already qualified participants
    for participant in advancing_participants:
        qualifiers_place = sorted_participants.index(participant) + 1

        if tournament.format == TournamentFormat.INDIVIDUAL:
            archer = session.get(ArcherTournamentLink, (participant.id, tournament_id))
            if not archer:
                raise HTTPException(
                    status_code=404, detail="Archer not found for advancing"
                )
            archer.qualifiers_place = qualifiers_place
            session.add(archer)
            session.commit()
            session.refresh(archer)
        elif tournament.format == TournamentFormat.TEAM:
            team = session.get(Team, participant.id)
            if not team:
                raise HTTPException(
                    status_code=404, detail="Team not found for advancing"
                )
            team.qualifiers_place = qualifiers_place
            session.add(team)
            session.commit()
            session.refresh(team)

    # Handle tie-break participants
    if data.tie_breaker_needed:
        if tournament.current_stage == TournamentStage.QUALIFIERS:
            tournament.current_stage = TournamentStage.QUALIFIERS_TIE_BREAK
        elif tournament.current_stage == TournamentStage.FINALS:
            tournament.current_stage = TournamentStage.FINALS_TIE_BREAK
        else:
            raise HTTPException(
                status_code=400, detail="Tie-break not applicable for current stage"
            )

        for participant in tie_break_participants:
            if tournament.format == TournamentFormat.INDIVIDUAL:
                archer = session.get(
                    ArcherTournamentLink, (participant.id, tournament_id)
                )
                if not archer:
                    raise HTTPException(
                        status_code=404, detail="Archer not found for tie-break"
                    )

                if tournament.current_stage == TournamentStage.QUALIFIERS_TIE_BREAK:
                    archer.tie_break_qualifiers = True
                elif tournament.current_stage == TournamentStage.FINALS_TIE_BREAK:
                    archer.tie_break_finals = True

                session.add(archer)
            elif tournament.format == TournamentFormat.TEAM:
                team = session.get(Team, participant.id)
                if not team:
                    raise HTTPException(
                        status_code=404, detail="Team not found for tie-break"
                    )

                if tournament.current_stage == TournamentStage.QUALIFIERS_TIE_BREAK:
                    team.tie_break_qualifiers = True
                elif tournament.current_stage == TournamentStage.FINALS_TIE_BREAK:
                    team.tie_break_finals = True

                session.add(team)
    else:
        if tournament.current_stage == TournamentStage.QUALIFIERS:
            tournament.current_stage = TournamentStage.FINALS
        elif tournament.current_stage == TournamentStage.FINALS:
            tournament.status = TournamentStatus.FINISHED
        else:
            raise HTTPException(
                status_code=400,
                detail="Cannot advance to next stage from current stage",
            )

    # Update tournament status
    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    await ws_instance.broadcast("tournament stage advanced")

    return tournament


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


def pick_match_archers(target_count: int, archers: List[Archer], matches: List[Match]):
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

    archers_to_user = archers_left_to_play or archers

    return archers_to_user[:target_count]


def pick_team_archers(
    session: Session, target_count: int, teams: List[Team], matches: List[Match]
):
    representative_ids = [team.archers[0].archer_id for team in teams]

    matches_per_representative = {
        rep_id: sum(1 for match in matches if rep_id in [a.id for a in match.archers])
        for rep_id in representative_ids
    }

    most_played = (
        max(matches_per_representative.values()) if matches_per_representative else 0
    )
    teams_left_to_play = [
        team
        for team in teams
        if matches_per_representative[team.archers[0].archer_id] < most_played
    ]

    teams_to_use = teams_left_to_play or teams

    selected_teams = []
    spots_remaining = target_count

    for team in teams_to_use:
        if spots_remaining <= 0:
            break
        selected_teams.append(team)
        spots_remaining -= len(team.archers)

    archer_ids = [
        archer.archer_id for team in selected_teams for archer in team.archers
    ]

    return session.exec(select(Archer).where(Archer.id.in_(archer_ids))).all()


def filter_participant(
    tournament: Tournament, participant: ArcherTournamentLink | Team
):
    if tournament.current_stage == TournamentStage.QUALIFIERS:
        return True
    elif tournament.current_stage == TournamentStage.QUALIFIERS_TIE_BREAK:
        return participant.tie_break_qualifiers
    elif tournament.current_stage == TournamentStage.FINALS:
        return participant.qualifiers_place is not None
    elif tournament.current_stage == TournamentStage.FINALS_TIE_BREAK:
        return participant.tie_break_finals
    return False


def generate_individual_match(
    session: Session, match_format: MatchFormat, tournament: Tournament
):
    archer_links = filter(
        lambda x: filter_participant(tournament, x), tournament.archers
    )
    archer_links = sorted(archer_links, key=lambda x: x.number)
    archers = session.exec(
        select(Archer).where(Archer.id.in_([link.archer_id for link in archer_links]))
    ).all()
    target_count = tournament.target_count
    matches = tournament.matches

    if match_format in {MatchFormat.STANDARD, MatchFormat.EMPEROR}:
        new_match_archers = pick_match_archers(target_count, archers, matches)
    elif match_format in {MatchFormat.IZUME, MatchFormat.ENKIN}:
        new_match_archers = archers

    new_match = Match()
    new_match.tournament = tournament
    new_match.format = match_format
    new_match.stage = tournament.current_stage
    new_match.archers = new_match_archers

    session.add(new_match)
    session.commit()
    session.refresh(new_match)
    session.refresh(tournament)

    return tournament


def generate_team_match(
    session: Session, match_format: MatchFormat, tournament: Tournament
):
    teams = filter(lambda x: filter_participant(tournament, x), tournament.teams)
    teams = sorted(teams, key=lambda x: x.number)
    target_count = tournament.target_count
    matches = tournament.matches

    new_match_archers = pick_team_archers(session, target_count, teams, matches)

    new_match = Match()
    new_match.tournament = tournament
    new_match.format = match_format
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
    data: TournamentTieBreakFormatInput,
    session: Session = Depends(get_session),
):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    match tournament.format:
        case TournamentFormat.INDIVIDUAL:
            tournament = generate_individual_match(session, data.format, tournament)
        case TournamentFormat.TEAM:
            tournament = generate_team_match(session, data.format, tournament)
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
