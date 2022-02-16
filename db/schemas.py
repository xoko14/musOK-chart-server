from pydantic import BaseModel


class SongBase(BaseModel):
    id: str
    song_name: str


class SongCreate(SongBase):
    pass


class Song(SongBase):
    author: str
    music: str
    easy_diff: tuple
    normal_diff: tuple
    hard_diff: tuple
    
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