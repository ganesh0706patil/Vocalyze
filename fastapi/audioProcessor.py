import os
import logging
from groq import Groq
from typing import Dict
from dotenv import load_dotenv
from fastapi import UploadFile, HTTPException

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

groq = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq)

LANGUAGE_CODES = {
    "Hindi": "hi",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Tamil": "ta",
    "Telugu": "te",
    "English": "en",
    "Assamese": "as",
    "Odia": "or"
}

# FIX: Much more aggressive prompts that force Whisper to preserve raw speech.
# Whisper ignores short prompts and defaults to cleaning. These prompts are
# long enough to shift the prior and include example hesitations that Whisper
# will pattern-match against.
PROMPTS = {
    "English": (
        "Transcribe exactly what is spoken. Do NOT correct grammar. Do NOT fix word choice. "
        "Do NOT clean up the speech. Preserve every hesitation, filler word, repeated word, "
        "mispronunciation, and grammatical mistake exactly as heard. "
        "Include sounds like: um, uh, hmm, ah, er, like, you know, basically, so, well, okay. "
        "Example of correct transcription style: "
        "'Um so I goes to the store yesterday, uh, and like I seen my friend there, you know, "
        "it were really um like surprising and stuff.' "
        "Always transcribe word-for-word with all errors intact."
    ),
    "Hindi": (
        "बिल्कुल वैसा ही लिखें जैसा बोला गया है। व्याकरण ठीक मत करें। "
        "हिचकिचाहट जैसे 'हम्म', 'उम्', 'उह', 'आआ', 'आ', 'मम्म', 'मम', 'आह', 'एर', 'एर्म' शामिल करें। "
        "हर गलत शब्द, रुकावट और दोहराए गए शब्द को वैसे ही लिखें।"
    ),
    "Bengali": (
        "ঠিক যেভাবে বলা হয়েছে সেভাবেই লিখুন। ব্যাকরণ ঠিক করবেন না। "
        "'হুম', 'উম', 'উহ', 'আআ', 'আ', 'ম্ম' এর মতো দ্বিধার শব্দ অন্তর্ভুক্ত করুন। "
        "প্রতিটি ভুল শব্দ এবং পুনরাবৃত্তি সংরক্ষণ করুন।"
    ),
    "Gujarati": (
        "બરાબર જે બોલ્યા છે તે જ લખો. વ્યાકરણ સુધારો નહીં. "
        "'હમ્મ', 'ઉમ', 'ઉહ', 'આઆ', 'આ', 'મ્મ' જેવા સંકોચ શબ્દો સાચવો. "
        "દરેક ભૂલ અને પુનરાવર્તન સચવો."
    ),
    "Kannada": (
        "ಮಾತನಾಡಿದ ಹಾಗೆ ನಿಖರವಾಗಿ ಬರೆಯಿರಿ. ವ್ಯಾಕರಣ ಸರಿಪಡಿಸಬೇಡಿ. "
        "'ಹುಮ್', 'ಉಮ್', 'ಉಹ್', 'ಆಆ', 'ಆ', 'ಮ್ಮ' ಮೊದಲಾದ ತಡಕಿದ ಶಬ್ದಗಳನ್ನು ಉಳಿಸಿ. "
        "ಪ್ರತಿ ತಪ್ಪು ಮತ್ತು ಪುನರಾವರ್ತನೆ ಸಂರಕ್ಷಿಸಿ."
    ),
    "Malayalam": (
        "സംസാരിച്ചത് അക്ഷരംപ്രതി എഴുതുക. വ്യാകരണം തിരുത്തരുത്. "
        "'ഹം', 'ഉം', 'ഉഹ്', 'ആആ', 'ആ', 'മ്മ്' തുടങ്ങിയ മടിച്ച ശബ്ദങ്ങൾ ഉൾപ്പെടുത്തുക. "
        "എല്ലാ തെറ്റുകളും ആവർത്തനങ്ങളും സൂക്ഷിക്കുക."
    ),
    "Marathi": (
        "बोललेले तसेच लिहा. व्याकरण सुधारू नका. "
        "'हम्म', 'उम्', 'उह', 'आआ', 'आ', 'म्म' असे संकोचाचे शब्द जपा. "
        "प्रत्येक चूक आणि पुनरावृत्ती जतन करा."
    ),
    "Punjabi": (
        "ਬੋਲੇ ਨੂੰ ਜਿਵੇਂ ਹੈ ਤਿਵੇਂ ਲਿਖੋ। ਵਿਆਕਰਣ ਠੀਕ ਨਾ ਕਰੋ। "
        "'ਹਮਮ', 'ਉਮ', 'ਉਹ', 'ਆਆ', 'ਆ', 'ਮਮਮ' ਵਰਗੇ ਝਿਜਕ ਸ਼ਬਦ ਸੰਭਾਲੋ। "
        "ਹਰ ਗਲਤੀ ਅਤੇ ਦੁਹਰਾਓ ਬਰਕਰਾਰ ਰੱਖੋ।"
    ),
    "Tamil": (
        "பேசியதை அப்படியே எழுதுங்கள். இலக்கணத்தை சரிசெய்யாதீர்கள். "
        "'ஹும்', 'உம்', 'உஹ்', 'ஆஆ', 'ஆ', 'ம்' போன்ற தயக்க வார்த்தைகளை வையுங்கள். "
        "ஒவ்வொரு தவறு மற்றும் மீண்டும் மீண்டும் சொல்வதையும் பாதுகாக்கவும்."
    ),
    "Telugu": (
        "మాట్లాడినట్లే రాయండి. వ్యాకరణాన్ని సరిచేయకండి. "
        "'హమ్', 'ఉమ్', 'ఉహ్', 'ఆఆ', 'ఆ', 'మ్మ్' వంటి సందిగ్ధత పదాలు ఉంచండి. "
        "ప్రతి తప్పు మరియు పునరావృత్తిని సంరక్షించండి."
    ),
    "Assamese": (
        "কোৱাটো হুবহু লিখক। ব্যাকৰণ ঠিক নকৰিব। "
        "'হুম', 'উম', 'উহ', 'আআ', 'আ', 'ম্ম' যেনে সন্দেহ শব্দবোৰ ৰাখক। "
        "প্ৰতিটো ভুল আৰু পুনৰাবৃত্তি সংৰক্ষণ কৰক।"
    ),
}


async def process_audio_file(file_path: str, language: str = "English") -> dict:
    """
    Process an audio file and return its transcription.
    Uses an aggressive prompt to preserve filler words, hesitations, and grammar errors.
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {"status": "error", "message": "File not found"}

        language_code = LANGUAGE_CODES.get(language, "en")
        logger.info(f"Processing audio in {language} (code: {language_code})")

        with open(file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), file.read()),
                model="whisper-large-v3",
                # FIX: Use the verbose_json format to get word-level timestamps,
                # which also tends to reduce Whisper's post-processing / cleaning.
                prompt=PROMPTS.get(language, PROMPTS["English"]),
                response_format="verbose_json",
                language=language_code,
                temperature=0.2,  # FIX: Tiny non-zero temp reduces over-cleaning
            )

        # verbose_json returns a richer object; .text is still the full transcript
        raw_text = transcription.text

        logger.info(f"Raw transcript: {raw_text}")

        return {
            "status": "success",
            "text": raw_text,
            "filename": os.path.basename(file_path),
            "language": language,
            "language_code": language_code,
        }

    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        return {
            "status": "error",
            "message": f"Error processing audio: {str(e)}",
            "filename": os.path.basename(file_path),
            "language": language,
        }


async def process_audio(audio_file: UploadFile) -> Dict:
    try:
        os.makedirs("temp_audio", exist_ok=True)

        file_path = os.path.join("temp_audio", "question_0.mp4")
        with open(file_path, "wb") as buffer:
            content = await audio_file.read()
            buffer.write(content)

        logger.info(f"Audio file saved to: {file_path}")

        with open(file_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), f.read()),
                model="whisper-large-v3",
                prompt=PROMPTS["English"],
                response_format="verbose_json",
                language="en",
                temperature=0.2,
            )

        return {"text": transcription.text}

    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))