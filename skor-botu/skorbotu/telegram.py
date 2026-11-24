"""Telegram Bot API ile mesaj ve dosya gönderimi (geçici hatalarda yeniden dener)."""
from __future__ import annotations

import time

import requests

API = "https://api.telegram.org/bot{token}/{method}"


def _post(token: str, method: str, chat: str, **kw) -> None:
    last = None
    for attempt in range(4):
        try:
            r = requests.post(API.format(token=token, method=method), timeout=(15, 90), **kw)
            if r.status_code == 200:
                return
            if r.status_code == 429:  # çok hızlı: Telegram'ın istediği kadar bekle
                time.sleep(r.json().get("parameters", {}).get("retry_after", 5) + 1)
                continue
            if 400 <= r.status_code < 500:  # yanlış anahtar/sohbet: tekrar denemek işe yaramaz
                raise RuntimeError(f"Telegram hatası ({chat}): {r.status_code} {r.text[:300]}")
            last = f"HTTP {r.status_code}"
        except requests.RequestException as e:
            last = e
        time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"Telegram'a gönderilemedi ({chat}): {last}")


def send(token: str, chat_ids: list[str], parts: list[str], document: tuple[str, bytes] | None = None) -> None:
    token = token.strip()
    for chat in chat_ids:
        for text in parts:
            _post(token, "sendMessage", chat, json={
                "chat_id": chat, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True,
            })
            time.sleep(1)
        if document:
            name, data = document
            _post(token, "sendDocument", chat,
                  data={"chat_id": chat, "caption": "Tam bülten: tüm maçlar, oranlar ve eksik oyuncular"},
                  files={"document": (name, data, "text/html")})
