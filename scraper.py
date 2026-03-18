import requests
import time
import random
from fake_useragent import UserAgent

class VintedScraper:
    def __init__(self, domain="vinted.fr"):
        self.domain = domain
        self.base_url = f"https://www.{domain}"
        self.api_url = f"https://www.{domain}/api/v2/catalog/items"
        self.session = requests.Session()
        self.ua = UserAgent()
        self.headers = {
            "User-Agent": self.ua.random,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        self._set_cookies()

    def _set_cookies(self):
        try:
            self.headers["User-Agent"] = self.ua.random
            response = self.session.get(self.base_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"[!] Erreur initialisation cookies: {response.status_code}")
        except Exception as e:
            print(f"[!] Erreur lors de la récupération des cookies: {e}")

    def search(self, params):
        try:
            time.sleep(random.uniform(0.5, 1.5))
            response = self.session.get(self.api_url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 401 or response.status_code == 403:
                print("[!] Session expirée ou bloquée, rafraîchissement des cookies...")
                self._set_cookies()
                response = self.session.get(self.api_url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json().get("items", [])
            else:
                print(f"[!] Erreur API: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"[!] Erreur lors de la recherche: {e}")
            return []

    def get_item_details(self, item_id):
        try:
            url = f"https://www.{self.domain}/api/v2/items/{item_id}"
            response = self.session.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json().get("item", {})
            return {}
        except Exception as e:
            print(f"[!] Erreur lors de la récupération des détails de l'item {item_id}: {e}")
            return {}

def filter_items(items, keywords, max_price, sizes):
    filtered = []
    for item in items:
        title = item.get("title", "").lower()
        # Gestion du prix qui peut être un dictionnaire ou une chaîne
        raw_price_data = item.get("total_item_price")
        if isinstance(raw_price_data, dict):
            price = float(raw_price_data.get("amount", 0))
        else:
            try:
                price = float(raw_price_data or 0)
            except:
                price = 0.0
        size = item.get("size_title", "").upper()
        
        if not any(kw.lower() in title for kw in keywords):
            continue
            
        if price > max_price:
            continue
            
        if size not in sizes:
            continue
            
        filtered.append(item)
    return filtered
