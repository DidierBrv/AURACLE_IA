import os
import warnings
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr
import queue

warnings.filterwarnings("ignore")

recognizer = sr.Recognizer()
FS = 44100
FILE_NAME = "temp_voice_buffer.wav"
THRESHOLD = 400
SILENCE_LIMIT = 1.5

ignore_audio = False 
print("[System]: EARS MODULE INITIALIZED (Smart VAD + Echo Canceller)")

def listen_to_user():
    q = queue.Queue()
    
    def callback(indata, frames, time, status):
        if ignore_audio:
            q.put(np.zeros_like(indata))
        else:
            q.put(indata.copy())

    audio_buffer = []
    is_speaking = False
    silence_chunks = 0
    chunk_size = int(FS * 0.1)

    try:
        with sd.InputStream(samplerate=FS, channels=1, dtype='int16', blocksize=chunk_size, callback=callback):
            while True:
                chunk = q.get()
                volume = np.max(np.abs(chunk))

                if volume > THRESHOLD:
                    if not is_speaking:
                        is_speaking = True
                    audio_buffer.append(chunk)
                    silence_chunks = 0
                    
                elif is_speaking:
                    audio_buffer.append(chunk)
                    silence_chunks += 1
                    
                    if silence_chunks > (SILENCE_LIMIT / 0.1):
                        break

        if not audio_buffer:
            return None

        recording = np.concatenate(audio_buffer, axis=0)
        if np.max(np.abs(recording)) == 0:
            return None

        wav.write(FILE_NAME, FS, recording)

        with sr.AudioFile(FILE_NAME) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="fr-FR")
            return text.lower()
            
    except sr.UnknownValueError:
        return None
    except Exception as e:
        return None
    finally:
        if os.path.exists(FILE_NAME):
            try: os.remove(FILE_NAME)
            except: pass