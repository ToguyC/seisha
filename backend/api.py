from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, create_engine, func, select

from .api_models import ArcherInput, ArrowInput
from .sql_models import Archer, HitEnum, Match, Series

ARROWS_PER_SERIES = 4


def get_session():
    with Session(engine) as session:
        yield session


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


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
sqlite_file_name = "tournament.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


@app.get("/series/:archer_id/:tournament_id", response_model=List[Series])
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


@app.post("/arrow")
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


@app.post("/match")
def post_match(session: Session = Depends(get_session)):
    match = Match()
    session.add(match)
    session.commit()
    session.refresh(match)
    return match


@app.get("/archers")
def get_archers_paginated(
    session: Session = Depends(get_session),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
):
    offset = (page - 1) * limit

    total_stmt = select(func.count()).select_from(Archer)
    total = session.exec(total_stmt).one()

    archers_stmt = (
        select(Archer).offset(offset).limit(limit).order_by(Archer.id.asc())
    )
    archers = session.exec(archers_stmt).all()

    total_pages = (total + limit - 1) // limit

    return {
        "count": len(archers),
        "total": total,
        "page": page,
        "total_pages": total_pages,
        "limit": limit,
        "data": archers,
    }


@app.post("/archers")
def post_archer(data: ArcherInput, session: Session = Depends(get_session)):
    archer = Archer(name=data.name, position=data.position)
    session.add(archer)
    session.commit()
    session.refresh(archer)
    return archer


@app.delete("/archers/{archer_id}")
def delete_archer(archer_id: int, session: Session = Depends(get_session)):
    archer = session.get(Archer, archer_id)
    if not archer:
        raise HTTPException(status_code=404, detail="Archer not found")

    session.delete(archer)
    session.commit()
    return {"message": "Archer deleted"}


@app.get("/match/{match_id}")
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
