# scrapers/indeed_scraper.py

import requests
from bs4 import BeautifulSoup
from .base import JobScraper

class IndeedScraper(JobScraper):
    def scrape(self, keywords, country, pages=1):
        cache_key = self._make_cache_key("indeed", keywords, country, pages)
        cached = self.get_cached(cache_key)
        if cached:
            return cached

        results = []
        headers = {"User-Agent": "Mozilla/5.0"}
        base_url = f"https://{country.lower()}.indeed.com/jobs"

        for i in range(pages):
            self._throttle()
            params = {"q": keywords, "start": i * 10}
            proxy = self._get_next_proxy()
            proxies = proxy if proxy else None
            response = requests.get(base_url, headers=headers, params=params, proxies=proxies, timeout=20)
            soup = BeautifulSoup(response.text, "html.parser")

            for card in soup.select("a.tapItem"):
                title_el = card.select_one("h2.jobTitle")
                company_el = card.select_one("span.companyName")
                location_el = card.select_one("div.companyLocation")
                if title_el and company_el and location_el:
                    results.append({
                        "portal": "Indeed",
                        "title": title_el.get_text(strip=True),
                        "employer": company_el.get_text(strip=True),
                        "location": location_el.get_text(strip=True),
                        "contract": None,
                        "url": "https://www.indeed.com" + card.get("href")
                    })

        self.set_cache(cache_key, results)
        return results
