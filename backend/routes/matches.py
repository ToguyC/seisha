from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..models.models import Match, Series
from ..utils.sqlite import get_session

router = APIRouter()


@router.post("/match")
def post_match(session: Session = Depends(get_session)):
    match = Match()
    session.add(match)
    session.commit()
    session.refresh(match)
    return match


@router.get("/match/{match_id}")
def get_match(match_id: int, session: Session = Depends(get_session)):
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    series = session.exec(
        select(Series)
        .where(Series.match_id == match_id)
        .order_by(Series.created_at.asc())
    ).all()

    if not series:
        raise HTTPException(status_code=404, detail="No series found for this match")

    return {
        "match": match,
        "series": {
            "archer_id": series[0].archer_id,
            "match_id": series[0].match_id,
            "arrows": [s.arrows for s in series],
        },
    }
