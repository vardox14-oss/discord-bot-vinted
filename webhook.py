import requests
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_vinted_embed(item, is_bon_plan=False):
    if not DISCORD_WEBHOOK_URL:
        print("[!] DISCORD_WEBHOOK_URL non configuré dans .env")
        return

    title = item.get("title", "Sans titre")
    price = item.get("total_item_price") or item.get("price", "N/A")
    size = item.get("size_title") or item.get("size", "N/A")
    brand = item.get("brand_title", "Inconnue")
    condition = item.get("status", "N/A")
    description = item.get("description", "Pas de description")
    currency = item.get("total_item_price_currency") or item.get("currency", "€")
    url = f"https://www.vinted.fr{item.get('path')}" if item.get('path') else item.get('url', '#')
    photo = ""
    if item.get("photo"):
        photo = item.get("photo", {}).get("url", "")
    elif item.get("photos"):
        photo = item.get("photos")[0].get("url", "")
    if len(description) > 300:
        description = description[:297] + "..."
    bon_plan_tag = "🔥 BON PLAN | " if is_bon_plan else ""
    color = 0xFF4500 if is_bon_plan else 0x01D758

    embed = {
        "title": f"{bon_plan_tag}{title}",
        "url": url,
        "description": f"*{description}*",
        "color": color,
        "fields": [
            {"name": "💰 Prix", "value": f"**{price} {currency}**", "inline": True},
            {"name": "📏 Taille", "value": size, "inline": True},
            {"name": "🏷️ Marque", "value": brand, "inline": True},
            {"name": "✨ État", "value": condition, "inline": True},
        ],
        "image": {"url": photo},
        "footer": {
            "text": "Bot Vinted Nike • Détection Instantanée",
            "icon_url": "https://www.vinted.fr/favicon.ico"
        }
    }

    payload = {
        "content": "🔔 **Nouvel article Nike détecté !**" if not is_bon_plan else "🔥 **OFFRE EXCEPTIONNELLE !**",
        "embeds": [embed]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code != 204:
            print(f"[!] Erreur Webhook: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[!] Erreur lors de l'envoi du Webhook: {e}")
