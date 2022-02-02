from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
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

    artist = db.query(models.Artist).filter(models.Artist.id == song.artist_id).first()
    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id: {song.artist_id} not found",
        )

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


@router.get("/", response_model=List[schemas.SongsOut])
def get_songs(
    db: Session = Depends(get_db),
    title: Optional[str] = "",
    genre: Optional[str] = "",
):
    """Retrieves all songs by query, default all if no parameter given"""

    results = (
        db.query(models.Song, func.count(models.Like.song_id).label("likes"))
        .join(models.Like, models.Like.song_id == models.Song.id, isouter=True)
        .filter(models.Song.title.contains(title))
        .filter(models.Song.genre.contains(genre))
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
    # song = db.query(models.Song).filter(models.Song.id == id).first()
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
