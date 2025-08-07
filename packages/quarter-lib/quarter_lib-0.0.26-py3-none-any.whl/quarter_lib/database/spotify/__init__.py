import requests

BASE_URL = "http://localhost:8200"


async def add_listened_songs(listened_songs):
    return requests.post(BASE_URL + "/spotify/add", json=listened_songs).json()
