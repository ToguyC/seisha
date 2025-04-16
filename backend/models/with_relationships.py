from typing import List

from .archer import ArcherPublic
from .match import MatchPublic
from .series import SeriesPublic
from .tournament import TournamentPublic


class SeriesWithArcher(SeriesPublic):
    archer: ArcherPublic


class MatchWithSeriesAndArchers(MatchPublic):
    series: List[SeriesWithArcher] = []
    archers: List[ArcherPublic] = []


class TournamentWithArchers(TournamentPublic):
    archers: List[ArcherPublic] = []


class TournamentWithArchersAndMatches(TournamentWithArchers):
    matches: List[MatchWithSeriesAndArchers] = []


class ArcherWithTournaments(ArcherPublic):
    tournaments: List[TournamentPublic] = []
