from sqlmodel import SQLModel

from models.archer import Archer
from models.match import Match
from models.series import Series
from models.tournament import Tournament
from models.team import Team
from models.many_to_many import ArcherTournamentLink, TeamTournamentLink
from utils.sqlite import engine


def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables(engine)
