import os
import json
import re
import logging
from groq import Groq
from typing import Dict, List, Optional
from dotenv import load_dotenv
from .check_correctness import check_answer_correctness
from .vocab_check import analyze_vocabulary
from .get_pause import get_pause_count
from deepgram import DeepgramClient
from .audio_utils import convert_audio_to_wav

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeedbackProcessor:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.deepgram = DeepgramClient()

        self.grammar_prompt = """You are a strict grammar expert analyzing a RAW speech transcript from a non-native English speaker.

The text was transcribed from audio — it contains filler words and hesitations. Ignore those.
Your task: find REAL grammatical errors. Be thorough. Do NOT give a pass to errors just because they sound informal.

ALWAYS flag these (with examples):
1. Subject-verb disagreement:
   - "he have" → "he has"
   - "she don't" → "she doesn't"
   - "they was" → "they were"
   - "he have to spend" → "he has to spend"

2. Missing or wrong articles (very common in Indian English):
   - "I reach office" → "I reach the office"
   - "get house" → "get a house"
   - "time management is important" ← OK (general statement)
   - "fill the house loans" → "pay off the home loans"

3. Wrong verb form:
   - "I wake at 7" → "I wake up at 7"
   - "I seen" → "I saw"
   - "I goes" → "I go"

4. Non-standard phrases (Indian English):
   - "near about" → "approximately"
   - "many much" → "much more" or "many more"
   - "do the needful" → "do what is needed"
   - "and all" (as sentence filler) → remove or rephrase

5. Wrong prepositions:
   - "good in English" → "good at English"
   - "invest in his skills" ← OK
   - "spend time with family" ← OK

DO NOT flag:
- Filler words: uh, um, hmm, like, basically, so, well, yeah
- Repeated words from hesitation: "he have to, uh, spend"
- Capitalization or punctuation
- Minor informal choices that are grammatically correct

IMPORTANT: "he have" and "he have to [verb]" are ALWAYS errors — flag every instance.

Return ONLY this JSON, no extra text:
{
    "error_count": <number>,
    "errors": [
        {
            "word": "<the incorrect phrase as spoken>",
            "suggestion": "<corrected phrase>",
            "explanation": "<one sentence explanation>"
        }
    ]
}"""

    def analyze_fluency(self, text: str) -> Dict:
        filler_patterns = [
            r'\b(hmm+|um+|uh+|aaa+|aa+|mmm+|mm+|ah+|er+|erm+|uhm+|uhmm+|uhhuh|uhuh|eh+|huh+|umm+)\b',
            r'\b(like|you know|basically|actually|literally|sort of|kind of|i mean|you see|right\?|okay\?|so yeah)\b',
            r'\b(so|well|look|listen|see|okay|like|right|yeah|um so|so basically)\b\s+',
            r'\b(maybe|probably|somewhat|somehow|kind of like|sort of like|i guess|i think|i suppose)\b',
            r'\b(at the end of the day|when all is said and done|you know what i mean|what im trying to say)\b',
            r'\b(and stuff|and things|and everything|and all that|or something|or whatever)\b',
            r'\b(anyway|anyhow|moving on|going back to|coming back to|speaking of)\b',
        ]
        combined_pattern = '|'.join(filler_patterns)
        matches = re.finditer(combined_pattern, text.lower())
        filler_words = []
        total_count = 0
        for match in matches:
            filler_words.append({
                "word": match.group(),
                "position": match.start(),
                "context": text[max(0, match.start() - 20):min(len(text), match.end() + 20)],
            })
            total_count += 1
        words_in_text = len(text.split())
        filler_ratio = total_count / max(1, words_in_text)
        fluency_score = max(0, min(100, 100 - (filler_ratio * 200)))
        return {
            "fluency_score": round(fluency_score, 1),
            "filler_word_count": total_count,
            "filler_words": filler_words,
            "words_analyzed": words_in_text,
            "filler_ratio": round(filler_ratio * 100, 1),
            "feedback": self._generate_fluency_feedback(total_count, words_in_text, fluency_score),
        }

    def _generate_fluency_feedback(self, filler_count: int, total_words: int, fluency_score: float) -> str:
        if fluency_score >= 90:
            return "Excellent fluency! Your speech flows naturally with minimal use of filler words."
        elif fluency_score >= 75:
            return "Good fluency overall. Consider reducing filler words slightly to improve clarity."
        elif fluency_score >= 60:
            return "Moderate fluency. Try to be more conscious of filler words and practice speaking with more confidence."
        else:
            return "Your speech contains frequent filler words. Focus on reducing hesitations and practice speaking with more confidence."

    async def analyze_grammar(self, text: str) -> Dict:
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.grammar_prompt},
                    {"role": "user", "content": f"Analyze this raw speech transcript for grammatical errors: {text}"},
                ],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.1,
            )
            return self._parse_grammar_response(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error in analyze_grammar: {str(e)}")
            return {"error_count": 0, "errors": []}

    # Words that Deepgram routinely under-scores on accented speech —
    # low confidence here reflects STT uncertainty, NOT mispronunciation.
    COMMON_WORDS = {
        # Articles / determiners
        "a", "an", "the", "this", "that", "these", "those",
        "my", "your", "his", "her", "its", "our", "their",
        "some", "any", "each", "every", "no", "all",
        # Prepositions
        "at", "in", "on", "to", "for", "of", "with", "by", "from",
        "up", "about", "into", "through", "during", "before", "after",
        "above", "below", "between", "out", "off", "over", "under",
        "near", "around", "as", "than",
        # Conjunctions / connectors
        "and", "or", "but", "so", "yet", "nor", "although", "because",
        "since", "while", "if", "then", "though", "when", "where",
        "which", "who", "whom", "whose",
        # Pronouns
        "i", "me", "we", "us", "you", "he", "him", "she", "they",
        "them", "it", "what",
        # Common auxiliaries & verbs
        "am", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "shall", "can", "go", "get",
        "got", "make", "take", "come", "see", "know", "think", "look",
        "want", "give", "use", "find", "tell", "ask", "seem", "feel",
        "try", "keep", "let", "run", "move", "live", "reach", "stand",
        "help", "start", "work", "speak", "spend", "earn", "switch",
        "gain", "fill", "invest",
        # Common adjectives / adverbs
        "more", "most", "much", "many", "very", "just", "also", "only",
        "really", "quite", "too", "not", "well", "even", "still",
        "already", "always", "never", "often", "here", "there", "now",
        "then", "how", "why", "both", "same", "other", "new", "good",
        "big", "important", "multiple", "common",
        # Everyday nouns that get mis-scored on accent
        "person", "people", "family", "money", "time", "house", "home",
        "work", "life", "day", "year", "way", "issue", "issues",
        "skills", "loans", "loan", "corporate", "management",
        # Filler / discourse words (handled by fluency already)
        "uh", "um", "hmm", "ah", "er", "yeah", "okay", "like",
        "basically", "so", "well",
        # Numbers / time
        "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten",
    }

    def _is_genuine_pronunciation_error(self, word: str, confidence: float) -> bool:
        """
        Return True only when the word is non-trivial AND confidence is
        genuinely low — not just because of accent or audio quality.

        Thresholds by word type:
          - Common/simple words        → never flag
          - Short words (≤ 3 chars)    → never flag (pure STT noise)
          - Medium words (4–5 chars)   → flag only below 0.60
          - Longer unfamiliar words    → flag below 0.68
        """
        clean = word.lower().strip(".,!?\"'")

        if clean in self.COMMON_WORDS:
            return False
        if len(clean) <= 3:
            return False
        if len(clean) <= 5:
            return confidence < 0.60
        return confidence < 0.68

    async def analyze_pronunciation(self, text: str, audio_file: str = None) -> Dict:
        """
        Analyze pronunciation using Deepgram word-level confidence.
        Uses smart filtering so common words (have, like, when, his, much,
        person, corporate …) are never flagged regardless of confidence.
        """
        if not audio_file or not os.path.exists(audio_file):
            return {"error_count": 0, "errors": [], "message": "No audio file provided or file not found"}

        try:
            with open(audio_file, "rb") as f:
                audio_bytes = f.read()

            response = self.deepgram.listen.v1.media.transcribe_file(
                request=audio_bytes,
                model="nova-2",
                language="en",
                punctuate=True,
                utterances=True,
                numerals=True,
                profanity_filter=False,
                filler_words=True,
                detect_language=True,
            )

            words = response.results.channels[0].alternatives[0].words or []

            pronunciation_errors = []
            error_count = 0
            total_confidence = 0.0
            total_words = len(words)
            flagged_words = set()   # deduplicate — flag each word only once

            for word_obj in words:
                word_text = getattr(word_obj, "word", "").strip(".,!?\"'")
                confidence = getattr(word_obj, "confidence", 1.0) or 1.0
                start = getattr(word_obj, "start", 0) or 0
                end = getattr(word_obj, "end", 0) or 0

                total_confidence += confidence

                if (
                    self._is_genuine_pronunciation_error(word_text, confidence)
                    and word_text.lower() not in flagged_words
                ):
                    error_count += 1
                    flagged_words.add(word_text.lower())
                    pronunciation_errors.append({
                        "word": word_text,
                        "confidence": round(confidence, 2),
                        "timestamp": {"start": start, "end": end},
                        "suggestion": "Review pronunciation of this word",
                        "severity": "high" if confidence < 0.55 else "medium",
                    })

            avg_confidence = total_confidence / total_words if total_words > 0 else 0
            return {
                "error_count": error_count,
                "errors": pronunciation_errors,
                "overall_confidence": round(avg_confidence, 3),
                "pronunciation_score": round(avg_confidence * 100, 1),
                "words_analyzed": total_words,
                "feedback": self._generate_pronunciation_feedback(avg_confidence, error_count, total_words),
            }

        except Exception as e:
            logger.error(f"Error in audio pronunciation analysis: {str(e)}")
            return {"error_count": 0, "errors": [], "message": f"Error analyzing pronunciation: {str(e)}"}

    async def analyze_pauses(self, text: str, tempFileName: str) -> Dict:
        logger.info(f"Starting pause analysis with file: {tempFileName}")
        try:
            if not tempFileName:
                return {"total_pauses": 0, "pause_details": [], "total_pause_duration": 0, "message": "No audio file provided"}
            audio_path = os.path.abspath(tempFileName)
            if not os.path.exists(audio_path):
                return {"total_pauses": 0, "pause_details": [], "total_pause_duration": 0, "message": f"Audio file not found at: {audio_path}"}
            wav_file = await convert_audio_to_wav(audio_path)
            if not wav_file:
                return {"total_pauses": 0, "pause_details": [], "total_pause_duration": 0, "message": "Audio conversion failed"}
            pause_analysis = get_pause_count(wav_file)
            logger.info(f"Pause analysis completed: {pause_analysis}")
            return pause_analysis
        except Exception as e:
            logger.error(f"Error in pause analysis: {str(e)}")
            return {"total_pauses": 0, "pause_details": [], "total_pause_duration": 0, "error": str(e)}

    def _parse_grammar_response(self, response: str) -> Dict:
        try:
            cleaned = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            return {"error_count": data.get("error_count", 0), "errors": data.get("errors", [])}
        except Exception as e:
            logger.error(f"Error parsing grammar response: {str(e)}")
            return {"error_count": 0, "errors": []}

    async def analyze_text(self, text: str, question: Optional[str] = None, tempFileName: str = "") -> Dict:
        try:
            grammar_analysis = await self.analyze_grammar(text)
            pronunciation_analysis = await self.analyze_pronunciation(text, tempFileName)
            vocabulary_analysis = analyze_vocabulary(text)
            fluency_analysis = self.analyze_fluency(text)
            pause_analysis = await self.analyze_pauses(text, tempFileName)
            correctness_analysis = None
            if question:
                correctness_analysis = check_answer_correctness(question, text)
                logger.info(f"Correctness — Relevance: {correctness_analysis.get('relevance_score', 0)}, Quality: {correctness_analysis.get('quality_score', 0)}")
            return {
                "grammar": grammar_analysis,
                "pronunciation": pronunciation_analysis,
                "vocabulary": vocabulary_analysis,
                "fluency": fluency_analysis,
                "pauses": pause_analysis,
                "correctness": correctness_analysis,
                "text": text,
            }
        except Exception as e:
            logger.error(f"Error in analyze_text: {e}")
            return {"error": str(e)}

    def _generate_pronunciation_feedback(self, confidence: float, error_count: int, total_words: int) -> str:
        if confidence >= 0.9:
            return "Excellent pronunciation! Your speech is very clear and well-articulated."
        elif confidence >= 0.75:
            return "Good pronunciation overall. Keep practicing to improve clarity."
        elif confidence >= 0.6:
            return "Fair pronunciation. Focus on clear articulation and practice challenging words."
        else:
            return "Your pronunciation needs improvement. Consider practicing difficult words and sounds."