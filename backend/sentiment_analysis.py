# from fastapi import FastAPI
# from pydantic import BaseModel
# from typing import List
# import re
# import uvicorn
# from fastapi.middleware.cors import CORSMiddleware
# from textblob import TextBlob
# from collections import Counter
# import nltk

# nltk.download('punkt')
# nltk.download('punkt_tab')
# nltk.download('averaged_perceptron_tagger')

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Or restrict to specific origins for security
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# # ---- Models ----
# class TextBlock(BaseModel):
#     text: str
#     tag: str

# class PagePayload(BaseModel):
#     url: str
#     blocks: List[TextBlock]

# class TextBlocks(BaseModel):
#     blocks: List[str]  # List of text blocks as strings 


# @app.post("/analyze_summary")
# def analyze_summary(data: TextBlocks):
#     print(f"Received {len(data.blocks)} text blocks for analysis.")
#     text = " ".join([block.strip() for block in data.blocks if len(block.strip()) > 10])
#     blob = TextBlob(text)
#     sentences = blob.sentences

#     sentiment_details = []
#     emotions = []
#     polarity_scores = []

#     for sentence in sentences:
#         pol = sentence.sentiment.polarity
#         subj = sentence.sentiment.subjectivity
#         polarity_scores.append(pol)

#         # Categorize emotion tone
#         if pol > 0.4:
#             emotions.append("hopeful")
#         elif pol > 0.1:
#             emotions.append("positive")
#         elif pol < -0.4:
#             emotions.append("angry")
#         elif pol < -0.1:
#             emotions.append("concerned")
#         else:
#             emotions.append("neutral")

#         sentiment_details.append({
#             "sentence": str(sentence),
#             "polarity": pol,
#             "subjectivity": subj
#         })

#     # Determine overall tone
#     avg_pol = sum(polarity_scores) / len(polarity_scores) if polarity_scores else 0
#     tone = (
#         "Positive" if avg_pol > 0.2 else
#         "Negative" if avg_pol < -0.2 else
#         "Neutral"
#     )

#     emotion_summary = Counter(emotions).most_common()

#     # Natural-language generation
#     readable_summary = f"This article has an overall **{tone.lower()} tone**. "
#     if emotion_summary:
#         top_emotions = [e for e, _ in emotion_summary[:3]]
#         readable_summary += f"The dominant emotions are: {', '.join(top_emotions)}. "
#     readable_summary += "Here is a quick sentiment breakdown:\n"

#     for detail in sentiment_details[:5]:  # limit to first 5 key lines
#         sentiment = (
#             "positive" if detail["polarity"] > 0.2 else
#             "negative" if detail["polarity"] < -0.2 else
#             "neutral"
#         )
#         readable_summary += f"\n- \"{detail['sentence']}\" → {sentiment}"

#     print(f"Processed {len(sentences)} sentences from the text.")
#     return {
#         "overall_tone": tone,
#         "top_emotions": emotion_summary,
#         "summary_text": readable_summary
#     }

# # ---- Run Server ----
# if __name__ == "__main__":
#     uvicorn.run("sentement_analysis:app", port=8000, reload=True)

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from collections import Counter
from fastapi.middleware.cors import CORSMiddleware
import re
import nltk
import logging
import uvicorn
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# Emotion model setup
emotion_model = AutoModelForSequenceClassification.from_pretrained("j-hartmann/emotion-english-distilroberta-base")
emotion_tokenizer = AutoTokenizer.from_pretrained("j-hartmann/emotion-english-distilroberta-base")
emotion_pipeline = pipeline("text-classification", model=emotion_model, tokenizer=emotion_tokenizer, top_k=1)

nltk.download('punkt')
from nltk import sent_tokenize

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize model
sentiment_pipeline = pipeline("sentiment-analysis")

# ---- FastAPI App Setup ----
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Data Models ----
class TextBlocks(BaseModel):
    blocks: List[str]

# ---- Utilities ----
def clean_text_block(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'http\S+', '', text)
    return text.strip()

# ---- Sentiment Analysis Endpoint ----
@app.post("/analyze_summary")
def analyze_summary(data: TextBlocks):
    logger.info(f"Received {len(data.blocks)} blocks.")
    cleaned = [clean_text_block(t) for t in data.blocks if len(t.strip()) > 10]
    text = " ".join(cleaned)
    if not text:
        return {"overall_tone": "Neutral", "top_emotions": [], "summary_text": "No valid text to analyze."}

    sentences = sent_tokenize(text)
    if not sentences:
        return {"overall_tone": "Neutral", "top_emotions": [], "summary_text": "No sentences found."}

    results = sentiment_pipeline(sentences)
    sentiment_details = []
    emotions = []
    weighted_scores = []

    for i, (sent, result) in enumerate(zip(sentences, results)):
        label = result['label']
        score = result['score']
        pos_weight = 1.0 + (i / len(sentences))  # weight later sentences higher
        sentiment_val = score if label == "POSITIVE" else -score
        weighted_scores.append(sentiment_val * pos_weight)

        sentiment = "positive" if label == "POSITIVE" else "negative"
        emotion_label = emotion_pipeline(sent)[0][0]['label'].lower()
        emotions.append(emotion_label)


        sentiment_details.append({
            "sentence": sent,
            "label": label,
            "confidence": round(score, 3)
        })

    # Compute overall score
    overall_score = sum(weighted_scores) / sum([1.0 + (i / len(sentences)) for i in range(len(sentences))])

    # Also analyze last 2 sentences separately for ending detection
    ending_sentences = sentences[-2:]
    ending_results = sentiment_pipeline(ending_sentences)
    ending_score = sum(
        (r['score'] if r['label'] == 'POSITIVE' else -r['score']) for r in ending_results
    ) / len(ending_results)

    # Blend overall tone with ending weight
    final_score = 0.7 * overall_score + 0.3 * ending_score

    overall_tone = (
        "Positive" if final_score > 0.2 else
        "Negative" if final_score < -0.2 else
        "Neutral"
    )

    emotion_summary = Counter(emotions).most_common()

    # Build readable summary
    readable_summary = f"This article has an overall **{overall_tone.lower()} tone**. "
    if emotion_summary:
        top_emotions = [e for e, _ in emotion_summary[:3]]
        readable_summary += f"Dominant emotions: {', '.join(top_emotions)}. "
    if overall_score < 0 and ending_score > 0.4:
        readable_summary += "\n\n⚠️ Although the article discusses negative events, it concludes on a hopeful note."

    readable_summary += "\n\nExample sentiments:\n"
    for d in sentiment_details[:5]:
        readable_summary += f"- \"{d['sentence']}\" → {d['label'].lower()} ({d['confidence']})\n"

    return {
        "overall_tone": overall_tone,
        "top_emotions": emotion_summary
    }    # "summary_text": readable_summary

# ---- Run Server ----
if __name__ == "__main__":
    uvicorn.run("sentiment_analysis:app", port=8000, reload=True)
