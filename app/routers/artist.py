from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix="/artists", tags=["Artists"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.ArtistCreateOut
)
def create_artist(
    artist: schemas.ArtistCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Add an artist to the database"""

    duplicate_artist = (
        db.query(models.Artist).filter(models.Artist.name == artist.name).first()
    )
    if duplicate_artist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Artist name: {artist.name} already exists",
        )

    new_artist = models.Artist(created_by=current_user.id, **artist.dict())
    db.add(new_artist)
    db.commit()
    db.refresh(new_artist)
    return new_artist


@router.put(
    "/{id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schemas.ArtistCreateOut,
)
def update_artist(
    id: int,
    updated_artist: schemas.ArtistCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Updates artist info if present and created_by == user.id"""

    artist_query = db.query(models.Artist).filter(models.Artist.id == id)
    artist = artist_query.first()

    if artist == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id: {id} not found",
        )

    if artist.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    artist_query.update(updated_artist.dict(), synchronize_session=False)
    db.commit()
    return artist_query.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artist(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Deletes one artist from database if created_by == user.id"""

    artist_query = db.query(models.Artist).filter(models.Artist.id == id)
    artist = artist_query.first()

    if artist == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id: {id} was not found",
        )

    if artist.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    artist_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/", response_model=List[schemas.ArtistsOut])
# @router.get("/")
def get_artists(
    db: Session = Depends(get_db),
    name: Optional[str] = "",
    limit: int = 10,
    skip: int = 0,
):
    """Returns a list of all artists in database if no query parameter entered"""

    artists = (
        db.query(models.Artist)
        .filter(models.Artist.name.contains(name))
        .limit(limit)
        .offset(skip)
        .all()
    )

    return artists


# @router.get("/{id}")
@router.get("/{id}", response_model=schemas.ArtistOut)
def get_artist(id: int, db: Session = Depends(get_db)):
    """Returns one artist by id with a list of their related songs"""

    artist = db.query(models.Artist).filter(models.Artist.id == id).first()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id: {id} was not found",
        )
    return artist
