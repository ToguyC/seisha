from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, create_engine, select

from .api_models import ShooterInput, ShotInput
from .sql_models import HitEnum, Series, Shooter, Match

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


@app.get("/series/:shooter_id/:tournament_id", response_model=List[Series])
def get_series_by_shooter_and_tournament(
    shooter_id: int,
    tournament_id: int,
    session: Session = Depends(get_session),
):
    statement = select(Series).where(
        Series.shooter_id == shooter_id, Series.match_id == tournament_id
    )
    results = session.exec(statement).all()

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No series found for this shooter in the given tournament.",
        )

    return results


@app.post("/shot")
def post_shot(data: ShotInput, session: Session = Depends(get_session)):
    # Get shooter's latest series in this tournament
    series = session.exec(
        select(Series)
        .where(
            Series.shooter_id == data.shooter_id,
            Series.match_id == data.tournament_id,
        )
        .order_by(Series.id.desc())
    ).first()

    if series and len(series.shots) < ARROWS_PER_SERIES:
        shots = series.shots
    else:
        # Validate shooter and tournament exist
        shooter = session.get(Shooter, data.shooter_id)
        tournament = session.get(Match, data.tournament_id)

        if not shooter:
            raise HTTPException(status_code=404, detail="Shooter not found.")
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found.")

        series = Series(shooter_id=data.shooter_id, match_id=data.tournament_id)
        series.shots = []
        session.add(series)
        session.commit()
        session.refresh(series)
        shots = []

    # Append and update
    hit_type = get_hit_enum(data.shot)
    if hit_type is None:
        raise HTTPException(status_code=400, detail="Invalid shot type.")

    shots.append(hit_type)
    series.shots = shots
    series.updated_at = datetime.now()
    session.commit()

    return {"message": "Shot recorded", "series_id": series.id, "shots": series.shots}


@app.post("/match")
def post_match(session: Session = Depends(get_session)):
    match = Match()
    session.add(match)
    session.commit()
    session.refresh(match)
    return match


@app.post("/shooter")
def post_shooter(data: ShooterInput, session: Session = Depends(get_session)):
    shooter = Shooter(name=data.name)
    session.add(shooter)
    session.commit()
    session.refresh(shooter)
    return shooter


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
        raise HTTPException(
            status_code=404, detail="No series found for this match"
        )

    return {
        "match": match,
        "series": {
            "shooter_id": series[0].shooter_id,
            "match_id": series[0].match_id,
            "shots": [s.shots for s in series],
        },
    }
