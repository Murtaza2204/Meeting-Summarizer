# Meeting Summarizer

Transcribe meeting audio and generate action-oriented summaries using AI.

Live app: https://meeting-summarizer-six-ivory.vercel.app/     
IMP: If you encounter a "Failed to fetch" error, try connecting your device to a mobile hotspot instead of your Wi-Fi router.

## Objective
Transcribe meeting audio files and generate summaries with key decisions and action items.

## Features
- **Audio Transcription**: Convert meeting audio to text using Sarvam AI Saaras v3
- **Summary Generation**: Generate concise summaries with LLM
- **Action Items**: Extract and organize action items from meetings
- **REST API**: Easy-to-use Flask API for integration
- **Multiple Audio Formats**: Support for MP3, WAV, M4A, FLAC, OGG, MP4

## Tech Stack
- **Backend**: Flask
- **Speech-to-Text**: Sarvam AI Saaras v3
- **LLM**: OpenAI GPT-3.5 Turbo
- **Frontend**: React + Vite

## Installation

### Prerequisites
- Python 3.8+
- FFmpeg (already downloaded ✓)
- Sarvam SDK dependencies (installed with `pip install -r requirements.txt`)
- Virtual environment (already created ✓)

### Setup

1. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file**
   ```bash
   # Copy example
   cp .env.example .env
   
   # Edit .env and add your API keys
   ```
   
   Add your API keys:
   ```
   OPENAI_API_KEY=your_key_here
   SARVAM_API_KEY=your_sarvam_key_here
   ```
   If you want English output from all audio, use:
   ```
   SARVAM_TRANSCRIPTION_MODE=translate
   ```

4. **Run the application**
   ```bash
   python backend/app.py
   ```

The API will be available at `http://localhost:5000`

### Frontend

1. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Create frontend env file**
   ```bash
   Copy-Item .env.example .env
   ```

3. **Run the frontend**
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### Health Check
```bash
GET /health
```

### Transcribe Audio
```bash
POST /transcribe
Content-Type: multipart/form-data

Body:
- audio: [audio file]

Response:
{
  "success": true,
  "transcript": "...",
  "language": "en-IN",
  "request_id": "..."
}
```

### Summarize Transcript
```bash
POST /summarize
Content-Type: application/json

Body:
{
  "transcript": "..."
}

Response:
{
  "success": true,
  "summary": "..."
}
```

### Process Complete Meeting
```bash
POST /process
Content-Type: multipart/form-data

Body:
- audio: [audio file]

Response:
{
  "success": true,
  "transcript": "...",
  "summary": "..."
}
```

## Configuration

Edit `backend/config.py` to customize:
- Sarvam model and transcription mode
- Optional Sarvam language code
- Upload folder
- Flask settings

## Next Steps
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Set up `.env` file with API keys
- [ ] Test API endpoints
- [ ] Install frontend dependencies and run the UI
- [ ] Deploy to production

## Evaluation Focus
- Transcription accuracy
- Summary quality
- LLM prompt effectiveness
- Code structure and organization
