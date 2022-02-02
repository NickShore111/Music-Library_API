from charset_normalizer import models
from fastapi import FastAPI
from . import models
from .database import engine
from .routers import like, playlist, user, artist, song, auth, playlist_songs
from .config import settings

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(playlist.router)
app.include_router(user.router)
app.include_router(artist.router)
app.include_router(song.router)
app.include_router(auth.router)
app.include_router(playlist_songs.router)
app.include_router(like.router)


@app.get("/")
def root():
    return {"message": "Hello World"}
