import json
import random
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
    {"name": "Alexandre Illi", "position": "rissha"},
    {"name": "Tanguy Cavagna", "position": "zasha"},
    {"name": "Jessica Da Silive", "position": "zasha"},
    {"name": "Sabine Bouron", "position": "zasha"},
    {"name": "Ambre Leya", "position": "zasha"},
    {"name": "Kazutaka Ito", "position": "zasha"},
    {"name": "Etienne Manuard", "position": "rissha"},
]
archers_accuracy = [0.75, 0.6, 0.4, 0.6, 0.5, 0.8, 0.6]

tournaments = [
    {
        "name": "月来会　第10回　定期弓道大会",
        "format": "individual",
        "start_date": datetime(2025, 6, 26),
        "end_date": datetime(2025, 6, 26),
        "advancing_count": 4,
        "target_count": 5,
        "status": "live",
        "current_stage": "finals",
    },
    {
        "name": "Tournoi Fun",
        "format": "team",
        "start_date": datetime(2025, 6, 26),
        "end_date": datetime(2025, 6, 26),
        "advancing_count": None,
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

# matches = {
#     1: [
#         {
#             "archers": [1, 2, 3, 4, 5],
#             "finished": True,
#             "created_at": datetime.now() - timedelta(hours=1),
#             "series": [
#                 {"archer_id": 1, "arrows": [0, 1, 1, 0]},
#                 {"archer_id": 2, "arrows": [1, 0, 1, 0]},
#                 {"archer_id": 3, "arrows": [0, 1, 0, 1]},
#                 {"archer_id": 4, "arrows": [1, 1, 0, 0]},
#                 {"archer_id": 5, "arrows": [0, 0, 1, 1]},
#             ],
#         },
#         {
#             "archers": [6, 7],
#             "finished": True,
#             "created_at": datetime.now() - timedelta(minutes=40),
#             "series": [
#                 {"archer_id": 6, "arrows": [1, 0, 0, 1]},
#                 {"archer_id": 7, "arrows": [0, 1, 1, 0]},
#             ],
#         },
#         {
#             "archers": [1, 2, 3, 4, 5],
#             "created_at": datetime.now() - timedelta(minutes=20),
#             "series": [
#                 {"archer_id": 1, "arrows": [1, 1, 1, 1]},
#                 {"archer_id": 2, "arrows": [1, 0, 1, 1]},
#                 {"archer_id": 3, "arrows": [1, 0, 0, 0]},
#                 {"archer_id": 4, "arrows": [0, 1, 0, 1]},
#                 {"archer_id": 5, "arrows": [0, 0, 1, 0]},
#             ],
#         },
#         {
#             "archers": [6, 7],
#             "created_at": datetime.now() - timedelta(minutes=10),
#             "series": [
#                 {"archer_id": 6, "arrows": [0, 0, 1, 0]},
#                 {"archer_id": 7, "arrows": [1, 1, 1, 1]},
#             ],
#         },
#     ],
#     2: [
#         {
#             "archers": [2, 3, 4, 1],
#             "stage": "finals",
#             "finished": True,
#             "series": [
#                 {"archer_id": 2, "arrows": [0, 1, 1, 0]},
#                 {"archer_id": 3, "arrows": [1, 0, 1, 0]},
#                 {"archer_id": 4, "arrows": [0, 1, 0, 1]},
#                 {"archer_id": 1, "arrows": [1, 1, 0, 0]},
#             ],
#         },
#         {
#             "archers": [6, 7],
#             "stage": "finals",
#             "finished": True,
#             "series": [
#                 {"archer_id": 6, "arrows": [1, 0, 0, 1]},
#                 {"archer_id": 7, "arrows": [0, 1, 1, 0]},
#             ],
#         },
#         {
#             "archers": [2, 3, 4, 1],
#             "stage": "finals",
#             "series": [
#                 {"archer_id": 2, "arrows": [0]},
#                 {"archer_id": 3, "arrows": [0]},
#                 {"archer_id": 4, "arrows": [1]},
#                 {"archer_id": 1, "arrows": [1]},
#             ],
#         },
#         {
#             "archers": [6, 7],
#             "stage": "finals",
#             "series": [
#                 {"archer_id": 6, "arrows": [1, 0, 1]},
#                 {"archer_id": 7, "arrows": [1, 1]},
#             ],
#         },
#     ],
# }


def generate_rotating_matches(archer_list, target_count, num_matches):
    matches = []
    total = len(archer_list)
    full_cycles = total // target_count
    remainder = total % target_count
    pointer = 0

    for i in range(num_matches):
        match_archers = []
        for j in range(target_count):
            index = (pointer + j) % total
            if (
                i % ((total + target_count - 1) // target_count) == full_cycles
                and j >= remainder
            ):
                break
            match_archers.append(archer_list[index])
        pointer = (pointer + len(match_archers)) % total

        series = [
            {
                "archer_id": aid,
                "arrows": [
                    random.choices(
                        [0, 1],
                        [1 - archers_accuracy[aid - 1], archers_accuracy[aid - 1]],
                    )[0]
                    for _ in range(4)
                ],
            }
            for aid in match_archers
        ]
        matches.append(
            {
                "archers": match_archers,
                "created_at": datetime.now() - timedelta(minutes=10 * i),
                "series": series,
                "finished": random.choice([True, False]),
            }
        )

    return matches


def generate_structured_matches(num_individual_matches, num_team_matches):
    matches = {1: [], 2: []}

    # Individual matches
    individual_archers = individuals[1]
    target_count_ind = tournaments[0]["target_count"]
    matches[1] = generate_rotating_matches(
        individual_archers, target_count_ind, num_individual_matches
    )

    # Team matches
    ordered_team_archers = [aid for team in teams[2] for aid in team["archers"]]
    target_count_team = tournaments[1]["target_count"]
    team_matches = generate_rotating_matches(
        ordered_team_archers, target_count_team, num_team_matches
    )

    # Add 'stage' field to individual matches
    for match in matches[1]:
        match["stage"] = "finals"

    matches[2] = team_matches
    return matches


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

        for tournament_id, match_list in generate_structured_matches(10, 10).items():
            print(f"Processing matches for tournament ID: {tournament_id}")
            print(f"Number of matches: {len(match_list)}")
            tournament = session.get(Tournament, tournament_id)

            for match_data in match_list:
                match = Match()
                match.tournament = tournament
                match.finished = match_data.get("finished", False)
                match.stage = match_data.get("stage", None)
                if match_data.get("created_at"):
                    match.created_at = match_data["created_at"]
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
