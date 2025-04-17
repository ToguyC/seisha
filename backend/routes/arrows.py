from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..api_models import ArrowInput
from ..models.models import Archer, Match, HitEnum, Series
from ..utils.sqlite import get_session

ARROWS_PER_SERIES = 4


router = APIRouter()


def get_hit_enum(value: int) -> Optional[HitEnum]:
    match value:
        case 0:
            return HitEnum.miss
        case 1:
            return HitEnum.hit
        case 2:
            return HitEnum.ensure
        case _:
            return None


@router.post("/arrow")
def post_arrow(data: ArrowInput, session: Session = Depends(get_session)):
    # Get archer's latest series in this tournament
    series = session.exec(
        select(Series)
        .where(
            Series.archer_id == data.archer_id,
            Series.match_id == data.tournament_id,
        )
        .order_by(Series.id.desc())
    ).first()

    if series and len(series.arrows) < ARROWS_PER_SERIES:
        arrows = series.arrows
    else:
        # Validate archer and tournament exist
        archer = session.get(Archer, data.archer_id)
        tournament = session.get(Match, data.tournament_id)

        if not archer:
            raise HTTPException(status_code=404, detail="Archer not found.")
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found.")

        series = Series(archer_id=data.archer_id, match_id=data.tournament_id)
        series.arrows = []
        session.add(series)
        session.commit()
        session.refresh(series)
        arrows = []

    # Append and update
    hit_type = get_hit_enum(data.arrow)
    if hit_type is None:
        raise HTTPException(status_code=400, detail="Invalid arrow type.")

    arrows.append(hit_type)
    series.arrows = arrows
    series.updated_at = datetime.now()
    session.commit()

    return {"message": "Shot recorded", "series_id": series.id, "arrows": series.arrows}
