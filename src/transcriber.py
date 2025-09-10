import json
import os
import wave
import vosk
from zipfile import ZipFile
import requests
import shutil

def get_word_timestamps(audio_path: str):
    """
    Transcribes an audio file and returns word-level timestamps.
    Downloads the Vosk model if it's not already present.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir) # Go up one level from 'src' to the project root
    model_path = os.path.join(project_root, "data", "models", "vosk-model-small-en-us-0.15")
    model_zip_name = "vosk-model-small-en-us-0.15.zip"
    model_url = f"https://alphacephei.com/vosk/models/{model_zip_name}"

    # Download and extract the model if it doesn't exist
    if not os.path.exists(model_path):
        print(f"Vosk model not found. Downloading from {model_url}...")
        try:
            # Ensure the data/models directory exists for the zip file
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            model_zip_full_path = os.path.join(os.path.dirname(model_path), model_zip_name)

            with requests.get(model_url, stream=True) as r:
                r.raise_for_status()
                with open(model_zip_full_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            print("Model downloaded. Extracting...")
            with ZipFile(model_zip_full_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(model_path)) # Extract to data/models
            
            os.remove(model_zip_full_path)
            print("Model extracted successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading model: {e}")
            return None
        except Exception as e:
            print(f"An error occurred during model setup: {e}")
            return None

    try:
        model = vosk.Model(model_path)
        wf = wave.open(audio_path, "rb")
        
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("Audio file must be WAV format mono 16-bit.")
            return None

        rec = vosk.KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)

        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                results.append(json.loads(rec.Result()))

        results.append(json.loads(rec.FinalResult()))

        words = []
        for res in results:
            if 'result' in res:
                words.extend(res['result'])
        
        return words

    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    sample_audio_file = "output/generatedVoice/generated_story.wav"
    if os.path.exists(sample_audio_file):
        word_timestamps = get_word_timestamps(sample_audio_file)
        if word_timestamps:
            print("Word timestamps:")
            for word_info in word_timestamps:
                print(f"  Word: {word_info['word']}, Start: {word_info['start']}, End: {word_info['end']}")
    else:
        print(f"Sample audio file not found: {sample_audio_file}")
        print("Please generate a voice first by running main.py")
