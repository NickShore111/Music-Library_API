from sqlite3 import IntegrityError
from fastapi import Response, status, HTTPException, Depends, APIRouter
from pydantic import HttpUrl
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix="/playlist-songs", tags=["PlaylistSongs"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_playlist_song(
    playlist_song: schemas.PlaylistSongs,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Add one song to existing playlist"""
    playlist_query = db.query(models.Playlist).filter(
        playlist_song.playlist_id == models.Playlist.id
    )
    playlist = playlist_query.first()

    if playlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Playlist with id: {playlist_song.playlist_id} not found",
        )

    if playlist.created_by != current_user.id and playlist.private == True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    song_query = db.query(models.Song).filter(playlist_song.song_id == models.Song.id)
    song = song_query.first()
    if song is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id: {playlist_song.song_id} not found",
        )

    try:
        new_playlist_song = models.PlaylistSongs(
            created_by=current_user.id, **playlist_song.dict()
        )
        db.add(new_playlist_song)
        db.commit()
        db.refresh(new_playlist_song)
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Unkown Error: Unable to add song to playlist",
        )

    return {"messgage": "Song successfully added to playlist"}


@router.delete("/{playlist_id}/{song_id}")
def delete_playlist_song(
    playlist_id: int,
    song_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Delete a song from existing playlist"""
    playlist = (
        db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()
    )

    if current_user.id != playlist.created_by:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action",
        )

    playlist_song_query = db.query(models.PlaylistSongs).filter(
        models.PlaylistSongs.playlist_id == playlist_id,
        models.PlaylistSongs.song_id == song_id,
    )

    if playlist_song_query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Playlist id: {playlist_id} with song id: {song_id} not found",
        )

    playlist_song_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}")
def get_playlist_songs(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Display a list of songs in given playlist id"""
    playlist = db.query(models.Playlist).filter(models.Playlist.id == id).first()

    if playlist.created_by != current_user.id and playlist.private == True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    playlist_songs = (
        db.query(models.Song)
        .join(models.PlaylistSongs)
        .filter(models.PlaylistSongs.playlist_id == id)
    ).all()
    return playlist_songs
