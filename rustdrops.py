import requests
from bs4 import BeautifulSoup
import time
import hashlib

WEBHOOK_URL = "https://discord.com/api/webhooks/1387427218539544586/H18wbRAwYU_D_96cP235Knk6eGIJqG0bjtBKNAyJy4PVr2t9RyWcJjFZpSmfQ3eim8ml"

TARGET_URL = "https://twitch.facepunch.com/"

CHECK_EVERY = 3600 

# last known version of the page here
last_drop_hash = None

# 👀 Function to check the site and pull drop info
def check_for_drops():
    # Get the page
    response = requests.get(TARGET_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Try to find the drop image
    image_tag = soup.find('img', class_='promotion-image')
    image_url = image_tag['src'] if image_tag else None

    # Try to find the date text (e.g. "25 June 2025 until 3 July 2025")
    date_tag = soup.find('div', class_='promotion-dates')
    date_text = date_tag.get_text(strip=True) if date_tag else "❓ Date info not found"

    # Grab the whole section where the drop info is shown
    drop_section = soup.find('section', class_='promotion') or soup

    # Hash the section to detect changes
    drop_hash = hashlib.md5(str(drop_section).encode('utf-8')).hexdigest()

    return image_url, date_text, drop_hash

#send a Discord message
def send_alert_to_discord(image_url, date_text):
    message = {
        "content": "@everyone New Twitch drops just went live! 👀🎁",
        "embeds": [
            {
                "title": "🚨 New Facepunch Twitch Drop!",
                "description": f"🗓️ **Dates:** {date_text}\n👉 [Claim it here]({TARGET_URL})",
                "image": {"url": image_url} if image_url else {},
                "color": 0x00aaff
            }
        ]
    }

    response = requests.post(WEBHOOK_URL, json=message)

    if response.status_code == 204:
        print("✅ Alert sent to Discord!")
    else:
        print(f"❌ Failed to send alert. Error: {response.text}")

# 🔁 Main loop to keep checking
print("🔄 Starting Twitch Drop Monitor...")

while True:
    try:
        # Grab the current drop info
        image_url, date_text, current_hash = check_for_drops()

        # If we’ve seen a previous version and it’s changed, send an alert
        if last_drop_hash and current_hash != last_drop_hash:
            print("🎉 New drop detected!")
            send_alert_to_discord(image_url, date_text)
        else:
            print("🔍 No changes yet...")

        # Update the saved hash
        last_drop_hash = current_hash

    except Exception as error:
        print(f"⚠️ Oops! Something went wrong: {error}")

    # Wait a bit before checking again
    time.sleep(CHECK_EVERY)