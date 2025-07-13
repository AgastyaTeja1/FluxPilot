# serving/app.py

import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from fastapi import Depends
from serving.auth import verify_api_key
from serving.metrics import MetricsMiddleware, metrics_endpoint
from serving.tracing import setup_tracing


class GenerationRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 50
    temperature: float = 1.0

app = FastAPI(
    title="FluxPilot Granite Inference API",
    description="FastAPI service for generating text using the fine-tuned Granite LLM",
    version="1.0.0"
)

setup_tracing(app)

# Attach Prometheus metrics middleware
app.add_middleware(MetricsMiddleware)

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return metrics_endpoint()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("serve")

MODEL_DIR = os.getenv("SERVE_MODEL_DIR", "./model")

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForCausalLM.from_pretrained(MODEL_DIR)
    model.eval()
    if torch.cuda.is_available():
        model.to("cuda")
    logger.info(f"Loaded model from {MODEL_DIR}")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    raise

@app.get("/")
async def root():
    return {"status": "FluxPilot Granite API is up"}

@app.post("/generate", dependencies=[Depends(verify_api_key)])
async def generate(request: GenerationRequest):
    try:
        inputs = tokenizer(
            request.prompt,
            return_tensors="pt"
        )
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        outputs = model.generate(
            **inputs,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature
        )
        text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {"generated_text": text}
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
