"""LocalPass 웹 서버 (FastAPI) — `python app.py` 로 실행 후 http://127.0.0.1:8000"""
import json
import logging
import threading

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import catalog
from ai_pipeline import ai_detect, llm, local_detector
from config import APP_NAME, LANGS, LLM_MODEL, REGIONS, ROOT
from data_sources import naver_blog, tour_api
from personalize import INTERESTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title=APP_NAME)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


@app.on_event("startup")
def _warm_detector():
    if ai_detect.backend() == "local":
        threading.Thread(target=local_detector.warmup, daemon=True).start()

Lang = Query("en", pattern="^(en|ja|zh|ko)$")


@app.get("/")
def index():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/status")
def status():
    return {
        "app": APP_NAME,
        "tour_api": "live" if tour_api.enabled() else "sample",
        "naver": "live" if naver_blog.enabled() else "sample",
        "llm": {"online": llm.is_online(), "model": LLM_MODEL},
        "ai_detector": ai_detect.backend(),
        "langs": list(LANGS),
        "interests": INTERESTS,
    }


@app.get("/api/regions")
def regions():
    return [{"key": k, "name": r["name"], "short": r["short"], "city": r["city"]} for k, r in REGIONS.items()]


@app.get("/api/places")
def places(region: str, lang: str = Lang, tags: str = ""):
    if region not in REGIONS:
        raise HTTPException(404, "unknown region")
    return catalog.list_places(region, lang, [t for t in tags.split(",") if t])


@app.get("/api/search")
def search(q: str = Query(..., min_length=1, max_length=40), lang: str = Lang):
    return catalog.search_places(q, lang)


@app.get("/api/place/{place_id}")
def place(place_id: str, type_id: str = "", lang: str = Lang, foreign_id: str = "", foreign_type: str = ""):
    try:
        return catalog.place_detail(place_id, type_id, lang, foreign_id, foreign_type)
    except tour_api.TourApiError as e:
        raise HTTPException(502, f"TourAPI: {e}")


@app.get("/api/reviews")
def reviews(place_id: str, title_ko: str, title: str = "", region: str = "", lang: str = Lang):
    def stream():
        for event in catalog.review_stream(place_id, title_ko, region, lang, title):
            yield json.dumps(event, ensure_ascii=False) + "\n"
    return StreamingResponse(stream(), media_type="application/x-ndjson")


class AnalyzeIn(BaseModel):
    title: str = Field("", max_length=200)
    text: str = Field(..., min_length=10, max_length=3000)
    lang: str = Field("en", pattern="^(en|ja|zh|ko)$")


@app.post("/api/analyze")
def analyze(body: AnalyzeIn):
    return catalog.analyze_text(body.title, body.text, body.lang)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
