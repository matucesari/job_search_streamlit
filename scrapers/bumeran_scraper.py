# scrapers/bumeran_scraper.py

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base import JobScraper

class BumeranScraper(JobScraper):
    def scrape(self, keywords, country, pages=1):
        cache_key = self._make_cache_key("bumeran", keywords, country, pages)
        cached = self.get_cached(cache_key)
        if cached:
            return cached

        results = asyncio.run(self._scrape_async(keywords, country, pages))
        self.set_cache(cache_key, results)
        return results

    async def _scrape_async(self, keywords, country, pages):
        results = []
        url_base = f"https://www.bumeran.com.ar/empleos-busqueda-{keywords.replace(' ', '-')}.html"
        proxy = self._get_next_proxy()
        proxy_config = {"server": proxy["http"]} if proxy else None

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(proxy=proxy_config)
            page = await context.new_page()
            await page.goto(url_base, timeout=60000)

            for i in range(pages):
                self._throttle()
                await page.wait_for_timeout(3000)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(3000)
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")

                for card in soup.select(".aviso a.aviso_link"),:
                    title_el = card.select_one(".aviso_title")
                    company_el = card.select_one(".aviso_empresa")
                    location_el = card.select_one(".aviso_lugar")
                    if title_el and company_el and location_el:
                        results.append({
                            "portal": "Bumeran",
                            "title": title_el.get_text(strip=True),
                            "employer": company_el.get_text(strip=True),
                            "location": location_el.get_text(strip=True),
                            "contract": None,
                            "url": "https://www.bumeran.com.ar" + card.get("href")
                        })

            await context.close()
            await browser.close()
        return results
