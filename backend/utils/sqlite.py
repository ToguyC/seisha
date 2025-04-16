from sqlmodel import Session, create_engine

sqlite_file_name = "tournament.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def get_session():
    with Session(engine) as session:
        yield session
