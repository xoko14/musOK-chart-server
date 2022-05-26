from distutils.command.upload import upload
from fcntl import F_SEAL_SEAL
from pyexpat import model
from sqlalchemy.orm import Session

from typing import Optional

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, hashed_password=user.password)
    db.add(db_user)
    db.commit() 
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user: schemas.UserUpdate, current_user: models.User):
    db_user: models.User = get_user(db, current_user.id)
    db_user.username = user.username if user.username is not None else db_user.username
    db_user.hashed_password = user.password if user.password is not None else db_user.hashed_password
    db.commit()

def get_song(db: Session, song_id: int):
    return db.query(models.Song).filter(models.Song.id == song_id).first()

def get_songs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Song).offset(skip).limit(limit).all()

def get_song_auth(db: Session, song_id: int, user: schemas.User):
    song: models.Song = db.query(models.Song).filter(models.Song.id == song_id).first()
    song_schema = schemas.Song(
        id=song.id,
        song_name=song.song_name,
        author=song.author,
        music=song.music,
        easy_diff=song.easy_diff,
        normal_diff=song.normal_diff,
        hard_diff=song.hard_diff,
        song_art=song.song_art,
        uploader=song.uploader
    )
    song_schema.isFaved = True if db.execute(f"select * from favs where user_id = {user.id} and song_id = {song_id}") else False
    return song_schema

def get_songs_auth(db: Session, user: schemas.User, skip: int = 0, limit: int = 100):
    songs = db.query(models.Song).offset(skip).limit(limit).all()
    songs_s = []
    for song in songs:
        song_schema = schemas.Song(
            id=song.id,
            song_name=song.song_name,
            author=song.author,
            music=song.music,
            easy_diff=song.easy_diff,
            normal_diff=song.normal_diff,
            hard_diff=song.hard_diff,
            song_art=song.song_art,
            uploader=song.uploader
        )
        song_schema.isFaved = True if db.query(models.User).filter([song_ls.id == song.id for song_ls in models.User.songs_faved]) else False
        songs_s.append(song_schema)
    return songs_s


def create_song(db: Session, song: schemas.SongCreateAPI, audio: str, art: str, easy: Optional[str] = None, normal: Optional[str]= None, hard: Optional[str] = None):
    db_song = models.Song(
        song_name=song.song_name,
        author=song.author,
        music=audio,
        easy_diff=[
            song.easy_diff_text,
            easy,
            song.easy_diff_charter
            ],
        normal_diff=[
            song.normal_diff_text,
            normal,
            song.normal_diff_charter
            ],
        hard_diff=[
            song.hard_diff_text,
            hard,
            song.hard_diff_charter
            ],
        song_art=[art, song.song_art_artist],
        uploader=song.uploader
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song

def get_total_songs(db: Session):
    result = db.execute("select count(id) from songs")
    return result.first()[0]

def fav_song(db: Session, user_id: int, song_id: int):
    try:
        db_user: models.User = get_user(db, user_id)
        db_user.songs_faved.append(get_song(db, song_id))
        db.commit()
    except:
        return False
    return True
    
def unfav_song(db: Session, user_id: int, song_id: int):
    db_user: models.User = get_user(db, user_id)
    try:
        db_user.songs_faved.remove(get_song(db, song_id))
        db.commit()
    except:
        return False
    return True

def delete_song(db: Session, song_id: int):
    db.delete(get_song(db, song_id))
    db.commit()