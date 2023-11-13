from sqlmodel import Session, SQLModel, create_engine, select
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}

SQL_ENGINE = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def init_db():
    SQLModel.metadata.create_all(SQL_ENGINE)

def get_session():
    with Session(SQL_ENGINE) as session:
        yield session