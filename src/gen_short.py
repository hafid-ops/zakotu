import asyncio
import os
import pysbd
from dotenv import load_dotenv
import google.generativeai as genai
from story_generator import generate_story
from voice_generator import generate_voice
from pollinations_image_generator import generate_pollinations_image
from transcriber import get_word_timestamps
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip
from moviepy.config import change_settings
import random
import subprocess
import platform

# Fix ImageMagick path - detect environment and set appropriate path
def setup_imagemagick():
    """Setup ImageMagick binary path based on environment"""
    # Check if we're running in Docker or local environment
    try:
        # Try Docker/Linux path first (convert command)
        result = subprocess.run(['convert', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            change_settings({"IMAGEMAGICK_BINARY": "convert"})
            print("Using Linux/Docker ImageMagick: convert")
            return
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try Linux/Unix paths
    unix_paths = ["/usr/bin/convert", "/usr/local/bin/convert", "convert"]
    for path in unix_paths:
        try:
            result = subprocess.run([path, '-version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                change_settings({"IMAGEMAGICK_BINARY": path})
                print(f"Using Linux ImageMagick: {path}")
                return
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    # Try common Windows paths as fallback
    if platform.system() == "Windows":
        windows_paths = [
            r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe",
            r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe", 
            r"C:\Program Files\ImageMagick-7.1.0-Q16-HDRI\magick.exe",
            r"C:\ImageMagick\magick.exe"
        ]
        for path in windows_paths:
            if os.path.exists(path):
                change_settings({"IMAGEMAGICK_BINARY": path})
                print(f"Using Windows ImageMagick: {path}")
                return
    
    print("Warning: ImageMagick not found. TextClip may not work properly.")

# Setup ImageMagick
setup_imagemagick()

# Load environment variables from .env file
load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

async def generate_content_task():
    """
    Generates the content for the video.
    """
    print("Generating content...")
    content = generate_story('Write a 3-sentence horror story that is short, funny, and unsettling.')

    return content

def generate_audio_task(text):
    """
    Generates audio from the given text.
    """
    print("Generating audio...")
    output_path = "output/generatedVoice/short_audio.wav"
    generate_voice(text, output_path)
    return output_path

async def generate_image_prompt(sentence: str) -> str:
    """
    Generates an image prompt for a sentence using Gemini.
    Falls back to simple prompt if API fails.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Extract the key elements from this sentence and list them as comma-separated values, suitable for an image generation prompt. The sentence is: '{sentence}'"
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating image prompt: {e}")
        # Enhanced fallback prompts based on content analysis
        sentence_lower = sentence.lower()
        if any(word in sentence_lower for word in ['dark', 'shadow', 'night', 'whisper']):
            return f"dark atmospheric scene, mysterious shadows, {sentence}"
        elif any(word in sentence_lower for word in ['old', 'vintage', 'antique']):
            return f"vintage atmosphere, old objects, nostalgic mood, {sentence}"
        elif any(word in sentence_lower for word in ['house', 'room', 'door']):
            return f"interior scene, atmospheric lighting, {sentence}"
        else:
            return f"cinematic shot, dramatic lighting, {sentence}" # Fallback prompt

async def generate_images_task(text):
    """
    Generates images for each sentence in the text.
    """
    print("Generating images...")
    segmenter = pysbd.Segmenter(language="en", clean=False)
    sentences = segmenter.segment(text)
    
    image_paths = []
    output_dir = "output/generatedImage/short"
    os.makedirs(output_dir, exist_ok=True)

    for i, sentence in enumerate(sentences):
        image_prompt = await generate_image_prompt(sentence)
        print(f"Generated Image Prompt: {image_prompt}")
        output_path = os.path.join(output_dir, f"image_{i}.png")
        image_path = generate_pollinations_image(image_prompt, output_path)
        if image_path:
            image_paths.append(image_path)
            
    return image_paths

def combine_assets_to_video_task(text, audio_path, image_paths):
    """
    Combines the text, audio, and images into a video with simple animations and text overlays.
    """
    print("Creating video...")
    
    if not image_paths:
        print("No images were generated. Cannot create video.")
        return None

    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration
    
    word_timestamps = get_word_timestamps(audio_path)
    
    if not word_timestamps:
        print("Could not get word timestamps. Cannot add text overlays.")
        # Fallback to creating video without text
        duration_per_image = audio_duration / len(image_paths)
        video_clips = [ImageClip(p).set_duration(duration_per_image) for p in image_paths]
        final_video = concatenate_videoclips(video_clips, method="compose")
        final_video = final_video.set_audio(audio_clip)
        output_path = "output/generatedVideo/short_video.mp4"
        final_video.write_videofile(output_path, fps=24)
        return output_path


    # Create a video clip for each image
    duration_per_image = audio_duration / len(image_paths)
    video_clips = []
    
    # Only allow zoom_in, pan_left, pan_right (no zoom_out)
    animations = ['zoom_in', 'pan_left', 'pan_right']

    for i, image_path in enumerate(image_paths):
        clip = ImageClip(image_path).set_duration(duration_per_image)
        # Always resize to fill the screen (cover 1920x1080)
        clip = clip.resize(height=1080).resize(width=1920)

        animation = random.choice(animations)
        if animation == 'zoom_in':
            # Start at 100%, zoom to 110% over the duration
            clip = clip.resize(lambda t: 1 + 0.1 * (t / duration_per_image))
        elif animation == 'pan_left':
            clip = clip.set_position(lambda t: (max(0, 100 - 20 * t), 'center'))
        elif animation == 'pan_right':
            clip = clip.set_position(lambda t: (min(0, -100 + 20 * t), 'center'))
        else:
            clip = clip.set_position(('center', 'center'))
        video_clips.append(clip)

    final_video = concatenate_videoclips(video_clips, method="compose")

    # Create text clips for each word
    text_clips = []
    for word_info in word_timestamps:
        word = word_info["word"]
        start_time = word_info["start"]
        end_time = word_info["end"]
        
        txt_clip = TextClip(word, fontsize=50, color='white', font='assets/fonts/FredokaOne-Regular.ttf', stroke_color='black', stroke_width=3)
        txt_clip = txt_clip.set_position('center').set_start(start_time).set_end(end_time)
        text_clips.append(txt_clip)

    final_clip = CompositeVideoClip([final_video] + text_clips)
    final_clip = final_clip.set_audio(audio_clip)
    
    output_path = "output/generatedVideo/short_video.mp4"
    final_clip.write_videofile(output_path, fps=24)
    
    return output_path

async def main():
    """
    Main function to generate the short video.
    """
    content = await generate_content_task()
    audio_path = generate_audio_task(content)
    image_paths = await generate_images_task(content)
    video_path = combine_assets_to_video_task(content, audio_path, image_paths)
    
    if video_path:
        print(f"Video generated successfully: {video_path}")
    else:
        print("Failed to generate video.")

if __name__ == "__main__":
    asyncio.run(main())