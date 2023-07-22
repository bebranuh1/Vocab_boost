from sqlalchemy import Column, ForeignKey, create_engine, Integer
from sqlalchemy.dialects.postgresql import CHAR, BIGINT, VARCHAR
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

"""Just creating database using sqlalchemy library"""

db_name = "BigData"
sqlite_database = f"sqlite:///{db_name}.db"

engine = create_engine(sqlite_database)


class Base(DeclarativeBase): pass


class Language(Base):
    """First table - language, that stores three columns: 1)id of user 2) source language 3) destination language,
    also there is relationship with table - word based on user in table words"""

    __tablename__ = "language"
    id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    source = Column(CHAR(2), nullable=False)
    destination = Column(CHAR(2), nullable=False)
    words = relationship("Word", back_populates="user")


class Word(Base):
    """Second table - word, that stores three columns: 1)user id 2) source language 3) destination language, also
    there is relationship with table - language based on words in table language"""

    __tablename__ = "word"
    user_id = Column(Integer, ForeignKey("language.id"), index=True, primary_key=True)
    source = Column(VARCHAR(100), primary_key=True)
    destination = Column(VARCHAR(100))
    user = relationship("Language", back_populates="words")


Base.metadata.create_all(bind=engine)


class DBWorker:
    def __init__(self, engine):
        self.engine = engine
        self.session_maker = sessionmaker(autoflush=False, bind=engine)

    def with_db(self, function):
        def wrapper(*args, **kwargs):
            with self.session_maker() as db:
                function(*args, **kwargs, db=db)
        return wrapper



db_worker = DBWorker(engine)
