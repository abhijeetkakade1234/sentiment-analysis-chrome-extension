# Web Sentiment Analyzer

A Chrome extension and backend service that analyzes the visible content of web pages for sentiment and emotion using advanced NLP models.

## Features

- 🌐 Chrome extension to extract and analyze text from any web page
- 📊 Sentiment and emotion detection using state-of-the-art models (TextBlob, Transformers)
- 🧠 Side panel displays real-time analysis results with no manual refresh needed
- 🔄 Automatic updates as you browse new content

## How It Works

1. **Install the extension** in your browser.
2. **Click "Open Analysis Panel"** on any web page.
3. The extension extracts visible text, sends it to the backend, and displays a summary of sentiment and top emotions in the side panel.

## Project Structure

```
.
├── backend/
│   ├── sentiment_analysis.py      # FastAPI backend for analysis
│   └── requirements.txt
├── extension/
│   ├── background.js
│   ├── contentScript.js
│   ├── manifest.json
│   ├── popup.html / popup.js
│   ├── sidePanel.html / sidePanel.js
│   └── style.css
```

## Setup

### 1. Backend

- Install Python dependencies:
  ```bash
  pip install -r backend/requirements.txt
  ```
- Download required NLTK/TextBlob data:
  ```bash
  python -m textblob.download_corpora
  ```
- Run the backend server:
  ```bash
  python backend/sentiment_analysis.py
  ```
  The server will start on `http://localhost:8000`.

### 2. Chrome Extension

- Go to `chrome://extensions/` and enable "Developer mode".
- Click "Load unpacked" and select the `extension/` folder.
- Make sure permissions are granted when prompted.

## Usage

1. Navigate to any article or web page.
2. Click the extension icon and select "Open Analysis Panel".
3. The side panel will open and display sentiment/emotion analysis for the current page.
4. The panel updates automatically as new analysis is available.

## Technologies Used

- **Frontend:** JavaScript, Chrome Extensions API, HTML/CSS
- **Backend:** Python, FastAPI, TextBlob, HuggingFace Transformers

## Troubleshooting

- If you see errors about missing NLTK/TextBlob data, run:
  ```
  python -m textblob.download_corpora
  ```
- Make sure the backend server is running before using the extension.
- Reload the extension after making code changes.

## License

MIT License

---

Made with ❤️ for web content understanding.