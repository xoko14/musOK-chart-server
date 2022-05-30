import os

from datetime import datetime, timedelta

from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from db import crud, models, schemas
from db.database import SessionLocal, engine
from response import responses

import response.responses

from passlib.context import CryptContext
from jose import JWTError, jwt

import uuid

from dotenv import load_dotenv

from xml.etree import ElementTree as ET

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "auth",
        "description": "OAuth2 Bearer token authentification",
    },
    {
        "name": "users",
        "description": "Operations with users.",
    },
    {
        "name": "songs",
        "description": "Operation with songs.",
    },
    {
        "name": "legal",
        "description": "Legal texts or anything the user needs to aknowledge before creating an account.",
    },
]

app = FastAPI(
    title="API for "+os.environ.get("STORE_NAME"),
    description=os.environ.get("STORE_DESCRIPTION"),
    openapi_tags=tags_metadata,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_optional(token: str = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    except:
        return None
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=schemas.Token, responses={**responses.UNAUTORIZED},tags=["auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/info", response_model=schemas.StoreInfo)
def get_info(db: Session = Depends(get_db)):
    info = schemas.StoreInfo(
        name=os.environ.get("STORE_NAME"),
        description=os.environ.get("STORE_DESCRIPTION"),
        total_songs=crud.get_total_songs(db)
        )
    return info

@app.post("/users/", response_model=schemas.User, responses={**responses.USER_ALREADY_REGISTERED}, tags=["users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User], tags=["users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/me", response_model=schemas.User, responses={**responses.UNAUTORIZED}, tags=["users"])
async def read_current_user(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@app.put("/users/me", response_model=schemas.User, responses={**responses.UNAUTORIZED}, tags=["users"])
async def update_user_info(user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    crud.update_user(db, user, current_user)

@app.get("/users/me/uploaded", response_model=List[schemas.Song], responses={**responses.UNAUTORIZED}, tags=["users"])
def read_current_user_uploaded(skip: int = 0, limit: int = 100, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user.songs_uploaded[skip:(limit + skip if limit is not None else None)]

@app.get("/users/me/favs", response_model=List[schemas.Song], responses={**responses.UNAUTORIZED}, tags=["users"])
def read_current_user_favs(skip: int = 0, limit: int = 100, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user.songs_faved[skip:(limit + skip if limit is not None else None)]

@app.delete("/users/me", responses={**responses.UNAUTORIZED}, tags=["users"])
def delete_current_user(current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    crud.delete_user(db, current_user.id)
    return

@app.get("/users/{user_id}", response_model=schemas.User, responses={**responses.ENTITY_NOT_FOUND}, tags=["users"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/{user_id}/uploaded", response_model=List[schemas.Song], responses={**responses.ENTITY_NOT_FOUND}, tags=["users"])
def read_current_user_uploaded(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user.songs_uploaded[skip:(limit + skip if limit is not None else None)]

@app.get("/users/{user_id}/favs", response_model=List[schemas.Song], responses={**responses.ENTITY_NOT_FOUND}, tags=["users"])
def read_user_favs(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user.songs_faved[skip:(limit + skip if limit is not None else None)]

@app.post("/songs/", response_model=schemas.Song, responses={**responses.INCORRECT_MEDIA_TYPE, **responses.UNAUTORIZED}, tags=["songs"])
def create_song(
    audio: UploadFile,
    art: UploadFile,
    song_info: UploadFile,
    token: str = Depends(oauth2_scheme),
    easy: Optional[UploadFile] = None,
    normal: Optional[UploadFile] = None,
    hard: Optional[UploadFile] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
    ):

    if audio.content_type != "audio/wav":
        raise HTTPException(status_code=415, detail="Media type must be audio/wav")
    if art.content_type != "image/png":
        raise HTTPException(status_code=415, detail="Media type must be image/png")
    if song_info.content_type != "text/xml":
        raise HTTPException(status_code=415, detail="Media type must be text/xml")

    xml = song_info.file.read()
    root: ET.Element = ET.fromstring(xml)

    try:
        song = schemas.SongCreateAPI(
            song_name=root.findtext("title"),
            author=root.findtext("artist"),
            easy_diff_text=root.find("easy").attrib["difficulty"],
            easy_diff_charter=root.find("easy").attrib["charter"],
            normal_diff_text=root.find("normal").attrib["difficulty"],
            normal_diff_charter=root.find("normal").attrib["charter"],
            hard_diff_text=root.find("hard").attrib["difficulty"],
            hard_diff_charter=root.find("hard").attrib["charter"],
            song_art_artist=root.find("jacket").attrib["artist"],
            uploader=current_user.id
        )
    except:
        raise HTTPException(415, "Song info XML not formed correctly")


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
    
@app.get("/songs/", response_model=List[schemas.Song], tags=["songs"])
def read_songs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user_optional)):
    if user:
        songs = crud.get_songs_auth(db, user, skip=skip, limit=limit)
    else:  
        songs = crud.get_songs(db, skip=skip, limit=limit)
    return songs

@app.get("/songs/{song_id}", response_model=schemas.Song, responses={**responses.ENTITY_NOT_FOUND}, tags=["songs"])
def get_song(song_id: str, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user_optional)):
    if user:
        db_song = crud.get_song_auth(db=db, song_id=song_id, user=user)
    else:
        db_song = crud.get_song(db=db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return db_song

@app.get("/songs/{song_id}/jacket", responses={**responses.ENTITY_NOT_FOUND}, tags=["songs"])
def get_song_jacket(song_id: str, db: Session = Depends(get_db)):
    db_song = crud.get_song(db=db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return FileResponse(f"./storage/images/{db_song.song_art[0]}")

@app.get("/songs/{song_id}/audio", responses={**responses.ENTITY_NOT_FOUND}, tags=["songs"])
def get_song_audio(song_id: str, db: Session = Depends(get_db)):
    db_song = crud.get_song(db=db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return FileResponse(f"./storage/audio/{db_song.music}")

@app.get("/songs/{song_id}/easy", responses={**responses.ENTITY_NOT_FOUND}, tags=["songs"])
def get_song_easy(song_id: str, db: Session = Depends(get_db)):
    db_song = crud.get_song(db=db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return FileResponse(f"./storage/charts/{db_song.easy_diff[1]}")

@app.get("/songs/{song_id}/normal", responses={**responses.ENTITY_NOT_FOUND}, tags=["songs"])
def get_song_normal(song_id: str, db: Session = Depends(get_db)):
    db_song = crud.get_song(db=db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return FileResponse(f"./storage/charts/{db_song.normal_diff[1]}")

@app.get("/songs/{song_id}/hard", responses={**responses.ENTITY_NOT_FOUND}, tags=["songs"])
def get_song_hard(song_id: str, db: Session = Depends(get_db)):
    db_song = crud.get_song(db=db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return FileResponse(f"./storage/charts/{db_song.hard_diff[1]}")

@app.put("/songs/{song_id}/fav", response_model=schemas.SongStatus, responses={**responses.ENTITY_NOT_FOUND, **responses.UNAUTORIZED}, tags=["songs"])
def fav_song(song_id: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    db_song = crud.get_song(db=db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    if crud.fav_song(db, current_user.id, song_id):
        fav_status = schemas.SongStatus(
            song = db_song,
            status = schemas.FavStatus.FAVED
        )
    else:
       fav_status = schemas.SongStatus(
            song = db_song,
            status = schemas.FavStatus.FAV_ERROR
        ) 
    return fav_status
    
@app.put("/songs/{song_id}/unfav", response_model=schemas.SongStatus, responses={**responses.ENTITY_NOT_FOUND, **responses.UNAUTORIZED}, tags=["songs"])
def unfav_song(song_id: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    db_song = crud.get_song(db=db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    if crud.unfav_song(db, current_user.id, song_id):
        fav_status = schemas.SongStatus(
            song = db_song,
            status = schemas.FavStatus.UNFAVED
        )
    else:
       fav_status = schemas.SongStatus(
            song = db_song,
            status = schemas.FavStatus.FAV_ERROR
        ) 
    return fav_status

@app.delete("/songs/{song_id}", responses={**responses.ENTITY_NOT_FOUND, **responses.UNAUTORIZED}, tags=["songs"])
def delete_song(song_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    db_song: models.Song = crud.get_song(db, song_id)
    if db_song.uploader is not current_user.id:
        raise HTTPException(status_code=401, detail="User did not upload this song")
    crud.delete_song(db, song_id)

@app.get("/legal", response_model=schemas.Legal, tags=["legal"])
def get_legal(db: Session = Depends(get_db)):
    with open("static/legal.text", "r") as f:
        text = f.read()
    return schemas.Legal(text=text)