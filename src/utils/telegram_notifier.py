import requests
from utils.config_data import get_telegram_token, get_telegram_chat_id

def get_ip_info():
    """Fetches public IP and location information."""
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        response.raise_for_status()
        data = response.json()
        ip = data.get("ip", "N/A")
        city = data.get("city", "N/A")
        country = data.get("country", "N/A")
        return f"{ip} ({city}, {country})"
    except requests.exceptions.RequestException:
        return "Could not retrieve IP info"

class TelegramNotifier:
    def __init__(self):
        self.token = get_telegram_token()
        self.chat_id = get_telegram_chat_id()
        if not self.token or "YOUR_TELEGRAM_BOT_TOKEN" in self.token:
            raise ValueError("Telegram token is not configured in src/utils/config_data.py")
        if not self.chat_id or "YOUR_TELEGRAM_CHAT_ID" in self.chat_id:
            raise ValueError("Telegram chat ID is not configured in src/utils/config_data.py")

    def send_message(self, message):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error sending message to Telegram: {e}")

def notify(event: str, status: str, details: str = ""):
    """
    Sends a structured and formatted message to Telegram.
    """
    emojis = {
        "Started": "🚀",
        "Completed": "✅",
        "Failed": "❌",
        "Info": "ℹ️"
    }
    status_emoji = emojis.get(status, "⚙️")
    ip_info = get_ip_info()

    # Format the message
    message = f"*{event}*\n\n"
    message += f"{status_emoji} *Status:* {status}\n"
    if details:
        details = details.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]')
        message += f"📝 *Details:* {details}\n"
    
    message += f"📍 *Location:* {ip_info}"

    notifier = TelegramNotifier()
    notifier.send_message(message)
