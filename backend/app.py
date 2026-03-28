import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI

from backend.routes import audio, records, report

app = FastAPI()


app.include_router(audio.router)
app.include_router(records.router)
app.include_router(report.router)
