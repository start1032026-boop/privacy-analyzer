from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from policy_fetcher import fetch_policy
from text_chunker import split_text
from llm_analyzer import analyze_policy
from risk_utils import combine_results

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestData(BaseModel):
    url: str

@app.post("/analyze")
def analyze(data: RequestData):
    policy_text = fetch_policy(data.url)
    chunks = split_text(policy_text)
    results = []
    for chunk in chunks[:3]:
        result = analyze_policy(chunk)
        results.append(result)
    combined = combine_results(results)
    return combined