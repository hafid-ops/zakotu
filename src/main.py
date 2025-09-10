import os
import random
import ffmpeg
from dotenv import load_dotenv
from story_generator import generate_story, generate_intro_text
from voice_generator import generate_voice
from video_generator import create_video
from utils.logger_config import logger
from utils.telegram_notifier import notify

load_dotenv()

def get_media_duration(file_path: str) -> float:
    """
    Gets the duration of an audio or video file using ffprobe.
    """
    try:
        probe = ffmpeg.probe(file_path)
        for stream in probe['streams']:
            if stream['codec_type'] in ['audio', 'video']:
                return float(stream['duration'])
        return 0.0
    except ffmpeg.Error as e:
        print(f"Error probing file {file_path}: {e.stderr.decode('utf8')}")
        logger.error(f"Error probing file {file_path}: {e.stderr.decode('utf8')}")
        return 0.0

def main():
    """
    Main function to generate a story, convert it to speech, and then create a video.
    """
    notify("Bot Status", "Started", "The video generation process has kicked off.")
    # Ensure GEMINI_API_KEY is set
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set it before running the script.")
        logger.error("GEMINI_API_KEY environment variable not set.")
        return

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir) # Go up one level from 'src' to the project root
    prompt_file_path = os.path.join(project_root, "config", "prompt.txt")
    if not os.path.exists(prompt_file_path):
        print(f"Error: Prompt file '{prompt_file_path}' not found.")
        print("Please create a file named 'prompt' with your story prompt.")
        logger.error(f"Prompt file '{prompt_file_path}' not found.")
        return
    
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        user_prompt = f.read().strip()

    if not user_prompt:
        print("Error: Prompt file is empty. Please provide a prompt in the 'prompt' file.")
        logger.error("Prompt file is empty. Please provide a prompt in the 'prompt' file.")
        notify("Story Generation", "Failed", "The prompt file is empty.")
        return

    print("\nGenerating story...")
    logger.info("Generating story...")
    story = generate_story(user_prompt)
    print("\nGenerated Story:")
    print(story)
    logger.info("Generated Story:\n" + story)

    # Generate intro text based on the story
    intro_text = generate_intro_text(story)
    print(f"\nGenerated Intro Text: {intro_text}")
    logger.info(f"Generated Intro Text: {intro_text}")
    notify("Content Generation", "Completed", f"The content has been successfully generated. contant ==> {intro_text}")

    # Save intro text to a dedicated file
    intro_text_path = os.path.join(project_root, "output", "generatedStory", "intro_and_thumb_text.txt")
    with open(intro_text_path, "w", encoding="utf-8") as f:
        f.write(intro_text)
    print(f"Intro text saved to {intro_text_path}")
    logger.info(f"Intro text saved to {intro_text_path}")

    # Generate Voice
    audio_output_dir = "output/generatedVoice"
    os.makedirs(audio_output_dir, exist_ok=True)
    output_audio_file = os.path.join(audio_output_dir, "generated_story.wav")
    output_text_file = os.path.join(audio_output_dir, "generated_story.txt")
    print(f"\nGenerating voice for the story and saving to {output_audio_file}...")
    logger.info(f"Generating voice for the story and saving to {output_audio_file}...")
    notify("Audio Generation", "Started", "Generating audio using Kokoro TTS.")
    # Remove intro_text from the main story before generating voice for the main content
    # This assumes intro_text is a direct prefix of story.
    if story.startswith(intro_text):
        main_story_content = story[len(intro_text):].strip()
        if not main_story_content: # Ensure main_story_content is not empty
            print("Warning: Main story content became empty after removing intro. Using full story for voice generation.")
            logger.warning("Main story content became empty after removing intro. Using full story for voice generation.")
            main_story_content = story
    else:
        print("Warning: Intro text not found at the beginning of the main story. Proceeding with full story for voice generation.")
        logger.warning("Intro text not found at the beginning of the main story. Proceeding with full story for voice generation.")
        main_story_content = story

    generate_voice(main_story_content, output_audio_file, output_text_path=output_text_file)
    print("\nVoice generation completed.")
    logger.info("Voice generation completed.")
    notify("Audio Generation", "Completed", f"Audio saved to {output_audio_file}")

    # Get actual voice duration (after potential speed-up in video_generator)
    # We need the original duration to select enough background videos
    original_voice_duration = get_media_duration(output_audio_file)
    if original_voice_duration == 0.0:
        print("Could not determine original voice duration. Exiting.")
        logger.error("Could not determine original voice duration. Exiting.")
        return
    
    # Assuming speed_factor is 1.6 as previously set in video_generator.py
    speed_factor = 1.6
    effective_voice_duration = original_voice_duration / speed_factor

    # Generate Video
    video_output_dir = "output/generatedVideo"
    os.makedirs(video_output_dir, exist_ok=True)
    output_video_file = os.path.join(video_output_dir, "final_story_video.mp4")
    
    # Random selection for background music
    background_music_dir = os.path.join(project_root, "assets", "stock", "music")
    music_files = [f for f in os.listdir(background_music_dir) if os.path.isfile(os.path.join(background_music_dir, f))]
    if not music_files:
        print(f"No background music files found in {background_music_dir}. Exiting.")
        logger.error(f"No background music files found in {background_music_dir}. Exiting.")
        return
    background_music_path = os.path.join(background_music_dir, random.choice(music_files))
    print(f"\nRandomly selected background music: {background_music_path}")
    logger.info(f"Randomly selected background music: {background_music_path}")

    # Random selection for background videos based on voice duration
    background_videos_dir = os.path.join(project_root, "assets", "stock", "videos")
    all_video_files = [f for f in os.listdir(background_videos_dir) if os.path.isfile(os.path.join(background_videos_dir, f))]
    if not all_video_files:
        print(f"No background video files found in {background_videos_dir}. Exiting.")
        logger.error(f"No background video files found in {background_videos_dir}. Exiting.")
        return

    random.shuffle(all_video_files) # Shuffle to get a random order
    background_video_paths = []
    current_video_duration = 0.0

    for video_file in all_video_files:
        video_path = os.path.join(background_videos_dir, video_file)
        duration = get_media_duration(video_path)
        if duration > 0:
            background_video_paths.append(video_path)
            current_video_duration += duration
            if current_video_duration >= effective_voice_duration:
                break
    
    if not background_video_paths:
        print("Could not select enough background videos to match voice duration. Exiting.")
        logger.error("Could not select enough background videos to match voice duration. Exiting.")
        return

    print(f"Selected {len(background_video_paths)} background videos with total duration {current_video_duration:.2f}s to cover voice duration {effective_voice_duration:.2f}s.")
    logger.info(f"Selected {len(background_video_paths)} background videos with total duration {current_video_duration:.2f}s to cover voice duration {effective_voice_duration:.2f}s.")

    # Import GPU detection function
    from video_generator import detect_gpu_support
    
    # Detect GPU availability and encoder support
    gpu_available, gpu_count, encoder_available = detect_gpu_support()
    
    # Use GPU if available and encoder is working
    use_gpu = gpu_available and encoder_available
    gpu_device_id = 0 # Default to GPU 0
    
    if use_gpu:
        print(f"GPU acceleration enabled: {gpu_count} GPU(s) detected with h264_nvenc support")
        logger.info(f"GPU acceleration enabled: {gpu_count} GPU(s) detected with h264_nvenc support")
    else:
        if gpu_available and not encoder_available:
            print("GPU detected but h264_nvenc encoder not available - using CPU encoding")
            logger.info("GPU detected but h264_nvenc encoder not available - using CPU encoding")
        elif not gpu_available:
            print("No GPU detected - using CPU encoding")
            logger.info("No GPU detected - using CPU encoding")
        else:
            print("Using CPU encoding")
            logger.info("Using CPU encoding")

    print(f"\nGenerating video and saving to {output_video_file}...")
    logger.info(f"Generating video and saving to {output_video_file}...")
    create_video(
        story_text=story,
        intro_text=intro_text,
        audio_path=output_audio_file,
        background_music_path=background_music_path,
        background_video_paths=background_video_paths,
        output_video_path=output_video_file,
        use_gpu=use_gpu,
        gpu_device_id=gpu_device_id,
    )
    print("\nProcess completed successfully!")
    logger.info("Process completed successfully!")
    notify("Video Generation", "Completed", f"The final video has been saved to {output_video_file}")

if __name__ == "__main__":
    main()
