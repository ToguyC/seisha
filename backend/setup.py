import json
from datetime import datetime, timedelta

from models.models import (
    Archer,
    ArcherMatchLink,
    ArcherTeamLink,
    ArcherTournamentLink,
    Match,
    Series,
    Team,
    Tournament,
)
from sqlmodel import Session, SQLModel, select
from utils.sqlite import engine

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
        "target_count": 5,
        "status": "live",
    },
    {
        "name": "Tournoi Fun",
        "format": "team",
        "start_date": datetime(2025, 6, 26),
        "end_date": datetime(2025, 6, 26),
        "target_count": 4,
        "status": "live",
    },
]

teams = {
    2: [
        {"name": "Team A", "archers": [2, 3]},
        {"name": "Team B", "archers": [4, 1]},
        {"name": "Team C", "archers": [6, 7]},
    ]
}

individuals = {1: [1, 2, 3, 4, 5, 6, 7]}

matches = {
    1: [
        {
            "archers": [1, 2, 3, 4, 5],
            "finished": True,
            "series": [
                {"archer_id": 1, "arrows": [0, 1, 1, 0]},
                {"archer_id": 2, "arrows": [1, 0, 1, 0]},
                {"archer_id": 3, "arrows": [0, 1, 0, 1]},
                {"archer_id": 4, "arrows": [1, 1, 0, 0]},
                {"archer_id": 5, "arrows": [0, 0, 1, 1]},
            ],
        },
        {
            "archers": [6, 7],
            "finished": True,
            "series": [
                {"archer_id": 6, "arrows": [1, 0, 0, 1]},
                {"archer_id": 7, "arrows": [0, 1, 1, 0]},
            ],
        },
        {
            "archers": [1, 2, 3, 4, 5],
            "series": [
                {"archer_id": 1, "arrows": [1]},
                {"archer_id": 2, "arrows": [1]},
                {"archer_id": 3, "arrows": [1]},
                {"archer_id": 4, "arrows": [2]},
                {"archer_id": 5, "arrows": [0]},
            ],
        },
    ],
    2: [
        {
            "archers": [2, 3, 4, 1],
            "finished": True,
            "series": [
                {"archer_id": 2, "arrows": [0, 1, 1, 0]},
                {"archer_id": 3, "arrows": [1, 0, 1, 0]},
                {"archer_id": 4, "arrows": [0, 1, 0, 1]},
                {"archer_id": 1, "arrows": [1, 1, 0, 0]},
            ]
        },
        {
            "archers": [6, 7],
            "finished": True,
            "series": [
                {"archer_id": 6, "arrows": [1, 0, 0, 1]},
                {"archer_id": 7, "arrows": [0, 1, 1, 0]},
            ]
        },
        {
            "archers": [2, 3, 4, 1],
            "started_at": datetime.today(),
            "series": [
                {"archer_id": 2, "arrows": [0]},
                {"archer_id": 3, "arrows": [0]},
                {"archer_id": 4, "arrows": [1]},
                {"archer_id": 1, "arrows": [1]},
            ]
        },
        {
            "archers": [6, 7],
            "started_at": datetime.today(),
            "series": [
                {"archer_id": 6, "arrows": [1, 0, 1]},
                {"archer_id": 7, "arrows": [1, 1]},
            ]
        }
    ]
}


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

        for tournament_id, match_list in matches.items():
            tournament = session.get(Tournament, tournament_id)

            for match_data in match_list:
                match = Match()
                match.tournament = tournament
                match.finished = match_data.get("finished", False)
                session.add(match)

                archer_ids = match_data["archers"]
                series_data = match_data["series"]

                archers = session.exec(
                    select(Archer).where(Archer.id.in_(archer_ids))
                ).all()

                for archer in archers:
                    archer_match_link = ArcherMatchLink(
                        archer_id=archer.id, match_id=match.id
                    )
                    session.add(archer_match_link)

                for series in series_data:
                    series_obj = Series(
                        match_id=match.id,
                        archer_id=series["archer_id"],
                        arrows_raw=json.dumps(series["arrows"]),
                    )
                    session.add(series_obj)

        session.commit()
