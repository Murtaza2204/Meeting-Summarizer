import json
import os
import shutil
import tempfile
from pathlib import Path

from config import (
    SARVAM_API_KEY,
    SARVAM_LANGUAGE_CODE,
    SARVAM_MODEL,
    SARVAM_TRANSCRIPTION_MODE,
)

try:
    from sarvamai import SarvamAI
except ImportError:  # pragma: no cover - handled at runtime with a clear error
    SarvamAI = None

class AudioTranscriber:
    def __init__(self):
        """Initialize the Sarvam client."""
        self.client = None
        if SarvamAI is not None and SARVAM_API_KEY:
            self.client = SarvamAI(api_subscription_key=SARVAM_API_KEY)
    
    def transcribe(self, audio_path: str) -> dict:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary with transcript and metadata
        """
        if SarvamAI is None:
            return {
                "success": False,
                "error": "sarvamai is not installed. Run `pip install -r requirements.txt` to add the Sarvam SDK."
            }

        if not SARVAM_API_KEY:
            return {
                "success": False,
                "error": "SARVAM_API_KEY is not set in the environment."
            }

        try:
            temp_dir = tempfile.mkdtemp(prefix="sarvam_stt_")
            try:
                job_kwargs = {
                    "model": SARVAM_MODEL,
                    "mode": SARVAM_TRANSCRIPTION_MODE,
                }
                if SARVAM_LANGUAGE_CODE:
                    job_kwargs["language_code"] = SARVAM_LANGUAGE_CODE

                job = self.client.speech_to_text_job.create_job(**job_kwargs)
                job.upload_files(file_paths=[audio_path])
                job.start()
                job.wait_until_complete()

                file_results = job.get_file_results()
                successful_files = file_results.get("successful", [])
                if not successful_files:
                    failed_files = file_results.get("failed", [])
                    error_message = "Sarvam transcription job failed."
                    if failed_files:
                        error_message = failed_files[0].get("error_message") or failed_files[0].get("error") or error_message
                    return {
                        "success": False,
                        "error": error_message
                    }

                job.download_outputs(output_dir=temp_dir)

                json_files = sorted(Path(temp_dir).rglob("*.json"))
                if not json_files:
                    return {
                        "success": False,
                        "error": "Sarvam completed the job, but no transcript file was downloaded."
                    }

                transcripts = []
                language_code = None
                request_id = None

                for json_file in json_files:
                    with json_file.open("r", encoding="utf-8") as handle:
                        payload = json.load(handle)

                    transcript = (payload.get("transcript") or "").strip()
                    if transcript:
                        transcripts.append(transcript)

                    language_code = payload.get("language_code") or language_code
                    request_id = payload.get("request_id") or request_id

                transcript_text = " ".join(transcripts).strip()
                if not transcript_text:
                    return {
                        "success": False,
                        "error": "Sarvam returned an empty transcript."
                    }

                return {
                    "success": True,
                    "transcript": transcript_text,
                    "language": language_code,
                    "request_id": request_id,
                    "model": SARVAM_MODEL,
                    "mode": SARVAM_TRANSCRIPTION_MODE,
                }
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
