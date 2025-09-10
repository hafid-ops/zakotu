import asyncio
import os
import pytest
from src.thumbnail_generator import generate_image_from_text

@pytest.mark.asyncio
async def test_generate_x_thumbnail():
    """
    Tests the generation of an X (Twitter) thumbnail.
    """
    output_path = "output/generatedThumbnail/test_x_thumbnail.png"
    text_content = "This is a test tweet for X! #testing"
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    await generate_image_from_text(
        text_content=text_content,
        output_path=output_path,
        platform="x",
        username="TestUserX",
        handle="@TestHandleX",
        time_ago="10m",
        likes="1.2K 😔",
        comments="100",
        shares="50"
    )
    
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0
    os.remove(output_path) # Clean up the generated file

@pytest.mark.asyncio
async def test_generate_facebook_thumbnail():
    """
    Tests the generation of a Facebook thumbnail.
    """
    output_path = "output/generatedThumbnail/test_fb_thumbnail.png"
    text_content = "This is a test post for Facebook! 😊"
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    await generate_image_from_text(
        text_content=text_content,
        output_path=output_path,
        platform="facebook",
        username="TestUserFB",
        time_ago="2h",
        likes="5.5K",
        comments="250",
        shares="120"
    )
    
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0
    os.remove(output_path) # Clean up the generated file

@pytest.mark.asyncio
async def test_generate_random_thumbnail():
    """
    Tests the generation of a random platform thumbnail.
    """
    output_path = "output/generatedThumbnail/test_random_thumbnail.png"
    text_content = "This is a random test post!"
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    await generate_image_from_text(
        text_content=text_content,
        output_path=output_path
    )
    
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0
    os.remove(output_path) # Clean up the generated file