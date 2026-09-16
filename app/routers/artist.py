from fastapi import APIRouter

from app.models.artist import Artist

router = APIRouter(
    prefix='/api/artists'
)

@router.get('/', response_model=list[Artist])
async def list_artists():
    artist_list = [
        Artist(id=1 ,name='Rush'),
        Artist(id=2, name='Megadeth')
    ]

    return artist_list