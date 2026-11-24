"""Telegram ayarlarını denetler (anahtarı yazdırmaz)."""
import os
import re

import requests

tok = os.environ.get("TELEGRAM_TOKEN", "")
chat = os.environ.get("TELEGRAM_CHAT_ID", "")
print("anahtar uzunluğu:", len(tok), "| biçim uygun:", bool(re.fullmatch(r"\d{6,12}:[A-Za-z0-9_-]{30,}", tok)),
      "| baş/son boşluk:", tok != tok.strip())
print("sohbet kimliği biçimi uygun:", bool(re.fullmatch(r"-?\d{5,16}|@\w+", chat.strip())), "| boşluk:", chat != chat.strip())
for method, params in (("getMe", {}), ("getChat", {"chat_id": chat.strip()})):
    try:
        r = requests.get(f"https://api.telegram.org/bot{tok.strip()}/{method}", params=params, timeout=(15, 60))
        j = r.json()
        print(method, r.status_code, j.get("ok"), j.get("description", ""), (j.get("result") or {}).get("username", "") if method == "getMe" else "")
    except Exception as e:
        print(method, "HATA:", type(e).__name__, e)
