from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, create_engine, select

from .api_models import ShooterInput, ShotInput, TournamentInput
from .sql_models import Series, Shooter, Tournament

ARROWS_PER_SERIES = 4


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()
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
        Series.shooter_id == shooter_id, Series.tournament_id == tournament_id
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
            Series.tournament_id == data.tournament_id,
        )
        .order_by(Series.id.desc())
    ).first()

    if series and len(series.shots) < ARROWS_PER_SERIES:
        shots = series.shots
    else:
        # Validate shooter and tournament exist
        shooter = session.get(Shooter, data.shooter_id)
        tournament = session.get(Tournament, data.tournament_id)

        if not shooter:
            raise HTTPException(status_code=404, detail="Shooter not found.")
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found.")

        series = Series(shooter_id=data.shooter_id, tournament_id=data.tournament_id)
        series.shots = []
        session.add(series)
        session.commit()
        session.refresh(series)
        shots = []

    # Append and update
    shots.append(data.shot)
    series.shots = shots
    series.updated_at = datetime.now()
    session.commit()

    return {"message": "Shot recorded", "series_id": series.id, "shots": series.shots}


@app.post("/tournament")
def post_tournament(data: TournamentInput, session: Session = Depends(get_session)):
    tournament = Tournament(name=data.name)
    session.add(tournament)
    session.commit()
    session.refresh(tournament)
    return tournament


@app.post("/shooter")
def post_shooter(data: ShooterInput, session: Session = Depends(get_session)):
    shooter = Shooter(name=data.name)
    session.add(shooter)
    session.commit()
    session.refresh(shooter)
    return shooter


@app.get("/tournament/{tournament_id}")
def get_tournament(tournament_id: int, session: Session = Depends(get_session)):
    tournament = session.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    series = session.exec(
        select(Series)
        .where(Series.tournament_id == tournament_id)
        .order_by(Series.id.desc())
    ).all()

    if not series:
        raise HTTPException(
            status_code=404, detail="No series found for this tournament"
        )

    return {
        "tournament": tournament,
        "series": {
            "shooter_id": series[0].shooter_id,
            "tournament_id": series[0].tournament_id,
            "shots": [s.shots for s in series],
        },
    }
