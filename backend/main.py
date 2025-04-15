import os
from typing import List

import numpy as np

ARROWS_PER_SERIES = 4


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
    print("    中     |    %")
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
                        else "?" if shot == 2 else "O" if shot else "X"
                    )
                    for j, shot in enumerate(series)
                ]
            )
            print(f"{str_series} | ", end="")

        arrows = shooter.flatten()[:current_arrow]
        hits = arrows == 1
        ensure_hits = arrows == 2
        print(
            f"{np.sum(hits):<2}/{total_arrows} {f'(± {np.sum(ensure_hits)})'}", end="| "
        )
        print(
            f"{np.sum(hits) / (shots.shape[1] * ARROWS_PER_SERIES) * 100:.2f} %"
        )


def ask_shot(shooter: str = ""):
    while True:
        try:
            shot = int(
                input(
                    f"Enter shot (0, 1, or 2) {'for shooter ' + shooter if shooter else ''}: "
                )
            )
            return shot
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


if __name__ == "__main__":
    # results = list(tournament(5, [0.8, 0.5, 0.1, 0.75], [0.5, 0.4, 0.5, 0.6], emulate=True, print_board=True))
    for current_arrow, shots in tournament(
        5, [0.8, 0.5, 0.1, 0.75], [0.5, 0.4, 0.5, 0.6], emulate=False, print_board=True
    ):
        shot_arrows = shots[1].flatten()[:current_arrow]
        print(np.sum(shot_arrows))
