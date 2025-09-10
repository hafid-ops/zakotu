import os
from src.story_generator import generate_story
from src.voice_generator import generate_audio
from src.video_generator import create_video

def run_niche(config):
    """
    Runs the kids story niche workflow.
    """
    story_prompt = config['prompt_template']
    story = generate_story(story_prompt)
    
    voice_style = config['voice_style']
    audio_path = os.path.join(config['output_dir'], "audio.wav")
    generate_audio(story, voice_style, audio_path)
    
    visual_strategy = config['visual_strategy']
    video_path = os.path.join(config['output_dir'], "video.mp4")
    create_video(story, audio_path, visual_strategy, video_path)