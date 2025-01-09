from fastapi import APIRouter

from app.api.v1 import app, wordlist


def register_route_v1():
    api_route_v1 = APIRouter(prefix='/v1')
    app.app_api.register(api_route_v1)
    wordlist.wordlist_api.register(api_route_v1)
    return api_route_v1
