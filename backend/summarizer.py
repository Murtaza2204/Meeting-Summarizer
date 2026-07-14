from openai import OpenAI
from config import OPENAI_API_KEY

class MeetingSummarizer:
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def summarize(self, transcript: str) -> dict:
        """
        Generate summary and action items from transcript
        
        Args:
            transcript: Full meeting transcript
            
        Returns:
            Dictionary with summary and action items
        """
        try:
            prompt = f"""Analyze this meeting transcript and provide:
1. A concise summary of key discussions
2. Key decisions made
3. Action items with assigned owners (if mentioned)

Transcript:
{transcript}

Format your response as:
SUMMARY:
[summary here]

KEY DECISIONS:
[decisions here]

ACTION ITEMS:
- [action]: [responsible person/team] (due date if mentioned)
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing meetings."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return {
                "success": True,
                "summary": response.choices[0].message.content
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
