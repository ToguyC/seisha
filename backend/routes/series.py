from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..models.models import Series
from ..utils.sqlite import get_session

router = APIRouter()


@router.get("/series/:archer_id/:tournament_id", response_model=List[Series])
def get_series_by_archer_and_tournament(
    archer_id: int,
    tournament_id: int,
    session: Session = Depends(get_session),
):
    statement = select(Series).where(
        Series.archer_id == archer_id, Series.match_id == tournament_id
    )
    results = session.exec(statement).all()

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No series found for this archer in the given tournament.",
        )

    return results
