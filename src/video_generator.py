import os
import random
import ffmpeg  # Import ffmpeg-python
import base64 # Import base64 for font embedding
import math # Import math for ceiling division
import time # Import time for sleep
from moviepy.config import change_settings
import pysbd
import numpy as np
import soundfile as sf
import subprocess
import sys
from voice_generator import extract_story_text, generate_and_measure_audio, kokoro, available_voices
from thumbnail_generator import generate_image_from_text

def detect_gpu_support():
    """
    Detect if GPU acceleration is available for video encoding.
    Returns (has_gpu, gpu_count, encoder_available)
    """
    has_gpu = False
    gpu_count = 0
    encoder_available = False
    
    try:
        # Check for NVIDIA GPU using nvidia-smi
        result = subprocess.run(['nvidia-smi', '--query-gpu=count', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            gpu_count = int(result.stdout.strip())
            has_gpu = gpu_count > 0
            print(f"Detected {gpu_count} NVIDIA GPU(s)")
        else:
            print("No NVIDIA GPU detected (nvidia-smi not available or failed)")
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, ValueError):
        print("GPU detection failed - nvidia-smi not available or error occurred")
    
    if has_gpu:
        try:
            # Test if h264_nvenc encoder is available
            result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and 'h264_nvenc' in result.stdout:
                encoder_available = True
                print("h264_nvenc encoder is available")
            else:
                print("h264_nvenc encoder not available in FFmpeg")
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            print("Could not check FFmpeg encoders")
    
    if has_gpu and encoder_available:
        try:
            # Test encoding a small sample to verify GPU functionality
            test_cmd = [
                'ffmpeg', '-hide_banner', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1',
                '-c:v', 'h264_nvenc', '-t', '1', '-f', 'null', '-'
            ]
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                print("GPU encoding test successful")
                return True, gpu_count, True
            else:
                print(f"GPU encoding test failed: {result.stderr}")
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            print("GPU encoding test failed due to timeout or error")
    
    print("Falling back to CPU encoding")
    return False, gpu_count, False

# -------------------------------
# 1) Fix ImageMagick path for cross-platform compatibility
# -------------------------------
def setup_imagemagick():
    """Setup ImageMagick binary path based on environment"""
    import platform
    import subprocess
    
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
    
    # Try common Linux paths
    linux_paths = ["/usr/bin/convert", "/usr/local/bin/convert", "convert"]
    for path in linux_paths:
        try:
            result = subprocess.run([path, '-version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                change_settings({"IMAGEMAGICK_BINARY": path})
                print(f"Using Linux ImageMagick: {path}")
                return
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    # Try Windows paths as fallback
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

# Setup ImageMagick for cross-platform compatibility
setup_imagemagick()
import textwrap

def wrap_text(text: str, font_path: str, font_size: int, max_width: int) -> str:
    """
    Wraps text to fit within a maximum width, given font and font size.
    This is a simplified approach and might not be perfectly accurate without
    actual font metrics, but provides a reasonable estimate.
    """
    # A rough estimate of characters per pixel. This will vary greatly by font.
    # For a more accurate solution, a library like Pillow with font metrics would be needed.
    # Assuming a monospace-like character width for simplicity.
    # Average character width can be estimated as font_size * 0.6 (a common heuristic)
    avg_char_width = font_size * 0.6
    max_chars_per_line = int(max_width / avg_char_width)
    
    wrapper = textwrap.TextWrapper(width=max_chars_per_line, break_long_words=False, replace_whitespace=False)
    wrapped_lines = []
    for line in text.splitlines():
        wrapped_lines.extend(wrapper.wrap(line))
    return "\n".join(wrapped_lines)



# -------------------------------
# 2) Main video creation function
# -------------------------------
def create_video(
    story_text: str,
    intro_text: str,
    audio_path: str,
    background_music_path: str,
    background_video_paths: list,
    output_video_path: str,
    caption_font: str = "Segoe UI Emoji", # Changed to a font that supports emojis
    caption_fontsize: int = 64,
    caption_fontcolor: str = "white",
    caption_stroke_color: str = "black",
    caption_stroke_width: int = 5, # Increased for "big black outline"
    caption_background_color: str = "red", # New parameter for red background
    caption_padding: int = 10, # Default padding for the background box
    caption_position: tuple = ("center", "center"),
    music_volume: float = 0.30,
    fade_duration: float = 1.0,
    use_gpu: bool = False,
    gpu_device_id: int = 0,
):
    """
    Generates a cinematic video with:
      - intro card
      - background videos
      - background music (ducked under voice)
      - voice-over
      - dynamic captions with bold/shadow
      - outro card
    """
    temp_looped_scaled_video_paths = [] # Initialize here to be accessible in outer finally
    temp_intro_audio_path = ""
    temp_intro_video_path = ""

    try: # Outer try block for overall cleanup
        # ---------------------------
        # Intro Video Generation
        # ---------------------------
        print("Generating intro video...")
        
        # Generate audio for intro text
        intro_voice = random.choice(available_voices) # Use a random available voice for intro
        intro_audio_samples, intro_sample_rate, intro_duration = generate_and_measure_audio(intro_text, intro_voice)
        
        temp_intro_audio_path = output_video_path.replace(".mp4", "_intro_audio.wav")
        sf.write(temp_intro_audio_path, intro_audio_samples, intro_sample_rate)
        print(f"Intro audio generated and saved to {temp_intro_audio_path} with duration {intro_duration:.2f} seconds.")

        # Create intro video from image with text overlay
        # Ensure the output directory for thumbnails exists
        thumbnail_dir = "output/generatedThumbnail"
        os.makedirs(thumbnail_dir, exist_ok=True)
        generated_intro_image_path = os.path.join(thumbnail_dir, "thumbnail.png")
        
        with open("output/generatedStory/intro_and_thumb_text.txt", "r", encoding="utf-8") as f:
            intro_image_text = f.read()
        
        # Run the async function
        import asyncio
        asyncio.run(generate_image_from_text(intro_image_text, generated_intro_image_path))

        intro_image_path = generated_intro_image_path
        temp_intro_video_path = output_video_path.replace(".mp4", "_intro_video.mp4")

        # Create a black background
        black_bg = ffmpeg.input(f'color=black:s=1920x1080:d={intro_duration}', f='lavfi')

        # Scale the intro image to be smaller and overlay it on the black background
        image_input = ffmpeg.input(intro_image_path, loop=1, t=intro_duration)
        scaled_image = image_input.video.filter('scale', w='if(gte(iw,ih), min(iw, 1280), -1)', h='if(gte(iw,ih), -1, min(ih, 720))')
        
        intro_video_stream = ffmpeg.overlay(black_bg, scaled_image, x='(W-w)/2', y='(H-h)/2')

        intro_video_stream = intro_video_stream.filter('fade', type='in', start_time=0, duration=fade_duration)
        intro_video_stream = intro_video_stream.filter('fade', type='out', start_time=intro_duration - fade_duration, duration=fade_duration)
        ffmpeg.output(intro_video_stream, temp_intro_video_path, t=intro_duration, r=24, pix_fmt='yuv420p').run(overwrite_output=True, quiet=True)
        print(f"Intro video generated and saved to {temp_intro_video_path}.")

        # ---------------------------
        # Prepare audio streams for FFmpeg
        # ---------------------------
        voice_audio_input = ffmpeg.input(audio_path)
        bg_music_input = ffmpeg.input(background_music_path)

        # Get duration of voice audio
        probe = ffmpeg.probe(audio_path)
        voice_duration = 0.0
        for stream in probe['streams']:
            if stream['codec_type'] == 'audio':
                voice_duration = float(stream['duration'])
                break
        if voice_duration == 0.0:
            raise ValueError("Could not determine audio duration from ffprobe.")
        
        # Speed up voice audio by 1.2x
        speed_factor = 0.9
        voice_duration /= speed_factor # Adjust duration for speed-up

        # Loop/trim background music
        bg_music_stream = bg_music_input.audio.filter('aloop', loop=0, size=int(voice_duration * 44100)).filter('atrim', duration=voice_duration)
        bg_music_stream = (
            bg_music_stream
            .filter('volume', f'{music_volume}')
            .filter('afade', t='in', st=0, d=fade_duration)
            .filter('afade', t='out', st=voice_duration - fade_duration, d=fade_duration)
        )

        # Voice audio with speed-up and fade
        voice_audio_stream = (
            voice_audio_input.audio
            .filter('atempo', speed_factor) # Speed up by 1.4x
            .filter('volume', '1.0')
        )

        # Mix audio
        # Concatenate intro audio with main audio
        intro_audio_input = ffmpeg.input(temp_intro_audio_path)
        # Create a 1-second silent audio stream for the pause
        silence_duration = 1.0
        silent_audio = ffmpeg.input(f'anullsrc=cl=stereo:r={intro_sample_rate}', f='lavfi').audio.filter('atrim', duration=silence_duration)

        # Loop/trim background music for intro
        intro_bg_music_stream = bg_music_input.audio.filter('aloop', loop=0, size=int(intro_duration * 44100)).filter('atrim', duration=intro_duration)
        intro_bg_music_stream = (
            intro_bg_music_stream
            .filter('volume', f'{music_volume}')
            .filter('afade', t='in', st=0, d=fade_duration)
            .filter('afade', t='out', st=intro_duration - fade_duration, d=fade_duration)
        )

        # Mix intro audio with intro background music
        mixed_intro_audio = ffmpeg.filter([intro_audio_input.audio, intro_bg_music_stream], 'amix', inputs=2, duration='longest')

        mixed_main_audio = ffmpeg.filter([voice_audio_stream, bg_music_stream], 'amix', inputs=2, duration='longest')
        mixed_audio = ffmpeg.concat(mixed_intro_audio, silent_audio, mixed_main_audio, v=0, a=1)

        # Get the actual duration of the mixed audio stream by writing to a temporary file
        temp_mixed_audio_path = output_video_path.replace(".mp4", "_mixed_audio.wav")
        try:
            ffmpeg.output(mixed_audio, temp_mixed_audio_path, format='wav').run(overwrite_output=True, quiet=True)
            probe_mixed_audio = ffmpeg.probe(temp_mixed_audio_path)
            mixed_audio_duration = 0.0
            for stream in probe_mixed_audio['streams']:
                if stream['codec_type'] == 'audio':
                    mixed_audio_duration = float(stream['duration'])
                    break
            if mixed_audio_duration == 0.0:
                raise ValueError("Could not determine mixed audio duration from ffprobe.")
        finally:
            if os.path.exists(temp_mixed_audio_path):
                os.remove(temp_mixed_audio_path)
                print(f"Cleaned up temporary mixed audio file: {temp_mixed_audio_path}")

        # ---------------------------
        # Prepare background videos
        # ---------------------------
        # Ensure the output directory for temporary files exists
        temp_dir = os.path.dirname(os.path.abspath(output_video_path))
        os.makedirs(temp_dir, exist_ok=True)

        for i, video_path in enumerate(background_video_paths):
            probe_video = ffmpeg.probe(video_path)
            video_stream_info = next((s for s in probe_video['streams'] if s['codec_type'] == 'video'), None)
            if video_stream_info is None:
                raise ValueError(f"Could not find video stream in {video_path}")
            
            # Use stream_loop=-1 to loop each video indefinitely at the input level
            input_stream = ffmpeg.input(video_path, stream_loop=-1)
            # Apply scale and setsar filters
            scaled_video_stream = input_stream.video.filter('scale', 1920, 1080).filter('setsar', '1/1')
            
            # Apply fade-in/fade-out to individual video segments
            # The 'start_time' for fade out should be relative to the duration of the individual video segment.
            # We need to get the duration of the input_stream before applying fade.
            # This requires probing each video individually before the loop, or passing duration.
            # For now, let's assume a fixed duration for fade out relative to the segment's duration.
            # The error "Unable to parse option value "duration-1.0" as duration" means 'duration-1.0' is not a valid expression for start_time.
            # We need to calculate the exact start time for the fade out.
            # Let's get the duration of the current video segment.
            video_duration_probe = ffmpeg.probe(video_path)
            current_video_duration = float(next((s for s in video_duration_probe['streams'] if s['codec_type'] == 'video'), None)['duration'])

            scaled_video_stream = scaled_video_stream.filter('fade', type='in', start_time=0, duration=fade_duration)
            scaled_video_stream = scaled_video_stream.filter('fade', type='out', start_time=current_video_duration - fade_duration, duration=fade_duration)

            # Output each processed stream to a temporary file
            # Ensure consistent forward slashes for the path
            temp_output_path = os.path.abspath(output_video_path.replace(".mp4", f"_looped_scaled_video_{i}.mp4")).replace('\\', '/')
            print(f"Attempting to create temporary video file: {temp_output_path}")
            try:
                # Use a reasonable duration for the temporary file, and capture all output
                temp_file_duration = min(60, mixed_audio_duration + 5)
                temp_stdout, temp_stderr = ffmpeg.output(scaled_video_stream, temp_output_path, format='mp4', t=temp_file_duration).run(
                    overwrite_output=True, quiet=False, capture_stdout=True, capture_stderr=True
                )
                print(f"FFmpeg stdout during temp file creation for {temp_output_path}:\n{temp_stdout.decode('utf8')}")
                print(f"FFmpeg stderr during temp file creation for {temp_output_path}:\n{temp_stderr.decode('utf8')}")
                
                # Wait a moment for file system operations to complete
                import time
                time.sleep(0.5)
                
                # Verify file creation and size with retry logic
                max_retries = 5
                for retry in range(max_retries):
                    if os.path.exists(temp_output_path):
                        break
                    print(f"Retry {retry + 1}/{max_retries}: Waiting for temp file to appear...")
                    time.sleep(1)
                else:
                    print(f"File system error during temporary video file creation: Temporary video file was not created: {temp_output_path}")
                    raise FileNotFoundError(f"Temporary video file was not created: {temp_output_path}")
                
                if os.path.getsize(temp_output_path) == 0:
                    raise ValueError(f"Temporary video file was created but is empty: {temp_output_path}")
                
                # Verify with ffprobe that it's a valid video file
                try:
                    ffmpeg.probe(temp_output_path)
                except ffmpeg.Error as e:
                    raise ValueError(f"Temporary video file {temp_output_path} is not a valid video file (ffprobe failed): {e.stderr.decode('utf8')}")

                temp_looped_scaled_video_paths.append(temp_output_path)
                print(f"Successfully created and verified temporary video file: {temp_output_path}")
                time.sleep(1.0) # Increased delay to ensure file is fully written
            except ffmpeg.Error as e:
                print(f"FFmpeg Error creating temporary video file {temp_output_path}: {e.stderr.decode('utf8')}")
                print(f"FFmpeg stdout during temp file creation: {e.stdout.decode('utf8')}")
                raise # Re-raise to stop execution if a temp file fails
            except (FileNotFoundError, ValueError) as e:
                print(f"File system error during temporary video file creation: {e}")
                raise # Re-raise other file system errors

        print("All temporary looped/scaled video files prepared. Proceeding to final concatenation.")
        # Now, create new input streams from these temporary files for concatenation
        final_concat_inputs = [ffmpeg.input(temp_intro_video_path)] # Start with the intro video
        for temp_path in temp_looped_scaled_video_paths:
            # The existence and validity checks are already done above, but keeping it here for robustness
            if not os.path.exists(temp_path):
                raise FileNotFoundError(f"Temporary video file not found during concatenation setup: {temp_path}")
            final_concat_inputs.append(ffmpeg.input(temp_path)) # Use raw input, concat will handle streams

        # Concatenate the temporary video files
        # Always concatenate, even if only one video (the intro)
        video_stream = ffmpeg.concat(*final_concat_inputs, v=1, a=0)

        # ---------------------------
        # Apply cinematic grading
        # ---------------------------
        video_stream = video_stream.filter('eq', brightness=0.0, contrast=1.1, saturation=1.1, gamma=1.0)

        # # ---------------------------
        # # Semi-transparent grey overlay (10% opacity)
        # # ---------------------------
        # grey_overlay = (
        #     ffmpeg.input(f'color=gray@0.1:s=1920x1080:d={voice_duration}', f='lavfi')
        #     .filter('format', 'yuva420p')  # apply pixel format after input
        # )


        # video_stream = ffmpeg.overlay(
        #     video_stream,
        #     grey_overlay,
        #     format='auto'
        # )


        # Trim video to mixed audio duration
        video_stream = video_stream.trim(end=mixed_audio_duration).setpts('PTS-STARTPTS')

        # ---------------------------
        # Dynamic captions
        # ---------------------------
        from transcriber import get_word_timestamps
        word_timestamps = get_word_timestamps(audio_path)

        # Generate ASS file for captions
        ass_path = output_video_path.replace(".mp4", ".ass")
        if word_timestamps:
            # Read font data to embed
            try:
                # No need to embed font if using a system font like Segoe UI Emoji
                font_base64 = ""
                font_filename = caption_font
            except FileNotFoundError:
                print(f"Warning: Font file not found at {caption_font}. Captions might not display correctly.")
                font_base64 = ""
                font_filename = ""

            # ASS header and style definition
            ass_content = f"""[Script Info]
; Script generated by FFmpeg
PlayResX: 1920
PlayResY: 1080
Timer: 100.0000
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
 
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{caption_font},{caption_fontsize},&H00FFFFFF,&H0000FFFF,&H00000000,&H000000FF,-1,0,0,0,100,100,0,0,1,{caption_stroke_width},0,5,0,0,0,1
 
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
            # Append caption events
            for i, word_info in enumerate(word_timestamps):
                start_time = (word_info["start"] / speed_factor) + intro_duration + silence_duration
                end_time = (word_info["end"] / speed_factor) + intro_duration + silence_duration
                word = word_info["word"]

                # Format time for ASS: H:MM:SS.cc (centiseconds)
                start_ass = f"{int(start_time // 3600)}:{int((start_time % 3600) // 60):02}:{int(start_time % 60):02}.{int((start_time * 100) % 100):02}"
                end_ass = f"{int(end_time // 3600)}:{int((end_time % 3600) // 60):02}:{int(end_time % 60):02}.{int((end_time * 100) % 100):02}"

                # For middle-center, Alignment=5 is set in the style.
                ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{word}\n"

            # Embed font if data is available
            if font_base64:
                ass_content += f"\n[Fonts]\nfontname: {font_filename}\n{font_base64}\n"

            with open(ass_path, "w", encoding="utf-8") as f:
                f.write(ass_content)
            
            # Use subtitles filter with the generated ASS file
            video_stream = video_stream.filter(
                'subtitles',
                filename=ass_path
            )
        else:
            print("No word timestamps found for captions.")

        # ---------------------------
        # Output arguments with GPU fallback
        # ---------------------------
        # Always try to detect GPU first, regardless of use_gpu parameter
        gpu_available, gpu_count, encoder_available = detect_gpu_support()
        
        # Override use_gpu based on actual GPU availability
        if use_gpu and not gpu_available:
            print("GPU was requested but not available. Falling back to CPU encoding.")
            use_gpu = False
        elif not use_gpu and gpu_available:
            print("GPU is available but not requested. Using CPU encoding as requested.")
        
        output_args = {
            'c:v': 'h264_nvenc' if use_gpu and gpu_available else 'libx264',
            'preset': 'fast',
            'pix_fmt': 'yuv420p',
            'c:a': 'aac',
            'b:a': '192k',
            'threads': 6,
        }

        if use_gpu and gpu_available:
            output_args['gpu'] = str(gpu_device_id)
            print(f"Using GPU {gpu_device_id} for video encoding with h264_nvenc.")
        else:
            print("Using CPU for video encoding with libx264.")

        # ---------------------------
        # Final output with error handling and fallback
        # ---------------------------
        final_output = ffmpeg.output(
            video_stream,
            mixed_audio,
            output_video_path,
            **output_args
        )

        print(f"FFmpeg command: {ffmpeg.compile(final_output)}")

        try:
            stdout, stderr = ffmpeg.run(final_output, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            print(f"Video generated and saved to {output_video_path}")
            print("\n--- FFmpeg stdout ---")
            print(stdout.decode('utf8'))
            print("--- End FFmpeg stdout ---\n")
        except ffmpeg.Error as e:
            # If GPU encoding failed, try CPU fallback
            if use_gpu and gpu_available and ('h264_nvenc' in str(e.stderr) or 'nvenc' in str(e.stderr) or 'libcuda' in str(e.stderr)):
                print("GPU encoding failed, attempting CPU fallback...")
                print(f"GPU Error: {e.stderr.decode('utf8')}")
                
                # Retry with CPU encoding
                cpu_output_args = output_args.copy()
                cpu_output_args['c:v'] = 'libx264'
                if 'gpu' in cpu_output_args:
                    del cpu_output_args['gpu']
                
                final_output_cpu = ffmpeg.output(
                    video_stream,
                    mixed_audio,
                    output_video_path,
                    **cpu_output_args
                )
                
                print("Retrying with CPU encoding...")
                print(f"CPU FFmpeg command: {ffmpeg.compile(final_output_cpu)}")
                
                try:
                    stdout, stderr = ffmpeg.run(final_output_cpu, overwrite_output=True, capture_stdout=True, capture_stderr=True)
                    print(f"Video generated and saved to {output_video_path} (using CPU fallback)")
                    print("\n--- FFmpeg stdout (CPU) ---")
                    print(stdout.decode('utf8'))
                    print("--- End FFmpeg stdout (CPU) ---\n")
                except ffmpeg.Error as cpu_e:
                    print(f"CPU encoding also failed: {cpu_e.stderr.decode('utf8')}")
                    print("\n--- FFmpeg stdout (CPU) ---")
                    print(cpu_e.stdout.decode('utf8'))
                    print("--- End FFmpeg stdout (CPU) ---\n")
                    print("\n--- FFmpeg stderr (CPU) ---")
                    print(cpu_e.stderr.decode('utf8'))
                    print("--- End FFmpeg stderr (CPU) ---\n")
                    raise cpu_e
            else:
                print(f"FFmpeg Error: {e.stderr.decode('utf8')}")
                print("\n--- FFmpeg stdout ---")
                print(e.stdout.decode('utf8'))
                print("--- End FFmpeg stdout ---\n")
                print("\n--- FFmpeg stderr ---")
                print(e.stderr.decode('utf8'))
                print("--- End FFmpeg stderr ---\n")
                raise
        finally:
            if os.path.exists(ass_path):
                os.remove(ass_path)
                print(f"Cleaned up temporary ASS file: {ass_path}")

    finally: # Outer finally block for cleaning up all temporary video files
        for temp_path in temp_looped_scaled_video_paths:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"Cleaned up temporary looped/scaled video file: {temp_path}")
        if os.path.exists(temp_intro_audio_path):
            os.remove(temp_intro_audio_path)
            print(f"Cleaned up temporary intro audio file: {temp_intro_audio_path}")
        if os.path.exists(temp_intro_video_path):
            os.remove(temp_intro_video_path)
            print(f"Cleaned up temporary intro video file: {temp_intro_video_path}")
