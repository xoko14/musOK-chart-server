from sqlalchemy import Column, ForeignKey, Integer, String, true
from sqlalchemy_utils import CompositeType
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True)
    hashed_password = Column("pass", String)
    songs_uploaded = relationship("Song", back_populates="user")

class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=true, index=True, autoincrement=True)
    song_name = Column(String)
    author = Column(String)
    easy_diff = Column(
        CompositeType(
            "song_diff",
            [
                Column("difficulty", String),
                Column("chart", String),
                Column("charter", String)
            ]
        )
    )
    normal_diff = Column(
        CompositeType(
            "song_diff",
            [
                Column("difficulty", String),
                Column("chart", String),
                Column("charter", String)
            ]
        )
    )
    hard_diff = Column(
        CompositeType(
            "song_diff",
            [
                Column("difficulty", String),
                Column("chart", String),
                Column("charter", String)
            ]
        )
    )
    song_art = Column(
        CompositeType(
            "albumart",
            [
                Column("image", String),
                Column("artist", String)
            ]
        )
    )
    music = Column(String)
    uploader = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="songs_uploaded")

    association_table = Table('association', Base.metadata,
    Column('left_id', ForeignKey('left.id'), primary_key=True),
    Column('right_id', ForeignKey('right.id'), primary_key=True)
)