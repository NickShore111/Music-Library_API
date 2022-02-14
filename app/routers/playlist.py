from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import or_
from typing import List, Optional
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix="/playlists", tags=["Playlists"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.PlaylistOut,
)
def create_playlist(
    playlist: schemas.PlaylistCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    duplicate_playlist = (
        db.query(models.Playlist)
        .filter(models.Playlist.name == playlist.name)
        .filter(models.Playlist.created_by == current_user.id)
        .first()
    )
    if duplicate_playlist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Playlist with name: '{playlist.name}' already exists for user: {current_user.id}",
        )
    new_playlist = models.Playlist(created_by=current_user.id, **playlist.dict())
    db.add(new_playlist)
    db.commit()
    db.refresh(new_playlist)
    return new_playlist


@router.put(
    "/{id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schemas.PlaylistOut,
)
def update_playlist(
    id: int,
    updated_playlist: schemas.PlaylistUpdate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    playlist_query = db.query(models.Playlist).filter(models.Playlist.id == id)
    playlist = playlist_query.first()

    if playlist == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Playlist with id: {id} not found",
        )

    if playlist.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    playlist_query.update(updated_playlist.dict(), synchronize_session=False)
    db.commit()
    return playlist_query.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_playlist(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    playlist_query = db.query(models.Playlist).filter(models.Playlist.id == id)
    playlist = playlist_query.first()

    if playlist == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Playlist with id: {id} was not found",
        )

    if playlist.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    playlist_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}", response_model=schemas.PlaylistOut)
def get_playlist(id: int, db: Session = Depends(get_db)):

    playlist = db.query(models.Playlist).filter(models.Playlist.id == id).first()
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Playlist with id: {id} was not found",
        )
    return playlist


@router.get("/", response_model=List[schemas.PlaylistOut])
# @router.get("/")
def get_playlists(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    name: Optional[str] = "",
    tags: Optional[str] = "",
):
    """Get playlist by name and/or tags, else retrieve all public and user created playlists"""

    playlist_query = db.query(models.Playlist).filter(
        models.Playlist.name.contains(name)
    )
    # .filter(models.Playlist.tags.contains(tags))
    or_expression = or_(
        models.Playlist.private == False,
        models.Playlist.created_by == current_user.id,
    )
    or_query = playlist_query.filter(or_expression)
    playlists = or_query.all()

    return playlists
