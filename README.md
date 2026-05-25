# Content Summarizer

A Python-based text summarization tool with both CLI and modern web UI interfaces. Extract and summarize long-form text with AI-powered analysis.

## Features

- **Extractive Summarization**: Automatically extracts key sentences from your text
- **Multiple Summary Lengths**: Choose from short (15%), medium (25%), or detailed (45%)
- **Output Styles**: Get summaries in paragraph or bullet point format
- **Sentiment Analysis**: Detects positive, negative, or neutral tone
- **Keyword Extraction**: Identifies important keywords and topics
- **Reading Time Estimation**: Shows original vs summary reading time
- **Web UI**: Modern, responsive web interface with drag-and-drop file upload
- **API Access**: RESTful API for programmatic access

## Structure

```
content_summarizer/
├── data/                    # Store input content or source documents
├── output/                  # Save generated summaries or results
├── content_summarizer/
│   ├── __init__.py
│   └── summarizer.py        # Core summarization logic
├── main.py                  # CLI entry point
├── server.py                # Web server with UI
└── requirements.txt         # Python dependencies
```

## Setup

1. **Create a virtual environment:**
   ```powershell
   python -m venv .venv
   ```

2. **Activate it:**
   ```powershell
   .\.venv\Scripts\Activate.ps1    # PowerShell
   # or
   .venv\Scripts\activate.bat      # CMD
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

## Usage

### Web UI (Recommended)

Start the web server:

```powershell
python server.py
```

Then open your browser and navigate to: **http://127.0.0.1:8000/**

The web interface provides:
- 📝 **Text Input**: Paste or type content directly
- 📁 **File Upload**: Drag & drop or browse to upload .txt files
- ⚙️ **Options**: Select summary length and output style
- ✨ **Generate**: Click to create your summary
- 📋 **Copy/Download**: Export results as TXT or JSON

### CLI

Run the main script with a file or direct text input:

```powershell
# Using a file
python main.py --file data\input.txt --length medium --style "paragraph"

# Using direct text
python main.py --text "Your text goes here." --length short --style "bullet points"
```

**Options:**
- `--file`: Path to a text file with content to summarize
- `--text`: Use a short text string directly for summarization
- `--length`: Summary length (`short`, `medium`, `detailed`)
- `--style`: Output style (`paragraph`, `bullet points`)

### API

The server also provides a REST API:

**GET /summarize**
```
http://127.0.0.1:8000/summarize?text=Your%20text%20here&length=medium&style=paragraph
```

**POST /summarize** (JSON body)
```json
{
  "text": "Your text here",
  "length": "medium",
  "style": "paragraph"
}
```

**Response:**
```json
{
  "title": "First sentence of the text",
  "main_topic": "Main topic extracted",
  "summary": "Generated summary text...",
  "key_points": ["point1", "point2", "point3", "point4"],
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "sentiment": "Positive|Negative|Neutral",
  "reading_time": {
    "original": "5 minutes",
    "summary": "1 minutes"
  }
}
```

## How It Works

The summarizer uses an extractive approach:

1. **Text Normalization**: Clean and normalize the input text
2. **Sentence Splitting**: Break text into individual sentences
3. **Word Frequency Analysis**: Count word occurrences (excluding stop words)
4. **Sentence Scoring**: Rank sentences by importance based on word frequency
5. **Selection**: Choose top sentences based on desired length ratio
6. **Ordering**: Maintain original sentence order for coherence

### Sentiment Detection

The tool analyzes sentiment by comparing positive and negative word occurrences:
- **Positive words**: improve, success, benefit, growth, support, better, etc.
- **Negative words**: decline, risk, problem, fail, loss, weak, issue, etc.

## Examples

### Input Text
```
Machine learning is a subset of artificial intelligence that enables systems to learn
and improve from experience without being explicitly programmed. It focuses on developing
computer programs that can access data and use it to learn for themselves. The primary
aim is to allow computers to learn automatically without human intervention or assistance.
Machine learning algorithms build a mathematical model based on sample data, known as
training data, in order to make predictions or decisions without being explicitly
programmed to do so.
```

### Summary (Medium, Paragraph)
```
Machine learning is a subset of artificial intelligence that enables systems to learn
and improve from experience without being explicitly programmed. Machine learning
algorithms build a mathematical model based on sample data, known as training data,
in order to make predictions or decisions without being explicitly programmed to do so.
```

## Notes

- This project includes a simple extractive summarizer
- Best results with well-structured text (articles, essays, reports)
- Works best with English text
- For production use, consider integrating with more advanced NLP models

## License

MIT License