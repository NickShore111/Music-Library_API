from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from sqlalchemy import func
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix="/songs", tags=["Songs"])


@router.post("/", response_model=schemas.Song)
def create_song(
    song: schemas.SongCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Add one song to database, artist_id required"""
    # Check for presence of artist.id in db
    artist = db.query(models.Artist).filter(models.Artist.id == song.artist_id).first()
    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id: {song.artist_id} not found",
        )

    # If genre is str then coerce song.genre to genre.id
    # And check if genre classification is in db
    if song.genre is not None:
        print(song.genre)
        if type(song.genre) is str:
            # print("Genre is type string")
            genre_str_id = (
                db.query(models.Genre).filter(models.Genre.genre == song.genre).first()
            )
            if genre_str_id is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Genre type: {song.genre} not found",
                )
            song.genre = genre_str_id.id
        else:
            genre_int_id = (
                db.query(models.Genre).filter(models.Genre.id == song.genre).first()
            )
            if genre_int_id is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Genre id: {song.genre} not found",
                )

    # Check if song is already in db under assigned artist
    duplicate_song = (
        db.query(models.Artist)
        .join(models.Song)
        .filter(models.Artist.id == song.artist_id, models.Song.title == song.title)
        .first()
    )
    if duplicate_song:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Artist with id: {song.artist_id} and song title: '{song.title}' already exists",
        )

    new_song = models.Song(created_by=current_user.id, **song.dict())
    print(new_song)
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    return new_song


@router.put(
    "/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.SongUpdateOut
)
def update_song(
    id: int,
    updated_song: schemas.SongUpdate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Update song info if present and created_by == user"""

    song_query = db.query(models.Song).filter(models.Song.id == id)
    song = song_query.first()

    if song == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id: {id} not found",
        )

    if song.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    song_query.update(updated_song.dict(), synchronize_session=False)
    db.commit()
    return song_query.first()


# @router.get("/", response_model=List[schemas.SongsOut])
@router.get("/")
def get_songs(
    db: Session = Depends(get_db),
    title: Optional[str] = "",
    genre: Optional[Union[int, str]] = "",
    # limit: int = 10,
    # skip: int = 0,
):
    """Retrieves all songs by query, default all if no parameter given"""

    if genre is not None and type(genre) == str:
        results = (
            db.query(models.Song, func.count(models.Like.song_id).label("likes"))
            .join(models.Like, models.Like.song_id == models.Song.id, isouter=True)
            .join(models.Genre, models.Song.genre == models.Genre.id, isouter=True)
            .filter(models.Song.title.contains(title))
            .filter(models.Genre.genre.contains(genre))
            .group_by(models.Song.id)
        ).all()
    else:
        results = (
            db.query(models.Song, func.count(models.Like.song_id).label("likes"))
            .join(models.Like, models.Like.song_id == models.Song.id, isouter=True)
            .join(models.Genre, models.Song.genre == models.Genre.id, isouter=True)
            .filter(models.Song.title.contains(title))
            .filter(models.Song.genre == genre)
            .group_by(models.Song.id)
        ).all()

    return results


@router.get("/{id}", response_model=schemas.SongsOut)
def get_song(id: int, db: Session = Depends(get_db)):
    """Return one song from database with id"""
    song = (
        db.query(models.Song, func.count(models.Like.song_id).label("likes"))
        .join(models.Like, models.Like.song_id == models.Song.id, isouter=True)
        .group_by(models.Song.id)
        .filter(models.Song.id == id)
    ).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id: {id} was not found",
        )
    return song


@router.delete("/{id}")
def delete_song(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Delete one song from database with id"""

    song_query = db.query(models.Song).filter(models.Song.id == id)
    song = song_query.first()

    if song == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id: {id} was not found",
        )

    if song.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    song_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
