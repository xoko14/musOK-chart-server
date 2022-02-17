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

def create_song(db: Session, song: schemas.SongCreate):
    db_song = models.Song(
        song_name=song.song_name,
        author=song.author,
        music=song.music,
        easy_diff=song.easy_diff,
        normal_diff=song.normal_diff,
        hard_diff=song.hard_diff,
        song_art=song.song_art
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song