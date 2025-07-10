import json
import math
import random
from datetime import datetime, timedelta
from functools import reduce

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
    {"name": "Naoko Tanaka", "position": "rissha"},
    {"name": "Hiroshi Sakamoto", "position": "zasha"},
    {"name": "Clara Moreau", "position": "rissha"},
    {"name": "Lucas Fontaine", "position": "zasha"},
    {"name": "Marie Curie", "position": "rissha"},
    {"name": "René Dupont", "position": "zasha"},
    {"name": "Yuki Nakamura", "position": "zasha"},
    {"name": "Antoine Lefèvre", "position": "rissha"},
    {"name": "Sophie Bernard", "position": "zasha"},
    {"name": "Kenta Fujiwara", "position": "rissha"},
    {"name": "Lucie Garnier", "position": "zasha"},
    {"name": "Jean-Paul Renaud", "position": "zasha"},
    {"name": "Miyu Takahashi", "position": "rissha"},
]
archers_accuracy = [
    0.6,
    0.6,
    0.6,
    0.6,
    0.7,
    0.8,
    0.6,
    0.7,
    0.55,
    0.65,
    0.75,
    0.5,
    0.6,
    0.6,
    0.68,
    0.72,
    0.58,
    0.6,
    0.62,
    0.66,
]

tournaments = [
    {
        "name": "月来会 第10回 明弓館弓道大会",
        "format": "individual",
        "type": "standard",
        "start_date": datetime(2025, 6, 26),
        "end_date": datetime(2025, 6, 26),
        "advancing_count": 5,
        "qualifiers_round_count": 4,
        "finals_round_count": 4,
        "target_count": 5,
        "status": "live",
        "current_stage": "qualifiers",
    },
    {
        "name": "Tournoi Fun",
        "format": "team",
        "type": "standard",
        "start_date": datetime(2025, 6, 26),
        "end_date": datetime(2025, 6, 26),
        "advancing_count": None,
        "qualifiers_round_count": 0,
        "finals_round_count": 4,
        "target_count": 4,
        "status": "live",
        "current_stage": "finals",
    },
    {
        "name": "Test",
        "format": "team",
        "type": "standard",
        "start_date": datetime(2025, 6, 26),
        "end_date": datetime(2025, 6, 26),
        "advancing_count": 2,
        "qualifiers_round_count": 4,
        "finals_round_count": 4,
        "target_count": 4,
        "status": "live",
        "current_stage": "qualifiers",
    },
]

teams = {
    2: [
        {"name": "Team A", "archers": [2, 3]},
        {"name": "Team B", "archers": [4, 1]},
        {"name": "Team C", "archers": [6, 7]},
    ],
    3: [
        {"name": "Team A", "archers": [1, 2]},
        {"name": "Team B", "archers": [4, 5]},
        {"name": "Team C", "archers": [7, 8]},
    ],
}

individuals = {
    1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
}


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
            }
        )

    return matches


def get_matches_count(t, id):
    if t["format"] == "individual":
        matches_per_round = math.ceil(len(individuals[id]) / t["target_count"])
    elif t["format"] == "team":
        players = reduce(list.__add__, [team["archers"] for team in teams[id]], [])
        matches_per_round = math.ceil(len(players) / t["target_count"])

    return matches_per_round * (
        t["qualifiers_round_count"]
        if t["current_stage"] == "qualifiers"
        else t["finals_round_count"]
    )


def generate_structured_matches():
    matches = {i + 1: [] for i in range(len(tournaments))}

    # Individual matches
    individual_archers = individuals[1]
    target_count_ind = tournaments[0]["target_count"]
    matches[1] = generate_rotating_matches(
        individual_archers, target_count_ind, get_matches_count(tournaments[0], 1)
    )

    # Team matches
    ordered_team_archers = [aid for team in teams[2] for aid in team["archers"]]
    target_count_team = tournaments[1]["target_count"]
    matches[2] = generate_rotating_matches(
        ordered_team_archers, target_count_team, get_matches_count(tournaments[1], 2)
    )
    ordered_team_archers = [aid for team in teams[3] for aid in team["archers"]]
    target_count_team = tournaments[2]["target_count"]
    matches[3] = generate_rotating_matches(
        ordered_team_archers, target_count_team, get_matches_count(tournaments[2], 3)
    )

    # Add 'stage' field to individual matches
    for match in matches[2]:
        match["stage"] = "finals"

    # Add 'finished' field to the first 80% of matches
    for i in range(int(0.8 * len(matches[1]))):
        matches[1][i]["finished"] = True

    for i in range(int(0.8 * len(matches[2]))):
        matches[2][i]["finished"] = True

    for i in range(int(0.8 * len(matches[3]))):
        matches[3][i]["finished"] = True

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

        for tournament_id, match_list in generate_structured_matches().items():
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
