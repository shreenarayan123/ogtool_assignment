import json
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from technical_knowledge import TechnicalKnowledgeScraper
from typing import List
import shutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "upload_pdf"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/scrape")
def scrape(
    team_id: str = Form(...),
    urls: str = Form(...),
    pdfs: List[UploadFile] = File(default=[]),
):
    urls_list = json.loads(urls)
    pdf_paths = []

    for pdf in pdfs:
        file_path = os.path.join(UPLOAD_DIR, pdf.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(pdf.file, buffer)
        pdf_paths.append(file_path)

    sources = urls_list + pdf_paths

    scraper = TechnicalKnowledgeScraper("aline123")
    knowledge_base = scraper.scrape_all_sources(sources)
    return knowledge_base.to_dict()
