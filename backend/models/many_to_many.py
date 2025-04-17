from sqlmodel import Field, SQLModel


class ArcherTournamentLink(SQLModel, table=True):
    archer_id: int = Field(foreign_key="archer.id", primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id", primary_key=True)


class TeamTournamentLink(SQLModel, table=True):
    team_id: int = Field(foreign_key="team.id", primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id", primary_key=True)