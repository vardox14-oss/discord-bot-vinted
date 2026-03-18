import time
import random
from scraper import VintedScraper, filter_items
from webhook import send_vinted_embed, send_startup_message
from config import KEYWORDS, MAX_PRICE, TARGET_SIZES, BON_PLAN_THRESHOLD, VINTED_PARAMS, INTERVAL

def main():
    print("--- [DÉMARRAGE DU BOT VINTED NIKE] ---")
    print(f"Keywords: {', '.join(KEYWORDS)}")
    print(f"Max Price: {MAX_PRICE}€ | Sizes: {', '.join(TARGET_SIZES)}")
    
    scraper = VintedScraper()
    seen_items = set()
    
    # Envoi du message de démarrage
    send_startup_message()
    
    print("[*] Initialisation de la mémoire (1er passage)...")
    for kw in KEYWORDS:
        params = VINTED_PARAMS.copy()
        params["search_text"] = kw
        items = scraper.search(params)
        for item in items:
            seen_items.add(item.get("id"))
    
    print(f"[*] Mémoire initialisée avec {len(seen_items)} articles. Lancement du monitoring...")

    while True:
        try:
            for kw in KEYWORDS:
                params = VINTED_PARAMS.copy()
                params["search_text"] = kw
                
                raw_items = scraper.search(params)
                filtered = filter_items(raw_items, [kw], MAX_PRICE, TARGET_SIZES)
                
                for item in filtered:
                    item_id = item.get("id", None)
                    
                    if item_id and item_id not in seen_items:
                        seen_items.add(item_id)
                        
                        item_details = scraper.get_item_details(item_id)
                        full_item = {**item, **item_details}
                        
                        raw_price = full_item.get("total_item_price")
                        if raw_price is None:
                            raw_price = full_item.get("price", 0)
                        try:
                            price = float(raw_price)
                        except (ValueError, TypeError):
                            price = 0.0

                        is_bon_plan = price < BON_PLAN_THRESHOLD
                        
                        item_title = full_item.get("title") or "N/A"
                        print(f"[!] NOUVEAU RUNNING DÉTECTÉ: {item_title} - {price}€")
                        send_vinted_embed(full_item, is_bon_plan=is_bon_plan)
                
                time.sleep(random.uniform(1, 2))

            time.sleep(INTERVAL)
            
        except KeyboardInterrupt:
            print("\n[!] Bot arrêté par l'utilisateur.")
            break
        except Exception as e:
            print(f"[!] Erreur critique dans la boucle principale: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
