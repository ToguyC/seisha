from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..models.models import Match, MatchWithSeries
from ..utils.sqlite import get_session

router = APIRouter()


@router.post("/match")
def post_match(session: Session = Depends(get_session)):
    match = Match()
    session.add(match)
    session.commit()
    session.refresh(match)
    return match


@router.get("/matches/{match_id}", response_model=MatchWithSeries)
def get_match(match_id: int, session: Session = Depends(get_session)):
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    print(match.archers)
    print(match.series)

    return match
