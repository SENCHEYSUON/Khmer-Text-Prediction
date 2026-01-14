import torch
import torch.nn as nn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
from transformers import AutoTokenizer

# ---------------------------
# CONFIG (edit paths)
# ---------------------------
TOKENIZER_DIR = r"D:\AMS_Year5\Semester_1\TP_IWR\Khmer-Text-Prediction\Trained_Model\BiLSTM\km-tokenizer-khmer"
MODEL_PATH    = r"D:\AMS_Year5\Semester_1\TP_IWR\Khmer-Text-Prediction\Trained_Model\BiLSTM\bilstm_khmer.pth"

EMBED_SIZE  = 256
HIDDEN_SIZE = 512
NUM_LAYERS  = 2
TOP_K       = 5

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="views")

# ---------------------------
# Load tokenizer
# ---------------------------
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_DIR, use_fast=False)
if tokenizer.pad_token_id is None:
    tokenizer.pad_token = tokenizer.eos_token if tokenizer.eos_token else tokenizer.unk_token

PAD_ID = tokenizer.pad_token_id
VOCAB_SIZE = tokenizer.vocab_size

# ---------------------------
# BiLSTM model (must match training)
# ---------------------------
class BiLSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.embedding = nn.Embedding(VOCAB_SIZE, EMBED_SIZE, padding_idx=PAD_ID)
        self.lstm = nn.LSTM(
            EMBED_SIZE, HIDDEN_SIZE, NUM_LAYERS,
            batch_first=True, bidirectional=True,
            dropout=0.2 if NUM_LAYERS > 1 else 0.0
        )
        self.fc = nn.Linear(HIDDEN_SIZE * 2, VOCAB_SIZE)

    def forward(self, x):
        x = self.embedding(x)
        out, _ = self.lstm(x)
        logits = self.fc(out[:, -1, :])
        return logits

device = "cuda" if torch.cuda.is_available() else "cpu"
model = BiLSTM().to(device)

state = torch.load(MODEL_PATH, map_location=device)
if isinstance(state, dict) and "model_state_dict" in state:
    state = state["model_state_dict"]
model.load_state_dict(state, strict=True)
model.eval()

@torch.no_grad()
def suggest(text: str, top_k: int = TOP_K):
    text = text or ""
    if not text.strip():
        return []

    ids = tokenizer.encode(text, add_special_tokens=False)
    if len(ids) == 0:
        return []

    x = torch.tensor([ids], dtype=torch.long, device=device)
    logits = model(x)
    probs = torch.softmax(logits, dim=-1)
    top_ids = torch.topk(probs, k=top_k, dim=-1).indices[0].tolist()

    suggestions = []
    seen = set()
    for tid in top_ids:
        tok = tokenizer.decode([tid]).strip()
        if tok and tok not in seen:
            seen.add(tok)
            suggestions.append(tok)

    return suggestions[:top_k]

# ---------------------------
# API schema
# ---------------------------
class SuggestRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/suggest")
def suggest_api(payload: SuggestRequest):
    return {"suggestions": suggest(payload.text)}
