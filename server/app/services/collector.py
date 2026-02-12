# backend/app/services/collector.py
import os
from typing import List
from apify_client import ApifyClient

class TikTokCollector:
    def __init__(self):
        token = os.getenv("APIFY_API_TOKEN")
        if not token:
            print("WARNING: APIFY_API_TOKEN not found in .env")
            self.client = None
        else:
            self.client = ApifyClient(token)
            
        # Используем именно этот актор
        self.actor_id = "apidojo/tiktok-scraper"

    def collect(self, targets: List[str], limit: int = 30, mode: str = "search", is_deep: bool = False):
        """
        Режимы (mode):
        - "search": Ищет по ключевым словам.
        - "profile": Ищет видео конкретных юзеров.
        - "urls":   Сканирует СПИСОК КОНКРЕТНЫХ ВИДЕО (для рескана).
        """
        if not self.client or not targets:
            return []

        # 1. ЛИМИТЫ (ГИБКИЕ)
        final_limit = limit
        if mode == "urls":
            final_limit = len(targets) # Для рескана лимит строго равен числу ссылок
        
        print(f"[Collector] Mode: '{mode}', Deep: {is_deep}. Targets: {len(targets)}. Limit: {final_limit}")

        # Базовый конфиг
        run_input = {
            "maxItems": final_limit,
            "resultsPerPage": 100,
        }

        # 2. Логика формирования инпутов (АДАПТИРОВАНО ПОД STARTURLS)
        if mode == "urls":
            # --- РЕЖИМ РЕСКАНА (Точечные ссылки) ---
            print(f"[Collector] Scanning {len(targets)} URLs via startUrls (String format)...")
            
            # ВАЖНО: Актор требует наличие startUrls или keywords.
            # Мы передаем список строк (URL видео) в startUrls.
            run_input["startUrls"] = targets
            
            # Удаляем postURLs если он вдруг там был, чтобы не путать актора
            if "postURLs" in run_input: del run_input["postURLs"]
            
        elif mode == "profile":
            # --- РЕЖИМ ПРОФИЛЯ ---
            urls = []
            for t in targets:
                # Очистка юзернейма
                clean_nick = t.strip().replace("@", "").replace("https://www.tiktok.com/", "").strip("/")
                urls.append(f"https://www.tiktok.com/@{clean_nick}")
            
            # ERROR WAS HERE: Passed objects instead of strings
            # run_input["startUrls"] = [{"url": u} for u in urls]

            # FIX: Pass just a list of strings
            run_input["startUrls"] = urls
            
        else:
            # --- РЕЖИМ ПОИСКА (По умолчанию) ---
            run_input["keywords"] = targets
            run_input["searchSection"] = "top"
            # startUrls не нужен для поиска по ключевым словам
            if "startUrls" in run_input: del run_input["startUrls"]

        try:
            # 3. Запуск актера
            run = self.client.actor(self.actor_id).call(run_input=run_input)
            
            if not run:
                print("ERROR: Actor run failed")
                return []

            # 4. Получение результатов
            dataset = self.client.dataset(run["defaultDatasetId"])
            raw_items = list(dataset.iterate_items())
            print(f"[Apidojo] Received {len(raw_items)} raw items.")
            
            return raw_items

        except Exception as exc:
            print(f"WARNING: Apify error: {exc}")
            return []