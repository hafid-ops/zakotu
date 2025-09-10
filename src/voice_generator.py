import soundfile as sf
from kokoro_onnx import Kokoro
import random
import onnxruntime as ort
import os
import pysbd
import numpy as np
import re

# -------------------------
# Helper to get GPU providers (Linux-optimized)
# -------------------------
def get_onnx_providers():
    providers = ort.get_available_providers()
    print("Detected ONNX providers:", providers)
    
    # For Linux, prioritize CUDA over other providers
    if "CUDAExecutionProvider" in providers:
        print("Using CUDA GPU acceleration")
        return ["CUDAExecutionProvider", "CPUExecutionProvider"]
    elif "DmlExecutionProvider" in providers:
        print("Using DirectML GPU (Windows compatibility mode)")
        return ["DmlExecutionProvider", "CPUExecutionProvider"]
    elif "OpenVINOExecutionProvider" in providers:
        print("Using Intel OpenVINO acceleration")
        return ["OpenVINOExecutionProvider", "CPUExecutionProvider"]
    
    print("No GPU acceleration detected, using CPU")
    return ["CPUExecutionProvider"]

# -------------------------
# Load Kokoro model
# -------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
print("Current directory:", current_dir)
print("Project root:", project_root)

kokoro_model_path = os.path.join(project_root, "data", "models", "kokoro-v1.0.onnx")
voices_file_path = os.path.join(project_root, "data", "models", "voices-v1.0.bin")

print("Loading Kokoro TTS model...")
kokoro = Kokoro(kokoro_model_path, voices_file_path)
print("Kokoro model loaded successfully")

print("Available voices:", list(kokoro.voices.keys()))
print("ONNX Runtime providers detected:", get_onnx_providers())

# -------------------------
# Allowed voices
# -------------------------
available_voices = [
    "am_adam",
]

# -------------------------
# Clean story text
# -------------------------
def extract_story_text(text: str) -> str:
    """
    Remove all metadata, bracketed text, emojis, image labels, and titles.
    Keeps only the story narration.
    """
    print("Extracting story text from raw input...")
    lines = text.splitlines()
    story_lines = []

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Skip metadata lines like Image:, Text:, or section titles in bold
        if re.match(r"^Image:|^Text:|\*\*.*?\*\*|^#+\s.*|\[.*?\]:", line):
            print(f"Skipping metadata line: {line[:50]}...")
            continue

        # For lines containing narration, remove the bracketed sounds
        # e.g., "[sound of rain] It started..." -> "It started..."
        clean_line = re.sub(r"\[.*?\]", "", line)
        
        # Remove emojis
        clean_line = re.sub(r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]", "", clean_line)
        
        # Remove leading/trailing whitespace
        clean_line = clean_line.strip()

        # Add the cleaned line if it's not empty
        if clean_line:
            story_lines.append(clean_line)

    print(f"Extracted {len(story_lines)} story lines")
    return " ".join(story_lines)

# -------------------------
# Generate voice function
# -------------------------
def generate_voice(
    text: str,
    output_path: str = "output.wav",
    voice: str = None,
    output_text_path: str = None
) -> None:
    """
    Generates a .wav file from text using Kokoro TTS.
    """
    print("Starting voice generation...")
    if voice is None:
        voice = random.choice(available_voices)
        print(f"No voice specified, randomly selected: {voice}")

    if voice not in kokoro.voices:
        raise ValueError(f"Voice '{voice}' not found. Available voices: {list(kokoro.voices.keys())}")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    print(f"Output directory ensured: {os.path.dirname(output_path)}")

    # Clean text
    clean_text = extract_story_text(text)

    if output_text_path:
        os.makedirs(os.path.dirname(output_text_path), exist_ok=True)
        with open(output_text_path, "w", encoding="utf-8") as f:
            f.write(clean_text)
        print(f"Cleaned story text saved to {output_text_path}")

    # Segment into sentences
    print("Segmenting text into sentences...")
    segmenter = pysbd.Segmenter(language="en", clean=False)
    sentences = segmenter.segment(clean_text)
    print(f"Total sentences to generate: {len(sentences)}")

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
        except Exception as e:
            print(f"Warning: Skipping sentence '{sentence[:50]}...'. Error: {e}")

    if not all_samples:
        raise RuntimeError("No audio samples were generated.")

    print("Concatenating all audio samples...")
    samples = np.concatenate(all_samples)

    print(f"Saving generated audio to {output_path}...")
    sf.write(output_path, samples, sample_rate)
    print(f"Voice '{voice}' successfully generated and saved.")

def generate_and_measure_audio(text: str, voice: str) -> tuple[np.ndarray, int, float]:
    """
    Generates audio for the given text and returns the samples, sample rate, and duration.
    """
    if voice == "random":
        voice = random.choice(available_voices)
        print(f"No voice specified for intro, randomly selected: {voice}")

    segmenter = pysbd.Segmenter(language="en", clean=False)
    sentences = segmenter.segment(text)
    
    all_samples = []
    sample_rate = None
    
    for sentence in sentences:
        sentence_samples, sentence_sample_rate = kokoro.create(
            text=sentence,
            voice=voice,
            speed=1.0,
            lang="en-us"
        )
        all_samples.append(sentence_samples)
        if sample_rate is None:
            sample_rate = sentence_sample_rate
            
    if not all_samples:
        raise RuntimeError("No audio samples were generated for intro text.")

    samples = np.concatenate(all_samples)
    duration = len(samples) / sample_rate
    
    return samples, sample_rate, duration

# -------------------------
# Example usage
# -------------------------
if __name__ == "__main__":
    print("Preparing story text...")
    story_text = """**1️⃣ Post-style Intro (Thumbnail/Social Media Text)**

Image: A blurry, rain-soaked street at night, a single figure walking away, looking distraught.

Text:  My best friend stole my fiancé, then framed me for a crime I didn't commit.  The truth? It was far more twisted than I could ever imagine…

**2️⃣ Full Story Script (1 Hour Narration)**

[NARRATOR]: It was a Tuesday, the kind of dreary Tuesday that soaked your bones even before the rain started. [sound of rain]  I was running, late again, the heels of my shoes clicking against the wet pavement. [footsteps approaching, echoing]  [thinking] “Just make it to the office, just make it to the office…”

[Scene change: office, night]

[NARRATOR]: My coworker, Mark [🧑 Jealous coworker], leaned against my desk, a smug look on his face.  [pause 1s] He held a crumpled piece of paper.

[MARK – jealous coworker]: "Well, well, looks like someone's got a little problem." [smugly]

[NARRATOR]:  The paper was a police report, my name scrawled across the top. Embezzlement. [long pause]  [sadly]  My heart plummeted. Embezzlement? Me?
"""

    output_folder = "output/generatedVoice"
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, "generated_story.wav")
    output_text_file = os.path.join(output_folder, "generated_story.txt")

    print("Starting TTS generation process...")
    generate_voice(story_text, output_file, voice="am_adam", output_text_path=output_text_file)
    print("TTS generation completed successfully!")
