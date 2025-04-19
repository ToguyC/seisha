from datetime import datetime

from sqlmodel import SQLModel, Session
from utils.sqlite import engine
from models.models import (
    Archer,
    Match,
    Series,
    Team,
    Tournament,
    ArcherTeamLink,
    ArcherTournamentLink,
)


archers = [
    {"name": "Tanguy Cavagna", "position": "zasha"},
    {"name": "Alexandre Illi", "position": "rissha"},
    {"name": "Jessica Da Silive", "position": "zasha"},
    {"name": "Sabine Bouron", "position": "zasha"},
    {"name": "Ambre Leya", "position": "zasha"},
    {"name": "Kazutaka Ito", "position": "zasha"},
    {"name": "Etienne Manuard", "position": "rissha"},
]

tournaments = [
    {
        "name": "月来会　第10回　定期弓道大会",
        "format": "individual",
        "start_date": datetime(2025, 6, 26),
        "end_date": datetime(2025, 6, 26),
        "status": "upcoming",
    },
    {
        "name": "Tournoi Fun",
        "format": "team",
        "start_date": datetime(2025, 6, 26),
        "end_date": datetime(2025, 6, 26),
        "status": "upcoming",
    },
]

teams = {
    2: [
        {"name": "Team A", "archers": [2, 3, 4]},
        {"name": "Team B", "archers": [1, 6, 7]},
    ]
}

individuals = {1: [1, 2, 3, 4, 5, 6, 7]}


def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables(engine)

    with Session(engine) as session:
        for archer in archers:
            archer_obj = Archer(**archer)
            session.add(archer_obj)

        for tournament in tournaments:
            tournament_obj = Tournament(**tournament)
            session.add(tournament_obj)

        for tournament_id, team_list in teams.items():
            tournament = session.get(Tournament, tournament_id)

            for i, team_data in enumerate(team_list):
                team = Team(name=team_data["name"], number=i + 1)
                tournament.teams.append(team)

                for j, archer_id in enumerate(team_data["archers"]):
                    archer = session.get(Archer, archer_id)

                    if archer:
                        session.add(
                            ArcherTeamLink(
                                team_id=team.id, archer_id=archer.id, number=j + 1
                            )
                        )

        for tournament_id, archer_ids in individuals.items():
            tournament = session.get(Tournament, tournament_id)

            for i, archer_id in enumerate(archer_ids):
                archer = session.get(Archer, archer_id)

                if tournament and archer:
                    session.add(
                        ArcherTournamentLink(
                            tournament_id=tournament.id,
                            archer_id=archer.id,
                            number=i + 1,
                        )
                    )

        session.commit()
