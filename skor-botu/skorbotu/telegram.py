"""Telegram Bot API ile mesaj gönderimi."""
from __future__ import annotations

import time

import requests


def send(token: str, chat_ids: list[str], parts: list[str]) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    for chat in chat_ids:
        for text in parts:
            r = requests.post(url, json={
                "chat_id": chat, "text": text, "parse_mode": "HTML",
                "disable_web_page_preview": True,
            }, timeout=30)
            if r.status_code != 200:
                raise RuntimeError(f"Telegram hatası ({chat}): {r.status_code} {r.text[:300]}")
            time.sleep(1)
