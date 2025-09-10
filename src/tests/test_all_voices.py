import os
import soundfile as sf
from kokoro_onnx import Kokoro
import random
import onnxruntime as ort
import pysbd # Import for sentence segmentation
import numpy as np # Import for audio concatenation

# Helper to get GPU providers
def get_onnx_providers():
    providers = ort.get_available_providers()
    if "DmlExecutionProvider" in providers:
        return ["DmlExecutionProvider", "CPUExecutionProvider"]
    elif "CUDAExecutionProvider" in providers:
        return ["CUDAExecutionProvider", "CPUExecutionProvider"]
    return ["CPUExecutionProvider"]

# Load Kokoro model once
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir)) # Go up two levels from 'src/tests' to the project root

kokoro_model_path = os.path.join(project_root, "data", "models", "kokoro-v1.0.onnx")
voices_file_path = os.path.join(project_root, "data", "models", "voices-v1.0.bin")

kokoro = Kokoro(
    kokoro_model_path,
    voices_file_path
)
print("Available voices:", list(kokoro.voices.keys()))
print("ONNX Runtime providers detected:", get_onnx_providers())

# List of allowed voices (can be expanded if needed for testing)
available_voices = list(kokoro.voices.keys())

def generate_voice_local(
    text: str,
    output_path: str = "output.wav",
    voice: str = None
) -> None:
    """
    Generates a .wav file from text using Kokoro TTS.
    Randomly picks a voice if none is specified.
    Uses GPU automatically if available.
    """
    if voice is None:
        voice = random.choice(available_voices)

    if voice not in kokoro.voices:
        raise ValueError(f"Voice '{voice}' not found. Available voices: {list(kokoro.voices.keys())}")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    segmenter = pysbd.Segmenter(language="en", clean=False)
    sentences = segmenter.segment(text)

    all_samples = []
    sample_rate = None

    for i, sentence in enumerate(sentences):
        print(f"Generating audio for sentence {i+1}/{len(sentences)}: '{sentence[:50]}...'")
        try:
            sentence_samples, sentence_sample_rate = kokoro.create(
                text=sentence,
                voice=voice,
                speed=1.0,
                lang="en-us"
            )
            all_samples.append(sentence_samples)
            if sample_rate is None:
                sample_rate = sentence_sample_rate
        except IndexError as e:
            print(f"Warning: IndexError encountered for sentence '{sentence[:50]}...'. Skipping this sentence. Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred for sentence '{sentence[:50]}...'. Skipping. Error: {e}")

    if not all_samples:
        raise RuntimeError("No audio samples were generated for the given text.")

    samples = np.concatenate(all_samples)
    sf.write(output_path, samples, sample_rate)
    print(f"Voice '{voice}' generated and saved to {output_path}")


def test_all_voices_audio_generation():
    """
    Generates 2-sentence audio vocal for all available voices.
    """
    test_text = "Hello! This is a test sentence for voice generation. I hope it works well! 😊"
    output_folder = "output/test_voices"
    os.makedirs(output_folder, exist_ok=True)

    print("\n--- Generating audio for all voices ---")
    for voice_name in available_voices:
        output_file = os.path.join(output_folder, f"{voice_name}.wav")
        print(f"Generating audio for voice: {voice_name} to {output_file}")
        try:
            generate_voice_local(test_text, output_file, voice_name)
            print(f"Successfully generated audio for {voice_name}")
        except Exception as e:
            print(f"Error generating audio for {voice_name}: {e}")

if __name__ == "__main__":
    test_all_voices_audio_generation()










    