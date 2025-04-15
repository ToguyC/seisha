import json
import os
from typing import List, Optional

import numpy as np
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select

ARROWS_PER_SERIES = 4


def get_session():
    with Session(engine) as session:
        yield session


class ShotInput(BaseModel):
    shooter_id: int
    tournament_id: int
    shot: int


class TournamentInput(BaseModel):
    name: str


class ShooterInput(BaseModel):
    name: str


class Tournament(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    series: List["Series"] = Relationship(back_populates="tournament")


class Shooter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    series: List["Series"] = Relationship(back_populates="shooter")


class Series(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    shots_raw: str

    shooter_id: int = Field(foreign_key="shooter.id")
    shooter: Optional[Shooter] = Relationship(back_populates="series")

    tournament_id: int = Field(foreign_key="tournament.id")
    tournament: Optional[Tournament] = Relationship(back_populates="series")

    @property
    def shots(self) -> List[int]:
        return json.loads(self.shots_raw)

    @shots.setter
    def shots(self, value: List[int]):
        self.shots_raw = json.dumps(value)


def print_scoreboard(shots: np.ndarray, names: list = None, current_arrow: int = 0):
    """
    Prints the scoreboard for the given shots.
    :param shots: A 2D numpy array where each row represents a series of shots. Shape is (shooter, series, arrows).
    """
    total_arrows = shots.shape[1] * ARROWS_PER_SERIES

    left_pad = " " * 10
    print(f"{left_pad}   ", end="")
    for i in range(shots.shape[1] * 4):
        print(i % 4 + 1, end=" ")
        if i % 4 == 3:
            print("| ", end="")
    print("  中  |    %")
    print("-" * (13 + 4 * shots.shape[1] * 2 + 2 * shots.shape[1] + 2 + 14))

    for i, shooter in enumerate(shots):
        name = names[i] if names is not None else f"Shooter {i + 1}"
        print(f"{name:<10} : ", end="")

        for s, series in enumerate(shooter):
            str_series = " ".join(
                [
                    (
                        " "
                        if current_arrow <= (s * ARROWS_PER_SERIES) + j
                        else "O" if shot else "X"
                    )
                    for j, shot in enumerate(series)
                ]
            )
            print(f"{str_series} | ", end="")

        print(
            f"{np.sum(shooter.flatten()[:current_arrow]):<2}/{total_arrows} ", end="| "
        )
        print(
            f"{np.sum(shooter.flatten()[:current_arrow]) / (shots.shape[1] * ARROWS_PER_SERIES) * 100:.2f} %"
        )


def ask_shot(shooter: str = ""):
    while True:
        try:
            shot = int(
                input(
                    f"Enter shot (0 or 1) {'for shooter ' + shooter if shooter else ''}: "
                )
            )
            return shot > 0
        except ValueError:
            print("Invalid input. Please enter 0 or 1.")


def generate_shots(series: int, accuracy: float):
    return np.random.choice(
        [0, 1], (series, ARROWS_PER_SERIES), p=[1 - accuracy, accuracy]
    )


def emulate_shot(accuracy: float):
    return np.random.choice([0, 1], p=[1 - accuracy, accuracy])


def tournament(
    series: int,
    bot_accuracies: List[float],
    human_accuracies: List[float] = None,
    emulate: bool = False,
    print_board: bool = False,
):
    """
    Simulates a tournament with multiple bots and humans.

    :param series: Number of series in the tournament.
    :param bot_accuracies: List of accuracies for each bot.
    :param human_accuracies: List of accuracies for each human (if emulated).
    :param emulate: Whether to emulate human shots or ask for input.
    :param print_board: Whether to print the scoreboard after each shot.
    """
    if print_board:
        os.system("cls" if os.name == "nt" else "clear")

    num_bots = len(bot_accuracies)
    num_humans = len(human_accuracies) if human_accuracies else 1

    bot_shots = np.array([generate_shots(series, acc) for acc in bot_accuracies])
    if emulate:
        human_shots = np.array(
            [
                np.zeros((series, ARROWS_PER_SERIES), dtype=int)
                for _ in range(num_humans)
            ]
        )
    else:
        human_shots = np.zeros_like(bot_shots)

    shots = np.concatenate((bot_shots, human_shots), axis=0)

    if print_board:
        names = [f"Bot {i+1}" for i in range(num_bots)] + [
            f"Human {i+1}" for i in range(num_humans)
        ]
        print_scoreboard(shots, names=names)

    current_arrow = 0
    for i in range(series):
        for j in range(ARROWS_PER_SERIES):
            yield current_arrow, shots

            for h in range(num_humans):
                human_index = num_bots + h
                shots[human_index][i][j] = (
                    emulate_shot(human_accuracies[h])
                    if emulate
                    else ask_shot(str(h + 1))
                )
            current_arrow += 1

            if print_board:
                os.system("cls" if os.name == "nt" else "clear")
                print_scoreboard(
                    shots,
                    names=[f"Bot {i+1}" for i in range(num_bots)]
                    + [f"Human {i+1}" for i in range(num_humans)],
                    current_arrow=current_arrow,
                )


app = FastAPI()
sqlite_file_name = "tournament.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()


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
    # Step 1: Find the latest incomplete Series
    statement = (
        select(Series)
        .where(
            Series.shooter_id == data.shooter_id,
            Series.tournament_id == data.tournament_id,
        )
        .order_by(Series.id.desc())
    )
    series_list = session.exec(statement).all()

    target_series: Optional[Series] = None

    for s in series_list:
        current_shots = s.shots
        if len(current_shots) < ARROWS_PER_SERIES:
            target_series = s
            break

    # Step 2: If no incomplete series, create a new one
    if not target_series:
        # Check if the tournament exists
        tournament_statement = select(Tournament).where(
            Tournament.id == data.tournament_id
        )
        tournament = session.exec(tournament_statement).first()
        if not tournament:
            raise HTTPException(
                status_code=404,
                detail="Tournament not found.",
            )
        # Check if the shooter exists
        shooter_statement = select(Shooter).where(Shooter.id == data.shooter_id)
        shooter = session.exec(shooter_statement).first()
        if not shooter:
            raise HTTPException(
                status_code=404,
                detail="Shooter not found.",
            )

        target_series = Series(
            shooter_id=data.shooter_id, tournament_id=data.tournament_id
        )
        target_series.shots = []
        session.add(target_series)
        session.commit()
        session.refresh(target_series)

    # Step 3: Append the shot
    current_shots = target_series.shots
    current_shots.append(data.shot)
    target_series.shots = current_shots

    session.add(target_series)
    session.commit()

    return {
        "message": "Shot recorded",
        "series_id": target_series.id,
        "shots": target_series.shots,
    }


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
        select(Series).where(Series.tournament_id == tournament_id)
    ).all()
    if not series:
        raise HTTPException(
            status_code=404, detail="No series found for this tournament"
        )

    return {
        "tournament": tournament,
        "series": series,
    }


# if __name__ == "__main__":
#     # results = list(tournament(5, [0.8, 0.5, 0.1, 0.75], [0.5, 0.4, 0.5, 0.6], emulate=True, print_board=True))
#     for current_arrow, shots in tournament(
#         5, [0.8, 0.5, 0.1, 0.75], [0.5, 0.4, 0.5, 0.6], emulate=False, print_board=True
#     ):
#         shot_arrows = shots[1].flatten()[:current_arrow]
#         print(np.sum(shot_arrows))
