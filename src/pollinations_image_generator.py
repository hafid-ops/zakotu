import os
import re
import requests
import pysbd
from PIL import Image
from io import BytesIO
import urllib.parse
import time

def clean_filename(text):
    """Sanitizes text to be a valid filename."""
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    return text[:100]

def generate_pollinations_image(prompt, output_path, retries=3, delay=10):
    """
    Generates an image using Pollinations AI and saves it.
    """
    print(f"Generating image for prompt: '{prompt}' ...")
    
    # URL-encode the prompt and add some style modifiers for better results
    encoded_prompt = urllib.parse.quote(prompt)
    # Construct the Pollinations URL, request 1920x1080, and remove logo
    url = f"https://pollinations.ai/p/{encoded_prompt}?model=dall-e-3&width=1920&height=1080&nologo=true"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/png,image/jpeg;q=0.9,*/*;q=0.8'
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=300) # Long timeout for image generation
            response.raise_for_status()  # Raise an exception for bad status codes
            
            if 'image' in response.headers.get('Content-Type', ''):
                try:
                    image_data = BytesIO(response.content)
                    image = Image.open(image_data)
                    image.save(output_path)
                    print(f"Image saved to {output_path}")
                    return output_path
                except Image.UnidentifiedImageError:
                    print("Error: The response was not a valid image file. The server may be overloaded or the prompt was rejected.")
                    return None
            else:
                print(f"Warning: Response from Pollinations was not an image. Content-Type: {response.headers.get('Content-Type')}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error generating image: {e}. Attempt {attempt + 1} of {retries}.")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to generate image after multiple retries.")
                return None

def main():
    output_dir = "output/generatedImage"
    os.makedirs(output_dir, exist_ok=True)

    while True:
        prompt = input("Enter a prompt to generate an image (or 'exit' to quit): ")
        if prompt.lower() == 'exit':
            break
        
        if prompt.strip():
            filename = f"generated_{clean_filename(prompt)}.png"
            output_path = os.path.join(output_dir, filename)
            generate_pollinations_image(prompt, output_path)

    print("--- Image generation session ended. ---")

if __name__ == "__main__":
    main()
