from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy.orm import Session

from db import crud, models, schemas
from db.database import SessionLocal, engine

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



@app.get("/songs/{song_id}", response_model=schemas.Song)
def get_song(song_id: str, db: Session = Depends(get_db)):
    return crud.get_song(db, song_id=song_id)

@app.post("/songs/", response_model=schemas.Song)
def create_song(song: schemas.Song, db: Session = Depends(get_db)):
    return crud.create_song(db=db, song=song)

# TODO: Placeholder, needs to connect to db and fetch id

@app.get("/songs/{song_id}/jacket")
def get_song_jacket(song_id: str):
    # return RedirectResponse(f"http://localhost/files/songs/{song_id}/jacket.png")
    return FileResponse(f"C:/xampp/htdocs/files/songs/{song_id}/jacket.png")

@app.get("/songs/{song_id}/audio")
def get_song_audio(song_id: str):
    return FileResponse(f"C:/xampp/htdocs/files/songs/{song_id}/song.wav")

@app.get("/songs/{song_id}/easy")
def get_song_easy(song_id: str):
    return FileResponse(f"C:/xampp/htdocs/files/songs/{song_id}/song_e.chart")

@app.get("/songs/{song_id}/normal")
def get_song_normal(song_id: str):
    return FileResponse(f"C:/xampp/htdocs/files/songs/{song_id}/song_n.chart")

@app.get("/songs/{song_id}/hard")
def get_song_hard(song_id: str):
    return FileResponse(f"C:/xampp/htdocs/files/songs/{song_id}/song_h.chart")