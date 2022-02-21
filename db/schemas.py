from typing import Optional, Type, List
from fastapi import Form
from pydantic import BaseModel
import inspect


def as_form(cls: Type[BaseModel]):
    """
    Adds an as_form class method to decorated models. The as_form class method
    can be used with FastAPI endpoints
    """
    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=(Form(field.default) if not field.required else Form(...)),
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig
    setattr(cls, "as_form", _as_form)
    return cls


class SongBase(BaseModel):
    song_name: str
    author: str
    music: str
    easy_diff: tuple
    normal_diff: tuple
    hard_diff: tuple
    song_art:tuple


class SongCreate(SongBase):
    pass


@as_form
class SongCreateAPI(BaseModel):
    song_name: str
    author: str
    easy_diff_text: Optional[str]
    easy_diff_charter: Optional[str]
    normal_diff_text: Optional[str]
    normal_diff_charter: Optional[str]
    hard_diff_text: Optional[str]
    hard_diff_charter: Optional[str]
    song_art_artist: str

    class Config:
        orm_mode = True



class Song(SongBase):
    id: str
    
    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    songs_uploaded: List[Song] = []

    class Config:
        orm_mode = True

class Store(BaseModel):
    name: str
    description: str

class StoreInfo(Store):
    total_songs: int

    class Config:
        orm_mode = True
