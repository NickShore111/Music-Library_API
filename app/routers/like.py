from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import schemas, database, models, oauth2


router = APIRouter(prefix="/like", tags=["Like"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def like_song(
    like: schemas.Like,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Create like = 1 or remove like = 0 from song_id"""

    song = db.query(models.Song).filter(models.Song.id == like.song_id).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song {like.song_id} does not exist",
        )
    like_query = db.query(models.Like).filter(
        models.Like.song_id == like.song_id,
        models.Like.created_by == current_user.id,
    )
    found_like = like_query.first()
    if like.dir == 1:
        if found_like:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {current_user.id} has already liked song {like.song_id}",
            )
        new_like = models.Like(song_id=like.song_id, created_by=current_user.id)
        db.add(new_like)
        db.commit()
        return {
            "message": f"User {current_user.id} successfully liked song {like.song_id}"
        }
    else:
        if not found_like:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Like does not exist"
            )

        like_query.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


# @router.post("/", status_code=status.HTTP_201_CREATED)
# def like_playlist(
#     like: schemas.Like,
#     db: Session = Depends(database.get_db),
#     current_user: int = Depends(oauth2.get_current_user),
# ):
#     """Create like = 1 or remove like = 0 from song_id"""

#     song = db.query(models.Playlist).filter(models.Song.id == like.song_id).first()
#     if not song:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Song {like.song_id} does not exist",
#         )

#     like_query = db.query(models.Like).filter(
#         models.Like.song_id == like.song_id,
#         models.Like.created_by == current_user.id,
#     )
#     found_like = like_query.first()
#     if like.dir == 1:
#         if found_like:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail=f"User {current_user.id} has already liked song {like.song_id}",
#             )
#         new_like = models.Like(song_id=like.song_id, created_by=current_user.id)
#         db.add(new_like)
#         db.commit()
#         return {
#             "message": f"User {current_user.id} successfully liked song {like.song_id}"
#         }
#     else:
#         if not found_like:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail="Like does not exist"
#             )

#         like_query.delete(synchronize_session=False)
#         db.commit()
#         return Response(status_code=status.HTTP_204_NO_CONTENT)
