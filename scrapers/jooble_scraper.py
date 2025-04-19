# scrapers/jooble_scraper.py

import requests
from bs4 import BeautifulSoup
from .base import JobScraper

class JoobleScraper(JobScraper):
    COUNTRY_DOMAINS = {
        "argentina": "ar",
        "mexico": "mx",
        "colombia": "co",
        "chile": "cl",
        "peru": "pe",
        "uruguay": "uy",
        "ecuador": "ec",
        "venezuela": "ve",
        "bolivia": "bo",
        "paraguay": "py",
        "panama": "pa",
    }

    def scrape(self, keywords, country, pages=1):
        cache_key = self._make_cache_key("jooble", keywords, country, pages)
        cached = self.get_cached(cache_key)
        if cached:
            return cached

        results = []
        headers = {"User-Agent": "Mozilla/5.0"}
        cc = self.COUNTRY_DOMAINS.get(country.lower(), "www")
        base_url = f"https://{cc}.jooble.org/jobs"

        for i in range(1, pages + 1):
            self._throttle()
            params = {"ukw": keywords, "p": i}
            proxy = self._get_next_proxy()
            proxies = proxy if proxy else None
            response = requests.get(base_url, headers=headers, params=params, proxies=proxies, timeout=20)
            soup = BeautifulSoup(response.text, "html.parser")

            for card in soup.select("article.single_job_listing"):
                title_el = card.select_one("h2")
                company_el = card.select_one("div.job_company")
                location_el = card.select_one("div.job_location")
                link_el = card.select_one("a")
                if title_el and company_el and location_el and link_el:
                    results.append({
                        "portal": "Jooble",
                        "title": title_el.get_text(strip=True),
                        "employer": company_el.get_text(strip=True),
                        "location": location_el.get_text(strip=True),
                        "contract": None,
                        "url": link_el.get("href")
                    })

        self.set_cache(cache_key, results)
        return results
