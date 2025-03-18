import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import requests
def transcribe_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🗣️ Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
            return recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""
import tempfile
from gtts import gTTS

def speak_text(text):
    """
    Converts text to speech and saves it as a temporary audio file.
    :param text: The text to be converted into speech.
    :return: Path to the temporary audio file.
    """
    try:
        tts = gTTS(text=text, lang="en")

        # ✅ Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)

        return temp_file.name  # Return file path instead of BytesIO
    except Exception as e:
        return f"❌ TTS Error: {str(e)}"
