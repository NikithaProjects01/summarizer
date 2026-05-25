from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json
import io
import cgi

from content_summarizer.summarizer import build_summary_response

def decode_bytes(data: bytes) -> str:
    # Attempt multiple encodings in sequence
    for encoding in ('utf-8-sig', 'utf-16', 'utf-16le', 'utf-16be', 'latin-1'):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    # Ultimate fallback with character replacement
    return data.decode('utf-8', errors='replace')

HOST = "127.0.0.1"
PORT = 8000

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Summarizer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }

        .card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }

        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1rem;
            font-family: inherit;
            resize: vertical;
            min-height: 150px;
            transition: border-color 0.3s;
        }

        textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .char-count {
            text-align: right;
            color: #999;
            font-size: 0.85rem;
            margin-top: 5px;
        }

        .options-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        @media (max-width: 600px) {
            .options-row {
                grid-template-columns: 1fr;
            }
        }

        select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1rem;
            background: white;
            cursor: pointer;
            transition: border-color 0.3s;
        }

        select:focus {
            outline: none;
            border-color: #667eea;
        }

        .file-upload-area {
            border: 2px dashed #e0e0e0;
            border-radius: 8px;
            padding: 30px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 20px;
        }

        .file-upload-area:hover {
            border-color: #667eea;
            background: #f8f9ff;
        }

        .file-upload-area.dragover {
            border-color: #667eea;
            background: #eef0ff;
        }

        .file-upload-area svg {
            margin-bottom: 10px;
        }

        .file-upload-area p {
            color: #666;
        }

        .file-upload-area .browse-link {
            color: #667eea;
            font-weight: 600;
        }

        #fileInput {
            display: none;
        }

        .file-name {
            background: #f0f0f0;
            padding: 10px 15px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 10px;
        }

        .file-name .remove-file {
            color: #e74c3c;
            cursor: pointer;
            font-weight: bold;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }

        /* Results Styles */
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 20px;
        }

        .result-title {
            font-size: 1.3rem;
            color: #333;
            flex: 1;
        }

        .result-actions {
            display: flex;
            gap: 10px;
        }

        .btn-small {
            padding: 8px 16px;
            font-size: 0.9rem;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
            background: white;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-small:hover {
            background: #f5f5f5;
            border-color: #667eea;
        }

        .summary-text {
            background: #f8f9ff;
            padding: 20px;
            border-radius: 8px;
            line-height: 1.8;
            color: #444;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }

        .summary-bullet {
            padding-left: 20px;
            margin-bottom: 10px;
            line-height: 1.6;
            color: #444;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: #f8f9ff;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }

        .stat-card .stat-label {
            font-size: 0.85rem;
            color: #888;
            margin-bottom: 5px;
        }

        .stat-card .stat-value {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
        }

        .sentiment-positive { color: #27ae60 !important; }
        .sentiment-negative { color: #e74c3c !important; }
        .sentiment-neutral { color: #f39c12 !important; }

        .keywords-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .keyword-tag {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.9rem;
        }

        .key-points-list {
            list-style: none;
            padding: 0;
        }

        .key-points-list li {
            padding: 10px 0 10px 25px;
            position: relative;
            border-bottom: 1px solid #eee;
        }

        .key-points-list li:last-child {
            border-bottom: none;
        }

        .key-points-list li::before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #667eea;
            font-weight: bold;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }

        .loading.active {
            display: block;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #e0e0e0;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .loading p {
            color: #666;
        }

        .hidden {
            display: none !important;
        }

        .back-link {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            color: #667eea;
            text-decoration: none;
            margin-bottom: 15px;
            font-weight: 500;
        }

        .back-link:hover {
            text-decoration: underline;
        }

        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #333;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            opacity: 0;
            transition: opacity 0.3s;
            z-index: 1000;
        }

        .toast.show {
            opacity: 1;
        }

        .reading-time-comparison {
            display: flex;
            align-items: center;
            gap: 20px;
            justify-content: center;
        }

        .reading-time-item {
            text-align: center;
        }

        .reading-time-item .time-value {
            font-size: 1.5rem;
            font-weight: 600;
        }

        .reading-time-arrow {
            font-size: 1.5rem;
            color: #27ae60;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📝 Content Summarizer</h1>
            <p>Transform long text into concise summaries with AI-powered analysis</p>
        </div>

        <!-- Input Form Card -->
        <div class="card" id="inputCard">
            <h2>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                Enter Your Content
            </h2>

            <!-- File Upload -->
            <div class="form-group">
                <label>Or upload a text file</label>
                <div class="file-upload-area" id="dropZone">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#667eea" stroke-width="1.5">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="17 8 12 3 7 8"/>
                        <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                    <p>Drag & drop a text file here or <span class="browse-link">browse</span></p>
                </div>
                <input type="file" id="fileInput" accept=".txt,.md,.csv,.log,.json,.xml,.html">
                <div id="fileName" class="file-name hidden">
                    <span id="fileNameText"></span>
                    <span class="remove-file" onclick="removeFile()">✕ Remove</span>
                </div>
            </div>

            <div style="text-align: center; color: #999; margin: 15px 0;">— OR —</div>

            <!-- Text Input -->
            <div class="form-group">
                <label for="textInput">Paste your text below</label>
                <textarea id="textInput" placeholder="Enter or paste your content here to summarize..."></textarea>
                <div class="char-count"><span id="charCount">0</span> characters</div>
            </div>

            <!-- Options -->
            <div class="options-row">
                <div class="form-group">
                    <label for="lengthSelect">Summary Length</label>
                    <select id="lengthSelect">
                        <option value="short">Short (15%)</option>
                        <option value="medium" selected>Medium (25%)</option>
                        <option value="detailed">Detailed (45%)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="styleSelect">Output Style</label>
                    <select id="styleSelect">
                        <option value="paragraph" selected>Paragraph</option>
                        <option value="bullet points">Bullet Points</option>
                    </select>
                </div>
            </div>

            <button class="btn" onclick="summarize()" id="summarizeBtn">
                ✨ Generate Summary
            </button>
        </div>

        <!-- Loading -->
        <div class="card loading" id="loadingCard">
            <div class="spinner"></div>
            <p>Analyzing your content...</p>
        </div>

        <!-- Results Card -->
        <div class="card hidden" id="resultCard">
            <a href="#" class="back-link" onclick="showInput(); return false;">← Create New Summary</a>

            <div class="result-header">
                <h2 class="result-title" id="resultTitle"></h2>
                <div class="result-actions">
                    <button class="btn-small" onclick="copySummary()">📋 Copy</button>
                    <button class="btn-small" onclick="downloadSummary('txt')">💾 Download TXT</button>
                    <button class="btn-small" onclick="downloadSummary('json')">📄 Download JSON</button>
                </div>
            </div>

            <!-- Stats -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Main Topic</div>
                    <div class="stat-value" id="mainTopic"></div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Sentiment</div>
                    <div class="stat-value" id="sentiment"></div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Reading Time</div>
                    <div class="stat-value" id="readingTime"></div>
                </div>
            </div>

            <!-- Summary -->
            <h2 style="margin-bottom: 15px; color: #333;">Summary</h2>
            <div id="summaryContent"></div>

            <!-- Key Points -->
            <h2 style="margin: 25px 0 15px; color: #333;">Key Points</h2>
            <ul class="key-points-list" id="keyPoints"></ul>

            <!-- Keywords -->
            <h2 style="margin: 25px 0 15px; color: #333;">Keywords</h2>
            <div class="keywords-container" id="keywords"></div>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        let currentResult = null;
        let uploadedFileContent = null;

        // Character count
        document.getElementById('textInput').addEventListener('input', function() {
            document.getElementById('charCount').textContent = this.value.length;
        });

        // File upload handling
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');

        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file) handleFile(file);
        });

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) handleFile(file);
        });

        function handleFile(file) {
            const maxSizeBytes = 5 * 1024 * 1024; // 5MB limit
            if (file.size > maxSizeBytes) {
                showToast('File is too large. Please upload a file smaller than 5MB.');
                return;
            }

            const allowedExtensions = [
                '.txt', '.md', '.csv', '.log', '.json', '.xml', '.html', 
                '.py', '.js', '.css', '.yaml', '.yml', '.ini', '.conf', 
                '.sh', '.bat', '.ps1', '.sql', '.java', '.cpp', '.c', '.h',
                '.toml', '.rst', '.tex'
            ];
            const fileParts = file.name.split('.');
            const fileExtension = fileParts.length > 1 ? '.' + fileParts.pop().toLowerCase() : '';
            if (fileExtension && !allowedExtensions.includes(fileExtension)) {
                showToast('Please upload a supported text or code file.');
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                uploadedFileContent = e.target.result;
                document.getElementById('textInput').value = uploadedFileContent;
                document.getElementById('charCount').textContent = uploadedFileContent.length;
                document.getElementById('fileNameText').textContent = file.name;
                document.getElementById('fileName').classList.remove('hidden');
                dropZone.style.display = 'none';
            };
            reader.onerror = function() {
                showToast('Error reading file. Please make sure it is a valid text file.');
            };
            reader.readAsText(file);
        }

        function removeFile() {
            uploadedFileContent = null;
            document.getElementById('textInput').value = '';
            document.getElementById('charCount').textContent = '0';
            document.getElementById('fileName').classList.add('hidden');
            dropZone.style.display = 'block';
            fileInput.value = '';
        }

        async function summarize() {
            const text = document.getElementById('textInput').value.trim();
            if (!text) {
                showToast('Please enter some text or upload a file');
                return;
            }

            console.log('Starting summarization with:', { text: text.substring(0, 50) + '...', length: document.getElementById('lengthSelect').value, style: document.getElementById('styleSelect').value });

            const length = document.getElementById('lengthSelect').value;
            const style = document.getElementById('styleSelect').value;

            // Show loading
            document.getElementById('inputCard').classList.add('hidden');
            document.getElementById('loadingCard').classList.add('active');
            document.getElementById('resultCard').classList.add('hidden');

            try {
                console.log('Sending POST request to /summarize');
                const response = await fetch('/summarize', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        text: text,
                        length: length,
                        style: style
                    })
                });

                console.log('Response status:', response.status);

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('Error response:', errorText);
                    let errorMessage = 'Summarization failed';
                    try {
                        const errorData = JSON.parse(errorText);
                        errorMessage = errorData.error || errorMessage;
                    } catch (e) {
                        // Response is not JSON
                    }
                    throw new Error(errorMessage);
                }

                currentResult = await response.json();
                console.log('Success! Result:', currentResult);
                displayResults(currentResult);

                document.getElementById('loadingCard').classList.remove('active');
                document.getElementById('resultCard').classList.remove('hidden');
            } catch (error) {
                console.error('Summarization error:', error);
                document.getElementById('loadingCard').classList.remove('active');
                document.getElementById('inputCard').classList.remove('hidden');
                showToast('Error: ' + error.message);
            }
        }

        function displayResults(result) {
            document.getElementById('resultTitle').textContent = result.title;
            document.getElementById('mainTopic').textContent = result.main_topic;

            const sentimentEl = document.getElementById('sentiment');
            sentimentEl.textContent = result.sentiment;
            sentimentEl.className = 'stat-value sentiment-' + result.sentiment.toLowerCase();

            document.getElementById('readingTime').innerHTML = `
                <div class="reading-time-comparison">
                    <div class="reading-time-item">
                        <div class="time-value" style="color: #e74c3c;">${result.reading_time.original}</div>
                        <div class="stat-label">Original</div>
                    </div>
                    <div class="reading-time-arrow">→</div>
                    <div class="reading-time-item">
                        <div class="time-value" style="color: #27ae60;">${result.reading_time.summary}</div>
                        <div class="stat-label">Summary</div>
                    </div>
                </div>
            `;

            // Summary content
            const summaryContent = document.getElementById('summaryContent');
            const style = document.getElementById('styleSelect').value;

            if (style === 'bullet points') {
                const sentences = result.summary.split('. ').filter(s => s.trim());
                summaryContent.innerHTML = sentences.map(s =>
                    `<div class="summary-bullet">• ${s}${s.endsWith('.') ? '' : '.'}</div>`
                ).join('');
            } else {
                summaryContent.innerHTML = `<div class="summary-text">${result.summary}</div>`;
            }

            // Key points
            const keyPointsEl = document.getElementById('keyPoints');
            keyPointsEl.innerHTML = result.key_points.map(point =>
                `<li>${point}</li>`
            ).join('');

            // Keywords
            const keywordsEl = document.getElementById('keywords');
            keywordsEl.innerHTML = result.keywords.map(kw =>
                `<span class="keyword-tag">${kw}</span>`
            ).join('');
        }

        function showInput() {
            document.getElementById('resultCard').classList.add('hidden');
            document.getElementById('inputCard').classList.remove('hidden');
        }

        function copySummary() {
            if (!currentResult) return;

            let text = `Title: ${currentResult.title}\\n`;
            text += `Main Topic: ${currentResult.main_topic}\\n`;
            text += `Sentiment: ${currentResult.sentiment}\\n\\n`;
            text += `Summary:\\n${currentResult.summary}\\n\\n`;
            text += `Key Points:\\n${currentResult.key_points.map(p => '- ' + p).join('\\n')}\\n\\n`;
            text += `Keywords: ${currentResult.keywords.join(', ')}`;

            navigator.clipboard.writeText(text).then(() => {
                showToast('Copied to clipboard!');
            });
        }

        function downloadSummary(format) {
            if (!currentResult) return;

            let content, filename, mimeType;

            if (format === 'json') {
                content = JSON.stringify(currentResult, null, 2);
                filename = 'summary.json';
                mimeType = 'application/json';
            } else {
                content = `Title: ${currentResult.title}\\n`;
                content += `Main Topic: ${currentResult.main_topic}\\n`;
                content += `Sentiment: ${currentResult.sentiment}\\n\\n`;
                content += `Summary:\\n${currentResult.summary}\\n\\n`;
                content += `Key Points:\\n${currentResult.key_points.map(p => '- ' + p).join('\\n')}\\n\\n`;
                content += `Keywords: ${currentResult.keywords.join(', ')}`;
                filename = 'summary.txt';
                mimeType = 'text/plain';
            }

            const blob = new Blob([content], { type: mimeType });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);

            showToast(`Downloaded as ${filename}`);
        }

        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        }

        window.removeFile = removeFile;
        window.summarize = summarize;
        window.showInput = showInput;
        window.copySummary = copySummary;
        window.downloadSummary = downloadSummary;
    </script>
</body>
</html>"""


class SummaryRequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, body: str, status: int = 200, content_type: str = "text/html; charset=utf-8") -> None:
        if "charset=" not in content_type and (
            content_type.startswith("text/") or content_type == "application/json"
        ):
            content_type = f"{content_type}; charset=utf-8"
        body_bytes = body.encode("utf-8")

        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.send_header("Content-Length", str(len(body_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body_bytes)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_response(HTML_PAGE)
            return

        if parsed.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if parsed.path == "/summarize":
            params = parse_qs(parsed.query)
            text = params.get("text", [""])[0].strip()
            length = params.get("length", ["medium"])[0]
            style = params.get("style", ["paragraph"])[0]

            if not text:
                self._send_response(json.dumps({"error": "Missing text parameter"}), status=400, content_type="application/json")
                return

            response = build_summary_response(text, length=length, style=style)
            self._send_response(json.dumps(response, indent=2), content_type="application/json")
            return

        self._send_response("Not Found", status=404, content_type="text/plain")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/summarize":
            content_type = self.headers.get('Content-Type', '')

            if 'application/json' in content_type:
                try:
                    content_length = int(self.headers.get('Content-Length', 0))
                    if content_length <= 0:
                        self._send_response(json.dumps({"error": "Missing or empty request body"}), status=400, content_type="application/json")
                        return
                    body = self.rfile.read(content_length)
                    data = json.loads(body.decode('utf-8'))
                except json.JSONDecodeError:
                    self._send_response(json.dumps({"error": "Invalid JSON in request body"}), status=400, content_type="application/json")
                    return
                except (ValueError, UnicodeDecodeError) as e:
                    self._send_response(json.dumps({"error": f"Invalid request: {str(e)}"}), status=400, content_type="application/json")
                    return

                text = data.get("text", "").strip()
                length = data.get("length", "medium")
                style = data.get("style", "paragraph")

                if not text:
                    self._send_response(json.dumps({"error": "Missing text parameter"}), status=400, content_type="application/json")
                    return

                try:
                    response = build_summary_response(text, length=length, style=style)
                    self._send_response(json.dumps(response, indent=2), content_type="application/json")
                except Exception as e:
                    self._send_response(json.dumps({"error": f"Summarization error: {str(e)}"}), status=500, content_type="application/json")
                return

            if 'multipart/form-data' in content_type:
                try:
                    form = cgi.FieldStorage(
                        fp=self.rfile,
                        headers=self.headers,
                        environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers.get('Content-Type', '')}
                    )

                    text = form.getvalue("text", "").strip() if form.getvalue("text") else ""
                    length = form.getvalue("length", "medium")
                    style = form.getvalue("style", "paragraph")

                    file_item = form.get("file")
                    if file_item and file_item.file:
                        text = decode_bytes(file_item.file.read())

                    if not text:
                        self._send_response(json.dumps({"error": "Missing text or file parameter"}), status=400, content_type="application/json")
                        return

                    response = build_summary_response(text, length=length, style=style)
                    self._send_response(json.dumps(response, indent=2), content_type="application/json")
                except Exception as e:
                    self._send_response(json.dumps({"error": f"File upload error: {str(e)}"}), status=500, content_type="application/json")
                return

        self._send_response(json.dumps({"error": "Endpoint not found"}), status=404, content_type="application/json")

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()




def run_server() -> None:
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, SummaryRequestHandler)
    print(f"Server running at http://{HOST}:{PORT}/")
    print(f"Open your browser and start summarizing!")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
