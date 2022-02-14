from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(prefix="/genres", tags=["Genres"])


@router.post("/")
def create_genre(genre: schemas.GenreCreate, db: Session = Depends(get_db)):
    """Add new genre to db"""

    duplicate_genre = (
        db.query(models.Genre).filter(models.Genre.genre == genre.genre).first()
    )
    if duplicate_genre:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Genre with name: '{genre.genre}' already exists",
        )
    new_genre = models.Genre(**genre.dict())
    db.add(new_genre)
    db.commit()
    db.refresh(new_genre)
    return new_genre


@router.get("/")
def get_genres(db: Session = Depends(get_db)):
    genres = db.query(models.Genre).all()
    return genres
