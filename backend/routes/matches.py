import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..api_models import MatchArrowInput, MatchEnkinInput
from ..models.models import Archer, Match, MatchWithSeries, Series
from ..models.constants import MatchArrows
from ..utils.sqlite import get_session
from ..utils.ws_manager_insance import ws_instance

router = APIRouter()


@router.post("/match")
async def post_match(session: Session = Depends(get_session)):
    match = Match()
    session.add(match)
    session.commit()
    session.refresh(match)
    return match


@router.get("/matches/{match_id}", response_model=MatchWithSeries)
async def get_match(match_id: int, session: Session = Depends(get_session)):
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    return match


@router.delete("/matches/{match_id}", status_code=204)
async def delete_match(match_id: int, session: Session = Depends(get_session)):
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    session.delete(match)
    session.commit()


@router.get("/matches/{match_id}/archers/{archer_id}/arrows/{arrow_id}")
async def get_arrow(
    match_id: int,
    archer_id: int,
    arrow_id: int,
    session: Session = Depends(get_session),
):
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    archer = session.get(Archer, archer_id)
    if not archer:
        raise HTTPException(status_code=404, detail="Archer not found")

    series = session.exec(
        select(Series)
        .where(
            Series.archer_id == archer_id,
            Series.match_id == match_id,
        )
        .order_by(Series.id.desc())
    ).first()

    if not series:
        raise HTTPException(status_code=404, detail="Series not found")

    if arrow_id >= len(series.arrows):
        raise HTTPException(status_code=404, detail="Arrow not found")

    return series.arrows[arrow_id]


@router.post("/matches/{match_id}/archers/{archer_id}/arrows")
async def add_arrow_to_match(
    match_id: int,
    archer_id: int,
    data: MatchArrowInput,
    session: Session = Depends(get_session),
):
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    archer = session.get(Archer, archer_id)
    if not archer:
        raise HTTPException(status_code=404, detail="Archer not found")

    series = session.exec(
        select(Series)
        .where(
            Series.archer_id == archer_id,
            Series.match_id == match_id,
        )
        .order_by(Series.id.desc())
    ).first()

    new_arrow = [data.arrow]
    arrows_per_match = MatchArrows[match.format.name]

    if series and len(series.arrows) < arrows_per_match.value:
        new_arrows = series.arrows + new_arrow
        series.arrows_raw = json.dumps(new_arrows)
    else:
        series = Series(archer_id=archer_id, match_id=match_id)
        series.arrows = new_arrow

    await ws_instance.broadcast("new arrow")

    session.add(series)
    session.commit()
    session.refresh(series)
    session.refresh(match)

    return series

@router.put("/matches/{match_id}/finish")
async def finish_match(
    match_id: int,
    session: Session = Depends(get_session),
):
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.finished:
        raise HTTPException(status_code=400, detail="Match already finished")

    if not match.verify_finish:
        raise HTTPException(status_code=400, detail="Match cannot be finished yet")
    
    match.finished = True
    session.add(match)
    session.commit()
    session.refresh(match)

    await ws_instance.broadcast("match finished")

    return match


@router.put("/matches/{match_id}/archers/{archer_id}/arrows/{arrow_id}")
async def update_arrow(
    match_id: int,
    archer_id: int,
    arrow_id: int,
    data: dict,
    session: Session = Depends(get_session),
):
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    archer = session.get(Archer, archer_id)
    if not archer:
        raise HTTPException(status_code=404, detail="Archer not found")

    series = session.exec(
        select(Series)
        .where(
            Series.archer_id == archer_id,
            Series.match_id == match_id,
        )
        .order_by(Series.id.desc())
    ).first()

    if not series:
        raise HTTPException(status_code=404, detail="Series not found")

    arrows = series.arrows
    if arrow_id >= len(arrows):
        raise HTTPException(status_code=404, detail="Arrow not found")

    arrows[arrow_id] = data["arrow"]
    series.arrows_raw = json.dumps(arrows)

    await ws_instance.broadcast("arrow update")

    session.add(series)
    session.commit()
    session.refresh(series)
    session.refresh(match)

    return series

@router.post("/matches/{match_id}/archers/{archer_id}/enkin-place")
async def set_enkin_place(
    match_id: int,
    archer_id: int,
    data: MatchEnkinInput,
    session: Session = Depends(get_session),
):
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    archer = session.get(Archer, archer_id)
    if not archer:
        raise HTTPException(status_code=404, detail="Archer not found")

    series = session.exec(
        select(Series)
        .where(
            Series.archer_id == archer_id,
            Series.match_id == match_id,
        )
        .order_by(Series.id.desc())
    ).first()

    if not series:
        series = Series(archer_id=archer_id, match_id=match_id)

    series.arrows_raw = json.dumps([data.place])

    await ws_instance.broadcast("arrow update")

    session.add(series)
    session.commit()
    session.refresh(series)

    return series