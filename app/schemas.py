from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, time
from pydantic.types import conint

""" Base Schemas """


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str
    username: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ArtistBase(BaseModel):
    id: int
    artist: str


class PlaylistSongs(BaseModel):
    playlist_id: int
    song_id: int


class PlaylistBase(BaseModel):
    name: str
    private: bool = True
    tags: List[str] = []


class SongBase(BaseModel):
    id: int
    title: str
    genre: Optional[str] = None


class Like(BaseModel):
    song_id: int
    dir: conint(ge=0, le=1)


""" Create Schemas """


class SongCreate(BaseModel):
    title: str
    genre: Optional[str] = None
    artist_id: int
    length: time


class PlaylistCreate(PlaylistBase):
    pass


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class ArtistCreate(BaseModel):
    name: str


""" Update Schemas """


class PlaylistUpdate(PlaylistBase):
    pass


class SongUpdate(BaseModel):
    title: Optional[str]
    genre: Optional[str]


""" Return Schemas """


class ArtistBaseOut(ArtistBase):
    class Config:
        orm_mode = True


class ArtistCreateOut(BaseModel):
    id: int
    artist: str

    class Config:
        orm_mode = True


class ArtistUpdateOut(BaseModel):
    id: int
    artist: str
    songs: Optional[List[SongBase]]

    class Config:
        orm_mode = True


class ArtistOut(BaseModel):
    id: int
    artist: str
    created_by: int
    songs: Optional[List[SongBase]]

    class Config:
        orm_mode = True


class SongUpdateOut(BaseModel):
    id: int
    title: str
    genre: Optional[str] = None
    length: time
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: int

    class Config:
        orm_mode = True


class Song(BaseModel):
    id: int
    title: str
    genre: Optional[str]
    length: time
    artist_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: int

    class Config:
        orm_mode = True


class SongOut(BaseModel):
    title: str
    genre: Optional[str]
    length: time
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: int
    like: int

    class Config:
        orm_mode = True


class SongsOut(BaseModel):
    Song: Song
    likes: int

    class Config:

        orm_mode = True


class SongGet(BaseModel):
    id: int
    title: str
    artist_id: int
    length: str
    created_at: str
    created_by: int

    class Config:
        orm_mode = True


class PlaylistSongsOut(BaseModel):
    id: int
    name: str
    private: bool
    created_by: int
    created_at: datetime
    songs: List[SongBase]

    class Config:
        orm_mode = True


class PlaylistOut(BaseModel):
    id: int
    name: str
    private: bool
    tags: Optional[List[str]]
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True
