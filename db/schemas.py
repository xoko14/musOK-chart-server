from pydantic import BaseModel


class SongBase(BaseModel):
    song_name: str
    author: str
    music: str
    easy_diff: tuple
    normal_diff: tuple
    hard_diff: tuple


class SongCreate(SongBase):
    pass


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
    items: list[Song] = []

    class Config:
        orm_mode = True