import asyncio
from playwright.async_api import async_playwright
import os
import random

def format_number(num):
    if num >= 1_000_000:
        return f"{round(num / 1_000_000, 1)}M"
    elif num >= 1_000:
        return f"{round(num / 1_000, 1)}K"
    return str(num)

async def generate_image_from_text(
    text_content: str,
    output_path: str,
    platform: str = None,
    profile_pic_path: str = None,
    username: str = "User Name",
    handle: str = "@username",
    time_ago: str = "1h",
    likes: str = None,
    comments: str = None,
    shares: str = None
):
    """
    Generates an image with text content using Playwright to render HTML and take a screenshot.
    Randomly selects between X and Facebook templates if platform is not specified.
    """
    if platform is None:
        platform = random.choice(["x", "facebook"])

    # Generate random high numbers if not provided
    if likes is None:
        likes = format_number(random.randint(20000, 100000))
    if comments is None:
        comments = format_number(random.randint(1000, 10000))
    if shares is None:
        shares = format_number(random.randint(500, 5000))

    if platform == "x":
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>X Post</title>
            <style>
                body {{
                    margin: 0;
                    font-family: "Segoe UI", Arial, sans-serif;
                    background-color: #000000; /* Black background for X */
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }}
                .tweet-card {{
                    background-color: #000000; /* Black background for card */
                    border: 1px solid #38444d; /* Subtle border */
                    border-radius: 16px;
                    padding: 16px;
                    max-width: 580px; /* Standard tweet width */
                    color: #e7e9ea; /* Light text color */
                    font-size: 15px;
                    line-height: 20px;
                    word-wrap: break-word;
                }}
                .tweet-header {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 8px;
                }}
                .avatar {{
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    margin-right: 10px;
                    background-size: cover;
                    background-position: center;
                    background-image: url('{profile_pic_path if profile_pic_path else 'https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png'}'); /* Default or provided */
                }}
                .verified-icon {{
                    width: 18px;
                    height: 18px;
                    margin-left: 5px;
                    vertical-align: middle;
                }}
                .user-info {{
                    display: flex;
                    flex-direction: column;
                }}
                .user-name {{
                    font-weight: bold;
                    color: #e7e9ea;
                }}
                .user-handle {{
                    color: #71767b;
                }}
                .tweet-content {{
                    white-space: pre-wrap; /* Preserves whitespace and line breaks */
                    margin-bottom: 12px;
                }}
                .tweet-footer {{
                    display: flex;
                    justify-content: space-around;
                    color: #71767b;
                    font-size: 13px;
                }}
                .tweet-footer div {{
                    display: flex;
                    align-items: center;
                }}
                .tweet-footer div svg {{
                    margin-right: 5px;
                }}
                /* Basic SVG icons for demonstration */
                .icon {{
                    width: 18px;
                    height: 18px;
                    fill: #71767b;
                }}
            </style>
        </head>
        <body>
            <div class="tweet-card">
                <div class="tweet-header">
                    <div class="avatar"></div>
                    <div class="user-info">
                        <span class="user-name">{username}</span>
                        <img src="https://upload.wikimedia.org/wikipedia/commons/e/e4/Twitter_Verified_Badge.svg" alt="Verified" class="verified-icon">
                        <span class="user-handle">{handle} · {time_ago}</span>
                    </div>
                </div>
                <div class="tweet-content">{text_content}</div>
                <div class="tweet-footer">
                    <div>
                        <svg viewBox="0 0 24 24" aria-hidden="true" class="icon"><g><path d="M12 21.638c-.838-.002-1.662-.27-2.357-.795-2.106-1.57-4.22-3.14-6.32-4.72-.96-1.08-1.44-2.34-1.44-3.63 0-3.33 2.72-6.05 6.05-6.05 1.65 0 3.22.66 4.34 1.78l.66.66.66-.66c1.12-1.12 2.69-1.78 4.34-1.78 3.33 0 6.05 2.72 6.05 6.05 0 1.29-.48 2.55-1.44 3.63-2.1 1.58-4.21 3.15-6.32 4.72-.695.525-1.519.793-2.357.795z"></path></g></svg>
                        {likes} 😔
                    </div>
                    <div>
                        <svg viewBox="0 0 24 24" aria-hidden="true" class="icon"><g><path d="M1.75 1.75L16.25 1.75L22.25 8.75L16.25 15.75L1.75 15.75L1.75 1.75ZM18.25 8.75L16.25 6.75L16.25 10.75L18.25 8.75Z"></path></g></svg>
                        {comments}
                    </div>
                    <div>
                        <svg viewBox="0 0 24 24" aria-hidden="true" class="icon"><g><path d="M3.75 3.75L20.25 3.75L20.25 20.25L3.75 20.25L3.75 3.75ZM12 16.25L12 7.75L12 16.25ZM16.25 12L7.75 12L16.25 12Z"></path></g></svg>
                        {shares}
                    </div>
                    <div>
                        <svg viewBox="0 0 24 24" aria-hidden="true" class="icon"><g><path d="M12 1.75C6.34 1.75 1.75 6.34 1.75 12C1.75 17.66 6.34 22.25 12 22.25C17.66 22.25 22.25 17.66 22.25 12C22.25 6.34 17.66 1.75 12 1.75ZM12 20.75C7.19 20.75 3.25 16.81 3.25 12C3.25 7.19 7.19 3.25 12 3.25C16.81 3.25 20.75 7.19 20.75 12C20.75 16.81 16.81 20.75 12 20.75ZM12.75 11.25V7.75H11.25V11.25H7.75V12.75H11.25V16.25H12.75V12.75H16.25V11.25H12.75Z"></path></g></svg>
                        5.9K
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    elif platform == "facebook":
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Facebook Post</title>
            <style>
                body {{
                    margin: 0;
                    font-family: Helvetica, Arial, sans-serif;
                    background-color: #18191a; /* Dark background for Facebook */
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }}
                .fb-card {{
                    background-color: #242526; /* Slightly lighter dark background for card */
                    border-radius: 8px;
                    padding: 16px;
                    max-width: 500px;
                    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
                    color: #e4e6eb; /* Light text color */
                    font-size: 15px;
                    line-height: 1.33;
                    word-wrap: break-word;
                }}
                .fb-header {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 12px;
                }}
                .fb-avatar {{
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    margin-right: 10px;
                    background-size: cover;
                    background-position: center;
                    background-image: url('{profile_pic_path if profile_pic_path else 'https://www.facebook.com/images/files/emoji_v2/svg/1f600.svg'}'); /* Default or provided */
                }}
                .fb-user-info {{
                    display: flex;
                    flex-direction: column;
                }}
                .fb-user-name {{
                    font-weight: bold;
                    color: #e4e6eb;
                }}
                .fb-time {{
                    color: #b0b3b8;
                    font-size: 13px;
                }}
                .fb-content {{
                    white-space: pre-wrap; /* Preserves whitespace and line breaks */
                    margin-bottom: 12px;
                }}
                .fb-actions {{
                    display: flex;
                    justify-content: space-between; /* Changed to space-between for better distribution */
                    border-top: 1px solid #3a3b3c;
                    padding-top: 8px;
                    margin-top: 8px;
                }}
                .fb-action-button {{
                    display: flex;
                    align-items: center;
                    color: #b0b3b8;
                    font-size: 14px;
                    cursor: pointer;
                }}
                .fb-action-button svg {{
                    margin-right: 6px;
                }}
                /* Basic SVG icons for demonstration */
                .fb-icon {{
                    width: 20px;
                    height: 20px;
                    fill: #b0b3b8;
                }}
                .fb-likes-comments-shares {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 8px;
                    color: #b0b3b8;
                    font-size: 13px;
                }}
                .fb-likes-comments-shares div {{
                    display: flex;
                    align-items: center;
                }}
                .fb-likes-comments-shares .emoji {{
                    margin-right: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="fb-card">
                <div class="fb-header">
                    <div class="fb-avatar"></div>
                    <div class="fb-user-info">
                        <span class="fb-user-name">{username}</span>
                        <span class="fb-time">{time_ago} · 🌍</span>
                    </div>
                </div>
                <div class="fb-content">{text_content}</div>
                <div class="fb-likes-comments-shares">
                    <div>
                        <span class="emoji">👍</span> {likes}
                    </div>
                    <div>
                        {comments} Comments · {shares} Shares
                    </div>
                </div>
                <div class="fb-actions">
                    <div class="fb-action-button">
                        <svg viewBox="0 0 24 24" class="fb-icon"><path d="M12 2.163c3.204 0 5.917 2.735 5.917 5.917 0 3.254-2.911 5.786-5.917 8.917-3.006-3.131-5.917-5.663-5.917-8.917 0-3.182 2.713-5.917 5.917-5.917zm0 1.5c-2.39 0-4.417 1.97-4.417 4.417 0 2.39 1.97 4.417 4.417 4.417s4.417-1.97 4.417-4.417c0-2.447-2.027-4.417-4.417-4.417z"></path></g></svg>
                        Like
                    </div>
                    <div class="fb-action-button">
                        <svg viewBox="0 0 24 24" class="fb-icon"><path d="M12 2.163c3.204 0 5.917 2.735 5.917 5.917 0 3.254-2.911 5.786-5.917 8.917-3.006-3.131-5.917-5.663-5.917-8.917 0-3.182 2.713-5.917 5.917-5.917zm0 1.5c-2.39 0-4.417 1.97-4.417 4.417 0 2.39 1.97 4.417 4.417 4.417s4.417-1.97 4.417-4.417c0-2.447-2.027-4.417-4.417-4.417z"></path></g></svg>
                        Comment
                    </div>
                    <div class="fb-action-button">
                        <svg viewBox="0 0 24 24" class="fb-icon"><path d="M12 2.163c3.204 0 5.917 2.735 5.917 5.917 0 3.254-2.911 5.786-5.917 8.917-3.006-3.131-5.917-5.663-5.917-8.917 0-3.182 2.713-5.917 5.917-5.917zm0 1.5c-2.39 0-4.417 1.97-4.417 4.417 0 2.39 1.97 4.417 4.417 4.417s4.417-1.97 4.417-4.417c0-2.447-2.027-4.417-4.417-4.417z"></path></g></svg>
                        Share
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    else:
        raise ValueError(f"Unsupported platform: {platform}. Choose 'x' or 'facebook'.")

    # Create a temporary HTML file
    temp_html_path = "temp_post.html"
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_template)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 720}) # Set a reasonable viewport size
        await page.goto(f"file://{os.path.abspath(temp_html_path)}")
        
        # Wait for the content to be fully rendered
        selector = ".tweet-card" if platform == "x" else ".fb-card"
        await page.wait_for_selector(selector)

        # Get the bounding box of the element
        post_card_element = await page.query_selector(selector)
        if post_card_element:
            bounding_box = await post_card_element.bounding_box()
            if bounding_box:
                await page.screenshot(path=output_path, clip=bounding_box)
            else:
                await page.screenshot(path=output_path) # Fallback if bounding box not found
        else:
            await page.screenshot(path=output_path) # Fallback if element not found

        await browser.close()

    # Clean up the temporary HTML file
    os.remove(temp_html_path)
    print(f"Image generated and saved to: {output_path}")

if __name__ == "__main__":
    # Example usage:
    sample_text = "This is a sample post with some emojis! 😊✨\n\nIt should automatically resize based on the content length and line breaks."
    output_file_x = "output/generatedVideo/x_post_image.png"
    output_file_fb = "output/generatedVideo/fb_post_image.png"
    
    asyncio.run(generate_image_from_text(sample_text, output_file_x, platform="x"))
    asyncio.run(generate_image_from_text(sample_text, output_file_fb, platform="facebook"))
    asyncio.run(generate_image_from_text(sample_text, "output/generatedVideo/random_post_image.png")) # Random platform
