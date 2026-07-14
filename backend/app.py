from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from config import FLASK_ENV, DEBUG, UPLOAD_FOLDER
from transcriber import AudioTranscriber
from summarizer import MeetingSummarizer

app = Flask(__name__)
CORS(app)
app.json.ensure_ascii = False

# Initialize services
transcriber = AudioTranscriber()
summarizer = MeetingSummarizer()

# Allowed audio formats
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'ogg', 'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """
    Transcribe audio file
    Expects multipart/form-data with 'audio' file
    """
    try:
        # Check if file is in request
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Transcribe
        result = transcriber.transcribe(filepath)
        
        # Clean up
        os.remove(filepath)
        
        return jsonify(result), 200 if result["success"] else 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    """
    Summarize meeting transcript
    Expects JSON with 'transcript' field
    """
    try:
        data = request.get_json()
        
        if not data or 'transcript' not in data:
            return jsonify({"error": "No transcript provided"}), 400
        
        transcript = data['transcript']
        result = summarizer.summarize(transcript)
        
        return jsonify(result), 200 if result["success"] else 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process', methods=['POST'])
def process_meeting():
    """
    Process complete meeting (transcribe + summarize)
    Expects multipart/form-data with 'audio' file
    """
    try:
        # Transcribe
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        file = request.files['audio']
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Step 1: Transcribe
        transcribe_result = transcriber.transcribe(filepath)
        os.remove(filepath)
        
        if not transcribe_result["success"]:
            return jsonify({"error": "Transcription failed"}), 400
        
        transcript = transcribe_result["transcript"]
        
        # Step 2: Summarize
        summary_result = summarizer.summarize(transcript)
        
        if not summary_result["success"]:
            return jsonify({"error": "Summarization failed"}), 400
        
        return jsonify({
            "success": True,
            "transcript": transcript,
            "summary": summary_result["summary"]
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
