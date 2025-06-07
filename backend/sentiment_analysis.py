from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import re
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from textblob import TextBlob
from collections import Counter
import nltk

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to specific origins for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---- Models ----
class TextBlock(BaseModel):
    text: str
    tag: str

class PagePayload(BaseModel):
    url: str
    blocks: List[TextBlock]

class TextBlocks(BaseModel):
    blocks: List[str]  # List of text blocks as strings 


# ---- Main Route ----
# @app.post("/analyze")
# async def analyze_page(payload: PagePayload):
#     # Extract all raw text blocks (no filtering yet)
#     all_texts = [block.text.strip() for block in payload.blocks if block.text.strip()]

#     full_text = "\n\n".join(all_texts)  

#     print(f"Received {len(all_texts)} blocks from: {payload.url}")
#     print(full_text[:500])  

#     return {
#         "url": payload.url,
#         "num_blocks_received": len(all_texts),
#         "combined_text": full_text
#     }

@app.post("/analyze_summary")
def analyze_summary(data: TextBlocks):
    print(f"Received {len(data.blocks)} text blocks for analysis.")
    text = " ".join([block.strip() for block in data.blocks if len(block.strip()) > 10])
    blob = TextBlob(text)
    sentences = blob.sentences

    sentiment_details = []
    emotions = []
    polarity_scores = []

    for sentence in sentences:
        pol = sentence.sentiment.polarity
        subj = sentence.sentiment.subjectivity
        polarity_scores.append(pol)

        # Categorize emotion tone
        if pol > 0.4:
            emotions.append("hopeful")
        elif pol > 0.1:
            emotions.append("positive")
        elif pol < -0.4:
            emotions.append("angry")
        elif pol < -0.1:
            emotions.append("concerned")
        else:
            emotions.append("neutral")

        sentiment_details.append({
            "sentence": str(sentence),
            "polarity": pol,
            "subjectivity": subj
        })

    # Determine overall tone
    avg_pol = sum(polarity_scores) / len(polarity_scores) if polarity_scores else 0
    tone = (
        "Positive" if avg_pol > 0.2 else
        "Negative" if avg_pol < -0.2 else
        "Neutral"
    )

    emotion_summary = Counter(emotions).most_common()

    # Natural-language generation
    readable_summary = f"This article has an overall **{tone.lower()} tone**. "
    if emotion_summary:
        top_emotions = [e for e, _ in emotion_summary[:3]]
        readable_summary += f"The dominant emotions are: {', '.join(top_emotions)}. "
    readable_summary += "Here is a quick sentiment breakdown:\n"

    for detail in sentiment_details[:5]:  # limit to first 5 key lines
        sentiment = (
            "positive" if detail["polarity"] > 0.2 else
            "negative" if detail["polarity"] < -0.2 else
            "neutral"
        )
        readable_summary += f"\n- \"{detail['sentence']}\" → {sentiment}"

    print(f"Processed {len(sentences)} sentences from the text.")
    return {
        "overall_tone": tone,
        "top_emotions": emotion_summary,
        "summary_text": readable_summary
    }

# ---- Run Server ----
if __name__ == "__main__":
    uvicorn.run("sentement_analysis:app", port=8000, reload=True)
