from sqlmodel import SQLModel
from utils.sqlite import engine
from models.models import (
    Archer,
    Match,
    Series,
    Tournament,
    ArcherTeamLink,
    ArcherTournamentLink,
)


def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables(engine)
