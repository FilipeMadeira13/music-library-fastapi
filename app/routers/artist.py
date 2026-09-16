from fastapi import APIRouter

from app.models.artist import Artist

router = APIRouter(
    prefix='/api/artists'
)

@router.get('/', response_model=list[Artist])
async def list_artists():
    artist_list = [
        Artist(id=1 ,name='Rush', formed_in=1969),
        Artist(id=2, name='Megadeth', formed_in=1984)
    ]

    return artist_list