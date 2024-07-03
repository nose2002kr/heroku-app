from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response

from app.service.github_api import GithubAPI
from app.service.svg_maker import SVGMaker

github_rank_router = APIRouter(prefix='/api/github_rank')
OK_RESULT = {"message": "OK"}
OK_RESULT_RESPONSE_EXAMPLE = {200:{"content":
                               {"application/json":{"example":OK_RESULT}}
                             }}

@github_rank_router.get("/top3", response_model=None)
async def get_top3():
    langs = await GithubAPI().get_used_language_count()
    return dict(list(langs.items())[:3])

@github_rank_router.get("/top/svg", response_model=None)
async def get_svg_of_top_lang():
    langs = await GithubAPI().get_used_language_count()
    first_key = next(iter(langs.keys()))
    svg = await SVGMaker().make_clock_wipe_transition(first_key)
    return Response(content=svg, media_type="application/svg+xml")

@github_rank_router.get("/{lang}/svg", response_model=None)
async def get_svg_of_specific_lang(lang: str):
    svg = await SVGMaker().make_clock_wipe_transition(lang)
    return Response(content=svg, media_type="application/svg+xml")
