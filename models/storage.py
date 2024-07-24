""""""

from sqlalchemy import URL, create_engine, select, insert
from sqlalchemy import Column, Float, Integer, MetaData, String, Table, Date, ForeignKey
from sqlalchemy.sql.expression import func
from dotenv import dotenv_values


db_params = dotenv_values()
db_url = URL.create(
    "postgresql+psycopg2",
    username=db_params["DB_USER"],
    password=db_params["DB_USER_PWD"],
    database=db_params["DB_NAME"],
    host="localhost",
)

engine = create_engine(db_url)

metadata_obj = MetaData()

word_tbl = Table(
    "words",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("title", String(300)),
    Column("freq", Float),
)

word_history_tbl = Table(
    "word_history",
    metadata_obj,
    Column("day", Date, nullable=False),
    Column("word_id", Integer, ForeignKey("words.id"), nullable=False),
)

metadata_obj.create_all(engine)


def select_day_words(date):
    picker = select(word_tbl.c.id, word_tbl.c.title).order_by(func.random()).limit(20)

    with engine.connect() as conn:
        words = conn.execute(picker).mappings().all()
        conn.execute(
            insert(word_history_tbl), [{"day": date, "word_id": w["id"]} for w in words]
        )
        conn.commit()

    return words


def load_day_words(date):
    stmt = (
        select(word_tbl.c.id, word_tbl.c.title)
        .join(word_history_tbl)
        .where(word_history_tbl.c.day == date)
    )
    with engine.connect() as conn:
        words = conn.execute(stmt).mappings().all()

    return words
