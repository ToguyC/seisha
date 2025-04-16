from typing import List

from .archer import ArcherPublic
from .match import MatchPublic
from .tournament import TournamentPublic


class TournamentWithArchers(TournamentPublic):
    archers: List[ArcherPublic] = []


class TournamentWithArchersAndMatches(TournamentWithArchers):
    matches: List[MatchPublic] = []


class ArcherWithTournaments(ArcherPublic):
    tournaments: List[TournamentPublic] = []
