from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(username=user.username, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit() 
    db.refresh(db_user)
    return db_user

def get_song(db: Session, song_id: int):
    return db.query(models.Song).filter(models.Song.id == song_id).first()

def create_song(db: Session, song: schemas.SongCreateAPI, audio: str, art: str, easy: str | None = None, normal: str | None = None, hard: str | None = None):
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
        song_art=[art, song.song_art_artist]
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song