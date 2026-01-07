from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import tensorflow as tf
import pickle
import numpy as np
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

app = FastAPI()
templates = Jinja2Templates(directory="templates")

model = tf.keras.models.load_model("sentiment_lstm.h5")
with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

def cleaningText(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text.lower()

def tokenizingText(text):
    return word_tokenize(text)

def filteringText(tokens):
    stop_words = set(stopwords.words('indonesian')).union(
        set(stopwords.words('english'))
    )
    return [t for t in tokens if t not in stop_words and len(t) > 2]

def toSentence(tokens):
    return " ".join(tokens)

def predict_sentiment(text):
    clean = cleaningText(text)
    tokens = tokenizingText(clean)
    filtered = filteringText(tokens)
    final = toSentence(filtered)

    seq = tokenizer.texts_to_sequences([final])
    pad = tf.keras.preprocessing.sequence.pad_sequences(seq, maxlen=100)

    pred = model.predict(pad, verbose=0)
    label = np.argmax(pred)

    return ["negatif", "netral", "positif"][label]

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request):
    form = await request.form()
    text = form.get("text")
    result = predict_sentiment(text)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "text": text,
            "result": result
        }
    )
