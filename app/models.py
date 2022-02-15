from .database import Base
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Time
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """Describes a User table in db"""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )


class Playlist(Base):
    """Describes a Playlist table in db"""

    __tablename__ = "playlists"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    private = Column(Boolean, server_default="True", nullable=False)
    desc = Column(String, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=text("NOW()"), nullable=True)
    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )


class Artist(Base):
    """Describes an Artists table in db"""

    __tablename__ = "artists"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=text("NOW()"), nullable=True)
    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    songs = relationship("Song")


class Genre(Base):
    """Creates a relationship table for Genres to Songs"""

    __tablename__ = "genres"
    id = Column(Integer, primary_key=True)
    genre = Column(String, nullable=False, unique=True)


class Song(Base):
    """Creates a Songs table in db"""

    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    length = Column(Time, nullable=True)
    genre_id = Column(
        Integer, ForeignKey("genres.id", ondelete="CASCADE"), nullable=True
    )
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=text("NOW()"), nullable=True)
    artist_id = Column(
        Integer, ForeignKey("artists.id", ondelete="CASCADE"), nullable=False
    )
    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    playlist = relationship("PlaylistSongs")


class PlaylistSongs(Base):
    """Creates a many-to-many relationship for Songs in Playlists"""

    __tablename__ = "playlist_songs"
    song_id = Column(
        Integer, ForeignKey("songs.id", ondelete="CASCADE"), primary_key=True
    )
    playlist_id = Column(
        Integer, ForeignKey("playlists.id", ondelete="CASCADE"), primary_key=True
    )
    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )


class Like(Base):
    """Creates a table for User to like song"""

    __tablename__ = "likes"
    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    song_id = Column(
        Integer, ForeignKey("songs.id", ondelete="CASCADE"), primary_key=True
    )
