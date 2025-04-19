# scrapers/computrabajo_scraper.py

import requests
from bs4 import BeautifulSoup
from .base import JobScraper

class ComputrabajoScraper(JobScraper):
    def scrape(self, keywords, country, pages=1):
        cache_key = self._make_cache_key("computrabajo", keywords, country, pages)
        cached = self.get_cached(cache_key)
        if cached:
            return cached

        base_url = f"https://www.computrabajo.com/{country.lower()}/ofertas-de-trabajo"
        headers = {"User-Agent": "Mozilla/5.0"}
        results = []

        for page in range(1, pages + 1):
            self._throttle()
            params = {"q": keywords, "p": page}
            proxy = self._get_next_proxy()
            proxies = proxy if proxy else None

            response = requests.get(base_url, headers=headers, params=params, proxies=proxies, timeout=20)
            soup = BeautifulSoup(response.text, "html.parser")

            for offer in soup.select("article.box_item"):
                title_el = offer.select_one("h1, h2")
                company_el = offer.select_one("a.it-emp")
                location_el = offer.select_one("p.fs12")
                contract_el = offer.select_one("span.b-tag")
                link_el = offer.select_one("a.js-o-link")
                if title_el and company_el and location_el and link_el:
                    results.append({
                        "portal": "Computrabajo",
                        "title": title_el.get_text(strip=True),
                        "employer": company_el.get_text(strip=True),
                        "location": location_el.get_text(strip=True),
                        "contract": contract_el.get_text(strip=True) if contract_el else None,
                        "url": "https://www.computrabajo.com" + link_el.get("href")
                    })

        self.set_cache(cache_key, results)
        return results
