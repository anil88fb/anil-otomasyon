"""Telegram Bot API ile mesaj ve dosya gönderimi."""
from __future__ import annotations

import time

import requests

API = "https://api.telegram.org/bot{token}/{method}"


def _check(r: requests.Response, chat: str) -> None:
    if r.status_code != 200:
        raise RuntimeError(f"Telegram hatası ({chat}): {r.status_code} {r.text[:300]}")


def send(token: str, chat_ids: list[str], parts: list[str], document: tuple[str, bytes] | None = None) -> None:
    for chat in chat_ids:
        for text in parts:
            r = requests.post(API.format(token=token, method="sendMessage"), json={
                "chat_id": chat, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True,
            }, timeout=30)
            _check(r, chat)
            time.sleep(1)
        if document:
            name, data = document
            r = requests.post(API.format(token=token, method="sendDocument"),
                              data={"chat_id": chat, "caption": "Tam bülten: tüm maçlar, oranlar ve eksik oyuncular"},
                              files={"document": (name, data, "text/html")}, timeout=60)
            _check(r, chat)
