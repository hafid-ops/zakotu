import google.generativeai as genai
import os
from utils.logger_config import logger
 
# Ensure the output directory exists
OUTPUT_DIR = "output/generatedStory"
os.makedirs(OUTPUT_DIR, exist_ok=True)
 
# Configure the Gemini API key
# It's recommended to set this as an environment variable
# For example: os.environ["GEMINI_API_KEY"] = "YOUR_API_KEY"
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
 
def save_story_to_file(story_content: str, filename: str = "generated_story.txt"):
    """
   
    """
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(story_content)
    logger.info(f"Story saved to {filepath}")
 
def generate_intro_text(story_content: str) -> str:
    """
    Generate intro text for the story content.
    Falls back to simple truncation if API is unavailable.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set.")
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    
    genai.configure(api_key=api_key)
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Summarize the following content into a maximum of 20 words for an intro: {story_content}"
        response = model.generate_content(prompt)
        intro_text = response.text
        # Ensure the intro text is indeed limited to 20 words
        words = intro_text.split()
        if len(words) > 20:
            intro_text = " ".join(words[:20]) + "..."
        return intro_text
    except Exception as e:
        logger.error(f"Error generating intro text with Gemini API: {e}")
        
        # Check if it's a quota error
        if "429" in str(e) or "quota" in str(e).lower():
            logger.warning("API quota exceeded for intro text. Using fallback method.")
            # Fallback: Use first 20 words of the story as intro
            words = story_content.split()
            if len(words) <= 20:
                intro_text = story_content
            else:
                intro_text = " ".join(words[:20]) + "..."
            logger.info(f"Using fallback intro text: {intro_text}")
            return intro_text
        else:
            # For other errors, still raise the exception
            raise RuntimeError(f"Error generating intro text with Gemini API: {e}")
 
def get_fallback_stories():
    """
    Returns a list of fallback stories for when API is unavailable.
    """
    return [
        "The old teddy bear sat on the shelf, watching children play for decades. One night, it whispered 'I remember you all.' The next morning, all the children's photos were facing the wall.",
        "Sarah found a diary in her new house that documented her daily routine perfectly. The entries were dated three months into the future. The last entry simply read: 'She found the diary today.'",
        "The smart doorbell kept recording even when unplugged. Every video showed the same figure approaching the door. The timestamp was always 3:33 AM, but the figure never knocked.",
        "My grandmother's recipe called for 'a pinch of love and a dash of memories.' When I made it exactly as written, I could taste conversations from fifty years ago. Some of them were about me.",
        "The GPS kept redirecting me to an empty field despite multiple route requests. When I finally arrived, there was a 'For Sale' sign with my phone number. I had never seen this place before.",
    ]

def generate_story(prompt: str) -> str:
    """
    Generates a content using the Gemini API based on the provided prompt.
    Falls back to pre-written stories if API is unavailable.
 
    Args:
        prompt (str): The prompt to guide the content generation.
 
    Returns:
        str: The generated content.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set.")
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    
    genai.configure(api_key=api_key)
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        content = response.text
        save_story_to_file(content) # Save the story
        return content
    except Exception as e:
        logger.error(f"Error generating story with Gemini API: {e}")
        
        # Check if it's a quota error
        if "429" in str(e) or "quota" in str(e).lower():
            logger.warning("API quota exceeded. Using fallback story.")
            import random
            fallback_stories = get_fallback_stories()
            content = random.choice(fallback_stories)
            logger.info(f"Using fallback story: {content[:50]}...")
            save_story_to_file(content, "fallback_story.txt")
            return content
        else:
            # For other errors, still raise the exception
            raise RuntimeError(f"Error generating story with Gemini API: {e}")
 
 
if __name__ == "__main__":
    # Example usage
    user_prompt = input("Enter a prompt for the story: ")
    try:
        story = generate_story(user_prompt)
        logger.info("\nGenerated Story:")
        logger.info(story)
        
        intro = generate_intro_text(story)
        logger.info("\nGenerated Intro Text:")
        logger.info(intro)
 
    except ValueError as e:
        logger.error(f"Error: {e}")
    except RuntimeError as e:
        logger.error(f"Error: {e}")
