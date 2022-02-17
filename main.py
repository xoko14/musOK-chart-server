from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from db import crud, models, schemas
from db.database import SessionLocal, engine

import uuid

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/songs", response_model=schemas.Song)
def create_song(
    audio: UploadFile,
    art: UploadFile,
    song: schemas.SongCreateAPI = Depends(schemas.SongCreateAPI.as_form),
    easy: UploadFile | None = None,
    normal: UploadFile | None = None,
    hard: UploadFile | None = None,
    db: Session = Depends(get_db)
    ):

    if audio.content_type != "audio/wav":
        raise HTTPException(status_code=415, detail="Media type must be audio/wav")
    if art.content_type != "image/png":
        raise HTTPException(status_code=415, detail="Media type must be image/png")

    file_audio = f"{uuid.uuid4().hex}.wav"
    f = open(f"./storage/audio/{file_audio}", "wb")
    f.write(audio.file.read())
    f.close()
    audio.close()

    file_art = f"{uuid.uuid4().hex}.png"
    f = open(f"./storage/images/{file_art}", "wb")
    f.write(art.file.read())
    f.close()
    art.close()
    
    if easy:
        file_easy = f"{uuid.uuid4().hex}.chart"
        f = open(f"./storage/charts/{file_easy}", "wb")
        f.write(easy.file.read())
        f.close()
        normal.close()
    else:
        file_easy = None
    
    if normal:
        file_normal = f"{uuid.uuid4().hex}.chart"
        f = open(f"./storage/charts/{file_normal}", "wb")
        f.write(normal.file.read())
        f.close()
        normal.close()
    else:
        file_normal = None
    
    if hard:
        file_hard = f"{uuid.uuid4().hex}.chart"
        f = open(f"./storage/charts/{file_hard}", "wb")
        f.write(hard.file.read())
        f.close()
        hard.close()
    else:
        file_hard = None

    

    return crud.create_song(db, song, file_audio, file_art, file_easy, file_normal, file_hard)
    


@app.get("/songs/{song_id}", response_model=schemas.Song)
def get_song(song_id: str, db: Session = Depends(get_db)):
    db_song = crud.get_song(db=db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return db_song

@app.get("/songs/{song_id}/jacket")
def get_song_jacket(song_id: str, db: Session = Depends(get_db)):
    db_song = crud.get_song(db=db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return FileResponse(f"./storage/images/{db_song.song_art[0]}")

@app.get("/songs/{song_id}/audio")
def get_song_audio(song_id: str, db: Session = Depends(get_db)):
    db_song = crud.get_song(db=db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return FileResponse(f"./storage/audio/{db_song.music}")

@app.get("/songs/{song_id}/easy")
def get_song_easy(song_id: str, db: Session = Depends(get_db)):
    db_song = crud.get_song(db=db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return FileResponse(f"./storage/charts/{db_song.easy_diff[1]}")

@app.get("/songs/{song_id}/normal")
def get_song_normal(song_id: str, db: Session = Depends(get_db)):
    db_song = crud.get_song(db=db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return FileResponse(f"./storage/charts/{db_song.normal_diff[1]}")

@app.get("/songs/{song_id}/hard")
def get_song_hard(song_id: str, db: Session = Depends(get_db)):
    db_song = crud.get_song(db=db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return FileResponse(f"./storage/charts/{db_song.hard_diff[1]}")